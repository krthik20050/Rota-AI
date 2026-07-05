"""
Latency tracker — rolling average of pipeline timings.

Tracks the last N sessions and computes average ASR, LLM, and injection
times so we can measure against the Wispr Flow <700ms goal.

Thread-safe (uses a lock since timings are updated from background thread
and read from the main thread for the debug window).
"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass


@dataclass
class SessionTimings:
    """Timings for a single processing session."""

    recording_ms: float = 0.0
    transcription_ms: float = 0.0
    ai_ms: float = 0.0
    injection_ms: float = 0.0
    backend: str = ""
    timestamp: float = 0.0
    success: bool = True

    @property
    def total_ms(self) -> float:
        """Total end-to-end latency in milliseconds."""
        return self.transcription_ms + self.ai_ms + self.injection_ms

    @property
    def status_emoji(self) -> str:
        """Color-coded status based on total latency."""
        total = self.total_ms
        if total < 700:
            return "🟢"  # Goal achieved
        elif total < 1500:
            return "🟡"  # Acceptable but slow
        else:
            return "🔴"  # Too slow


class LatencyTracker:
    """Rolling average tracker for pipeline latency."""

    def __init__(self, window_size: int = 50):
        self._window_size = window_size
        self._sessions: deque[SessionTimings] = deque(maxlen=window_size)
        self._lock = threading.Lock()

    def record(self, timings: SessionTimings) -> None:
        """Record a session's timings. Thread-safe."""
        with self._lock:
            timings.timestamp = time.time()
            self._sessions.append(timings)

    def record_from_dict(self, timing_dict: dict, backend: str = "", success: bool = True) -> None:
        """Record timings from the _latest_timings dict format. Thread-safe."""

        def _parse_ms(key: str) -> float:
            val = timing_dict.get(key, "0 ms")
            if isinstance(val, str):
                val = val.replace(" ms", "").replace(",", "")
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0

        self.record(
            SessionTimings(
                recording_ms=_parse_ms("recording_ms"),
                transcription_ms=_parse_ms("transcription_ms"),
                ai_ms=_parse_ms("ai_ms"),
                injection_ms=_parse_ms("injection_ms"),
                backend=backend,
                success=success,
            )
        )

    @property
    def average(self) -> SessionTimings:
        """Compute the rolling average across all tracked sessions."""
        with self._lock:
            n = len(self._sessions)
            if n == 0:
                return SessionTimings()

            avg = SessionTimings()
            for s in self._sessions:
                avg.recording_ms += s.recording_ms
                avg.transcription_ms += s.transcription_ms
                avg.ai_ms += s.ai_ms
                avg.injection_ms += s.injection_ms
                avg.success = avg.success and s.success

            avg.recording_ms /= n
            avg.transcription_ms /= n
            avg.ai_ms /= n
            avg.injection_ms /= n
            # Collect unique backends
            backends = {s.backend for s in self._sessions if s.backend}
            avg.backend = "+".join(sorted(backends))
            return avg

    @property
    def session_count(self) -> int:
        with self._lock:
            return len(self._sessions)

    @property
    def success_rate(self) -> float:
        """Percentage of successful sessions (0-100)."""
        with self._lock:
            n = len(self._sessions)
            if n == 0:
                return 100.0
            successes = sum(1 for s in self._sessions if s.success)
            return (successes / n) * 100.0

    def summary(self) -> str:
        """Return a formatted summary string for the debug window."""
        avg = self.average
        count = self.session_count
        total = avg.total_ms

        if total < 700:
            status = f"🟢 {total:.0f}ms"
        elif total < 1500:
            status = f"🟡 {total:.0f}ms"
        else:
            status = f"🔴 {total:.0f}ms"

        lines = [
            f"📊 LATENCY  (last {count} sessions)  {status}",
            f"   Goal: <700ms  {'✓' if total < 700 else '✗'} Achieving",
            f"   ASR: {avg.transcription_ms:.0f}ms  |  "
            f"LLM: {avg.ai_ms:.0f}ms  |  "
            f"Inject: {avg.injection_ms:.0f}ms",
        ]
        if avg.backend:
            lines.append(f"   Backend: {avg.backend}")
        lines.append(f"   Success rate: {self.success_rate:.0f}%")

        return "\n".join(lines)

    def latest(self) -> SessionTimings | None:
        """Return the most recent session timing."""
        with self._lock:
            if self._sessions:
                return self._sessions[-1]
            return None
