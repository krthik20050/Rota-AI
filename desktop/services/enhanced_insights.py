from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from services._insights_analytics import InsightsAnalyticsMixin
from services.session_store import SessionStore

# ── ponytail:merge — models inlined from _insights_models.py ──────────────
# (removed separate file to reduce file count)


@dataclass
class Persona:
    name: str
    level: int
    xp: int
    title: str
    description: str


@dataclass
class PhraseInsight:
    phrase: str
    count: int
    rank: int


@dataclass
class YearInReview:
    total_words: int
    total_sessions: int
    total_time_saved: float
    avg_wpm: int
    avg_clarity: int
    streak_record: int
    top_phrases: list[PhraseInsight]
    app_breakdown: dict[str, int]
    percentile: int
    persona: Persona


@dataclass
class Achievement:
    id: str
    name: str
    description: str
    icon: str
    unlocked: bool
    unlocked_at: str | None = None


@dataclass
class DailyChallenge:
    id: str
    description: str
    target: int
    progress: int
    completed: bool


PERSONAS = [
    {
        "level": 1,
        "name": "Silent Beginner",
        "title": "Whisperer",
        "description": "First words transcribed",
    },
    {
        "level": 5,
        "name": "Chatterbox",
        "title": "Sprinter",
        "description": "5000 words transcribed",
    },
    {
        "level": 10,
        "name": "Orator",
        "title": "Silver Tongue",
        "description": "10000 words transcribed",
    },
    {
        "level": 20,
        "name": "Polyglot",
        "title": "Word Smith",
        "description": "25000 words transcribed",
    },
    {"level": 50, "name": "Sage", "title": "Oracle", "description": "100000 words transcribed"},
]

ACHIEVEMENTS = [
    {
        "id": "first_session",
        "name": "First Flight",
        "description": "Complete your first transcription",
        "icon": "🎤",
    },
    {
        "id": "week_streak",
        "name": "Week Warrior",
        "description": "Transcribe for 7 consecutive days",
        "icon": "🔥",
    },
    {
        "id": "month_streak",
        "name": "Monthly Master",
        "description": "Transcribe for 30 consecutive days",
        "icon": "🏆",
    },
    {
        "id": "clean_speech",
        "name": "Pristine",
        "description": "Complete a session with 0% filler words",
        "icon": "✨",
    },
    {
        "id": "power_user",
        "name": "Power User",
        "description": "100 sessions completed",
        "icon": "⚡",
    },
]


# Re-export public names so existing imports keep working
__all__ = [
    "EnhancedInsightsService",
    "Persona",
    "PhraseInsight",
    "YearInReview",
    "Achievement",
    "DailyChallenge",
]


