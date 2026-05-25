from __future__ import annotations

import json
import os
import random
import sys
import uuid
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from services.session_store import SessionRecord

if TYPE_CHECKING:
    from services.session_store import SessionStore

# Realistic text templates for transcription mock data
MOCK_DIKTAT_SAMPLES = [
    {
        "text": "Essentially, I think we should refactor the landing page layout to be much more responsive. Actually, the current design is a bit slow on mobile devices.",
        "app": "VS Code",
        "category": "editor",
        "fillers": ["essentially", "actually", "i think"],
    },
    {
        "text": "Hi team, so just a quick update on the database migration. The migration scripts are ready to run, but let me know if anyone has questions.",
        "app": "Slack",
        "category": "chat",
        "fillers": ["so", "let me know"],
    },
    {
        "text": "I mean, the marketing copy for the product launch looks pretty good, but we should definitely simplify the pricing section so it's clearer for users.",
        "app": "Chrome",
        "category": "browser",
        "fillers": ["i mean", "so"],
    },
    {
        "text": "Good morning. I've compiled the financial projections for Q3, and basically, we are seeing a steady 12% growth in active subscriptions.",
        "app": "Excel",
        "category": "productivity",
        "fillers": ["basically"],
    },
    {
        "text": "In my opinion, we should definitely prioritize the security audit before launching the OAuth2 changes. Actually, let's discuss this in our next sprint sync.",
        "app": "Notion",
        "category": "productivity",
        "fillers": ["actually", "in my opinion"],
    },
    {
        "text": "Oh, absolutely. The new design system is so much cleaner and the custom widgets are working flawlessly across all screens. Thank you!",
        "app": "Figma",
        "category": "design",
        "fillers": ["absolutely", "so"],
    },
    {
        "text": "Um, let's verify if the backend API has the correct CORS headers configured. Otherwise, the frontend app might fail to load resource files.",
        "app": "VS Code",
        "category": "editor",
        "fillers": ["um", "let's"],
    },
]

APP_LIST = [
    ("VS Code", "editor"),
    ("Slack", "chat"),
    ("Chrome", "browser"),
    ("Notion", "productivity"),
    ("Figma", "design"),
    ("Outlook", "mail"),
]


