"""Tests for PersonalDictionary, SystemAudioController, transcriber, and hallucination guards."""

import json
import os
import tempfile
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

try:
    import pycaw  # noqa: F401

    HAS_PYCAW = True
except ImportError:
    HAS_PYCAW = False

_skip_no_pycaw = pytest.mark.skipif(not HAS_PYCAW, reason="pycaw not installed")

from ai.ai_processor import AIProcessor, PersonalDictionary
from audio.audio_control import SystemAudioController
from audio.transcriber import AudioTranscriber

# ==============================================================================
# Helper: Fake AppContext for testing
# ==============================================================================


@dataclass
class FakeAppContext:
    app_name: str = ""
    process_name: str = ""
    category: str = "other"
    tone: str = "neutral"


# ==============================================================================
# PersonalDictionary Tests
# ==============================================================================


def test_personal_dictionary_creation():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        d = PersonalDictionary(dict_path=path)
        assert d.get_terms() == []
    finally:
        os.unlink(path)


def test_personal_dictionary_learn_proper_nouns():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        d = PersonalDictionary(dict_path=path)
        d.learn_from_text("I was talking to Alice about the RotaAI project in Springfield.")
        terms = d.get_terms()
        assert "Alice" in terms
        assert "RotaAI" in terms
        assert "Springfield" in terms
    finally:
        os.unlink(path)


def test_personal_dictionary_learn_technical_terms():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        d = PersonalDictionary(dict_path=path)
        d.learn_from_text("The camelCase variable uses snake_case in the API endpoint.")
        terms = d.get_terms()
        assert "camelCase" in terms
        assert "snake_case" in terms
        assert "API" in terms
    finally:
        os.unlink(path)


def test_personal_dictionary_ignores_common_words():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        d = PersonalDictionary(dict_path=path)
        d.learn_from_text("the quick brown fox jumps over the lazy dog")
        terms = d.get_terms()
        # Common words should NOT be learned
        assert "the" not in terms
        assert "quick" not in terms
    finally:
        os.unlink(path)


def test_personal_dictionary_persistence():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        d1 = PersonalDictionary(dict_path=path)
        d1.add_term("WisprFlow")
        d1.add_term("RotaAI")

        # Load from disk
        d2 = PersonalDictionary(dict_path=path)
        terms = d2.get_terms()
        assert "WisprFlow" in terms
        assert "RotaAI" in terms
    finally:
        os.unlink(path)


def test_personal_dictionary_manual_add_remove():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        d = PersonalDictionary(dict_path=path)
        d.add_term("CustomTerm")
        assert "CustomTerm" in d.get_terms()
        d.remove_term("CustomTerm")
        assert "CustomTerm" not in d.get_terms()
    finally:
        os.unlink(path)


# ==============================================================================
# SystemAudioController Tests
# ==============================================================================


class MockConfig:
    def __init__(self, data):
        self.data = data

    def get(self, key, default=None):
        return self.data.get(key, default)


@patch("audio.audio_control.SystemAudioController._get_master_volume_interface")
def test_audio_controller_mute_mode(mock_get_volume):
    mock_volume = MagicMock()
    mock_volume.GetMute.return_value = 0
    mock_get_volume.return_value = mock_volume

    config = MockConfig({"bg_audio_control": "mute"})
    controller = SystemAudioController(config)

    # Test Muting
    controller.pause_or_mute()
    mock_volume.SetMute.assert_called_once_with(1, None)
    assert controller._muted_by_us is True

    # Test Unmuting
    controller.resume_or_unmute()
    mock_volume.SetMute.assert_any_call(0, None)
    assert controller._muted_by_us is False


@_skip_no_pycaw
@patch("win32api.keybd_event")
@patch("audio.audio_control.get_active_app")
@patch("pycaw.pycaw.AudioUtilities.GetAllSessions")
def test_audio_controller_pause_mode(mock_get_sessions, mock_get_active_app, mock_keybd_event):
    mock_get_active_app.return_value = FakeAppContext(
        app_name="Spotify Premium",
        process_name="Spotify.exe",
        category="media",
        tone="neutral",
    )

    # Case 1: Active audio with peak > 0.005 (Should Pause)
    mock_session = MagicMock()
    mock_session.State = 1  # AudioSessionStateActive
    mock_session.Process = MagicMock()
    mock_session.Process.name.return_value = "spotify.exe"

    mock_meter = MagicMock()
    mock_meter.GetPeakValue.return_value = 0.5  # Active sound
    mock_session._ctl.QueryInterface.return_value = mock_meter

    mock_get_sessions.return_value = [mock_session]

    config = MockConfig({"bg_audio_control": "pause"})
    controller = SystemAudioController(config)

    # Test Pausing when sound is active
    controller.pause_or_mute()
    assert controller._media_paused is True
    assert mock_keybd_event.call_count == 2

    # Test Resuming when paused
    mock_keybd_event.reset_mock()
    controller.resume_or_unmute()
    assert controller._media_paused is False
    assert mock_keybd_event.call_count == 2

    # Case 2: Active session but silent (peak <= 0.005) (Should NOT Pause)
    mock_meter.GetPeakValue.return_value = 0.0  # Silent
    controller = SystemAudioController(config)
    mock_keybd_event.reset_mock()

    controller.pause_or_mute()
    assert controller._media_paused is False
    assert mock_keybd_event.call_count == 0