class EnhancedInsightsService(InsightsAnalyticsMixin):
    def __init__(self, session_store: SessionStore):
        self.session_store = session_store

    # ------------------------------------------------------------------
    # Persona & gamification
    # ------------------------------------------------------------------

    def get_persona(self) -> Persona:
        history = self.session_store.get_history(limit=1000)
        total_words = sum(h.get("words", 0) for h in history)

        xp = total_words
        level = max(1, xp // 100)

        matched_persona = PERSONAS[0]
        for p in reversed(PERSONAS):
            if xp >= p["level"] * 100:
                matched_persona = p
                break

        return Persona(
            name=matched_persona["name"],
            level=level,
            xp=xp,
            title=matched_persona["title"],
            description=matched_persona["description"],
        )

    def get_phrase_rankings(self, limit: int = 10) -> list[PhraseInsight]:
        phrases = self.session_store.get_total_phrases()
        sorted_phrases = sorted(phrases.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [
            PhraseInsight(phrase=phrase, count=count, rank=i + 1)
            for i, (phrase, count) in enumerate(sorted_phrases)
        ]

    def get_app_usage(self) -> dict[str, int]:
        return self.session_store.get_app_usage()

    def calculate_percentile(self, clarity_score: int) -> int:
        history = self.session_store.get_history(limit=1000)
        if not history:
            return 50
        scores = sorted([h.get("clarity_score", 50) for h in history])
        if not scores:
            return 50
        idx = sum(1 for s in scores if s <= clarity_score)
        return int((idx / len(scores)) * 100)

    # ------------------------------------------------------------------
    # Year in review
    # ------------------------------------------------------------------

    def get_year_in_review(self) -> YearInReview:
        history = self.session_store.get_history(limit=10000)

        total_words = sum(h.get("words", 0) for h in history)
        total_sessions = len(history)
        total_time = sum(h.get("recording_seconds", 0) for h in history)
        avg_wpm = int(total_words / (total_time / 60)) if total_time > 0 else 0
        avg_clarity = (
            int(sum(h.get("clarity_score", 0) for h in history) / total_sessions)
            if total_sessions > 0
            else 0
        )

        streak = self.session_store.get_streak()
        streak_record = streak.get("daily_streak", 0)

        latest = history[0] if history else {}
        latest_clarity = latest.get("clarity_score", 50)
        percentile = self.calculate_percentile(latest_clarity)

        persona = self.get_persona()
        top_phrases = self.get_phrase_rankings()
        app_breakdown = self.get_app_usage()

        return YearInReview(
            total_words=total_words,
            total_sessions=total_sessions,
            total_time_saved=max(0.0, (total_words / 40.0) - (total_time / 60.0)),
            avg_wpm=avg_wpm,
            avg_clarity=avg_clarity,
            streak_record=streak_record,
            top_phrases=top_phrases,
            app_breakdown=app_breakdown,
            percentile=percentile,
            persona=persona,
        )

    # ------------------------------------------------------------------
    # Achievements & daily challenge
    # ------------------------------------------------------------------

    def get_achievements(self) -> list[Achievement]:
        history = self.session_store.get_history(limit=1000)
        streak = self.session_store.get_streak()

        total_sessions = len(history)
        sessions_with_zero_filler = sum(1 for h in history if h.get("filler_ratio", 1) == 0)

        achievements = []
        for ach in ACHIEVEMENTS:
            unlocked = False

            if ach["id"] == "first_session":
                unlocked = total_sessions >= 1
            elif ach["id"] == "week_streak":
                unlocked = streak.get("daily_streak", 0) >= 7
            elif ach["id"] == "month_streak":
                unlocked = streak.get("daily_streak", 0) >= 30
            elif ach["id"] == "clean_speech":
                unlocked = sessions_with_zero_filler >= 1
            elif ach["id"] == "power_user":
                unlocked = total_sessions >= 100

            achievements.append(
                Achievement(
                    id=ach["id"],
                    name=ach["name"],
                    description=ach["description"],
                    icon=ach["icon"],
                    unlocked=unlocked,
                    unlocked_at=datetime.now().isoformat() if unlocked else None,
                )
            )

        return achievements

    def get_daily_challenge(self) -> DailyChallenge:
        today = date.today().isoformat()
        history = self.session_store.get_history(limit=10)

        today_words = 0
        for h in history:
            created_at = h.get("created_at", "")
            if created_at.startswith(today):
                today_words += h.get("words", 0)

        return DailyChallenge(
            id="daily_words",
            description="Transcribe 500 words today",
            target=500,
            progress=today_words,
            completed=today_words >= 500,
        )

    # ------------------------------------------------------------------
    # Dashboard aggregation
    # ------------------------------------------------------------------

    def get_dashboard_insights(self) -> dict:
        persona = self.get_persona()
        streak = self.session_store.get_streak()
        history = self.session_store.get_history(limit=1)
        latest = history[0] if history else {}

        advanced_coaching = self.get_advanced_speech_coaching()

        return {
            "persona": {
                "name": persona.name,
                "title": persona.title,
                "level": persona.level,
                "xp": persona.xp,
            },
            "streak": streak,
            "daily_challenge": self.get_daily_challenge(),
            "achievements_unlocked": sum(1 for a in self.get_achievements() if a.unlocked),
            "latest_session": {
                "clarity_score": latest.get("clarity_score", 0),
                "conciseness_score": latest.get("conciseness_score", 0),
                "filler_ratio": latest.get("filler_ratio", 0.0),
                "percentile": self.calculate_percentile(latest.get("clarity_score", 50)),
            },
            "speech_profile": self.get_speech_profile(),
            "crutch_words": self.get_crutch_words(),
            "lexical_diversity": self.get_lexical_diversity(),
            "active_hours": self.get_active_hours_breakdown(),
            "trends": self.get_trends_data(),
            "productivity": self.get_productivity_stats(),
            "advanced_coaching": advanced_coaching,
            "vocal_drills": self.get_vocal_drills(),
        }
