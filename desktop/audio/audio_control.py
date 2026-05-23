import os
import structlog
import win32api
import win32con
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

from injection.app_detector import get_active_app

logger = structlog.get_logger(__name__)

MEDIA_PROCESS_NAMES = {
    "spotify.exe",
    "vlc.exe",
    "wmplayer.exe",
    "music.ui.exe",
    "itunes.exe",
    # Web Browsers (often used for playing YouTube, Spotify Web, Netflix, etc.)
    "chrome.exe",
    "msedge.exe",
    "firefox.exe",
    "brave.exe",
    "opera.exe",
    "vivaldi.exe",
    "arc.exe",
    "librewolf.exe",
    "floorp.exe",
    "waterfox.exe",
    "browser.exe",
    # Additional Media Players
    "foobar2000.exe",
    "aimp.exe",
    "plex.exe",
    "resonic.exe",
    "mpv.exe",
    "potplayermini64.exe",
    "potplayer.exe",
    "kmplayer.exe",
    "gomp.exe",
    "deezer.exe",
    "tidal.exe",
    "qobuz.exe",
    "amazonmusic.exe",
    "applemusic.exe",
}


class SystemAudioController:
    """
    Manages system background audio during recording:
    - Master Muting: Mutes/unmutes Windows master volume via pycaw.
    - Pause Media: Pauses/resumes active background players (Spotify, YouTube, browser)
      via virtual media keyboard simulation.

    IMPORTANT: Do NOT call comtypes.CoInitialize/CoUninitialize here.
    pycaw manages COM initialization internally per-thread. Calling CoUninitialize
    after using pycaw COM objects invalidates their internal proxies and causes crashes.
    """

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self._muted_by_us = False
        self._media_paused = False

    def _get_master_volume_interface(self):
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            if not devices:
                return None
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            return cast(interface, POINTER(IAudioEndpointVolume))
        except Exception as e:
            logger.warning("failed_to_get_master_volume_interface", error=str(e))
            return None

    def _is_media_process(self, process_name: str) -> bool:
        return (process_name or "").lower() in MEDIA_PROCESS_NAMES

    def _has_playing_media_session(self) -> bool:
        """
        Returns True if any known media app has an active audio session with
        measurable audio output (i.e. is actually playing, not just paused/idle).

        Uses a very low peak threshold (0.0001) so music playing at any audible
        volume is detected, while truly silent/paused sessions are skipped.
        """
        try:
            from pycaw.pycaw import AudioUtilities, IAudioMeterInformation
            sessions = AudioUtilities.GetAllSessions()
        except Exception as e:
            logger.error("failed_to_inspect_audio_sessions", error=str(e))
            return False

        for session in sessions:
            if session.State != 1:  # AudioSessionStateActive
                continue

            process = session.Process
            if process is None:
                continue

            try:
                if process.pid == os.getpid():
                    continue
            except Exception:
                pass

            try:
                process_name = process.name().lower()
            except Exception:
                continue

            if not self._is_media_process(process_name):
                continue

            # Check if actually producing audio (any measurable output = playing)
            try:
                from pycaw.pycaw import IAudioMeterInformation
                meter = session._ctl.QueryInterface(IAudioMeterInformation)
                peak = meter.GetPeakValue()
                if peak > 0.0001:
                    logger.info("playing_media_detected", process=process_name, peak=round(float(peak), 5))
                    return True
            except Exception:
                # If we can't read the meter, assume it's playing to be safe
                logger.debug("meter_read_failed_assuming_playing", process=process_name)
                return True

        return False

    def _has_active_media_session(self) -> bool:
        """
        Returns True if any known media app has an active audio session
        (regardless of whether audio is currently playing or paused).
        Used when we want to always pause media that could play.
        """
        try:
            from pycaw.pycaw import AudioUtilities
            sessions = AudioUtilities.GetAllSessions()
        except Exception as e:
            logger.error("failed_to_inspect_audio_sessions", error=str(e))
            return False

        for session in sessions:
            if session.State != 1:  # AudioSessionStateActive
                continue

            process = session.Process
            if process is None:
                continue

            try:
                if process.pid == os.getpid():
                    continue
            except Exception:
                pass

            try:
                process_name = process.name().lower()
            except Exception:
                continue

            if self._is_media_process(process_name):
                logger.info("active_media_session_found", process=process_name)
                return True

        return False

    def pause_or_mute(self):
        """
        Called when recording starts. Pauses or mutes background audio.
        Never raises — audio control failure must not block recording.
        """
        try:
            mode = self.config_manager.get("bg_audio_control", "pause")
            if mode == "none" or mode is None:
                return

            logger.info("bg_audio_control_start", mode=mode)

            if mode == "mute":
                volume = self._get_master_volume_interface()
                if volume:
                    try:
                        if not bool(volume.GetMute()):
                            volume.SetMute(1, None)
                            self._muted_by_us = True
                            logger.debug("master_volume_muted")
                    except Exception as e:
                        logger.error("failed_to_mute_master_volume", error=str(e))

            elif mode == "pause":
                try:
                    # Use active session check (not peak-based) so we catch any
                    # media app that is open and could be playing.
                    # If it's actually playing → pause it.
                    # If it's already paused → sending the key starts it, then
                    #   resume sends the key again → ends up paused. Net: safe.
                    if self._has_playing_media_session():
                        logger.info("media_session_detected_pausing")
                        win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
                        win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0)
                        self._media_paused = True
                    else:
                        logger.info("bg_audio_control_skipped", mode=mode, reason="no_playing_media_session")
                except Exception as e:
                    logger.error("failed_to_pause_media", error=str(e))

        except Exception as exc:
            logger.error("unhandled_audio_controller_pause_failure", error=str(exc))

    def resume_or_unmute(self):
        """
        Called when recording stops. Resumes or unmutes background audio.
        Never raises — audio control failure must not block transcription.
        """
        try:
            mode = self.config_manager.get("bg_audio_control", "pause")
            if mode == "none" or mode is None:
                return

            logger.info("bg_audio_control_stop", mode=mode)

            if mode == "mute" and self._muted_by_us:
                volume = self._get_master_volume_interface()
                if volume:
                    try:
                        volume.SetMute(0, None)
                        logger.debug("master_volume_unmuted")
                    except Exception as e:
                        logger.error("failed_to_unmute_master_volume", error=str(e))
                self._muted_by_us = False

            elif mode == "pause" and self._media_paused:
                try:
                    logger.info("resuming_media")
                    win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
                    win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0)
                except Exception as e:
                    logger.error("failed_to_resume_media", error=str(e))
                self._media_paused = False

        except Exception as exc:
            logger.error("unhandled_audio_controller_resume_failure", error=str(exc))
