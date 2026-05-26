import io
import json
import os
import re
import threading
import time
import wave
from collections.abc import Generator
from pathlib import Path

import numpy as np

from utils.log import get_logger

logger = get_logger(__name__)

_GROQ_MODEL = "whisper-large-v3-turbo"
_GROQ_LATENCY_THRESHOLD = 3.0  # seconds — switch to local if exceeded
_GROQ_RECOVERY_COOLDOWN = 30.0  # seconds — wait before re-trying Groq after failure

_SAMPLERATE = 16000  # must match AudioRecorder.samplerate
_MAX_CHUNK_S = 55.0  # split sessions longer than this (Groq 25 MB limit safe zone)
_SILENCE_RMS = 0.015  # RMS below this = silence (matches recorder threshold)

# Whisper known end-of-clip hallucination artifacts
_HALLUCINATION_RE = re.compile(
    r"^\s*(?:"
    r"thanks?\s+(?:for\s+)?(?:watching|listening|tuning\s+in)|"
    r"please\s+(?:like|subscribe|comment|share)|"
    r"\[(?:music|applause|laughter|silence|noise|blank\s+audio|inaudible|crosstalk)\]|"
    r"subtitle[sd]?\s+by\s+\w+|"
    r"(?:auto-?)?generated\s+(?:captions?|subtitles?)"
    r")\s*[.!]?\s*$",
    re.IGNORECASE,
)


def _strip_hallucinations(text: str) -> str:
    """Remove Whisper's known end-of-clip artifacts. Returns empty string if matched."""
    stripped = text.strip()
    if not stripped:
        return ""
    if _HALLUCINATION_RE.match(stripped):
        logger.debug("hallucination_stripped text=%r", stripped[:60])
        return ""
    # Reject punctuation-only or single non-alnum outputs (silent clip artifacts)
    if len(stripped) <= 2 and not any(c.isalnum() for c in stripped):
        logger.debug("hallucination_stripped_short text=%r", stripped)
        return ""
    return stripped


def _load_initial_prompt() -> str:
    try:
        path = Path(__file__).parent.parent / "data" / "dictionary.json"
        with open(path, encoding="utf-8") as f:
            return json.load(f).get("initial_prompt", "")
    except Exception:
        return ""


