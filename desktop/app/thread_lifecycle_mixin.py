"""Thread lifecycle helpers — mixed into RotaApp."""
from __future__ import annotations

import structlog
from PyQt6.QtCore import QTimer

from app.signal_bridges import RecordingState
from app.logging_config import log_event
from ui.overlay.pill_state import PillState

logger = structlog.get_logger(__name__)


class ThreadLifecycleMixin:
    """Manages processor and transcriber thread lifecycle for RotaApp."""

    def _cleanup_processor_thread(self, session_id=None):
        thread = self._processor_thread
        if thread is None:
            return
        if thread.isRunning():
            return
        if (
            session_id is not None
            and self.state == RecordingState.PROCESSING
            and self._processing_session_id == session_id
            and session_id in self._sessions
        ):
            log_event("processor_cleanup", "deferred", session_id=session_id, reason="awaiting_result_handler")
            return
        if (
            session_id is not None
            and self._processing_session_id is not None
            and session_id != self._processing_session_id
        ):
            return
        if session_id is not None:
            session = self._sessions.get(session_id)
            if session is not None and session.state == "DROPPED_TOO_SHORT":
                self._sessions.pop(session_id, None)
                self._active_session = None
                self._set_state(RecordingState.IDLE, "recording too short", session_id)
                self.overlay.set_state(PillState.IDLE)
        self._processing_timeout_timer.stop()
        self._retire_qthread(thread, self._retired_processor_threads)
        self._processor_thread = None
        self._processing_session_id = None

    def _clear_processor_refs(self, session_id=None):
        if session_id is not None and self._processing_session_id not in (None, session_id):
            return
        self._processing_timeout_timer.stop()
        thread = self._processor_thread
        if thread is not None and thread.isRunning():
            log_event(
                "processor_cleanup",
                "deferred",
                session_id=session_id,
                reason="thread_still_running",
            )
            return
        self._retire_qthread(thread, self._retired_processor_threads)
        self._processor_thread = None
        self._processing_session_id = None

    def _retire_qthread(self, thread, bucket):
        if thread is None:
            return
        if thread not in bucket:
            bucket.append(thread)

        def release_thread():
            if thread.isRunning():
                return
            if thread in bucket:
                bucket.remove(thread)
            try:
                thread.deleteLater()
            except RuntimeError:
                pass

        try:
            thread.finished.connect(lambda: QTimer.singleShot(5000, release_thread))
        except (AttributeError, RuntimeError, TypeError):
            pass
        if not thread.isRunning():
            QTimer.singleShot(5000, release_thread)

    def _cancel_processor_thread(self, session, reason: str) -> bool:
        thread = self._processor_thread
        if thread is None or not thread.isRunning():
            return True

        try:
            session.audio_queue.put_nowait(None)
        except Exception:
            pass

        thread.requestInterruption()
        thread.quit()
        if thread.wait(1000):
            return True

        logger.warning("processor_thread_cancel_timeout", correlation_id=session.id, reason=reason)
        thread.terminate()
        if not thread.wait(1000):
            logger.critical("processor_thread_force_terminate_failed", correlation_id=session.id, reason=reason)
            return False
        return True
