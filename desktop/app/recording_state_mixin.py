"""Recording state machine — mixed into RotaApp."""
from __future__ import annotations

import time

import structlog
from PyQt6.QtCore import QTimer

from app.signal_bridges import RecordingState
from app.logging_config import log_event
from ui.overlay.pill_state import PillState

logger = structlog.get_logger(__name__)


class RecordingStateMixin:
    """State machine helpers for RotaApp."""

    def _set_state(self, new_state, reason="", session_id=None):
        allowed_transitions = {
            RecordingState.IDLE: {RecordingState.LISTENING, RecordingState.ERROR},
            RecordingState.LISTENING: {RecordingState.PROCESSING, RecordingState.ERROR},
            RecordingState.PROCESSING: {RecordingState.SUCCESS, RecordingState.ERROR, RecordingState.IDLE},
            RecordingState.SUCCESS: {RecordingState.IDLE, RecordingState.ERROR},
            RecordingState.ERROR: {RecordingState.IDLE},
        }

        with self._state_lock:
            old_state = self.state
            if old_state == new_state:
                log_event(
                    "state_change",
                    "ignored",
                    from_state=old_state.value,
                    to_state=new_state.value,
                    reason=reason,
                    session_id=session_id,
                )
                return False

            if new_state not in allowed_transitions.get(old_state, set()):
                log_event(
                    "state_change",
                    "ignored",
                    from_state=old_state.value,
                    to_state=new_state.value,
                    reason=f"invalid_transition:{reason}",
                    session_id=session_id,
                )
                return False

            self.state = new_state
            self._last_session_id = session_id or self._last_session_id
            log_event(
                "state_change",
                "success",
                from_state=old_state.value,
                to_state=new_state.value,
                reason=reason,
                session_id=session_id,
            )

        if new_state != RecordingState.ERROR:
            self.main_window.set_error_details("")
        self._refresh_debug_window()
        return True

    def _set_error_state(self, reason, session_id=None):
        self._set_state(RecordingState.ERROR, reason, session_id)
        QTimer.singleShot(500, self._auto_recover_from_error)

    def _auto_recover_from_error(self):
        if self.state == RecordingState.ERROR:
            logger.info("auto_recovery_from_error")
            self._set_state(RecordingState.IDLE, "auto_recovery")
            self.main_window.update_state("IDLE")
            self.main_window.set_error_details("")
            self.overlay.set_state(PillState.IDLE)

    def _should_ignore_hotkey_trigger(self, action: str) -> bool:
        now = time.monotonic()
        if now - self._hotkey_last_trigger_at < self._hotkey_debounce_seconds:
            log_event("hotkey_input", "ignored", action=action, reason="debounce")
            return True
        self._hotkey_last_trigger_at = now
        return False

    def _on_processing_timeout(self):
        thread = self._processor_thread
        if thread is None or not thread.isRunning() or self.state != RecordingState.PROCESSING:
            return

        session_id = self._processing_session_id or self._last_session_id
        log_event(
            "processing_timeout",
            "fail",
            session_id=session_id,
            reason="transcription timeout after 30s",
        )
        self._set_error_state("Transcription timed out", session_id)
        self.overlay.set_state(PillState.IDLE)
        self.main_window.set_error_details("Transcription timed out")
        self.show_toast(
            "Transcription timed out — try a shorter recording or switch to a smaller model in Settings",
            warning=True,
        )

        try:
            thread.requestInterruption()
            thread.quit()
            if not thread.wait(500):
                logger.critical("processor_thread_hard_cancel", correlation_id=session_id)
                thread.terminate()
                thread.wait(500)
        finally:
            self._cleanup_processor_thread(session_id)

    def _return_to_idle_if_state(self, expected_state, reason, session_id=None):
        if self.state == expected_state:
            self._set_state(RecordingState.IDLE, reason, session_id)

    def _friendly_start_error_message(self, exc):
        text = str(exc).lower()
        mic_indicators = ("audio", "input", "micro", "mic", "sounddevice", "portaudio", "device")
        if any(token in text for token in mic_indicators):
            return "No mic detected — check your microphone is connected and not in use by another app"
        return "Could not start recording — check mic permissions in Windows Settings > Privacy > Microphone"
