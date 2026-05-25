from unittest.mock import MagicMock

from services.enhanced_insights import EnhancedInsightsService, Persona
from utils.text_metrics import calculate_text_metrics, count_syllables


def test_count_syllables():
    # Simple words
    assert count_syllables("cat") == 1
    assert count_syllables("dog") == 1
    # Silent 'e' at end
    assert count_syllables("phone") == 1
    assert count_syllables("define") == 2
    # Multisyllable complex words
    assert count_syllables("beautiful") == 3
    assert count_syllables("analytical") == 5
    # Special cases and empty values
    assert count_syllables("") == 0
    assert count_syllables(None) == 0
    assert count_syllables("123") == 0


def test_calculate_text_metrics():
    text = "Basically, we definitely will execute a critical refactor. It is absolutely vital!"
    metrics = calculate_text_metrics(text)

    assert metrics.total_words > 0
    assert metrics.pause_efficiency > 0.0
    assert metrics.gunning_fog > 0.0
    assert metrics.grade_level in [
        "Academic / Dense",
        "Executive / Advanced",
        "Clear Professional",
        "Standard Conversational",
        "Simple / Direct",
    ]
    assert "confident" in metrics.tone_ratios
    assert "technical" in metrics.tone_ratios


def test_enhanced_insights_service():
    mock_store = MagicMock()

    # Mock history list
    mock_store.get_history.return_value = [
        {
            "words": 150,
            "recording_seconds": 60,
            "clarity_score": 92,
            "conciseness_score": 85,
            "filler_ratio": 0.02,
            "filler_count": 3,
            "wpm": 150,
            "created_at": "2026-05-21T10:00:00",
            "transcript_text": "Basically, we definitely will execute a critical refactor of the database. It is absolutely vital!",
        },
        {
            "words": 80,
            "recording_seconds": 40,
            "clarity_score": 75,
            "conciseness_score": 70,
            "filler_ratio": 0.06,
            "filler_count": 5,
            "wpm": 120,
            "created_at": "2026-05-21T11:00:00",
            "transcript_text": "I think maybe we should consider other options. Perhaps it's better to verify the metrics first.",
        },
    ]
    mock_store.get_streak.return_value = {"daily_streak": 5}
    mock_store.get_total_phrases.return_value = {"refactor": 2, "metrics": 1}
    mock_store.get_app_usage.return_value = {"VSCode": 5, "Slack": 2}

    service = EnhancedInsightsService(session_store=mock_store)

    # Test get_persona
    persona = service.get_persona()
    assert isinstance(persona, Persona)
    assert persona.level >= 1

    # Test get_speech_profile
    profile = service.get_speech_profile()
    assert "archetype_name" in profile
    assert profile["avg_wpm"] == 135

    # Test get_advanced_speech_coaching
    coaching = service.get_advanced_speech_coaching()
    assert "pause_efficiency_pct" in coaching
    assert "cadence_variety" in coaching
    assert "speech_coach" in coaching
    assert "focus_title" in coaching["speech_coach"]

    # Test get_dashboard_insights
    insights = service.get_dashboard_insights()
    assert "persona" in insights
    assert "advanced_coaching" in insights
    assert (
        insights["advanced_coaching"]["speech_coach"]["focus_title"]
        == coaching["speech_coach"]["focus_title"]
    )
