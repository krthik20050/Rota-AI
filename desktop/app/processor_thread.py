from __future__ import annotations

import time
import traceback

import numpy as np
from PySide6.QtCore import QThread, Signal

from app.logging_config import log_event, logger

# ── Failure stage codes (exact strings logged & shown toasts) ──────────────
# Shared codes from lower layers — imported so we don't re-define them.
from audio.transcriber import (
    FAIL_GROQ_AUTH,
    FAIL_GROQ_ERROR,
    FAIL_GROQ_RATE_LIMIT,
    FAIL_GROQ_TIMEOUT,
    FAIL_LOCAL_MODEL,
    AudioTranscriber,
)
from audio.vad import FAIL_VAD_NO_SPEECH

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
    # Streaming transcription: transcribe every ~1 second when Groq is active
    # (fast API, <500ms per call on short clips) so the user sees partial text
    # arriving during recording and only the last <1s tail needs transcribing
    # after stop — achieving Wispr Flow-level latency.
    # Falls back to ~55s intervals for local Whisper (slow CPU inference).
    _STREAM_FLUSH_INTERVAL_GROQ = int(1.0 * 16000)  # 16000 samples = ~1s
    _STREAM_FLUSH_INTERVAL_LOCAL = int(55.0 * 16000)  # 880000 samples = ~55s
    # Minimum audio to accumulate before a streaming flush fires (~3s).
    # Short utterances (<3s) skip streaming flushes entirely — they get a
    # single transcription call on stop, cutting latency in half.
    _MIN_STREAM_SAMPLES = int(3.0 * 16000)  # 48000 samples = ~3s

    def __init__(self, session, transcriber, ai_processor=None, live_transcription_enabled=True):
        super().__init__()
        self.session = session
        self.transcriber = transcriber
        self.ai_processor = ai_processor
        self.live_transcription_enabled = live_transcription_enabled
        self.correlation_id = session.id
        # Exposed for debug window memory diagnostic
        self.stream_buffer_samples = 0
        self._total_recording_samples = 0

    @property
    def stream_buffer_memory_mb(self) -> float:
        """Current stream buffer memory in MB (int16 = 2 bytes per sample)."""
        return (self.stream_buffer_samples * 2) / (1024.0 * 1024.0)

    @property
    def _effective_flush_interval(self) -> int:
        """
        Use 1s intervals when Groq is fast (very tiny tail on stop, ~Wispr Flow latency).
        Use 55s intervals for local Whisper (avoids backlog from slow CPU inference).
        """
        if (
            hasattr(self.transcriber, "active_backend")
            and self.transcriber.active_backend == "groq"
        ):
            return self._STREAM_FLUSH_INTERVAL_GROQ
        return self._STREAM_FLUSH_INTERVAL_LOCAL

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

    def _flush_stream_segment(
        self,
        buffer_chunks: list,
        out_texts: list,
        app_ctx,
        thread_logger,
    ) -> bool:
        """
        Transcribe one streaming segment and append to out_texts.

        Returns True on success (text was transcribed and emitted), False on
        failure so the caller can decide whether to clear the buffer.
        On failure the buffer is kept intact so the audio is NOT lost — the
        next flush cycle will retry on the accumulated data.

        This is the heart of the streaming memory optimization — instead of
        accumulating the entire recording into one giant array, we transcribe
        in chunks so peak memory stays at ~7MB per segment rather than ~230MB+
        for a 60-minute recording.
        """
        if not buffer_chunks:
            return True  # Nothing to do is not a failure
        try:
            segment_audio = np.concatenate(buffer_chunks).astype(np.float32, copy=False)
            # No per-segment VAD — Whisper handles silence internally.
            # Per-segment VAD would strip segment boundaries, losing words
            # that straddle them.
            text, backend = self.transcriber.transcribe_array_with_backend(
                segment_audio, app_context=app_ctx
            )
            text = (text or "").strip()
            if text:
                out_texts.append(text)
                if backend:
                    self._backends_used.add(backend)
                self.partial.emit(" ".join(out_texts), str(self.correlation_id or ""))
            return True
        except Exception:
            thread_logger.warning("stream_segment_transcribe_failed", exc_info=True)
        return False

    def run(self):
        thread_logger = logger.bind(correlation_id=self.correlation_id)
        processing_start = time.perf_counter()
        log_event("processing_start", correlation_id=self.correlation_id)
        try:
            transcription_start = time.perf_counter()
            stream_buffer = []
            stream_sample_count = 0
            stream_texts = []
            self._backends_used: set[str] = set()
            segment_chunks = []
            partial_segments = []
            silence_run = 0

            # Resolve app context early — needed for streaming transcription.
            # session.app_context is captured at recording start so it's safe.
            app_ctx = self.session.app_context
            if app_ctx is None:
                from injection.app_detector import get_active_app

                app_ctx = get_active_app()
            thread_logger.info(
                "processor_active_app",
                app_name=app_ctx.app_name,
                process=app_ctx.process_name,
                tone=app_ctx.tone,
                category=getattr(app_ctx, "category", ""),
            )
            app_category = getattr(app_ctx, "category", "") or ""
            is_prompt = bool(app_category == "prompt")
            if is_prompt:
                thread_logger.info(
                    "prompt_context_detected_skipping_ai_cleanup",
                    app_name=app_ctx.app_name,
                    process=app_ctx.process_name,
                )

            # Track whether ANY chunk had speech-level audio — if the entire
            # recording is silence, we skip the transcription API call entirely
            # and emit empty immediately, avoiding wasted time and API quota.
            _had_speech = False

            for chunk in self.session.iter_chunks():
                if self.isInterruptionRequested():
                    raise RuntimeError("processing cancelled")

                stream_buffer.append(chunk)
                stream_sample_count += len(chunk)
                self.stream_buffer_samples = stream_sample_count

                # Expose total recording sample count for debug window
                self._total_recording_samples += len(chunk)

                # Partial transcription (live feedback via greedy decode, unchanged)
                rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2))) if len(chunk) else 0.0
                if rms >= self._SPEECH_RMS:
                    _had_speech = True
                    segment_chunks.append(chunk)
                    silence_run = 0
                elif segment_chunks:
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
                else:
                    silence_run = 0

                # Flush streaming buffer at dynamic intervals (1s for Groq, 55s for local).
                # For Groq: transcribe small segments during recording so the user sees
                # partial text arriving in ~1s bursts. On stop, only the final <1s tail
                # is left — achieving Wispr Flow-level latency.
                # Only clear the buffer on success so failed segments aren't lost.
                # Minimum accumulation guard: only apply BEFORE the first flush so very
                # short recordings (<3s) skip streaming entirely and get one call on stop.
                # After the first flush, subsequent flushes fire at the normal interval.
                # stream_texts is empty before the first flush, so it works as the gate.
                if stream_sample_count >= self._effective_flush_interval and (
                    stream_texts or stream_sample_count >= self._MIN_STREAM_SAMPLES
                ):
                    ok = self._flush_stream_segment(
                        stream_buffer, stream_texts, app_ctx, thread_logger
                    )
                    if ok:
                        stream_buffer = []
                        stream_sample_count = 0
                        self.stream_buffer_samples = 0

            # Early empty: if NO chunk had speech-level audio, skip the
            # transcription API call entirely — saves time and API quota.
            if not _had_speech:
                transcription_seconds = time.perf_counter() - transcription_start
                log_event(
                    "transcription_end",
                    duration_ms=transcription_seconds * 1000.0,
                    has_text=False,
                    correlation_id=self.correlation_id,
                    reason="no_speech_detected",
                )
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

            # Finalize remaining partial segments (live feedback)
            segment_chunks, partial_segments = self._finalize_segment(
                segment_chunks, partial_segments
            )

            # Flush final stream buffer (on stop — <1s tail for Groq, <55s for local)
            if stream_buffer:
                self._flush_stream_segment(stream_buffer, stream_texts, app_ctx, thread_logger)
                stream_buffer = []

            # Assemble final text from all streaming segments
            raw_text = " ".join(t for t in stream_texts if t).strip()
            backend_used = "+".join(sorted(self._backends_used)) if self._backends_used else ""

            # Safety fallback: use live partial segments if streaming produced nothing
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
            # For prompt contexts (ChatGPT, Claude, etc.), skip AI cleanup entirely
            # to preserve the user's dictated prompt verbatim.
            ai_start = time.perf_counter()
            ai_failed = False
            if is_prompt:
                cleaned_text = raw_text
                thread_logger.debug(
                    "ai_cleanup_skipped_prompt_context",
                    chars=len(raw_text),
                )
            elif self.ai_processor is not None:
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
                is_prompt=is_prompt,
            )
            self.completed.emit(
                str(raw_text or ""),
                str(cleaned_text or ""),
                bool(is_prompt),
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
