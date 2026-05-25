"""
Smoke tests for SessionStore — extracted from services/session_store.py.
Run: python -m tests.test_session_store  (from desktop/)
"""

from __future__ import annotations

import json
import os
import sys
import time
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.session_store import SessionRecord, SessionStore

DB = "data/_test_sessions.db"


def run() -> None:
    if os.path.exists(DB):
        os.remove(DB)

    store = SessionStore(DB)
    print("=== SessionStore tests ===")

    sid1 = str(uuid.uuid4())
    sid2 = str(uuid.uuid4())

    # Test 1: save_session (new API)
    store.save_session(
        session_id=sid1,
        transcript_text="Hello this is a test",
        audio_path="/tmp/audio1.wav",
        app_context={"app_name": "Brave", "category": "browser", "tone": "neutral"},
        backend_used="groq",
        filler_count=2,
        phrases={"thank you": 1, "good morning": 2},
        words=5,
    )
    print("[PASS] save_session (new API)")

    # Test 2: add_session (legacy API)
    store.add_session(
        SessionRecord(
            session_id=sid2,
            started_at=time.time() - 10,
            ended_at=time.time(),
            recording_seconds=10.0,
            words=10,
            wpm=60,
            filler_ratio=0.1,
            clarity_score=85,
            conciseness_score=80,
            insight_summary="Good",
            insight_suggestion="Keep going",
            transcript_text="Another test session",
            backend_used="local",
            filler_count=1,
        )
    )
    print("[PASS] add_session (legacy API)")

    # Test 3: get_history
    history = store.get_history()
    assert len(history) == 2, f"expected 2 rows, got {len(history)}"
    print(f"[PASS] get_history: {len(history)} rows")

    # Test 4: get_last_n
    last1 = store.get_last_n(1)
    assert len(last1) == 1
    print(f"[PASS] get_last_n(1): {last1[0]['session_id'][:8]}...")
    row = next(r for r in history if r["session_id"] == sid1)
    assert row["backend_used"] == "groq", f"backend_used: {row['backend_used']}"
    assert row["filler_count"] == 2, f"filler_count: {row['filler_count']}"
    ctx = json.loads(row["app_context"])
    assert ctx["category"] == "browser"
    phrases = json.loads(row["phrases_json"])
    assert phrases.get("thank you") == 1
    print("[PASS] extended fields saved correctly")

    # Test 6: get_total_phrases
    total_phrases = store.get_total_phrases()
    assert total_phrases.get("thank you") == 1
    print("[PASS] get_total_phrases")

    # Test 7: get_app_usage
    app_usage = store.get_app_usage()
    assert app_usage.get("Brave") == 1
    print("[PASS] get_app_usage")

    # Test 8: delete_session
    deleted = store.delete_session(sid1)
    assert deleted is True
    history2 = store.get_history()
    assert len(history2) == 1
    print("[PASS] delete_session")

    # Test 9: get_latest
    latest = store.get_latest()
    assert latest is not None
    print(f"[PASS] get_latest: session_id={latest['session_id'][:8]}...")

    # Test 10: idempotent migration (create store again against same DB)
    store2 = SessionStore(DB)
    assert len(store2.get_history()) == 1
    print("[PASS] idempotent migration on re-open")

    # Cleanup
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(DB + suffix)
        except OSError:
            pass
    print("\nAll SessionStore tests passed.")


if __name__ == "__main__":
    run()
