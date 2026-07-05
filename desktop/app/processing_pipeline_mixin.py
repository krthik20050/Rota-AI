"""Audio processing pipeline — mixed into RotaApp."""

from __future__ import annotations

import json
import re
import threading
import time

import structlog
from PySide6.QtCore import Qt, QTimer, Slot

from app.logging_config import log_event
from app.processor_thread import (
    FAIL_CANCELLED,
    FAIL_GROQ_AUTH,
    FAIL_GROQ_ERROR,
    FAIL_GROQ_RATE_LIMIT,
    FAIL_GROQ_TIMEOUT,
    FAIL_TIMEOUT,
    FAIL_UNKNOWN,
    FAILURE_MESSAGES,
    ProcessorThread,
)
from app.signal_bridges import RecordingState
from audio.vad import FAIL_VAD_NO_SPEECH
from injection.field_reader import read_focused_field_text
from services.session_store import SessionRecord
from telemetry.latency_tracker import SessionTimings
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
            # error signal now includes failure_code as 4th argument
            self._processor_thread.error.connect(
                self.on_processing_error, Qt.ConnectionType.QueuedConnection
            )
            self._processor_thread.finished.connect(
                lambda: self._cleanup_processor_thread(session.id),
                Qt.ConnectionType.QueuedConnection,
            )
            self._processor_thread.start()

    @Slot(str, str)
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

        # Read existing field text for AI context BEFORE processor thread starts
        # (the processor reads session.field_text during process_text())
        try:
            session.field_text = read_focused_field_text()
        except Exception:
            session.field_text = ""

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
        # Scale processing timeout with recording duration so very long recordings
        # (>60s) don't get killed mid-transcription. Minimum 30s, scales to 2x
        # recording duration (capped at 300s / 5 min max wait).
        scaled_timeout = max(30000, min(int(recording_seconds * 2000), 300000))
        self._processing_timeout_timer.start(scaled_timeout)
        QTimer.singleShot(700, self._advance_overlay_to_processing)
        self._active_session = None

    def _advance_overlay_to_processing(self):
        if (
            self.state == RecordingState.PROCESSING
            and self.overlay.get_state() == PillState.TRANSCRIBING
        ):
            self.overlay.set_state(PillState.PROCESSING)

    @Slot(str, str, bool, str, float, float, bool, str)
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

            # Notify user when injecting long text so they know data wasn't lost
            _inject_chars = len(inject_text)
            _is_long_injection = _inject_chars > 8000  # ~1500 words

            # Per-app config: override settings based on active app
            app_ctx = getattr(session, "app_context", None) if session else None
            if app_ctx:
                app_name = getattr(app_ctx, "process_name", "") or getattr(app_ctx, "app_name", "")
                per_app = self.config.get("per_app_config", {}).get(app_name, {})
                if per_app and self.ai_processor is not None:
                    if "writing_mode" in per_app:
                        self.ai_processor.writing_mode = per_app["writing_mode"]
                    if "ai_provider" in per_app:
                        self.ai_processor.ai_provider = per_app["ai_provider"]

            is_terminal = app_ctx and getattr(app_ctx, "category", "") == "terminal"
            if is_terminal:
                logger.warning(
                    "injection_into_terminal",
                    correlation_id=correlation_id,
                    process=getattr(app_ctx, "process_name", ""),
                )

            # Cursor marker split injection: if {{cursor}} is in the text,
            # inject only the part before {{cursor}} — the cursor stays there
            cursor_marker = (
                self.snippets.cursor_marker()
                if hasattr(self.snippets, "cursor_marker")
                else "__CURSOR_MARKER__"
            )
            cursor_split_tail = None
            if cursor_marker in inject_text:
                parts = inject_text.split(cursor_marker, 1)
                inject_text = parts[0]
                if len(parts) > 1 and parts[1]:
                    cursor_split_tail = parts[1]

            log_event("injection_start", correlation_id=correlation_id)
            injection_start = time.perf_counter()
            field_info = session.field_info if session else None
            try:
                success, msg = self.injector.inject(
                    inject_text,
                    correlation_id=correlation_id,
                    field_info=field_info,
                    use_paste_shortcut=True,
                )
            finally:
                # Defer clipboard restore to keep the UI responsive — the
                # injector's time.sleep(restore_delay) (up to 800ms for long
                # text) runs on the next Qt event loop tick, not blocking.
                # Scheduled in finally so it always runs, even if inject()
                # raises an unexpected exception.
                if hasattr(self.injector, "restore_clipboard"):
                    QTimer.singleShot(0, self.injector.restore_clipboard)
            # If there's text after cursor, store it for optional paste
            if cursor_split_tail:
                # Store remaining text so Ctrl+V after injection pastes it
                try:
                    import pyperclip

                    pyperclip.copy(cursor_split_tail)
                except Exception:
                    pass
                QTimer.singleShot(
                    100,
                    lambda: self.show_toast(
                        "Cursor placed — paste (Ctrl+V) to insert remaining text"
                    ),
                )
            if success:
                self.auto_improvement.track_injection(correlation_id, inject_text)
                if _is_long_injection:
                    self.show_toast(
                        f"{len(inject_text.split())} words injected — long text handled successfully"
                    )
            else:
                self.show_toast(
                    "Saved to history — paste (Ctrl+V) or open the app to copy", duration_ms=6000
                )
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

            # Record latency for the debug dashboard
            try:
                if hasattr(self, "_latency_tracker") and self._latency_tracker is not None:
                    self._latency_tracker.record(
                        SessionTimings(
                            recording_ms=self._last_recording_seconds * 1000.0,
                            transcription_ms=transcription_seconds * 1000.0,
                            ai_ms=ai_seconds * 1000.0,
                            injection_ms=injection_seconds * 1000.0,
                            backend=backend_used,
                            success=True,
                        )
                    )
            except Exception:
                pass

            # Signal success to UI immediately after injection
            self._sessions.pop(correlation_id, None)
            self.overlay.show_success("Long text injected" if _is_long_injection else "Sent")
            self._set_state(RecordingState.SUCCESS, "processing finished", correlation_id)
            QTimer.singleShot(
                450,
                lambda: self._return_to_idle_if_state(
                    RecordingState.SUCCESS, "ready", correlation_id
                ),
            )
            self.overlay.set_state(PillState.DONE)
            self._clear_processor_refs(correlation_id)

            # --- Save history immediately on main thread so UI refresh is instant ---
            try:
                self.history.add_entry(raw, cleaned, is_prompt)
            except Exception:
                logger.warning("history_add_entry_failed", exc_info=True)
            # Refresh history immediately — no background thread delay
            try:
                self.main_window.refresh_history(highlight_latest=True)
            except Exception:
                logger.warning("history_refresh_failed", exc_info=True)

            # --- Defer analytics to background thread (compute-heavy work off main thread) ---
            _recording_seconds = self._last_recording_seconds
            _main_window = self.main_window
            _session_store = self.session_store
            _insights_service = self.insights_service
            _update_metrics = self._update_metrics
            _refresh_debug = self._refresh_debug_window

            def _run_analytics():
                # Always-available insight values (populated only when analytics succeed)
                _insight_summary = ""
                _insight_suggestion = ""
                _insight_clarity = 0
                _insight_conciseness = 0
                _analytics_ok = False

                try:
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

                    _insight_summary = insight.summary
                    _insight_suggestion = insight.suggestion
                    _insight_clarity = insight.clarity_score
                    _insight_conciseness = insight.conciseness_score
                    _analytics_ok = True
                except Exception:
                    logger.warning("analytics_thread_failed", exc_info=True)

                # Schedule insight + metrics UI update after analytics completes
                def _ui_updates():
                    try:
                        _update_metrics()
                        if _analytics_ok:
                            _main_window.update_insight(
                                _insight_summary,
                                _insight_suggestion,
                                _insight_clarity,
                                _insight_conciseness,
                            )
                        if hasattr(_main_window, "_dict_refresh"):
                            _main_window._dict_refresh()
                        _refresh_debug()
                    except Exception:
                        pass

                QTimer.singleShot(0, _ui_updates)

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
        """
        Consume and discard backend fallback events silently.

        The user should NEVER see a toast about Groq→local fallback — it is
        automatic, recovers within 30 seconds, and produces identical results.
        Only critical auth failures (invalid API key) still get a warning.
        """
        if self.transcriber is None:
            return
        failure_code = self.transcriber.consume_last_failure_code()
        backend, reason = self.transcriber.consume_backend_event()

        # Only the user-facing auth failure gets a toast — everything else
        # (rate limits, timeouts, latency) is handled silently.
        if failure_code == FAIL_GROQ_AUTH:
            message = FAILURE_MESSAGES.get(failure_code)
            if message:
                self.show_toast(message, warning=True)
            return
        # Non-auth failures are silent — the system already fell back to local
        # and will recover within _GROQ_RECOVERY_COOLDOWN (30s).
        if failure_code:
            logger.info("backend_fallback_silent", failure_code=failure_code)
            return
        if backend == "local" and reason:
            logger.info("backend_fallback_silent", reason=reason[:80])

    @Slot(str, str, str, str)
    def on_processing_error(
        self, err_msg, correlation_id, traceback_text, failure_code=FAIL_UNKNOWN
    ):
        """
        Handle a processing thread error.

        The user should NOT see an error overlay or alarming dialog for
        recoverable failures (timeout, VAD no-speech, Groq fallback).
        Only critical failures (auth, model missing) get a muted toast.
        The recording loop ALWAYS continues — auto-recovery returns to IDLE.
        """
        if correlation_id != self._processing_session_id:
            log_event(
                "processing_result", "ignored", correlation_id=correlation_id, reason="stale_error"
            )
            return
        self._processing_timeout_timer.stop()
        session = self._sessions.get(correlation_id)
        if session:
            session.mark_failed()

        # Determine which failures are non-critical (silent recovery)
        _silent_failures = {FAIL_VAD_NO_SPEECH, "FAIL_VAD_NO_SPEECH"}
        _muted_failures = {
            FAIL_TIMEOUT,
            FAIL_CANCELLED,
            FAIL_UNKNOWN,
            FAIL_GROQ_ERROR,
            FAIL_GROQ_RATE_LIMIT,
            FAIL_GROQ_TIMEOUT,
            "FAIL_TIMEOUT",
            "FAIL_CANCELLED",
            "FAIL_UNKNOWN",
        }
        _is_silent = failure_code in _silent_failures
        _is_muted = failure_code in _muted_failures

        log_event(
            "processing_failed",
            status="failed",
            failure_code=failure_code,
            correlation_id=correlation_id,
            error=err_msg,
            traceback=traceback_text,
            silent=_is_silent or _is_muted,
        )

        # Silently recover — no overlay, no toast, no dialog
        if _is_silent:
            self._sessions.pop(correlation_id, None)
            self._clear_processor_refs(correlation_id)
            self._set_state(RecordingState.IDLE, f"silent_recovery_{failure_code}", correlation_id)
            self.overlay.set_state(PillState.IDLE)
            return

        # Muted failure — show overlay briefly, no error dialog
        if _is_muted:
            user_message = FAILURE_MESSAGES.get(failure_code, "")
            self._last_session_id = correlation_id
            self._latest_timings = {
                "recording_ms": f"{round(self._last_recording_seconds * 1000, 2)} ms",
                "error": f"[{failure_code}] {err_msg[:80]}",
            }
            self._refresh_debug_window()
            # Quick overlay flash, no error dialog
            self.overlay.show_success("No speech detected")
            self._sessions.pop(correlation_id, None)
            self._clear_processor_refs(correlation_id)
            self._set_state(RecordingState.IDLE, f"muted_recovery_{failure_code}", correlation_id)
            QTimer.singleShot(500, lambda: self.overlay.set_state(PillState.IDLE))
            return

        # Critical failure — show muted toast, no error dialog
        user_message = FAILURE_MESSAGES.get(failure_code, "")
        log_event(
            "processing_failed",
            status="failed",
            failure_code=failure_code,
            correlation_id=correlation_id,
            error=err_msg,
            traceback=traceback_text,
        )
        self._set_error_state("processing thread error", correlation_id)
        self._last_session_id = correlation_id
        self._latest_timings = {
            "recording_ms": f"{round(self._last_recording_seconds * 1000, 2)} ms",
            "error": f"[{failure_code}] {err_msg[:80]}",
        }
        self._refresh_debug_window()
        if user_message:
            self.show_toast(user_message, warning=True)
        self._sessions.pop(correlation_id, None)
        self._clear_processor_refs(correlation_id)
        QTimer.singleShot(
            1000,
            lambda: self._return_to_idle_if_state(
                RecordingState.ERROR, "ready after error", correlation_id
            ),
        )
