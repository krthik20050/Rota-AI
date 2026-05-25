"""Tests for _RateLimiter in ai.rate_limiter."""

import threading
import time

from ai.rate_limiter import _RateLimiter


def test_allows_calls_within_limit():
    rl = _RateLimiter(max_calls=3, period_seconds=60.0)
    for _ in range(3):
        allowed, retry = rl.acquire()
        assert allowed is True
        assert retry == 0.0


def test_blocks_calls_over_limit():
    rl = _RateLimiter(max_calls=2, period_seconds=60.0)
    rl.acquire()
    rl.acquire()
    allowed, retry = rl.acquire()
    assert allowed is False
    assert retry > 0.0


def test_retry_after_is_positive_when_blocked():
    rl = _RateLimiter(max_calls=1, period_seconds=10.0)
    rl.acquire()
    allowed, retry = rl.acquire()
    assert allowed is False
    assert 0.0 < retry <= 10.0


def test_slots_refill_after_period():
    rl = _RateLimiter(max_calls=1, period_seconds=0.05)
    allowed, _ = rl.acquire()
    assert allowed is True
    # Slot taken
    allowed, _ = rl.acquire()
    assert allowed is False
    # Wait for period to expire
    time.sleep(0.1)
    allowed, _ = rl.acquire()
    assert allowed is True


def test_thread_safety():
    rl = _RateLimiter(max_calls=5, period_seconds=60.0)
    results = []
    lock = threading.Lock()

    def try_acquire():
        allowed, _ = rl.acquire()
        with lock:
            results.append(allowed)

    threads = [threading.Thread(target=try_acquire) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results.count(True) == 5
    assert results.count(False) == 5
