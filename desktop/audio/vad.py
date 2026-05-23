from utils.log import get_logger
import threading
from typing import Optional

import numpy as np

logger = get_logger(__name__)

_model = None
_lock = threading.Lock()


def _load_model():
    """Lazy-load Silero VAD (ONNX backend, no torchaudio required)."""
    global _model
    if _model is not None:
        return _model
    with _lock:
        if _model is not None:
            return _model
        from silero_vad import load_silero_vad
        _model = load_silero_vad(onnx=True)
        logger.debug("silero_vad_model_loaded")
    return _model


def strip_silence(
    audio: np.ndarray,
    sample_rate: int = 16000,
    threshold: float = 0.5,
    min_speech_duration_ms: int = 250,
    speech_pad_ms: int = 30,
) -> np.ndarray:
    """
    Strips silence from audio using Silero VAD.

    Returns concatenated speech segments as float32 array.
    Returns an empty float32 array when no speech is detected.
    Returns the original audio unchanged on any exception.

    Args:
        audio: mono float32 numpy array
        sample_rate: must be 8000 or 16000 (Silero constraint)
        threshold: speech probability threshold (0.0-1.0)
        min_speech_duration_ms: discard speech segments shorter than this
        speech_pad_ms: extra padding kept around each detected segment
    """
    try:
        import torch
        from silero_vad import get_speech_timestamps, collect_chunks

        if audio is None or audio.size == 0:
            return np.array([], dtype=np.float32)

        model = _load_model()
        audio_t = torch.from_numpy(audio.astype(np.float32))

        timestamps = get_speech_timestamps(
            audio_t,
            model,
            threshold=threshold,
            sampling_rate=sample_rate,
            min_speech_duration_ms=min_speech_duration_ms,
            speech_pad_ms=speech_pad_ms,
        )

        if not timestamps:
            logger.debug("vad_no_speech_detected length_s=%.2f", len(audio) / sample_rate)
            return np.array([], dtype=np.float32)

        cleaned = collect_chunks(timestamps, audio_t)
        result = cleaned.numpy().astype(np.float32)
        logger.debug(
            "vad_stripped_silence original_s=%.2f cleaned_s=%.2f",
            len(audio) / sample_rate,
            len(result) / sample_rate,
        )
        return result

    except Exception:
        logger.warning("vad_failed_returning_original", exc_info=True)
        return audio


if __name__ == "__main__":
    import time

    SR = 16000

    def _make_silence(duration_s: float) -> np.ndarray:
        return np.zeros(int(SR * duration_s), dtype=np.float32)

    def _make_voiced(duration_s: float) -> np.ndarray:
        """Harmonic stack resembling voiced speech (F0=120Hz, formants)."""
        t = np.linspace(0, duration_s, int(SR * duration_s), dtype=np.float32)
        wave = sum(
            (0.15 / i) * np.sin(2 * np.pi * 120 * i * t) for i in range(1, 12)
        ).astype(np.float32)
        rng = np.random.default_rng(0)
        wave += rng.normal(0, 0.005, len(wave)).astype(np.float32)
        return wave

    print("=== Silero VAD tests ===\n")

    # Test 1: empty input -> empty output
    result = strip_silence(np.array([], dtype=np.float32))
    assert result.size == 0, "empty input should return empty"
    print("[PASS] empty input -> empty output")

    # Test 2: all silence -> no speech -> empty output
    silence_only = _make_silence(2.0)
    result = strip_silence(silence_only, SR)
    assert result.size == 0, "silence-only should return empty"
    print("[PASS] silence-only -> empty output")

    # Test 3: fallback on exception (pass invalid input)
    bad_audio = np.array([float("nan")] * 100, dtype=np.float32)
    result = strip_silence(bad_audio, SR)
    # NaN input — VAD may return empty or original; must not raise
    print(f"[PASS] NaN input handled gracefully (returned {len(result)} samples)")

    # Test 4: silence + voiced + silence -> VAD runs without crash
    voiced_segment = _make_voiced(1.5)
    audio_with_silence = np.concatenate([
        _make_silence(0.5),
        voiced_segment,
        _make_silence(0.5),
    ])
    t0 = time.perf_counter()
    result = strip_silence(audio_with_silence, SR)
    elapsed = time.perf_counter() - t0
    print(
        f"[PASS] voiced+silence audio: original={len(audio_with_silence)/SR:.2f}s "
        f"-> result={len(result)/SR:.2f}s  ({elapsed*1000:.1f}ms)"
    )

    # Test 5: return type always float32 numpy array
    assert isinstance(result, np.ndarray), "result must be ndarray"
    assert result.dtype == np.float32, f"result dtype must be float32, got {result.dtype}"
    print("[PASS] return type is float32 ndarray")

    print("\nAll tests passed.")
