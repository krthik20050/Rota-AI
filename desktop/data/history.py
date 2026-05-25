import os
import sqlite3
import sys
import threading

"""
History manager — stores transcription history in SQLite.

PRIVACY NOTE: All transcriptions (raw + cleaned) are stored in PLAINTEXT
in %APPDATA%/RotaAI/history.db. This includes everything the user ever spoke.
There is no encryption at rest. Any process with file access can read this data.
"""


class HistoryManager:
    """
    Manages a SQLite database to store transcription history.
    Limits the number of entries to 200.
    Uses a single persistent connection to avoid per-call open/close overhead.
    """

    def __init__(self, db_path=None):
        if db_path is None:
            if sys.platform == "darwin":
                appdata_dir = os.path.join(
                    os.path.expanduser("~/Library/Application Support"), "RotaAI"
                )
            else:
                appdata_dir = os.path.join(os.environ.get("APPDATA", "."), "RotaAI")
            if not os.path.exists(appdata_dir):
                os.makedirs(appdata_dir)
            db_path = os.path.join(appdata_dir, "history.db")

        self.db_path = db_path
        self._write_lock = threading.Lock()
        # Persistent connection — check_same_thread=False + _write_lock keeps writes safe.
        # WAL mode allows concurrent reads without locking.
        self._conn = sqlite3.connect(db_path, check_same_thread=False, timeout=5)
        self._init_db()

    def _init_db(self):
        """Initializes the database schema."""
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA synchronous=NORMAL;")
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                raw_text TEXT,
                cleaned_text TEXT,
                is_prompt BOOLEAN
            )
        """)
        self._conn.commit()

    def add_entry(self, raw_text, cleaned_text, is_prompt):
        """Adds a new transcription entry and maintains the 200 entry limit."""
        with self._write_lock:
            cursor = self._conn.cursor()
            cursor.execute(
                """
                INSERT INTO history (raw_text, cleaned_text, is_prompt)
                VALUES (?, ?, ?)
            """,
                (raw_text, cleaned_text, is_prompt),
            )

            # Enforce limit of 200 entries
            cursor.execute("SELECT COUNT(*) FROM history")
            count = cursor.fetchone()[0]
            if count > 200:
                cursor.execute(
                    """
                    DELETE FROM history
                    WHERE id IN (
                        SELECT id FROM history ORDER BY id ASC LIMIT ?
                    )
                """,
                    (count - 200,),
                )

            self._conn.commit()

    def get_entries(self, search_query=None):
        """Retrieves history rows newest-first: (id, timestamp, raw_text, cleaned_text, is_prompt)."""
        cursor = self._conn.cursor()
        if search_query:
            # SECURITY: Sanitize search query to prevent LIKE injection
            sanitized = search_query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            # SECURITY: Limit search query length to prevent abuse
            sanitized = sanitized[:200]
            cursor.execute(
                """
                SELECT id, timestamp, raw_text, cleaned_text, is_prompt
                FROM history
                WHERE raw_text LIKE ? ESCAPE '\\' OR cleaned_text LIKE ? ESCAPE '\\'
                ORDER BY id DESC
            """,
                (f"%{sanitized}%", f"%{sanitized}%"),
            )
        else:
            cursor.execute("""
                SELECT id, timestamp, raw_text, cleaned_text, is_prompt
                FROM history
                ORDER BY id DESC
            """)
        return cursor.fetchall()

    def get_entry(self, entry_id: int):
        """Returns a single entry (id, timestamp, raw_text, cleaned_text, is_prompt) or None."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, timestamp, raw_text, cleaned_text, is_prompt FROM history WHERE id = ?",
            (entry_id,),
        )
        return cursor.fetchone()

    def update_entry(self, entry_id: int, cleaned_text: str):
        """Updates the cleaned_text field of an existing entry."""
        with self._write_lock:
            self._conn.execute(
                "UPDATE history SET cleaned_text = ? WHERE id = ?",
                (cleaned_text, entry_id),
            )
            self._conn.commit()

    def delete_entry(self, entry_id: int):
        """Deletes a single history entry by ID."""
        with self._write_lock:
            self._conn.execute("DELETE FROM history WHERE id = ?", (entry_id,))
            self._conn.commit()

    def prune_old_entries(self, days: int) -> int:
        """
        Delete entries older than `days` days. Returns count of deleted rows.
        Called at startup so history_days config actually trims storage, not just UI.
        """
        days = max(1, min(int(days), 3650))  # clamp 1 day – 10 years
        with self._write_lock:
            cur = self._conn.execute(
                "DELETE FROM history WHERE timestamp < datetime('now', ? || ' days')",
                (f"-{days}",),
            )
            self._conn.commit()
            return cur.rowcount

    def clear_all(self):
        """Deletes ALL history entries. Use with caution."""
        with self._write_lock:
            self._conn.execute("DELETE FROM history")
            self._conn.commit()


if __name__ == "__main__":
    # Quick test
    manager = HistoryManager("test_history.db")
    manager.add_entry("Hello, um, how are you?", "Hello, how are you?", False)
    print(manager.get_entries())
    os.remove("test_history.db")
