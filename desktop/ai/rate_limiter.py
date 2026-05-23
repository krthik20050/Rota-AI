import re
import threading
import time

# SECURITY: Maximum lengths to prevent abuse
_MAX_TRANSCRIPT_LENGTH = 10000       # chars — reject longer inputs to LLM
_MAX_PERSONAL_TERMS = 50            # cap personal dictionary terms sent to LLM
_MAX_SYSTEM_PROMPT_LENGTH = 8000    # chars — prevent prompt overflow

# SECURITY: Patterns that indicate prompt injection attempts
_INJECTION_PATTERNS = [
    re.compile(r'ignore\s+(?:all\s+)?(?:previous|prior|above|earlier)\s+(?:instructions?|rules?|prompts?)', re.I),
    re.compile(r'(?:new|updated?|different)\s+(?:instructions?|rules?|prompts?|system)', re.I),
    re.compile(r'(?:reveal|show|output|print|leak|expose)\s+(?:the\s+)?(?:system|prompt|dictionary|keys?)', re.I),
    re.compile(r'(?:you\s+are\s+now|act\s+as|pretend\s+to\s+be|roleplay\s+as)', re.I),
    re.compile(r'(?:jailbreak|DAN|developer\s+mode|sudo|root\s+access)', re.I),
]


# ---------------------------------------------------------------------------
# SECURITY: Rate limiter — prevents API quota exhaustion and abuse
# ---------------------------------------------------------------------------

class _RateLimiter:
    """Token-bucket rate limiter. Thread-safe."""

    def __init__(self, max_calls: int, period_seconds: float):
        self._max = max_calls
        self._period = period_seconds
        self._timestamps: list[float] = []
        self._lock = threading.Lock()

    def acquire(self) -> tuple[bool, float]:
        """Try to acquire a slot. Returns (allowed, retry_after_seconds)."""
        now = time.monotonic()
        with self._lock:
            cutoff = now - self._period
            self._timestamps = [t for t in self._timestamps if t > cutoff]
            if len(self._timestamps) < self._max:
                self._timestamps.append(now)
                return True, 0.0
            oldest = self._timestamps[0]
            retry_after = self._period - (now - oldest)
            return False, max(0.0, retry_after)


# Limits: Gemini free tier ~60 RPM, Groq free tier ~30 RPM. We cap conservatively.
_gemini_rate_limiter = _RateLimiter(max_calls=30, period_seconds=60.0)
_groq_rate_limiter   = _RateLimiter(max_calls=20, period_seconds=60.0)
