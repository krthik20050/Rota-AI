import os
import sys
import structlog

logger = structlog.get_logger(__name__)

_IS_WINDOWS = sys.platform == "win32"

if _IS_WINDOWS:
    from injection.app_detector import get_active_app
else:
    def get_active_app():
        return None

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
        self._playerctl_paused = False  # Linux: paused via playerctl

    def _get_master_volume_interface(self):
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
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

    def _playerctl_cmd(self, cmd: str) -> bool:
        """Run a playerctl command (pause/play/play-pause). Returns True on success.

        playerctl uses MPRIS2 D-Bus protocol, supported by:
        Spotify, VLC, mpv, Firefox (with extension), Chromium, Rhythmbox, etc.
        """
        import shutil
        import subprocess
        if not shutil.which("playerctl"):
            return False
        try:
            result = subprocess.run(
                ["playerctl", cmd],
                timeout=3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning("playerctl_cmd_failed", cmd=cmd, error=str(e))
            return False

    def _playerctl_is_playing(self) -> bool:
        """Return True if any MPRIS2 player reports 'Playing' status."""
        import shutil
        import subprocess
        if not shutil.which("playerctl"):
            return False
        try:
            result = subprocess.run(
                ["playerctl", "status"],
                timeout=3, capture_output=True,
            )
            return result.stdout.decode(errors="replace").strip() == "Playing"
        except Exception:
            return False

    def _pactl_active_media_pids(self) -> set:
        """
        Parse 'pactl list sink-inputs' to find PIDs of known media processes
        actively routing audio to the default sink. Catches browsers and apps
        that bypass MPRIS (e.g. Chrome playing YouTube, Spotify web player).
        Returns an empty set when pactl is unavailable or nothing is playing.
        """
        import re
        import shutil
        import subprocess
        if not shutil.which("pactl"):
            return set()
        try:
            result = subprocess.run(
                ["pactl", "list", "sink-inputs"],
                capture_output=True, timeout=5,
            )
            if result.returncode != 0:
                return set()
            output = result.stdout.decode(errors="replace")
            pids: set = set()
            current_pid = None
            for line in output.splitlines():
                line = line.strip()
                # Grab PID line: application.process.id = "1234"
                m = re.match(r'application\.process\.id\s*=\s*"(\d+)"', line)
                if m:
                    current_pid = int(m.group(1))
                    continue
                # Grab binary name and check if it's a known media process
                m2 = re.match(r'application\.process\.binary\s*=\s*"([^"]+)"', line)
                if m2 and current_pid is not None:
                    binary = m2.group(1).lower()
                    # Match against the .exe list (works because _is_media_process strips .exe)
                    if (self._is_media_process(binary + ".exe") or
                            self._is_media_process(binary)):
                        pids.add(current_pid)
                    current_pid = None
            return pids
        except Exception as e:
            logger.warning("pactl_list_sink_inputs_failed", error=str(e))
            return set()

    def _pactl_mute(self, mute: bool) -> bool:
        """Mute/unmute the default sink via pactl (Linux). Returns True on success."""
        import shutil
        import subprocess
        if not shutil.which("pactl"):
            return False
        try:
            val = "1" if mute else "0"
            result = subprocess.run(
                ["pactl", "set-sink-mute", "@DEFAULT_SINK@", val],
                timeout=3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning("pactl_mute_failed", mute=mute, error=str(e))
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
                if not _IS_WINDOWS:
                    if self._pactl_mute(True):
                        self._muted_by_us = True
                        logger.debug("master_volume_muted_pactl")
                else:
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
                    if _IS_WINDOWS and self._has_playing_media_session():
                        logger.info("media_session_detected_pausing")
                        import win32api, win32con
                        win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
                        win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0)
                        self._media_paused = True
                    elif not _IS_WINDOWS:
                        # Linux: try playerctl (MPRIS2) first — pauses only active player.
                        # If no MPRIS player is found, check pactl sink-inputs for non-MPRIS
                        # media (browsers playing YouTube, web Spotify, etc.).
                        if self._playerctl_is_playing():
                            if self._playerctl_cmd("pause"):
                                self._playerctl_paused = True
                                logger.info("media_paused_via_playerctl")
                            else:
                                # playerctl found but failed; mute via pactl
                                if self._pactl_mute(True):
                                    self._muted_by_us = True
                                    logger.info("media_muted_via_pactl_fallback")
                        else:
                            # Check for non-MPRIS media playing (browser tabs, etc.)
                            media_pids = self._pactl_active_media_pids()
                            if media_pids:
                                logger.info("non_mpris_media_detected_muting", pids=list(media_pids))
                                if self._pactl_mute(True):
                                    self._muted_by_us = True
                                    logger.info("media_muted_via_pactl_non_mpris")
                            else:
                                logger.info("bg_audio_control_skipped_linux",
                                            reason="no_media_playing")
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

            if self._playerctl_paused:
                try:
                    self._playerctl_cmd("play")
                    logger.info("media_resumed_via_playerctl")
                except Exception as e:
                    logger.error("failed_to_resume_playerctl", error=str(e))
                self._playerctl_paused = False

            if self._muted_by_us:
                if not _IS_WINDOWS:
                    self._pactl_mute(False)
                    logger.debug("master_volume_unmuted_pactl")
                else:
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
                    if _IS_WINDOWS:
                        import win32api, win32con
                        win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
                        win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0)
                except Exception as e:
                    logger.error("failed_to_resume_media", error=str(e))
                self._media_paused = False

        except Exception as exc:
            logger.error("unhandled_audio_controller_resume_failure", error=str(exc))
