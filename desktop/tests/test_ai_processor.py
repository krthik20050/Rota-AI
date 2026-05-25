"""Tests for AIProcessor core: spoken punctuation, rule-based cleaning, prompt builder, and AI backend."""

import json
import os
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

from ai.ai_processor import (
    AIProcessor,
    _build_dynamic_prompt,
    _preprocess_spoken_punctuation,
    _rule_based_clean,
)

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
# Spoken Punctuation Pre-processor Tests
# ==============================================================================


def test_spoken_punctuation_period():
    assert _preprocess_spoken_punctuation("Hello world period") == "Hello world."


def test_spoken_punctuation_comma():
    assert _preprocess_spoken_punctuation("Hello comma world") == "Hello, world"


def test_spoken_punctuation_question_mark():
    assert _preprocess_spoken_punctuation("How are you question mark") == "How are you?"


def test_spoken_punctuation_new_line():
    result = _preprocess_spoken_punctuation("first line new line second line")
    assert "\n" in result


def test_spoken_punctuation_new_paragraph():
    result = _preprocess_spoken_punctuation("paragraph one new paragraph paragraph two")
    assert "\n\n" in result


def test_spoken_punctuation_mixed():
    result = _preprocess_spoken_punctuation("Hello comma how are you question mark")
    assert result == "Hello, how are you?"


# ==============================================================================
# Rule-Based Clean Tests
# ==============================================================================


def test_rule_based_removes_fillers():
    result = _rule_based_clean("um uh Hello world")
    assert "um" not in result
    assert "uh" not in result
    assert "Hello" in result


def test_rule_based_capitalizes_sentences():
    result = _rule_based_clean("hello world. this is a test.")
    assert result.startswith("Hello")
    assert "This is a test." in result


def test_rule_based_adds_trailing_period():
    result = _rule_based_clean("Hello world this is nice")
    assert result.endswith(".")


def test_rule_based_empty_input():
    assert _rule_based_clean("") == ""
    assert _rule_based_clean("   ") == ""


# ==============================================================================
# Dynamic Prompt Builder Tests
# ==============================================================================


def test_dynamic_prompt_includes_base():
    prompt = _build_dynamic_prompt("clean")
    assert "voice-to-text post-processor" in prompt
    assert "ANTI-HALLUCINATION" in prompt


def test_dynamic_prompt_with_email_context():
    ctx = FakeAppContext(app_name="Outlook", category="email", tone="formal")
    prompt = _build_dynamic_prompt("clean", app_context=ctx)
    assert "Email Application" in prompt
    assert "Outlook" in prompt


def test_dynamic_prompt_with_chat_context():
    ctx = FakeAppContext(app_name="Slack", category="chat", tone="casual")
    prompt = _build_dynamic_prompt("clean", app_context=ctx)
    assert "Chat Application" in prompt
    assert "Slack" in prompt
    assert "casual" in prompt


def test_dynamic_prompt_with_editor_context():
    ctx = FakeAppContext(app_name="VS Code", category="editor", tone="technical")
    prompt = _build_dynamic_prompt("clean", app_context=ctx)
    assert "Code Editor" in prompt
    assert "camelCase" in prompt


def test_dynamic_prompt_with_field_text():
    prompt = _build_dynamic_prompt("clean", field_text="I was just saying that")
    assert "EXISTING TEXT IN FIELD" in prompt
    assert "I was just saying that" in prompt


def test_dynamic_prompt_with_personal_terms():
    prompt = _build_dynamic_prompt("clean", personal_terms=["RotaAI", "Groq", "WisprFlow"])
    assert "PERSONAL VOCABULARY" in prompt
    assert "RotaAI" in prompt


def test_dynamic_prompt_professional_mode():
    """Professional mode should return a dedicated prompt, not the dynamic one."""
    prompt = _build_dynamic_prompt("professional")
    assert "FORMAL PROFESSIONAL" in prompt


def test_dynamic_prompt_email_mode():
    """Email mode should return a dedicated email formatting prompt."""
    prompt = _build_dynamic_prompt("email")
    assert "PROFESSIONAL EMAIL" in prompt


def test_dynamic_prompt_bullets_mode():
    prompt = _build_dynamic_prompt("bullets")
    assert "BULLET POINTS" in prompt


# ==============================================================================
# AIProcessor Tests
# ==============================================================================


@patch.dict(os.environ, {"GROQ_API_KEY": "fake-groq-key", "GEMINI_API_KEY": "fake-gemini-key"})
def test_ai_processor_initialization():
    processor = AIProcessor(
        writing_mode="clean",
        ai_provider="groq",
        ollama_model="llama3.2:1b",
        ollama_url="http://localhost:11434",
    )
    assert processor.writing_mode == "clean"
    assert processor.ai_provider == "groq"
    assert processor.ollama_model == "llama3.2:1b"
    assert processor.ollama_url == "http://localhost:11434"
    assert processor.active_backend == "groq"
    assert processor.model == "llama-3.3-70b-versatile"


@patch.dict(os.environ, {"GROQ_API_KEY": "fake-groq-key", "GEMINI_API_KEY": "fake-gemini-key"})
def test_ai_processor_active_backend_selection():
    # Test Groq selection
    processor = AIProcessor(ai_provider="groq")
    assert processor.active_backend == "groq"

    # Test Gemini selection
    processor = AIProcessor(ai_provider="gemini")
    assert processor.active_backend == "gemini"

    # Test Ollama selection
    processor = AIProcessor(ai_provider="ollama")
    assert processor.active_backend == "ollama"

    # Test fallback to rule-based if keys are missing
    with patch.dict(os.environ, {"GROQ_API_KEY": "", "GEMINI_API_KEY": ""}, clear=True):
        processor_no_keys = AIProcessor(ai_provider="groq")
        assert processor_no_keys.active_backend == "rule-based"


