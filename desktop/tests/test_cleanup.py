"""Tests for core/cleanup.py — mocks Groq so no real API calls."""
from unittest.mock import MagicMock, patch

import pytest

from ai.cleanup import clean_text


def _mock_groq(response_text: str):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=response_text))]
    )
    return mock_client


# --- No command → passthrough (zero API calls) ---

def test_no_command_returns_input_unchanged():
    raw = "The meeting starts at nine."
    assert clean_text(raw) == raw


def test_empty_string_passthrough():
    assert clean_text("") == ""


def test_clean_sentence_no_api_call():
    raw = "She walked to the store and bought milk."
    with patch("ai.cleanup.Groq") as mock_cls:
        result = clean_text(raw)
    mock_cls.assert_not_called()
    assert result == raw


# --- Commands → API called ---

_FAKE_ENV = {"GROQ_API_KEY": "test-key"}


def test_change_x_to_y():
    raw = "Send the report change Tuesday to Wednesday."
    expected = "Send the report Wednesday."
    with patch.dict("os.environ", _FAKE_ENV):
        with patch("ai.cleanup.Groq") as mock_cls:
            mock_cls.return_value = _mock_groq(expected)
            result = clean_text(raw)
    mock_cls.assert_called_once()
    assert result == expected


def test_replace_x_with_y():
    raw = "Call John replace John with Sarah tomorrow."
    expected = "Call Sarah tomorrow."
    with patch.dict("os.environ", _FAKE_ENV):
        with patch("ai.cleanup.Groq") as mock_cls:
            mock_cls.return_value = _mock_groq(expected)
            result = clean_text(raw)
    assert result == expected


def test_scratch_that():
    raw = "Buy eggs. Scratch that. Buy milk."
    expected = "Buy milk."
    with patch.dict("os.environ", _FAKE_ENV):
        with patch("ai.cleanup.Groq") as mock_cls:
            mock_cls.return_value = _mock_groq(expected)
            result = clean_text(raw)
    assert result == expected


def test_actually_new_content():
    raw = "The event is on Friday. Actually it is on Saturday."
    expected = "The event is on Saturday."
    with patch.dict("os.environ", _FAKE_ENV):
        with patch("ai.cleanup.Groq") as mock_cls:
            mock_cls.return_value = _mock_groq(expected)
            result = clean_text(raw)
    assert result == expected


def test_i_meant():
    raw = "Finish the project by Monday I meant Tuesday."
    expected = "Finish the project by Tuesday."
    with patch.dict("os.environ", _FAKE_ENV):
        with patch("ai.cleanup.Groq") as mock_cls:
            mock_cls.return_value = _mock_groq(expected)
            result = clean_text(raw)
    assert result == expected


def test_i_meant_name_correction():
    raw = "I meant Vijay not Ram."
    expected = "Vijay."
    with patch.dict("os.environ", _FAKE_ENV):
        with patch("ai.cleanup.Groq") as mock_cls:
            mock_cls.return_value = _mock_groq(expected)
            result = clean_text(raw)
    mock_cls.assert_called_once()
    assert result == expected


def test_no_api_key_returns_raw():
    raw = "Send the email scratch that ignore that."
    with patch("ai.cleanup.Groq") as mock_cls:
        with patch.dict("os.environ", {"GROQ_API_KEY": ""}, clear=False):
            result = clean_text(raw)
    mock_cls.assert_not_called()
    assert result == raw
