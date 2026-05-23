"""Hotkey handling and recording start — mixed into RotaApp."""
from __future__ import annotations

import uuid

import structlog
from PyQt6.QtCore import pyqtSlot

from app.signal_bridges import RecordingState
from app.logging_config import log_event
from audio.recording_session import RecordingSession
from injection.field_detector import (
    get_focused_field_info,
    warn_no_text_field_banner,
    scan_for_text_inputs,
    focus_text_input,
)
from ui.overlay.pill_state import PillState

logger = structlog.get_logger(__name__)


class HotkeyMixin:
    """Hotkey dispatch and recording start/cancel for RotaApp."""

    @pyqtSlot()
    def _handle_hotkey_start(self):
        if self.state == RecordingState.ERROR:
            logger.info("Recovering from ERROR state to IDLE")
            self._set_state(RecordingState.IDLE, "error_recovery")
            self.main_window.update_state("IDLE")
            self.main_window.set_error_details("")
        if self.state not in (RecordingState.IDLE, RecordingState.ERROR):
            logger.info("Ignoring hotkey start in state=%s", self.state.value)
            return
        if not self._recording_enabled:
            self.show_toast("F9 unavailable until startup checks pass — wait a moment")
            return
        self._dispatch_pipeline_action("start")

    @pyqtSlot()
    def _handle_hotkey_stop(self):
        if self.state != RecordingState.LISTENING:
            logger.info("Ignoring hotkey stop in state=%s", self.state.value)
            return
        self._dispatch_pipeline_action("stop")

    @pyqtSlot()
    def _cancel_recording(self):
        if self.state != RecordingState.LISTENING:
            return
        session = self._active_session
        if session is None:
            return
        log_event("recording_cancel", correlation_id=session.id)
        try:
            self.recorder.stop(session)
        except Exception:
            pass
        try:
            self.audio_controller.resume_or_unmute()
        except Exception:
            pass
        if self._processor_thread is not None and self._processor_thread.isRunning():
            self._cancel_processor_thread(session, "user_cancel")
        self._sessions.pop(session.id, None)
        self._active_session = None
        self._duration_timer.stop()
        self._processing_timeout_timer.stop()
        self._processing_session_id = None
        self._processor_thread = None
        self.overlay.set_state(PillState.IDLE)
        self._set_state(RecordingState.IDLE, "user_cancel", session.id)

    def _setup_tray_connections(self):
        self.tray.open_action.triggered.connect(self.show_main_window)
        self.tray.settings_action.triggered.connect(self.show_settings)
        self.tray.mode_action.triggered.connect(self.toggle_mode)
        self.tray.ai_action.triggered.connect(self.toggle_ai)
        self.tray.exit_action.triggered.connect(self.exit_app)
        self.tray.update_status(self.config.get("hotkey_mode"), self.config.get("ai_enabled"))
        self.tray.show()

    def show_main_window(self):
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
        logger.info("main_window_focus_requested", visible=self.main_window.isVisible())

    def _on_instance_wake_ready(self, *_args):
        if self._instance_listen_sock is None:
            return
        try:
            conn, _addr = self._instance_listen_sock.accept()
        except (BlockingIOError, OSError):
            return
        try:
            conn.settimeout(0.5)
            try:
                data = conn.recv(64)
            finally:
                conn.close()
            if data.startswith(b"ROTA_WAKE_MAIN"):
                self.show_main_window()
                logger.info("instance_wake_signal_handled")
        except OSError:
            pass

    def on_start_recording(self):
        if self.state != RecordingState.IDLE:
            logger.info("Start ignored: invalid state=%s", self.state.value)
            log_event("hotkey_input", "ignored", action="start", reason=f"state:{self.state.value}")
            return
        if self._processor_thread is not None and self._processor_thread.isRunning():
            logger.warning("start_blocked_processor_alive")
            self.show_toast("Processing is still stopping — wait a moment")
            return
        if not self._recording_enabled:
            self.show_toast("Recording is disabled — restart the app if this persists", warning=True)
            return
        if self.transcriber is None:
            if not self._transcriber_loading:
                self._load_transcriber_async(self._current_model_size)
            self._update_readiness_status()
            self.show_toast("Speech model is still loading — try again in a few seconds")
            return

        session = RecordingSession(id=str(uuid.uuid4()))
        try:
            log_event("recording_start", correlation_id=session.id)
            field_info = get_focused_field_info()
            session.field_info = field_info
            fc = field_info.get("focused_class", "") or "unknown"
            logger.debug(
                "field_detected",
                exe_name=field_info.get("exe_name", ""),
                is_text_field=field_info.get("is_text_field"),
                focused_class=fc,
            )
            try:
                from injection.field_reader import get_field_text
                session.field_text = get_field_text()
                if session.field_text:
                    logger.debug("field_text_captured", char_count=len(session.field_text))
                    self.auto_improvement.analyze_field_for_corrections(session.field_text)
            except Exception:
                session.field_text = ""
            try:
                from injection.app_detector import get_active_app
                session.app_context = get_active_app()
            except Exception:
                session.app_context = None
            if not field_info.get("is_text_field"):
                warn_no_text_field_banner(field_info.get("exe_name") or "")
                text_inputs = scan_for_text_inputs(field_info.get("hwnd") or 0)
                if text_inputs:
                    auto_focused = focus_text_input(text_inputs[0])
                    if auto_focused:
                        logger.info(
                            "auto_focused_text_input",
                            class_name=text_inputs[0].get("class_name"),
                            area=text_inputs[0].get("area"),
                        )
                        self.show_toast("Auto-selected text field — speak now")
                        session.field_info = get_focused_field_info()
                    else:
                        self.show_toast(
                            "Could not auto-focus text field — recording anyway. Click a text box before speaking",
                            warning=True,
                        )
                else:
                    self.show_toast(
                        "No text field found — click a text box first, then press F9",
                        warning=True,
                    )
                    logger.warning("no_text_inputs_found_in_window", exe=field_info.get("exe_name"))
            try:
                self.audio_controller.pause_or_mute()
            except Exception as ae:
                logger.error("Failed to pause background audio during start", error=str(ae))

            self.recorder.start(session)
            self._active_session = session
            self._sessions[session.id] = session
            self._last_session_id = session.id
            self._start_time = session.start_time
            self._set_state(RecordingState.LISTENING, "hotkey start", session.id)
            self.overlay.set_state(PillState.RECORDING)
            self.overlay.show_overlay()
            self._duration_timer.start(1000)
            self._start_streaming_processor(session)
            self._refresh_debug_window()
        except Exception as exc:
            try:
                self.audio_controller.resume_or_unmute()
            except Exception as ae:
                logger.error("Failed to resume audio in start failure", error=str(ae))
            self._set_error_state("recording start failed", session.id)
            logger.error("recording_start_failed", correlation_id=session.id, exc_info=True)
            try:
                self.recorder.stop(session)
            except Exception:
                pass
            self.overlay.set_state(PillState.IDLE)
            self.show_toast(self._friendly_start_error_message(exc), warning=True)
