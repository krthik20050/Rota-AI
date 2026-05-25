"""Transcriber loading and hotkey readiness — mixed into RotaApp."""
from __future__ import annotations

import structlog
from PyQt6.QtCore import pyqtSlot

from app.processor_thread import TranscriberLoadThread

logger = structlog.get_logger(__name__)


class TranscriberMixin:
    """Transcriber async-load and readiness status helpers for RotaApp."""

    def _update_readiness_status(self):
        backend = getattr(self.hotkey_handler, "backend", None) or "ready"
        hotkey = str(self.config.get("hotkey") or "hotkey").upper()
        if self._transcriber_loading:
            self.main_window.update_hotkey_status(f"Loading speech model... {hotkey} ready ({backend})")
        elif self.transcriber is None:
            self.main_window.update_hotkey_status("Speech model unavailable — check Settings > Model")
        else:
            self.main_window.update_hotkey_status(f"{hotkey} ready ({backend})")

    def _friendly_transcriber_error(self, error_message: str) -> str:
        msg = error_message.lower()
        if "disk" in msg or "space" in msg or "no space" in msg:
            return "Speech model failed to load — insufficient disk space. Free up space and restart"
        if "memory" in msg or "oom" in msg:
            return "Speech model failed to load — not enough RAM. Try the 'tiny' model in Settings"
        if "download" in msg or "network" in msg or "connection" in msg:
            return "Speech model failed to download — check your internet connection"
        return "Speech model failed to load — try a smaller model in Settings > Model"

    def _load_transcriber_async(self, model_size):
        cpu_threads = int(self.config.get("cpu_threads", 0))
        transcription_quality = str(self.config.get("transcription_quality", "balanced"))
        with self._transcriber_state_lock:
            if self._transcriber_loading:
                self._pending_transcriber_model_size = model_size
                return

            self._pending_transcriber_model_size = None
            self.transcriber = None
            self._transcriber_error = None
            self._transcriber_loading = True

        self._update_readiness_status()

        thread = TranscriberLoadThread(
            model_size,
            cpu_threads=cpu_threads,
            transcription_quality=transcription_quality,
        )
        thread.loaded.connect(self._on_transcriber_loaded)
        thread.error.connect(self._on_transcriber_load_error)
        self._transcriber_thread = thread
        thread.start()

    @pyqtSlot(object, str, str, float)
    def _on_transcriber_loaded(self, transcriber, requested_model_size, actual_model_size, load_seconds):
        with self._transcriber_state_lock:
            self._retire_qthread(self._transcriber_thread, self._retired_transcriber_threads)
            self._transcriber_loading = False
            self._transcriber_thread = None

        if requested_model_size != self._current_model_size:
            pending_model_size = getattr(self, "_pending_transcriber_model_size", None)
            logger.info("transcriber_load_outdated", requested=requested_model_size, current=self._current_model_size)
            if pending_model_size and pending_model_size != requested_model_size:
                self._load_transcriber_async(pending_model_size)
            return

        self.transcriber = transcriber
        self._transcriber_error = None
        if actual_model_size != requested_model_size:
            self._current_model_size = actual_model_size
            self.show_toast(f"Speech model fallback: using {actual_model_size}")
        logger.info(
            "transcriber_loaded",
            requested_model_size=requested_model_size,
            actual_model_size=actual_model_size,
            duration_ms=round(load_seconds * 1000, 2),
        )
        self._update_readiness_status()

    @pyqtSlot(str, str)
    def _on_transcriber_load_error(self, model_size, error_message):
        with self._transcriber_state_lock:
            self._retire_qthread(self._transcriber_thread, self._retired_transcriber_threads)
            self._transcriber_loading = False
            self._transcriber_thread = None

        if model_size != self._current_model_size:
            pending_model_size = getattr(self, "_pending_transcriber_model_size", None)
            if pending_model_size and pending_model_size != model_size:
                self._load_transcriber_async(pending_model_size)
            return

        self.transcriber = None
        self._transcriber_loading = False
        self._transcriber_error = error_message
        logger.error(
            "transcriber_unavailable",
            model_size=model_size,
            error_message=error_message,
        )
        self._update_readiness_status()
        self.show_toast(self._friendly_transcriber_error(error_message), warning=True)