def _numpy_to_wav_bytes(audio: np.ndarray, sample_rate: int = 16000) -> bytes:
    """Convert float32 mono numpy array to WAV bytes (16-bit PCM)."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        pcm = (audio * 32767.0).clip(-32768, 32767).astype(np.int16)
        wf.writeframes(pcm.tobytes())
    return buf.getvalue()


class AudioTranscriber:
    """
    Transcribes audio with Groq API (primary) and faster-whisper (fallback).

    Backend selection:
    - Groq is used when GROQ_API_KEY is set and no failures are active.
    - Auto-switches to local only if Groq raises an exception (slow calls still succeed).
    - Auto-recovers to Groq after GROQ_RECOVERY_COOLDOWN seconds.
    - Thread-safe backend state; model inference is not locked (each call is
      independent and faster-whisper is not thread-safe, so callers must
      serialize ProcessorThread instances — which the existing state machine does).
    """

    def __init__(
        self,
        model_size: str = "base.en",
        device: str = "cpu",
        compute_type: str = "int8",
        cpu_threads: int = 0,
        transcription_quality: str = "balanced",
    ):
        self._model_size = model_size
        self._device = device
        self._compute_type = compute_type
        self._cpu_threads = cpu_threads
        self.transcription_quality = transcription_quality
        self.model = None  # faster-whisper WhisperModel, lazy-loaded
        self._is_running = False

        # Groq state
        self._groq_api_key: str = os.environ.get("GROQ_API_KEY", "")
        self._use_groq: bool = bool(self._groq_api_key)
        self._groq_failure_count: int = 0
        self._last_groq_failure_time: float = 0.0
        self._groq_client = None  # reused across calls to avoid per-call HTTP session setup
        self._state_lock = threading.Lock()
        self._backend_event_lock = threading.Lock()
        self._last_backend_used: str = ""
        self._last_backend_reason: str = ""

        # Vocabulary priming
        self._initial_prompt: str = _load_initial_prompt()

        logger.info(
            "transcriber_initialized model=%s groq_enabled=%s prompt_loaded=%s threads=%d quality=%s",
            model_size,
            self._use_groq,
            bool(self._initial_prompt),
            cpu_threads,
            transcription_quality,
        )

    # ------------------------------------------------------------------ #
    #  Local model management
    # ------------------------------------------------------------------ #

    def _ensure_model(self):
        """Load CTranslate2 weights on demand (first local transcription only)."""
        if self.model is not None:
            return self.model
        from faster_whisper import WhisperModel

        cpu_threads = self._cpu_threads
        if cpu_threads == 0:
            try:
                import psutil

                cpu_threads = psutil.cpu_count(logical=False) or os.cpu_count() or 4
            except Exception:
                cpu_threads = os.cpu_count() or 4
            logger.info("transcriber_threads_autodetect physical_cores=%d", cpu_threads)

        # Cap threads to prevent ctranslate2 SIMD stack overflows (STATUS_STACK_BUFFER_OVERRUN).
        # inter_threads=1 prevents parallel beam decoding which amplifies stack usage.
        cpu_threads = min(cpu_threads, 4)

        logger.info("loading_local_whisper model=%s cpu_threads=%d", self._model_size, cpu_threads)
        self.model = WhisperModel(
            self._model_size,
            device=self._device,
            compute_type=self._compute_type,
            cpu_threads=cpu_threads,
            num_workers=1,
        )
        self._warmup()
        return self.model

    def ensure_loaded(self) -> None:
        """Force-load local Whisper. Used by diagnostics/startup pre-warm."""
        self._ensure_model()

    def _warmup(self):
        try:
            silent = np.zeros(16000, dtype=np.float32)
            segs, _ = self.model.transcribe(silent, beam_size=1, language="en", vad_filter=False)
            for _ in segs:
                pass
            logger.info("transcriber_warmup_complete model=%s", self._model_size)
        except Exception:
            logger.warning("transcriber_warmup_failed", exc_info=True)

    # ------------------------------------------------------------------ #
    #  Backend state management  (thread-safe)
    # ------------------------------------------------------------------ #

    def _should_use_groq(self) -> bool:
        if not self._groq_api_key:
            return False
        with self._state_lock:
            if not self._use_groq:
                elapsed = time.monotonic() - self._last_groq_failure_time
                if elapsed >= _GROQ_RECOVERY_COOLDOWN:
                    logger.info("transcriber_groq_recovery_attempt")
                    self._use_groq = True
                    self._groq_failure_count = 0
            return self._use_groq

    def _mark_groq_success(self):
        with self._state_lock:
            self._groq_failure_count = 0
        with self._backend_event_lock:
            self._last_backend_used = "groq"
            self._last_backend_reason = ""

    def _mark_groq_failure(self, reason: str):
        with self._state_lock:
            self._groq_failure_count += 1
            self._use_groq = False
            self._last_groq_failure_time = time.monotonic()
        with self._backend_event_lock:
            self._last_backend_used = "local"
            self._last_backend_reason = reason
        logger.warning(
            "transcriber_groq_disabled reason=%s total_failures=%d cooldown_s=%.0f",
            reason,
            self._groq_failure_count,
            _GROQ_RECOVERY_COOLDOWN,
        )

    # ------------------------------------------------------------------ #
    #  Backend implementations
    # ------------------------------------------------------------------ #

    def _get_groq_client(self):
        """Return a cached Groq client, creating it once on first use."""
        if self._groq_client is None:
            from groq import Groq

            self._groq_client = Groq(api_key=self._groq_api_key)
        return self._groq_client

    def _transcribe_groq(self, audio: np.ndarray, app_context: any = None) -> str:
        """Call Groq Whisper API with dynamic app-context vocabulary priming."""
        wav_bytes = _numpy_to_wav_bytes(audio)
        client = self._get_groq_client()
        prompt_parts = []
        if self._initial_prompt:
            prompt_parts.append(self._initial_prompt)

        tone = "neutral"
        if app_context:
            if hasattr(app_context, "tone"):
                tone = app_context.tone
            elif isinstance(app_context, dict):
                tone = app_context.get("tone", "neutral")
            elif isinstance(app_context, str):
                tone = app_context

        if tone == "technical":
            prompt_parts.append(
                "Preserve technical terms, identifiers, and product names exactly. Do not invent code snippets, functions, classes, or terminal commands unless they were explicitly dictated."
            )
        elif tone == "casual":
            prompt_parts.append(
                "Casual tone, slang, shortcuts, friendly text messages, quick chat."
            )
        elif tone == "formal":
            prompt_parts.append(
                "Formal business English, professional vocabulary, structured sentences, proper capitalization, polite corporate dictation."
            )
        else:
            prompt_parts.append("Transcribe spoken dictation accurately.")

        kwargs: dict = {
            "file": ("audio.wav", wav_bytes, "audio/wav"),
            "model": _GROQ_MODEL,
            "language": "en",
            "response_format": "text",
            "temperature": 0.0,
            "prompt": " ".join(prompt_parts),
        }
        response = client.audio.transcriptions.create(**kwargs)
        text = (
            response
            if isinstance(response, str)
            else (response.text if hasattr(response, "text") else str(response))
        )
        return _strip_hallucinations(text.strip())

    def _transcribe_local(
        self,
        audio: np.ndarray,
        app_context: any = None,
        beam_size: int = None,
        best_of: int = None,
    ) -> str:
        """Transcribe via local faster-whisper (CTranslate2) with app-context priming & quality presets."""
        self._ensure_model()

        if beam_size is None or best_of is None:
            quality = getattr(self, "transcription_quality", "balanced")
            if quality == "high":
                res_beam = 5
                res_best = 5
            elif quality == "fast":
                res_beam = 1
                res_best = 1
            else:  # balanced
                res_beam = 3
                res_best = 3

            beam_size = beam_size or res_beam
            best_of = best_of or res_best

        kwargs: dict = {
            "beam_size": beam_size,
            "best_of": best_of,
            "language": "en",
            "temperature": 0.0,
            "no_speech_threshold": 0.6,
            "compression_ratio_threshold": 2.4,
            "log_prob_threshold": -1.0,
            "condition_on_previous_text": False,
            "vad_filter": False,
        }

        prompt_parts = []
        if self._initial_prompt:
            prompt_parts.append(self._initial_prompt)

        tone = "neutral"
        if app_context:
            if hasattr(app_context, "tone"):
                tone = app_context.tone
            elif isinstance(app_context, dict):
                tone = app_context.get("tone", "neutral")
            elif isinstance(app_context, str):
                tone = app_context

        if tone == "technical":
            prompt_parts.append(
                "Preserve technical terms, identifiers, and product names exactly. Do not invent code snippets, functions, classes, or terminal commands unless they were explicitly dictated."
            )
        elif tone == "casual":
            prompt_parts.append(
                "Casual tone, slang, shortcuts, friendly text messages, quick chat."
            )
        elif tone == "formal":
            prompt_parts.append(
                "Formal business English, professional vocabulary, structured sentences, proper capitalization, polite corporate dictation."
            )

        if prompt_parts:
            kwargs["initial_prompt"] = " ".join(prompt_parts)

        segs, _ = self.model.transcribe(audio, **kwargs)
        return _strip_hallucinations(" ".join(seg.text for seg in segs).strip())

    def _preprocess_audio(self, audio: np.ndarray) -> np.ndarray:
        """DC-remove, normalize, and optionally denoise before transcription."""
        # 1. DC offset removal
        audio = audio - np.mean(audio)
        # 2. Peak normalization to -3 dBFS (0.708 linear)
        peak = np.max(np.abs(audio))
        if peak > 1e-6:
            audio = (audio * (0.708 / peak)).astype(np.float32)
        # 3. Optional noise reduction (disabled by default for accuracy safety)
        # Enable via config or ROTA_ENABLE_DENOISE=1 environment variable.
        if os.environ.get("ROTA_ENABLE_DENOISE", "0") == "1" or getattr(
            self, "denoise_enabled", False
        ):
            try:
                import noisereduce as nr

                audio = nr.reduce_noise(y=audio, sr=16000, stationary=True).astype(np.float32)
            except ImportError:
                pass
        return audio

    def _transcribe_with_fallback(
        self, audio: np.ndarray, app_context: any = None
    ) -> tuple[str, str]:
        """
        Returns (transcript_text, backend_used).
        Tries Groq first; falls back to local on failure or high latency.
        """
        audio = self._preprocess_audio(audio)
        if self._should_use_groq():
            t0 = time.monotonic()
            try:
                text = self._transcribe_groq(audio, app_context=app_context)
                elapsed = time.monotonic() - t0

                if elapsed > _GROQ_LATENCY_THRESHOLD:
                    logger.warning(
                        "transcriber_backend=groq elapsed_ms=%.0f latency_high_but_success=True",
                        elapsed * 1000,
                    )
                else:
                    logger.info("transcriber_backend=groq elapsed_ms=%.0f", elapsed * 1000)
                self._mark_groq_success()
                return text, "groq"

            except Exception as exc:
                elapsed = time.monotonic() - t0
                self._mark_groq_failure(str(exc)[:120])
                logger.info(
                    "transcriber_groq_failed_falling_back elapsed_ms=%.0f",
                    elapsed * 1000,
                    exc_info=True,
                )

        # Local fallback
        t0 = time.monotonic()
        text = self._transcribe_local(audio, app_context=app_context)
        elapsed = time.monotonic() - t0
        logger.info(
            "transcriber_backend=local model=%s elapsed_ms=%.0f",
            self._model_size,
            elapsed * 1000,
        )
        with self._backend_event_lock:
            self._last_backend_used = "local"
        return text, "local"

    # ------------------------------------------------------------------ #
    #  Public interface  (unchanged contract)
    # ------------------------------------------------------------------ #

    # ------------------------------------------------------------------ #
    #  Long-session chunking
    # ------------------------------------------------------------------ #

    def _find_split_point(self, audio: np.ndarray, target: int, window: int = 5) -> int:
        """
        Find the best split point near `target` samples by locating the
        lowest-RMS (most silence-like) frame within a ±window second search band.
        Falls back to exactly `target` if no silence is found.
        """
        half = int(window * _SAMPLERATE)
        lo = max(0, target - half)
        hi = min(len(audio), target + half)
        if lo >= hi:
            return target

        frame = int(0.02 * _SAMPLERATE)  # 20 ms frames
        best_rms = float("inf")
        best_pos = target

        for pos in range(lo, hi - frame, frame):
            rms = float(np.sqrt(np.mean(audio[pos : pos + frame].astype(np.float32) ** 2)))
            if rms < best_rms:
                best_rms = rms
                best_pos = pos

        return best_pos if best_rms < _SILENCE_RMS else target

    def _transcribe_chunked(self, full_audio: np.ndarray, app_context=None) -> list[str]:
        """
        Transcribe arbitrarily long audio by splitting at silence boundaries
        near every _MAX_CHUNK_S interval. Each segment is sent as a separate
        Groq/local call so no single chunk exceeds the API size limit.
        """
        max_samples = int(_MAX_CHUNK_S * _SAMPLERATE)
        if len(full_audio) <= max_samples:
            text, _ = self._transcribe_with_fallback(full_audio, app_context)
            return [text] if text else []

        duration_s = len(full_audio) / _SAMPLERATE
        logger.info("long_session_chunking duration_s=%.1f chunk_s=%.0f", duration_s, _MAX_CHUNK_S)

        texts: list[str] = []
        start = 0
        while start < len(full_audio):
            target = start + max_samples
            if target >= len(full_audio):
                segment = full_audio[start:]
            else:
                split = self._find_split_point(full_audio, target)
                if split <= start:
                    # Guard: _find_split_point returned a non-advancing position;
                    # force progress to avoid an infinite loop.
                    split = min(start + max_samples, len(full_audio))
                segment = full_audio[start:split]
                target = split

            text, _ = self._transcribe_with_fallback(segment, app_context)
            if text:
                texts.append(text)
            start = target

        logger.info(
            "long_session_chunks=%d joined_text_len=%d", len(texts), sum(len(t) for t in texts)
        )
        return texts

    def process_stream(self, audio_generator) -> Generator[tuple[str, bool], None, None]:
        """
        Accumulate all chunks, transcribe (chunking automatically for long sessions),
        yield (text, is_final=True). Signature unchanged — all callers unaffected.
        """
        accumulated = []
        self._is_running = True

        for chunk in audio_generator:
            if chunk is None:
                break
            accumulated.append(chunk)

        if accumulated:
            full_audio = np.concatenate(accumulated)
            texts = self._transcribe_chunked(full_audio)
            yield " ".join(texts), True

        self._is_running = False

    def transcribe_array(self, full_audio: np.ndarray, app_context: any = None) -> str:
        """Single-shot transcription. Automatically chunks long recordings."""
        if full_audio is None or full_audio.size == 0:
            return ""
        texts = self._transcribe_chunked(full_audio.astype(np.float32, copy=False), app_context)
        return " ".join(texts)

    def transcribe_array_with_backend(
        self, full_audio: np.ndarray, app_context: any = None
    ) -> tuple[str, str]:
        """Single-shot transcription with backend metadata."""
        if full_audio is None or full_audio.size == 0:
            return "", ""
        return self._transcribe_with_fallback(
            full_audio.astype(np.float32, copy=False), app_context=app_context
        )

    def transcribe_array_local(self, full_audio: np.ndarray, app_context: any = None) -> str:
        """Single-shot transcription that always uses local faster-whisper."""
        if full_audio is None or full_audio.size == 0:
            return ""
        text = self._transcribe_local(
            full_audio.astype(np.float32, copy=False), app_context=app_context
        )
        with self._backend_event_lock:
            self._last_backend_used = "local"
        return text

    def transcribe_array_local_fast(self, full_audio: np.ndarray) -> str:
        """Single-shot transcription that forces greedy (beam_size=1) decoding for live/partial feedback."""
        if full_audio is None or full_audio.size == 0:
            return ""
        text = self._transcribe_local(
            full_audio.astype(np.float32, copy=False), beam_size=1, best_of=1
        )
        with self._backend_event_lock:
            self._last_backend_used = "local"
        return text

    def consume_backend_event(self) -> tuple[str, str]:
        """
        Return and clear the most recent backend event.
        Used by UI to show fallback notifications without duplicates.
        """
        with self._backend_event_lock:
            backend = self._last_backend_used
            reason = self._last_backend_reason
            self._last_backend_used = ""
            self._last_backend_reason = ""
        return backend, reason

    @property
    def active_backend(self) -> str:
        """Which backend will be used on the next transcription call."""
        return "groq" if self._should_use_groq() else "local"
