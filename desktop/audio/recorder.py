import numpy as np
import queue
from utils.log import get_logger
import time as _time
from typing import Optional

from PyQt6.QtCore import pyqtSignal, QObject
from audio.recording_session import RecordingSession

logger = get_logger(__name__)

_SILENCE_RMS = 0.015  # RMS below this = silence (tune if needed)

try:
    import sounddevice as sd
except Exception:
    sd = None
    logger.warning("sounddevice import failed; audio recording will be unavailable")


class AudioRecorder(QObject):
    """Captures mono audio at 16kHz using sounddevice.

    Provides real-time RMS amplitude for UI feedback and audio chunks for transcription.
    """

    audio_level_signal = pyqtSignal(float)
    auto_stop_signal = pyqtSignal()  # emitted when silence exceeds threshold

    def __init__(self, samplerate=16000, chunk_size=1024):
        super().__init__()
        self.samplerate = samplerate
        self.chunk_size = chunk_size
        self._is_recording = False
        self._stream = None
        self._rms_value = 0.0
        self._active_session: Optional[RecordingSession] = None
        # Silence auto-stop state
        self._auto_stop_s: float = 0.0      # 0 = disabled
        self._silence_start: float = 0.0    # monotonic time silence started
        self._speech_detected: bool = False  # require speech before timing silence
        self._auto_stop_emitted: bool = False

    def set_auto_stop(self, seconds: float) -> None:
        """Enable silence-based auto-stop. seconds=0 disables it."""
        self._auto_stop_s = max(0.0, seconds)

    def _audio_callback(self, indata, frames, time, status):
        """Callback function to receive audio data from the stream."""
        if status:
            logger.warning("Audio callback status: %s", status)

        audio_chunk = indata.copy().flatten()
        if self._active_session is not None:
            self._active_session.audio_queue.put(audio_chunk)

        if len(audio_chunk) > 0 and self._is_recording:
            rms = float(np.sqrt(np.mean(audio_chunk.astype(np.float32) ** 2)))
            self.audio_level_signal.emit(rms)

            # Auto-stop on silence
            if self._auto_stop_s > 0 and not self._auto_stop_emitted:
                if rms > _SILENCE_RMS:
                    self._speech_detected = True
                    self._silence_start = 0.0          # reset on speech
                elif self._speech_detected:
                    now = _time.monotonic()
                    if self._silence_start == 0.0:
                        self._silence_start = now
                    elif now - self._silence_start >= self._auto_stop_s:
                        self._auto_stop_emitted = True
                        self.auto_stop_signal.emit()
                        logger.info(
                            "auto_stop_triggered silence_s=%.1f", self._auto_stop_s
                        )

    @property
    def rms_amplitude(self):
        """Current RMS amplitude for UI animation."""
        return self._rms_value

    @property
    def is_recording(self):
        """Public read-only recording state."""
        return self._is_recording

    def start(self, session: RecordingSession):
        """Starts the audio recording stream."""
        if self._is_recording:
            return

        if sd is None:
            raise RuntimeError("Audio input backend is unavailable. Install PortAudio/sounddevice for this environment.")

        # Reset silence-detection state for each new recording
        self._silence_start = 0.0
        self._speech_detected = False
        self._auto_stop_emitted = False

        self._is_recording = True
        self._active_session = session
        self._stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=1,
            dtype='float32',
            callback=self._audio_callback,
            blocksize=self.chunk_size
        )
        self._stream.start()

    def stop(self, session: Optional[RecordingSession] = None):
        """Stops the audio recording stream."""
        if not self._is_recording:
            return

        self._is_recording = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        target_session = session or self._active_session
        if target_session is not None:
            target_session.audio_queue.put(None)
            target_session.mark_stopped()
        self._rms_value = 0.0
        self._active_session = None

    def get_chunks(self, session: Optional[RecordingSession] = None):
        """Generator that yields audio chunks from the session queue."""
        if session is None:
            session = self._active_session
        if session is None:
            return
        while True:
            chunk = session.audio_queue.get()
            if chunk is None:
                break
            yield chunk