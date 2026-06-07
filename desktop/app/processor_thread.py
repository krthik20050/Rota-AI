from __future__ import annotations

import time
import traceback

import numpy as np
from PySide6.QtCore import QThread, Signal

from app.logging_config import log_event, logger
from audio.transcriber import AudioTranscriber

# ── Failure stage codes (exact strings logged & shown toasts) ──────────────
# Shared codes from lower layers — imported so we don't re-define them.
from audio.transcriber import (
    FAIL_GROQ_AUTH,
    FAIL_GROQ_ERROR,
    FAIL_GROQ_RATE_LIMIT,
    FAIL_GROQ_TIMEOUT,
    FAIL_LOCAL_MODEL,
    classify_groq_error,
)
from audio.vad import FAIL_VAD_ERROR, FAIL_VAD_NO_SPEECH, strip_silence

# Processor-thread-only codes (not shared with audio layer)
FAIL_CANCELLED = "FAIL_CANCELLED"
FAIL_TIMEOUT = "FAIL_TIMEOUT"
FAIL_UNKNOWN = "FAIL_UNKNOWN"


# ── User-facing messages keyed by failure code ────────────────────────────
FAILURE_MESSAGES: dict[str, str] = {
    FAIL_VAD_NO_SPEECH: "No speech detected — your mic may be off, too quiet, or muted",
    FAIL_GROQ_ERROR: "Groq transcription failed (unknown error). Falling back to local Whisper.",
    FAIL_GROQ_AUTH: "Groq API key is invalid. Go to Settings → API Keys to update it.",
    FAIL_GROQ_RATE_LIMIT: "Groq rate limit reached. Switched to local transcription. Try again in a minute.",
    FAIL_GROQ_TIMEOUT: "Groq timed out. Switched to local transcription — try again.",
    FAIL_LOCAL_MODEL: "Local Whisper model unavailable — restart the app or check Settings → Model",
    FAIL_CANCELLED: "Recording cancelled.",
    FAIL_TIMEOUT: "Transcription timed out — try a shorter recording or a smaller model",
    FAIL_UNKNOWN: "An unexpected error occurred during transcription. Check the log file for details.",
}


