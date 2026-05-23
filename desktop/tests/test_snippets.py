"""Tests for SnippetsManager — validates exact, fuzzy, and inline expansions."""
import os
from unittest.mock import patch
import pytest
from data.snippets import SnippetsManager

@pytest.fixture
def temp_snippets(tmp_path):
    path = os.path.join(tmp_path, "test_snippets.json")
    manager = SnippetsManager(snippets_path=path)
    return manager

def test_snippets_crud(temp_snippets):
    manager = temp_snippets
    assert manager.count() == 0

    # Add a snippet
    ok, msg = manager.set("cal link", "https://calendly.com/user")
    assert ok
    assert manager.count() == 1
    assert manager.all() == {"cal link": "https://calendly.com/user"}

    # Validation: Trigger phrase too long
    long_trigger = "a" * 61
    ok, msg = manager.set(long_trigger, "too long")
    assert not ok
    assert "too long" in msg

    # Validation: Expansion too long
    long_expansion = "a" * 4001
    ok, msg = manager.set("trigger", long_expansion)
    assert not ok
    assert "too long" in msg

    # Delete snippet
    deleted = manager.delete("cal link")
    assert deleted
    assert manager.count() == 0

def test_exact_expansion(temp_snippets):
    manager = temp_snippets
    manager.set("email signature", "Best regards,\nJohn Doe")

    # Exact match case-insensitive
    expanded = manager.expand("email signature")
    assert expanded == "Best regards,\nJohn Doe"

    expanded_caps = manager.expand("EMAIL SIGNATURE")
    assert expanded_caps == "Best regards,\nJohn Doe"

    # Non-matching
    assert manager.expand("signature") is None

def test_fuzzy_expansion(temp_snippets):
    manager = temp_snippets
    manager.set("my calendar link", "https://calendly.com/user")

    # Close enough fuzzy match (e.g. spelling or speech recognition slip)
    expanded = manager.expand("my calender link")
    assert expanded == "https://calendly.com/user"

    # Too different
    assert manager.expand("calendar link") is None

def test_inline_expansion_wispr_flow_parity(temp_snippets):
    manager = temp_snippets
    manager.set("cal link", "https://calendly.com/user")
    manager.set("my address", "123 Main St, Seattle")

    # In-sentence replacement
    sentence = "Here is my cal link and my address is 123 Main St."
    expanded = manager.expand(sentence)
    
    assert expanded is not None
    assert "https://calendly.com/user" in expanded
    assert "123 Main St, Seattle" in expanded
    assert expanded == "Here is my https://calendly.com/user and 123 Main St, Seattle is 123 Main St."

    # Test word boundary safety (should NOT expand "cal" inside "calendar")
    non_trigger_sentence = "Please check my calendar tomorrow."
    assert manager.expand(non_trigger_sentence) is None

def test_variables_replacement(temp_snippets):
    manager = temp_snippets
    manager.set("today date", "Today is {{date}}.")
    
    # Mock date
    import datetime
    fixed_date = datetime.datetime(2026, 5, 20)
    
    with patch("data.snippets.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_date
        expanded = manager.expand("today date")
        assert expanded == "Today is 2026-05-20."

    # Test clipboard variable
    manager.set("paste clipboard", "Info: {{clipboard}}")
    with patch("data.snippets._get_clipboard_text", return_value="secret clipboard content"):
        expanded = manager.expand("paste clipboard")
        assert expanded == "Info: secret clipboard content"