@patch.dict(os.environ, {"GROQ_API_KEY": "fake-groq-key", "GEMINI_API_KEY": "fake-gemini-key"})
def test_ai_processor_gemini_is_default():
    """Gemini should be selected when ai_provider is 'gemini' (the new default)."""
    processor = AIProcessor(ai_provider="gemini")
    assert processor.active_backend == "gemini"
    assert processor.model == "gemini-2.0-flash"


@patch.dict(os.environ, {"GROQ_API_KEY": "fake-groq-key", "GEMINI_API_KEY": "fake-gemini-key"})
def test_ai_processor_auto_provider():
    """Auto mode should prefer Gemini when both keys are available."""
    processor = AIProcessor(ai_provider="auto")
    assert processor.active_backend == "gemini"


@patch.dict(os.environ, {"GROQ_API_KEY": "fake-groq-key"})
@patch("ai.ai_processor.Groq")
def test_groq_process_success(mock_groq_class):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Polished text from Groq"))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_groq_class.return_value = mock_client

    processor = AIProcessor(ai_provider="groq")
    result = processor.process_text("Raw dictation um actually scratch that polished text")
    assert result == "Polished text from Groq"


@patch.dict(os.environ, {"GROQ_API_KEY": "fake-groq-key"})
@patch("ai.ai_processor.Groq")
def test_groq_process_fallback_to_8b(mock_groq_class):
    mock_client = MagicMock()
    # First call (70B) raises, second call (8B) succeeds
    mock_client.chat.completions.create.side_effect = [
        Exception("Rate limit"),
        MagicMock(
            choices=[MagicMock(message=MagicMock(content="Polished text from instant fallback"))]
        ),
    ]
    mock_groq_class.return_value = mock_client

    processor = AIProcessor(ai_provider="groq")
    result = processor.process_text("Raw dictation")
    assert result == "Polished text from instant fallback"
    assert mock_client.chat.completions.create.call_count == 2


@patch.dict(os.environ, {"GEMINI_API_KEY": "fake-gemini-key"})
@patch("urllib.request.urlopen")
def test_gemini_process_success(mock_urlopen):
    response_data = {
        "candidates": [{"content": {"parts": [{"text": "Polished text from Gemini"}]}}]
    }
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(response_data).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    processor = AIProcessor(ai_provider="gemini")
    result = processor.process_text("Raw dictation")
    assert result == "Polished text from Gemini"


@patch.dict(os.environ, {"GEMINI_API_KEY": "fake-gemini-key", "GROQ_API_KEY": "fake-groq-key"})
@patch("ai.ai_processor.Groq")
@patch("urllib.request.urlopen")
def test_gemini_fallback_to_groq(mock_urlopen, mock_groq_class):
    """When Gemini fails, should cascade to Groq."""
    import urllib.error

    mock_urlopen.side_effect = urllib.error.URLError("Connection failed")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Groq fallback text"))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_groq_class.return_value = mock_client

    processor = AIProcessor(ai_provider="gemini")
    result = processor.process_text("Raw dictation")
    assert result == "Groq fallback text"


def test_rule_based_fallback_when_no_keys():
    with patch.dict(os.environ, {"GROQ_API_KEY": "", "GEMINI_API_KEY": ""}, clear=True):
        processor = AIProcessor(ai_provider="groq")
        result = processor.process_text("um uh Hello world like you know")
        assert result == "Hello world like you know."


def test_raw_mode_passthrough():
    """Raw mode should return text unchanged."""
    processor = AIProcessor(writing_mode="raw")
    result = processor.process_text("um uh hello world")
    assert result == "um uh hello world"


def test_process_text_empty_input():
    processor = AIProcessor()
    assert processor.process_text("") == ""
    assert processor.process_text("   ") == ""
    assert processor.process_text(None) == ""


@patch.dict(os.environ, {"GROQ_API_KEY": "fake-groq-key"})
@patch("ai.ai_processor.Groq")
def test_process_text_with_app_context(mock_groq_class):
    """Verify that app context is included in the prompt sent to the LLM."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Cleaned text"))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_groq_class.return_value = mock_client

    ctx = FakeAppContext(app_name="Slack - General", category="chat", tone="casual")
    processor = AIProcessor(ai_provider="groq")
    result = processor.process_text("hey what's up", app_context=ctx)
    assert result == "Cleaned text"

    # Verify the system prompt includes chat context
    call_args = mock_client.chat.completions.create.call_args
    system_msg = call_args.kwargs["messages"][0]["content"]
    assert "Chat Application" in system_msg or "Messaging" in system_msg


def test_command_detection():
    processor = AIProcessor()

    # Test email command
    mode, text = processor.detect_command("mail this I want to send a message")
    assert mode == "email"
    assert "I want to send a message" in text

    # Test summarize command
    mode, text = processor.detect_command("summarize this meeting was about the product launch")
    assert mode == "summarize"

    # Test no command
    mode, text = processor.detect_command("just regular text nothing special")
    assert mode == ""
    assert text == "just regular text nothing special"
