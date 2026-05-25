from __future__ import annotations

from dataclasses import dataclass


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

CRUTCH_SYNONYMS = {
    "basically": ["fundamentally", "in essence", "at its core"],
    "actually": ["in fact", "indeed", "precisely"],
    "literally": ["truly", "genuinely", "exactly"],
    "seriously": ["sincerely", "genuinely", "earnestly"],
    "obviously": ["clearly", "evidently", "it follows that"],
    "essentially": ["at its core", "fundamentally", "in principle"],
    "you know": ["as you may recall", "consider this", "notably"],
    "i mean": ["to clarify", "what I'm saying is", "put simply"],
    "so": ["therefore", "consequently", "as a result"],
    "like": ["such as", "similar to", "for instance"],
    "just": ["simply", "merely", "precisely"],
    "kind of": ["somewhat", "to some extent", "rather"],
    "sort of": ["in a way", "to a degree", "partially"],
    "um": ["[pause]", "[breathe]", "[silent beat]"],
    "uh": ["[pause]", "[breathe]", "[silent beat]"],
}