class ProcessorThread(QThread):
    """Background thread for chunked transcription and AI cleanup.

    Every failure path emits ``error`` with a human-readable failure_code
    so the UI can show a specific toast instead of a generic message.
    """

    partial = Signal(str, str)
    completed = Signal(str, str, bool, str, float, float, bool, str)
    error = Signal(str, str, str, str)  # (err_msg, correlation_id, traceback, failure_code)

    _SPEECH_RMS = 0.015
    _SILENCE_CHUNKS = 6
    _MIN_SEGMENT_CHUNKS = 8

    def __init__(self, session, transcriber, ai_processor=None, live_transcription_enabled=True):
        super().__init__()
        self.session = session
        self.transcriber = transcriber
        self.ai_processor = ai_processor
        self.live_transcription_enabled = live_transcription_enabled
        self.correlation_id = session.id

    def _finalize_segment(self, segment_chunks, partial_segments):
        if not segment_chunks:
            return segment_chunks, partial_segments

        # If live feedback is disabled, don't waste CPU doing greedy partial decodes
        if not self.live_transcription_enabled:
            return [], partial_segments

        try:
            audio = np.concatenate(segment_chunks).astype(np.float32, copy=False)
            text = self.transcriber.transcribe_array_local_fast(audio).strip()
            if text:
                partial_segments.append(text)
                self.partial.emit(" ".join(partial_segments), str(self.correlation_id or ""))
        except Exception:
            pass  # Partial transcription failure is non-fatal
        return [], partial_segments

    def run(self):
        thread_logger = logger.bind(correlation_id=self.correlation_id)
        processing_start = time.perf_counter()
        log_event("processing_start", correlation_id=self.correlation_id)
        try:
            transcription_start = time.perf_counter()
            all_chunks = []
            segment_chunks = []
            partial_segments = []
            silence_run = 0

            for chunk in self.session.iter_chunks():
                if self.isInterruptionRequested():
                    raise RuntimeError("processing cancelled")
                all_chunks.append(chunk)

                rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2))) if len(chunk) else 0.0
                if rms >= self._SPEECH_RMS:
                    segment_chunks.append(chunk)
                    silence_run = 0
                    continue

                if segment_chunks:
                    segment_chunks.append(chunk)
                    silence_run += 1
                    if (
                        silence_run >= self._SILENCE_CHUNKS
                        and len(segment_chunks) >= self._MIN_SEGMENT_CHUNKS
                    ):
                        segment_chunks, partial_segments = self._finalize_segment(
                            segment_chunks, partial_segments
                        )
                        silence_run = 0

            segment_chunks, partial_segments = self._finalize_segment(
                segment_chunks, partial_segments
            )

            # Use the app context captured when recording started.
            # By stop time, focus is often back on Rota AI itself.
            app_ctx = self.session.app_context
            if app_ctx is None:
                from injection.app_detector import get_active_app

                app_ctx = get_active_app()
            thread_logger.info(
                "processor_active_app",
                app_name=app_ctx.app_name,
                process=app_ctx.process_name,
                tone=app_ctx.tone,
            )

            # Strip silence from full audio using Silero VAD before transcribing
            raw_text = ""
            backend_used = ""
            if all_chunks:
                full_audio = np.concatenate(all_chunks).astype(np.float32, copy=False)

                # Apply Silero VAD to strip all non-speech silence/noise
                cleaned_audio = strip_silence(full_audio)

                if cleaned_audio is None or cleaned_audio.size == 0:
                    # User only captured silence/noise: skip Whisper completely and return immediately!
                    thread_logger.info("%s silence_only_detected_skipping_whisper", FAIL_VAD_NO_SPEECH)
                    raw_text = ""
                    backend_used = FAIL_VAD_NO_SPEECH
                else:
                    if self.isInterruptionRequested():
                        raise RuntimeError("processing cancelled before full-audio decode")
                    try:
                        raw_text, backend_used = self.transcriber.transcribe_array_with_backend(
                            cleaned_audio, app_context=app_ctx
                        )
                        raw_text = (raw_text or "").strip()
                    except Exception as inner_exc:
                        failure_code = classify_groq_error(str(inner_exc))
                        thread_logger.error(
                            "transcription_failed",
                            failure_code=failure_code,
                            exc_info=True,
                        )
                        raw_text = ""
                        backend_used = failure_code  # stores failure code for analytics/diagnostics

            # Safety fallback if final decode returns empty.
            if not raw_text and self.live_transcription_enabled:
                raw_text = " ".join(partial_segments).strip()

            transcription_seconds = time.perf_counter() - transcription_start
            self.session.raw_text = raw_text
            log_event(
                "transcription_end",
                duration_ms=transcription_seconds * 1000.0,
                has_text=bool(raw_text.strip()),
                correlation_id=self.correlation_id,
            )

            if not raw_text:
                self.completed.emit(
                    "",
                    "",
                    False,
                    str(self.correlation_id or ""),
                    float(transcription_seconds or 0.0),
                    0.0,
                    False,
                    "",
                )
                return

            # AI cleanup — passthrough if ai_processor not set
            ai_start = time.perf_counter()
            ai_failed = False
            if self.ai_processor is not None:
                try:
                    cleaned_text = self.ai_processor.process_text(
                        raw_text,
                        correlation_id=self.correlation_id,
                        app_context=app_ctx,
                        field_text=getattr(self.session, "field_text", ""),
                    )
                except Exception:
                    thread_logger.error("ai_cleanup_failed_using_raw", exc_info=True)
                    cleaned_text = raw_text
                    ai_failed = True
            else:
                cleaned_text = raw_text
            ai_seconds = time.perf_counter() - ai_start
            self.session.cleaned_text = cleaned_text

            log_event(
                "processing_success",
                duration_ms=(time.perf_counter() - processing_start) * 1000.0,
                correlation_id=self.correlation_id,
            )
            self.completed.emit(
                str(raw_text or ""),
                str(cleaned_text or ""),
                False,
                str(self.correlation_id or ""),
                float(transcription_seconds or 0.0),
                float(ai_seconds or 0.0),
                bool(ai_failed),
                str(backend_used or ""),
            )
        except Exception as exc:
            tb = traceback.format_exc()
            err_text = str(exc)
            failure_code = FAIL_UNKNOWN
            if "cancelled" in err_text.lower():
                failure_code = FAIL_CANCELLED
            thread_logger.error(
                "processing_failed",
                failure_code=failure_code,
                exc_info=True,
            )
            log_event(
                "processing_failed",
                status="failed",
                failure_code=failure_code,
                duration_ms=(time.perf_counter() - processing_start) * 1000.0,
                correlation_id=self.correlation_id,
                error=err_text,
            )
            self.error.emit(
                str(err_text),
                str(self.correlation_id or ""),
                str(tb or ""),
                str(failure_code),
            )


class TranscriberLoadThread(QThread):
    loaded = Signal(object, str, str, float)
    error = Signal(str, str)

    def __init__(self, model_size, cpu_threads=0, transcription_quality="balanced"):
        super().__init__()
        self.model_size = model_size
        self.cpu_threads = cpu_threads
        self.transcription_quality = transcription_quality

    def run(self):
        try:
            load_start = time.perf_counter()
            try:
                transcriber = AudioTranscriber(
                    model_size=self.model_size,
                    cpu_threads=self.cpu_threads,
                    transcription_quality=self.transcription_quality,
                )
                self.loaded.emit(
                    transcriber, self.model_size, self.model_size, time.perf_counter() - load_start
                )
            except RuntimeError as exc:
                if "mkl_malloc" in str(exc).lower() and self.model_size != "base":
                    logger.warning("mkl_malloc_fallback", model_size=self.model_size)
                    # Fallback to base model if large model fails
                    transcriber = AudioTranscriber(
                        model_size="base",
                        cpu_threads=self.cpu_threads,
                        transcription_quality=self.transcription_quality,
                    )
                    self.loaded.emit(
                        transcriber, self.model_size, "base", time.perf_counter() - load_start
                    )
                else:
                    raise
        except Exception as exc:
            logger.error("transcriber_load_failed", model_size=self.model_size, exc_info=True)
            self.error.emit(self.model_size, str(exc))
