from __future__ import annotations

import json
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class SessionRecord:
    session_id: str
    started_at: float
    ended_at: float
    recording_seconds: float
    words: int
    wpm: int
    filler_ratio: float
    clarity_score: int
    conciseness_score: int
    insight_summary: str
    insight_suggestion: str
    audio_path: str = ""
    transcript_text: str = ""
    app_context: str = ""
    backend_used: str = ""
    filler_count: int = 0
    phrases_json: str = ""


# New columns added in this version
_MIGRATION_COLUMNS: list[tuple[str, str]] = [
    ("audio_path",      "TEXT DEFAULT ''"),
    ("transcript_text", "TEXT DEFAULT ''"),
    ("app_context",     "TEXT DEFAULT ''"),
    ("backend_used",    "TEXT DEFAULT ''"),
    ("filler_count",    "INTEGER DEFAULT 0"),
    ("phrases_json",    "TEXT DEFAULT ''"),
]


class SessionStore:
    """Stores session analytics + transcript history with per-session context."""

    def __init__(self, db_path: str = "data/history.db"):
        self.db_path = db_path
        self._write_lock = threading.Lock()
        self._init_db()

    # ------------------------------------------------------------------ #
    #  Schema management
    # ------------------------------------------------------------------ #

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id          TEXT UNIQUE NOT NULL,
                    started_at          REAL NOT NULL,
                    ended_at            REAL NOT NULL,
                    recording_seconds   REAL NOT NULL DEFAULT 0.0,
                    words               INTEGER NOT NULL DEFAULT 0,
                    wpm                 INTEGER NOT NULL DEFAULT 0,
                    filler_ratio        REAL NOT NULL DEFAULT 0.0,
                    clarity_score       INTEGER NOT NULL DEFAULT 0,
                    conciseness_score   INTEGER NOT NULL DEFAULT 0,
                    insight_summary     TEXT NOT NULL DEFAULT '',
                    insight_suggestion  TEXT NOT NULL DEFAULT '',
                    audio_path          TEXT DEFAULT '',
                    transcript_text     TEXT DEFAULT '',
                    app_context         TEXT DEFAULT '',
                    backend_used        TEXT DEFAULT '',
                    filler_count        INTEGER DEFAULT 0,
                    phrases_json        TEXT DEFAULT '',
                    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
            self._migrate(conn)

    def _migrate(self, conn: sqlite3.Connection) -> None:
        """Add any missing columns (idempotent)."""
        for col_name, col_def in _MIGRATION_COLUMNS:
            try:
                conn.execute(f"ALTER TABLE sessions ADD COLUMN {col_name} {col_def}")
                conn.commit()
            except sqlite3.OperationalError:
                pass  # Column already exists — expected on second+ startup

    # ------------------------------------------------------------------ #
    #  Write operations
    # ------------------------------------------------------------------ #

    def add_session(self, item: SessionRecord) -> None:
        """Original write API — backward-compatible with existing callers."""
        with self._write_lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO sessions (
                        session_id, started_at, ended_at, recording_seconds,
                        words, wpm, filler_ratio, clarity_score, conciseness_score,
                        insight_summary, insight_suggestion,
                        audio_path, transcript_text, app_context, backend_used, filler_count, phrases_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item.session_id,
                        item.started_at,
                        item.ended_at,
                        item.recording_seconds,
                        item.words,
                        item.wpm,
                        item.filler_ratio,
                        item.clarity_score,
                        item.conciseness_score,
                        item.insight_summary,
                        item.insight_suggestion,
                        item.audio_path,
                        item.transcript_text,
                        item.app_context,
                        item.backend_used,
                        item.filler_count,
                        item.phrases_json,
                    ),
                )
                conn.commit()

    def save_session(
        self,
        session_id: str,
        transcript_text: str,
        *,
        started_at: Optional[float] = None,
        ended_at: Optional[float] = None,
        audio_path: str = "",
        app_context: Optional[Dict[str, str]] = None,
        backend_used: str = "",
        filler_count: int = 0,
        phrases: Optional[Dict[str, int]] = None,
        recording_seconds: float = 0.0,
        words: int = 0,
        wpm: int = 0,
        filler_ratio: float = 0.0,
        clarity_score: int = 0,
        conciseness_score: int = 0,
        insight_summary: str = "",
        insight_suggestion: str = "",
    ) -> None:
        """
        Convenience write API for the new pipeline fields.
        app_context: dict like {"app_name": "...", "category": "...", "tone": "..."}
        phrases: dict of phrase -> count
        """
        now = time.time()
        record = SessionRecord(
            session_id=session_id,
            started_at=started_at or now,
            ended_at=ended_at or now,
            recording_seconds=recording_seconds,
            words=words,
            wpm=wpm,
            filler_ratio=filler_ratio,
            clarity_score=clarity_score,
            conciseness_score=conciseness_score,
            insight_summary=insight_summary,
            insight_suggestion=insight_suggestion,
            audio_path=audio_path,
            transcript_text=transcript_text,
            app_context=json.dumps(app_context) if app_context else "",
            backend_used=backend_used,
            filler_count=filler_count,
            phrases_json=json.dumps(phrases) if phrases else "",
        )
        self.add_session(record)

    def prune_old_sessions(self, days: int) -> int:
        """
        Delete sessions older than `days` days. Returns count of deleted rows.
        Called at startup so history_days config trims storage, not just UI display.
        """
        days = max(1, min(int(days), 3650))  # clamp 1 day – 10 years
        with self._write_lock:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute(
                    "DELETE FROM sessions WHERE created_at < datetime('now', ? || ' days')",
                    (f"-{days}",),
                )
                conn.commit()
                return cur.rowcount

    def delete_session(self, session_id: str) -> bool:
        """Delete session by session_id. Returns True if a row was deleted."""
        with self._write_lock:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute(
                    "DELETE FROM sessions WHERE session_id = ?", (session_id,)
                )
                conn.commit()
                return cur.rowcount > 0

    # ------------------------------------------------------------------ #
    #  Read operations
    # ------------------------------------------------------------------ #

    def _row_to_dict(self, row: tuple, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        cols = [d[0] for d in cursor.description]
        return dict(zip(cols, row))

    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return all sessions newest-first, up to limit."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT * FROM sessions ORDER BY created_at DESC LIMIT ?", (limit,)
            )
            rows = cur.fetchall()
            return [self._row_to_dict(r, cur) for r in rows]

    def get_last_n(self, n: int) -> List[Dict[str, Any]]:
        """Return the last n sessions (newest-first)."""
        return self.get_history(limit=n)

    def get_latest(self) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                """
                SELECT session_id, words, wpm, filler_ratio, clarity_score, conciseness_score,
                       insight_summary, insight_suggestion, created_at
                FROM sessions
                ORDER BY created_at DESC
                LIMIT 1
                """
            )
            row = cur.fetchone()
            if row is None:
                return None
            return {
                "session_id": row[0],
                "words": row[1],
                "wpm": row[2],
                "filler_ratio": row[3],
                "clarity_score": row[4],
                "conciseness_score": row[5],
                "insight_summary": row[6],
                "insight_suggestion": row[7],
                "created_at": row[8] or datetime.utcnow().isoformat(),
            }

    def _aggregate(self, today_only: bool) -> dict:
        where = (
            "WHERE date(started_at, 'unixepoch', 'localtime') = date('now', 'localtime')"
            if today_only
            else ""
        )
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                f"""
                SELECT COALESCE(SUM(words), 0),
                       COALESCE(SUM(recording_seconds), 0.0),
                       COUNT(*)
                FROM sessions {where}
                """
            )
            row = cur.fetchone() or (0, 0.0, 0)
        words = int(row[0] or 0)
        secs = float(row[1] or 0.0)
        mins = secs / 60.0
        return {
            "words": words,
            "recording_seconds": secs,
            "sessions": int(row[2] or 0),
            "wpm": int(round(words / mins)) if mins > 1e-6 else 0,
        }

    def get_dashboard_metrics(self) -> dict:
        return {
            "today": self._aggregate(today_only=True),
            "lifetime": self._aggregate(today_only=False),
            "latest": self.get_latest(),
        }

    def get_daily_word_counts(self, days: int = 91) -> dict:
        """Returns {YYYY-MM-DD: word_count} for the last N days."""
        days = max(1, min(int(days), 3650))  # validate — prevents SQL injection via f-string
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                """
                SELECT date(started_at, 'unixepoch', 'localtime') AS day,
                       COALESCE(SUM(words), 0) AS total
                FROM sessions
                WHERE started_at >= strftime('%s', 'now', 'localtime', ? || ' days')
                GROUP BY day
                """,
                (f"-{days}",),
            )
            return {row[0]: int(row[1]) for row in cur.fetchall()}

    def get_streak(self) -> dict:
        """Returns daily_streak and weekly_streak (consecutive days/weeks with ≥1 session)."""
        from datetime import date, timedelta
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                """
                SELECT DISTINCT date(started_at, 'unixepoch', 'localtime') AS day
                FROM sessions WHERE words > 0 ORDER BY day DESC
                """
            )
            days_list = [row[0] for row in cur.fetchall()]

        today = date.today()

        daily_streak = 0
        for i, day_str in enumerate(days_list):
            if date.fromisoformat(day_str) == today - timedelta(days=i):
                daily_streak += 1
            else:
                break

        week_set: set = set()
        for day_str in days_list:
            d = date.fromisoformat(day_str)
            iso = d.isocalendar()
            week_set.add((iso[0], iso[1]))

        weekly_streak = 0
        iso_today = today.isocalendar()
        current_week = (iso_today[0], iso_today[1])
        while current_week in week_set:
            weekly_streak += 1
            prev_monday = date.fromisocalendar(current_week[0], current_week[1], 1) - timedelta(weeks=1)
            iso_prev = prev_monday.isocalendar()
            current_week = (iso_prev[0], iso_prev[1])

        return {"daily_streak": daily_streak, "weekly_streak": weekly_streak}

    def get_range_metrics(self, range_key: str) -> dict:
        """Aggregate metrics. range_key: 'today' | 'week' | 'month' | 'all'"""
        where_map = {
            "today": "WHERE date(started_at, 'unixepoch', 'localtime') = date('now', 'localtime')",
            "week":  "WHERE started_at >= strftime('%s', date('now', 'localtime', '-6 days'))",
            "month": "WHERE started_at >= strftime('%s', date('now', 'localtime', 'start of month'))",
            "all":   "",
        }
        where = where_map.get(range_key, "")
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                f"""
                SELECT COALESCE(SUM(words), 0),
                       COALESCE(SUM(recording_seconds), 0.0),
                       COUNT(*)
                FROM sessions {where}
                """
            )
            row = cur.fetchone() or (0, 0.0, 0)
        words = int(row[0] or 0)
        secs  = float(row[1] or 0.0)
        mins  = secs / 60.0
        sessions = int(row[2] or 0)
        # Time saved: dictating is faster than typing (assume 40 WPM baseline)
        time_saved = max(0.0, (words / 40.0) - mins)
        return {
            "words":            words,
            "recording_seconds": secs,
            "sessions":         sessions,
            "wpm":              int(round(words / mins)) if mins > 1e-6 else 0,
            "time_saved_mins":  time_saved,
        }

    def get_total_phrases(self) -> Dict[str, int]:
        """Aggregate phrase counts across all sessions."""
        total: Dict[str, int] = {}
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT phrases_json FROM sessions WHERE phrases_json != '' AND phrases_json IS NOT NULL"
            )
            for row in cur.fetchall():
                phrases = json.loads(row[0])
                for phrase, count in phrases.items():
                    total[phrase] = total.get(phrase, 0) + count
        return total

    def get_app_usage(self) -> Dict[str, int]:
        """Count sessions per app."""
        usage: Dict[str, int] = {}
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT app_context FROM sessions WHERE app_context != '' AND app_context IS NOT NULL"
            )
            for row in cur.fetchall():
                ctx = json.loads(row[0])
                app_name = ctx.get("app_name", "unknown")
                usage[app_name] = usage.get(app_name, 0) + 1
        return usage


# Run tests via: python -m tests.test_session_store  (see tests/test_session_store.py)