@_skip_no_pycaw
@patch("win32api.keybd_event")
@patch("audio.audio_control.get_active_app")
@patch("pycaw.pycaw.AudioUtilities.GetAllSessions")
def test_audio_controller_pauses_background_spotify_when_foreground_is_editor(
    mock_get_sessions, mock_get_active_app, mock_keybd_event
):
    mock_get_active_app.return_value = FakeAppContext(
        app_name="Visual Studio Code",
        process_name="Code.exe",
        category="editor",
        tone="technical",
    )

    mock_session = MagicMock()
    mock_session.State = 1
    mock_session.Process = MagicMock()
    mock_session.Process.name.return_value = "spotify.exe"

    mock_meter = MagicMock()
    mock_meter.GetPeakValue.return_value = 0.5
    mock_session._ctl.QueryInterface.return_value = mock_meter

    mock_get_sessions.return_value = [mock_session]

    config = MockConfig({"bg_audio_control": "pause"})
    controller = SystemAudioController(config)

    controller.pause_or_mute()
    assert controller._media_paused is True
    assert mock_keybd_event.call_count == 2


@_skip_no_pycaw
@patch("win32api.keybd_event")
@patch("audio.audio_control.get_active_app")
@patch("pycaw.pycaw.AudioUtilities.GetAllSessions")
def test_audio_controller_pauses_background_browser_audio_when_playing(
    mock_get_sessions, mock_get_active_app, mock_keybd_event
):
    mock_get_active_app.return_value = FakeAppContext(
        app_name="Google Chrome",
        process_name="chrome.exe",
        category="browser",
        tone="neutral",
    )

    mock_session = MagicMock()
    mock_session.State = 1
    mock_session.Process = MagicMock()
    mock_session.Process.name.return_value = "chrome.exe"
    mock_session.Process.pid = 9999  # Mock non-matching PID to bypass os.getpid()

    mock_meter = MagicMock()
    mock_meter.GetPeakValue.return_value = 0.5
    mock_session._ctl.QueryInterface.return_value = mock_meter

    mock_get_sessions.return_value = [mock_session]

    config = MockConfig({"bg_audio_control": "pause"})
    controller = SystemAudioController(config)

    controller.pause_or_mute()
    assert controller._media_paused is True
    assert mock_keybd_event.call_count == 2


# ==============================================================================
# AudioTranscriber Tests
# ==============================================================================


@patch("groq.Groq")
def test_transcriber_technical_prompt_stays_prose(mock_groq_class):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "clean output"
    mock_client.audio.transcriptions.create.return_value = mock_response
    mock_groq_class.return_value = mock_client

    transcriber = AudioTranscriber()
    audio = np.zeros(16000, dtype=np.float32)
    result = transcriber._transcribe_groq(
        audio, app_context=FakeAppContext(category="editor", tone="technical")
    )

    assert result == "clean output"
    prompt = mock_client.audio.transcriptions.create.call_args.kwargs["prompt"]
    assert "Code snippets, programming syntax" not in prompt
    assert "Do not invent code snippets" in prompt


# ==============================================================================
# Hallucination Guard Tests
# ==============================================================================


@patch.dict(os.environ, {"GEMINI_API_KEY": "fake-gemini-key"})
@patch("urllib.request.urlopen")
def test_ai_processor_falls_back_when_output_is_too_different(mock_urlopen):
    """
    Test that a tiny 1-word output for a 10+ word input is rejected as hallucination.
    Guard 3: len(original_words) > 10 and len(candidate_words) < 3 -> reject.
    """
    response_data = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "Wednesday"}]  # Only 1 word for a 10-word input
                }
            }
        ]
    }
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(response_data).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    processor = AIProcessor(ai_provider="gemini")
    # Input has 11 words; returning "Wednesday" (1 word) triggers Guard 3
    result = processor.process_text("I want to move the meeting from Tuesday to Wednesday please")
    # Should fall back to rule-based, NOT accept the 1-word AI output
    assert "Wednesday" in result  # rule-based preserves the original text
    assert len(result.split()) > 1  # must be more than just "Wednesday"


@patch.dict(os.environ, {"GEMINI_API_KEY": "fake-gemini-key"})
@patch("urllib.request.urlopen")
def test_ai_processor_rejects_cleanup_with_too_many_new_words(mock_urlopen):
    """
    Test that an AI output with 0 word overlap and tiny candidate is rejected.
    Guard 2: overlap_count == 0 and len(candidate_words) <= 3 and len(original_words) > 5.
    """
    response_data = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "OK done."}]  # 0 overlap with original, tiny output
                }
            }
        ]
    }
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(response_data).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    processor = AIProcessor(ai_provider="gemini")
    result = processor.process_text("Send the invoice to Priya after lunch tomorrow")

    # "OK done." has 0 overlap with original, 2 words vs 8 input words -> Guard 2 triggers
    # Should fall back to rule-based, preserving original content
    assert "invoice" in result.lower() or "priya" in result.lower() or "send" in result.lower()


# ==============================================================================
# LLM Output Sanitizer Tests
# ==============================================================================


def test_sanitize_llm_output():
    from ai.ai_processor import _sanitize_llm_output

    original = "Update test AI processor.py with new test cases."

    # 1. Output containing code blocks (which should trigger fallback to rule-based because it's mostly code)
    code_output = "Sure! Here is the code:\n```python\ndef test_fn():\n    pass\n```"
    sanitized = _sanitize_llm_output(code_output, original)
    assert "```python" not in sanitized
    assert "def test_fn():" not in sanitized

    # 2. Output with preambles and minor markdown
    markdown_output = "Here's the cleaned text: **This is exciting** and some text."
    sanitized = _sanitize_llm_output(markdown_output, original)
    assert sanitized == "This is exciting and some text."

    # 3. Output that is way too long compared to input (> 20 chars input)
    original_longer = "This is a relatively short input text for testing."
    long_output = "This is a very long text " * 15
    sanitized = _sanitize_llm_output(long_output, original_longer)
    # Should fall back to rule-based cleaning of original_longer
    assert sanitized == "This is a relatively short input text for testing."