def seed_mock_data(session_store: SessionStore) -> int:
    """
    Idempotent seeder: Checks if the database is empty, and if so, seeds
    25 realistic historical sessions over the last 30 days to immediately
    populate the Insights & Analytics dashboard for high visual fidelity.

    SECURITY: Only seeds if the database is completely empty AND the app
    has never been run before (no config file exists). This prevents
    overwriting real user data.
    """
    existing = session_store.get_history(limit=5)
    if existing:
        return 0

    # SECURITY: Don't seed if config already exists (app has been configured)
    if sys.platform == "win32":
        appdata_dir = os.path.join(os.environ.get("APPDATA", "."), "RotaAI")
    elif sys.platform == "darwin":
        appdata_dir = os.path.join(os.path.expanduser("~/Library/Application Support"), "RotaAI")
    else:
        xdg_data = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        appdata_dir = os.path.join(xdg_data, "rota-ai")
    config_path = os.path.join(appdata_dir, "config.json")
    if os.path.exists(config_path):
        return 0

    count = 0
    now = datetime.now()

    # Generate 25 sessions over the past 30 days
    # We will spread them with a higher probability on weekdays to create a natural heatmap.
    timestamps = []
    current_date = now - timedelta(days=30)

    # Keep adding days and sessions
    while current_date <= now:
        # 75% chance of a dictation session on a weekday, 20% on weekend
        is_weekend = current_date.weekday() >= 5
        chance = 0.20 if is_weekend else 0.75

        if random.random() < chance:
            # 1 to 3 sessions on that day
            num_sessions = random.randint(1, 3)
            for _ in range(num_sessions):
                # Random hour of the day, leaning towards productivity hours (9 AM - 6 PM)
                if random.random() < 0.8:
                    hour = random.randint(9, 18)
                else:
                    hour = random.choice([7, 8, 19, 20, 21, 22])

                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                session_time = current_date.replace(hour=hour, minute=minute, second=second)
                if session_time <= now:
                    timestamps.append(session_time)

        current_date += timedelta(days=1)

    # Sort chronological
    timestamps.sort()

    # We only need 25-30, let's limit if too many, or expand if too few
    if len(timestamps) < 25:
        # Force add some more
        for i in range(25 - len(timestamps)):
            timestamps.append(now - timedelta(hours=i * 6))
        timestamps.sort()
    else:
        timestamps = timestamps[:28]

    for ts in timestamps:
        sample = random.choice(MOCK_DIKTAT_SAMPLES)
        text = sample["text"]
        app_name = sample["app"]
        app_cat = sample["category"]

        # Randomize content slightly
        words_list = text.split()
        total_words = len(words_list)

        # Calculate scores
        # Clarity depends on filler words. Filler count is random between 0 and 3
        filler_count = random.randint(0, 3)
        filler_ratio = filler_count / max(1, total_words)

        clarity_score = max(
            55, min(100, int(round(100 - (filler_ratio * 200) + random.randint(-5, 5))))
        )
        conciseness_score = random.randint(70, 98)

        # WPM: Speaking is typically 120 - 160 WPM
        wpm = random.randint(120, 160)
        recording_seconds = float(total_words / (wpm / 60.0))

        started_at = ts.timestamp()
        ended_at = started_at + recording_seconds

        # App context
        app_ctx = {"app_name": app_name, "category": app_cat, "tone": "professional"}

        # Filler phrases count
        phrases = {}
        for filler in sample["fillers"]:
            if random.random() < 0.7:
                phrases[filler] = random.randint(1, 2)

        # Generate insight
        if clarity_score >= 85:
            summary = "Your speech is exceptionally clear and structured."
            suggestion = "Great pacing and breathing pattern. Keep doing exactly this."
        elif clarity_score >= 70:
            summary = "Good overall delivery, minor filler words."
            suggestion = "Try adding a brief pause between thoughts to lower the filler count."
        else:
            summary = "High filler ratio detected in this session."
            suggestion = "Consciously slow down and let silent gaps replace wordy hesitations."

        record = SessionRecord(
            session_id=str(uuid.uuid4()),
            started_at=started_at,
            ended_at=ended_at,
            recording_seconds=recording_seconds,
            words=total_words,
            wpm=wpm,
            filler_ratio=filler_ratio,
            clarity_score=clarity_score,
            conciseness_score=conciseness_score,
            insight_summary=summary,
            insight_suggestion=suggestion,
            transcript_text=text,
            app_context=json.dumps(app_ctx),
            backend_used=random.choice(["groq", "local"]),
            filler_count=filler_count,
            phrases_json=json.dumps(phrases) if phrases else "",
        )

        # Add to DB
        # To bypass CURRENT_TIMESTAMP of sqlite, we will manually insert with custom created_at
        with session_store._write_lock:
            import sqlite3

            with sqlite3.connect(session_store.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO sessions (
                        session_id, started_at, ended_at, recording_seconds,
                        words, wpm, filler_ratio, clarity_score, conciseness_score,
                        insight_summary, insight_suggestion,
                        audio_path, transcript_text, app_context, backend_used,
                        filler_count, phrases_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.session_id,
                        record.started_at,
                        record.ended_at,
                        record.recording_seconds,
                        record.words,
                        record.wpm,
                        record.filler_ratio,
                        record.clarity_score,
                        record.conciseness_score,
                        record.insight_summary,
                        record.insight_suggestion,
                        record.audio_path,
                        record.transcript_text,
                        record.app_context,
                        record.backend_used,
                        record.filler_count,
                        record.phrases_json,
                        ts.strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )
                conn.commit()
        count += 1

    return count
