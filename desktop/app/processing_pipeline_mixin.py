"""Audio processing pipeline — mixed into RotaApp."""

from __future__ import annotations

import json
import re
import threading
import time

import structlog
from PyQt6.QtCore import Qt, QTimer, pyqtSlot

from app.logging_config import log_event
from app.processor_thread import ProcessorThread
from app.signal_bridges import RecordingState
from services.session_store import SessionRecord
from ui.overlay.pill_state import PillState
from utils.text_metrics import calculate_text_metrics

logger = structlog.get_logger(__name__)


class ProcessingPipelineMixin:
    """Audio → transcription → AI → injection pipeline for RotaApp."""

    def _start_streaming_processor(self, session):
        with self._processor_thread_lock:
            if self._processor_thread is not None and self._processor_thread.isRunning():
                logger.critical("processor_thread_already_running", correlation_id=session.id)
                raise RuntimeError("processing already active")

            ai_processor = self.ai_processor if self.config.get("ai_enabled") else None
            live_trans_enabled = bool(self.config.get("live_transcription_enabled", True))
            self._processor_thread = ProcessorThread(
                session,
                self.transcriber,
                ai_processor,
                live_transcription_enabled=live_trans_enabled,
            )
            self._processing_session_id = session.id
            self._processor_thread.partial.connect(
                self.on_partial_transcription, Qt.ConnectionType.QueuedConnection
            )
            self._processor_thread.completed.connect(
                self.on_processing_finished, Qt.ConnectionType.QueuedConnection
            )
            self._processor_thread.error.connect(
                self.on_processing_error, Qt.ConnectionType.QueuedConnection
            )
            self._processor_thread.finished.connect(
                lambda: self._cleanup_processor_thread(session.id),
                Qt.ConnectionType.QueuedConnection,
            )
            self._processor_thread.start()

    @pyqtSlot(str, str)
    def on_partial_transcription(self, partial_text: str, correlation_id: str):
        try:
            active_session_id = self._active_session.id if self._active_session else None
            if correlation_id != active_session_id:
                return
            self.overlay.set_partial_text(partial_text)
        except Exception:
            pass

    def _check_max_duration(self):
        pass  # Disabled: infinite recording

    def on_stop_recording(self):
        if self.state != RecordingState.LISTENING:
            logger.info("Stop ignored: invalid state=%s", self.state.value)
            log_event("hotkey_input", "ignored", action="stop", reason=f"state:{self.state.value}")
            return
        if not self.recorder.is_recording:
            self._set_error_state("state says recording but recorder is stopped")
            logger.warning("Recorder mismatch: state=LISTENING but recorder.is_recording=False")
            return

        session = self._active_session
        if session is None:
            self._set_error_state("no active session during stop")
            logger.error("stop_failed_missing_session")
            return
        self._set_state(RecordingState.PROCESSING, "hotkey stop", session.id)
        self._duration_timer.stop()
        recording_seconds = time.time() - session.start_time
        self._last_recording_seconds = recording_seconds
        log = logger.bind(correlation_id=session.id)
        log_event(
            "recording_end",
            duration_ms=recording_seconds * 1000.0,
            correlation_id=session.id,
        )

        try:
            self.recorder.stop(session)
        except Exception:
            self._set_error_state("recording stop failed", session.id)
            log.error("recording_stop_failed", exc_info=True)
            self.overlay.set_state(PillState.IDLE)
            self.show_toast(
                "Failed to stop recording — mic may have disconnected. Reconnect and try again",
                warning=True,
            )
            try:
                self.audio_controller.resume_or_unmute()
            except Exception as ae:
                logger.error("Failed to resume audio in stop error path", error=str(ae))
            return

        try:
            self.audio_controller.resume_or_unmute()
        except Exception as ae:
            logger.error("Failed to resume background audio", error=str(ae))

        self.overlay.set_state(PillState.TRANSCRIBING)

        if recording_seconds < 0.5:
            log.info("recording_ignored_too_short", duration_ms=round(recording_seconds * 1000, 2))
            self.show_toast("Recording too short. Hold the hotkey for at least half a second.")
            session.state = "DROPPED_TOO_SHORT"
            self._processing_timeout_timer.stop()
            if self._processor_thread is not None and self._processor_thread.isRunning():
                if not self._cancel_processor_thread(session, "short_recording"):
                    self.show_toast("Stopping processing took too long", warning=True)
                    self._refresh_debug_window()
                    return
            if self._processing_session_id == session.id:
                self._processing_session_id = None
            self._sessions.pop(session.id, None)
            self._cleanup_processor_thread(session.id)
            self._active_session = None
            self.overlay.set_state(PillState.IDLE)
            self._set_state(RecordingState.IDLE, "recording too short", session.id)
            self._latest_timings = {"recording_ms": f"{round(recording_seconds * 1000, 2)} ms"}
            self._refresh_debug_window()
            return

        log.info("processing_enqueued", recording_duration_ms=round(recording_seconds * 1000, 2))
        if self.transcriber is None:
            self._set_error_state("speech model unavailable", session.id)
            self.overlay.set_state(PillState.IDLE)
            self.show_toast(
                "Speech model not loaded yet — wait a moment and try again",
                warning=True,
            )
            self._refresh_debug_window()
            return

        if self._processor_thread is None:
            self._set_error_state("processing thread missing", session.id)
            self.overlay.set_state(PillState.IDLE)
            self.show_toast(
                "Processing thread unavailable. Restart the app if this persists.", warning=True
            )
            self._sessions.pop(session.id, None)
            self._active_session = None
            return

        session.mark_processing()
        self._processing_timeout_timer.start(30000)
        QTimer.singleShot(700, self._advance_overlay_to_processing)
        self._active_session = None

    def _advance_overlay_to_processing(self):
        if (
            self.state == RecordingState.PROCESSING
            and self.overlay.get_state() == PillState.TRANSCRIBING
        ):
            self.overlay.set_state(PillState.PROCESSING)

    @pyqtSlot(str, str, bool, str, float, float, bool, str)
    def on_processing_finished(
        self,
        raw,
        cleaned,
        is_prompt,
        correlation_id,
        transcription_seconds,
        ai_seconds,
        ai_failed,
        backend_used="",
    ):
        if correlation_id != self._processing_session_id:
            log_event(
                "processing_result", "ignored", correlation_id=correlation_id, reason="stale_result"
            )
            return
        log = logger.bind(correlation_id=correlation_id)
        try:
            session = self._sessions.get(correlation_id)
            if session and session.state == "DROPPED_TOO_SHORT":
                if self.transcriber is not None:
                    self.transcriber.consume_backend_event()
                log_event(
                    "processing_result",
                    "ignored",
                    correlation_id=correlation_id,
                    reason="dropped_too_short",
                )
                self._clear_processor_refs(correlation_id)
                return
            self._processing_timeout_timer.stop()
            if session:
                session.mark_completed(raw, cleaned)
            self._last_session_id = correlation_id
            self._maybe_notify_backend_fallback()
            self._latest_raw_text = raw or ""
            self._latest_cleaned_text = cleaned or ""
            if ai_failed:
                self.show_toast("AI cleanup unavailable. Raw transcript used.")
            if not cleaned:
                log.info("processing_completed_empty")
                self._sessions.pop(correlation_id, None)
                self.overlay.show_success("No speech detected")
                self._set_state(
                    RecordingState.SUCCESS, "empty transcription result", correlation_id
                )
                QTimer.singleShot(
                    450,
                    lambda: self._return_to_idle_if_state(
                        RecordingState.SUCCESS, "ready", correlation_id
                    ),
                )
                self._latest_timings = {
                    "recording_ms": f"{round(self._last_recording_seconds * 1000, 2)} ms",
                    "transcription_ms": f"{round(transcription_seconds * 1000, 2)} ms",
                    "ai_ms": f"{round(ai_seconds * 1000, 2)} ms",
                    "injection_ms": "0.0 ms",
                }
                self._refresh_debug_window()
                self._clear_processor_refs(correlation_id)
                return

            command_recognized, command_ok, handled_msg = self._handle_voice_edit_command(
                cleaned, correlation_id
            )
            if command_recognized and command_ok:
                self._sessions.pop(correlation_id, None)
                self.overlay.show_success("Edited")
                self._set_state(RecordingState.SUCCESS, "voice edit command", correlation_id)
                QTimer.singleShot(
                    450,
                    lambda: self._return_to_idle_if_state(
                        RecordingState.SUCCESS, "ready", correlation_id
                    ),
                )
                if handled_msg:
                    self.show_toast(handled_msg)
                self._latest_timings = {
                    "recording_ms": f"{round(self._last_recording_seconds * 1000, 2)} ms",
                    "transcription_ms": f"{round(transcription_seconds * 1000, 2)} ms",
                    "ai_ms": f"{round(ai_seconds * 1000, 2)} ms",
                    "injection_ms": "command_mode",
                }
                self._refresh_debug_window()
                self._clear_processor_refs(correlation_id)
                return
            if command_recognized and not command_ok:
                self._sessions.pop(correlation_id, None)
                self.overlay.show_error("Edit failed")
                self._set_state(RecordingState.IDLE, "voice edit failed", correlation_id)
                self._latest_timings = {
                    "recording_ms": f"{round(self._last_recording_seconds * 1000, 2)} ms",
                    "transcription_ms": f"{round(transcription_seconds * 1000, 2)} ms",
                    "ai_ms": f"{round(ai_seconds * 1000, 2)} ms",
                    "injection_ms": "command_failed",
                }
                self._refresh_debug_window()
                self.show_toast(handled_msg or "Could not apply edit command. Try again.")
                self._clear_processor_refs(correlation_id)
                return

            # --- INJECT FIRST — minimise perceived latency ---
            expanded = self.snippets.expand(cleaned)
            inject_text = expanded if expanded is not None else cleaned

            app_ctx = getattr(session, "app_context", None) if session else None
            is_terminal = app_ctx and getattr(app_ctx, "category", "") == "terminal"
            if is_terminal:
                logger.warning(
                    "injection_into_terminal",
                    correlation_id=correlation_id,
                    process=getattr(app_ctx, "process_name", ""),
                )

            log_event("injection_start", correlation_id=correlation_id)
            injection_start = time.perf_counter()
            field_info = session.field_info if session else None
            success, msg = self.injector.inject(
                inject_text,
                correlation_id=correlation_id,
                field_info=field_info,
                use_paste_shortcut=True,
            )
            if success:
                self.auto_improvement.track_injection(correlation_id, inject_text)
            else:
                self.show_toast("Could not paste. Click a text field first, then try again.")
            injection_seconds = time.perf_counter() - injection_start
            log_event(
                "injection_end",
                status="ok" if success else "degraded",
                duration_ms=injection_seconds * 1000.0,
                success=success,
                message=msg,
                correlation_id=correlation_id,
                transcription_duration_ms=round(transcription_seconds * 1000, 2),
                ai_duration_ms=round(ai_seconds * 1000, 2),
            )
            self._latest_timings = {
                "recording_ms": f"{round(self._last_recording_seconds * 1000, 2)} ms",
                "transcription_ms": f"{round(transcription_seconds * 1000, 2)} ms",
                "ai_ms": f"{round(ai_seconds * 1000, 2)} ms",
                "injection_ms": f"{round(injection_seconds * 1000, 2)} ms",
                "injection_success": str(success),
            }

            # Signal success to UI immediately after injection
            self._sessions.pop(correlation_id, None)
            self._maybe_notify_backend_fallback()
            self.overlay.show_success("Sent")
            self._set_state(RecordingState.SUCCESS, "processing finished", correlation_id)
            QTimer.singleShot(
                450,
                lambda: self._return_to_idle_if_state(
                    RecordingState.SUCCESS, "ready", correlation_id
                ),
            )
            self.overlay.set_state(PillState.DONE)
            self._clear_processor_refs(correlation_id)

            # --- Defer analytics to background thread (compute-heavy work off main thread) ---
            _recording_seconds = self._last_recording_seconds
            _main_window = self.main_window
            _history = self.history
            _session_store = self.session_store
            _insights_service = self.insights_service
            _update_metrics = self._update_metrics
            _refresh_debug = self._refresh_debug_window

            def _run_analytics():
                try:
                    _history.add_entry(raw, cleaned, is_prompt)
                    text_metrics = calculate_text_metrics(raw)

                    # Avoid full metrics calculation for cleaned — only need word count
                    cleaned_word_count = len(cleaned.split()) if cleaned else 0
                    if text_metrics.total_words > 0:
                        reduction = max(
                            0.0,
                            (text_metrics.total_words - cleaned_word_count)
                            / text_metrics.total_words,
                        )
                        text_metrics.conciseness_score = max(
                            30, min(100, int(round(100 - (reduction * 150))))
                        )
                    else:
                        text_metrics.conciseness_score = 100

                    # Pass precomputed metrics to avoid a third calculate_text_metrics call
                    insight = _insights_service.build_insight(raw, metrics=text_metrics)
                    started_at = session.start_time if session else time.time()
                    ended_at = time.time()
                    elapsed_minutes = max(1e-6, (ended_at - started_at) / 60.0)
                    words_per_minute = int(round(text_metrics.total_words / elapsed_minutes))

                    _app_ctx = getattr(session, "app_context", None) if session else None
                    app_ctx_dict = {}
                    if _app_ctx:
                        if hasattr(_app_ctx, "__dict__"):
                            app_ctx_dict = _app_ctx.__dict__
                        elif isinstance(_app_ctx, dict):
                            app_ctx_dict = _app_ctx

                    _session_store.add_session(
                        SessionRecord(
                            session_id=correlation_id,
                            started_at=started_at,
                            ended_at=ended_at,
                            recording_seconds=_recording_seconds,
                            words=text_metrics.total_words,
                            wpm=words_per_minute,
                            filler_ratio=text_metrics.filler_ratio,
                            clarity_score=text_metrics.clarity_score,
                            conciseness_score=text_metrics.conciseness_score,
                            insight_summary=insight.summary,
                            insight_suggestion=insight.suggestion,
                            transcript_text=raw or "",
                            backend_used=backend_used or "",
                            app_context=json.dumps(app_ctx_dict) if app_ctx_dict else "",
                            phrases_json=json.dumps(text_metrics.phrases)
                            if text_metrics.phrases
                            else "",
                        )
                    )

                    # Schedule UI updates back on the main thread
                    def _ui_updates():
                        try:
                            _update_metrics()
                            _main_window.update_insight(
                                insight.summary,
                                insight.suggestion,
                                insight.clarity_score,
                                insight.conciseness_score,
                            )
                            _main_window.refresh_history(highlight_latest=True)
                            if hasattr(_main_window, "_dict_refresh"):
                                _main_window._dict_refresh()
                            _refresh_debug()
                        except Exception:
                            pass

                    QTimer.singleShot(0, _ui_updates)
                except Exception:
                    logger.warning("analytics_thread_failed", exc_info=True)

            threading.Thread(target=_run_analytics, daemon=True).start()
        except Exception as _exc:
            _err_msg = str(_exc)
            logger.error(
                "on_processing_finished_failed", correlation_id=correlation_id, exc_info=True
            )
            for fn in [
                lambda: self._sessions.pop(correlation_id, None),
                lambda: self.overlay.show_error("Processing failed"),
                lambda: self._set_state(
                    RecordingState.IDLE, f"processing finished error: {_err_msg}", correlation_id
                ),
                lambda: self.overlay.set_state(PillState.IDLE),
                lambda: self._clear_processor_refs(correlation_id),
                lambda: self._refresh_debug_window(),
                lambda: self.show_toast(
                    f"Processing error: {_err_msg[:60]} — check the error log in the app",
                    warning=True,
                ),
            ]:
                try:
                    fn()
                except Exception:
                    pass

    def _handle_voice_edit_command(
        self, cleaned_text: str, correlation_id: str
    ) -> tuple[bool, bool, str]:
        text = (cleaned_text or "").strip()
        if not text:
            return False, False, ""

        lowered = text.lower()
        if lowered in {"scratch that", "scratch that.", "scratch that!"}:
            ok, msg = self.injector.scratch_that(correlation_id=correlation_id)
            log_event(
                "voice_edit_scratch",
                status="ok" if ok else "failed",
                correlation_id=correlation_id,
                message=msg,
            )
            self._maybe_notify_backend_fallback()
            return True, ok, msg

        match = re.match(r"^\s*change\s+(.+?)\s+to\s+(.+?)\s*[.!?]?\s*$", text, flags=re.IGNORECASE)
        if match:
            old_text = match.group(1).strip().strip("\"'\u201c\u201d")
            new_text = match.group(2).strip().strip("\"'\u201c\u201d")
            ok, msg = self.injector.replace_last_injected(
                old_text, new_text, correlation_id=correlation_id
            )
            log_event(
                "voice_edit_change",
                status="ok" if ok else "failed",
                correlation_id=correlation_id,
                old_text=old_text,
                new_text=new_text,
                message=msg,
            )
            self._maybe_notify_backend_fallback()
            return True, ok, msg

        return False, False, ""

    def _maybe_notify_backend_fallback(self):
        if self.transcriber is None:
            return
        backend, reason = self.transcriber.consume_backend_event()
        if backend != "local" or not reason:
            return
        reason_lower = reason.lower()
        if reason_lower.startswith("latency="):
            self.show_toast("Groq slow. Switched to local transcription.")
            return
        if any(
            token in reason_lower
            for token in ("429", "rate", "quota", "limit", "too many requests")
        ):
            self.show_toast(
                "Groq rate limit reached. Switched to local transcription. Try again in a minute."
            )
            return
        self.show_toast("Groq unavailable. Switched to local transcription.")

    @pyqtSlot(str, str, str)
    def on_processing_error(self, err_msg, correlation_id, traceback_text):
        if correlation_id != self._processing_session_id:
            log_event(
                "processing_result", "ignored", correlation_id=correlation_id, reason="stale_error"
            )
            return
        self._processing_timeout_timer.stop()
        session = self._sessions.get(correlation_id)
        if session:
            session.mark_failed()
        log_event(
            "processing_failed",
            status="failed",
            correlation_id=correlation_id,
            error=err_msg,
            traceback=traceback_text,
        )
        self._set_error_state("processing thread error", correlation_id)
        self._last_session_id = correlation_id
        self._latest_timings = {
            "recording_ms": f"{round(self._last_recording_seconds * 1000, 2)} ms",
            "error": err_msg,
        }
        self.overlay.show_error("Could not process recording")
        self.main_window.set_error_details(err_msg)
        self._refresh_debug_window()
        self._maybe_notify_backend_fallback()
        self.show_toast(
            f"Processing failed: {err_msg[:60]} — see full details in the app",
            warning=True,
        )
        self._sessions.pop(correlation_id, None)
        self._clear_processor_refs(correlation_id)
        QTimer.singleShot(
            1000,
            lambda: self._return_to_idle_if_state(
                RecordingState.ERROR, "ready after error", correlation_id
            ),
        )
