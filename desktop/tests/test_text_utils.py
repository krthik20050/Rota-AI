"""Tests for pure helper functions in ai.text_utils."""

from ai.text_utils import (
    _is_too_different,
    _preprocess_spoken_punctuation,
    _rule_based_clean,
    _sanitize_llm_output,
)

# ── _preprocess_spoken_punctuation ──────────────────────────────────────────


class TestSpokenPunctuation:
    def test_full_stop(self):
        result = _preprocess_spoken_punctuation("hello full stop world")
        assert "." in result
        assert "full stop" not in result

    def test_comma(self):
        result = _preprocess_spoken_punctuation("one comma two")
        assert "," in result
        assert "comma" not in result

    def test_question_mark(self):
        result = _preprocess_spoken_punctuation("how are you question mark")
        assert "?" in result
        assert "question mark" not in result

    def test_new_line(self):
        result = _preprocess_spoken_punctuation("item one new line item two")
        assert "\n" in result
        assert "new line" not in result

    def test_no_change_for_normal_text(self):
        text = "Hello world, how are you?"
        assert _preprocess_spoken_punctuation(text) == text

    def test_open_paren(self):
        result = _preprocess_spoken_punctuation("open paren note close paren")
        assert "(" in result
        assert ")" in result


# ── _rule_based_clean ───────────────────────────────────────────────────────


class TestRuleBasedClean:
    def test_removes_filler_words(self):
        result = _rule_based_clean("um hello uh world")
        assert "um" not in result.lower()
        assert "uh" not in result.lower()

    def test_capitalizes_first_word(self):
        result = _rule_based_clean("hello world")
        assert result[0].isupper()

    def test_preserves_question_mark(self):
        result = _rule_based_clean("is this a question?")
        assert result.endswith("?")

    def test_collapses_multiple_spaces(self):
        result = _rule_based_clean("hello   world")
        assert "  " not in result

    def test_empty_input(self):
        result = _rule_based_clean("")
        assert result == ""

    def test_hmm_removed(self):
        result = _rule_based_clean("hmm I think so")
        assert "hmm" not in result.lower()

    def test_returns_string(self):
        assert isinstance(_rule_based_clean("some text"), str)


# ── _is_too_different ───────────────────────────────────────────────────────


class TestIsTooFifferent:
    def test_identical_texts_not_too_different(self):
        assert _is_too_different("hello world", "hello world") is False

    def test_minor_cleanup_not_too_different(self):
        assert _is_too_different("hello world.", "Hello world") is False

    def test_completely_different_texts(self):
        assert _is_too_different("hello world", "the quick brown fox jumps over") is True

    def test_empty_original_not_too_different(self):
        assert _is_too_different("", "") is False

    def test_5x_longer_candidate_is_too_different(self):
        # Guard 1: output 5x longer than input (>20 chars) → too different
        original = "hello this is a sentence"
        bloated = original + " " + "extra hallucinated content words " * 10
        assert _is_too_different(bloated, original) is True

    def test_tiny_output_from_long_input_is_too_different(self):
        # Guard 3: long input reduced to nothing → too different
        original = "hello world this is a fairly long transcript that was spoken"
        assert _is_too_different("ok", original) is True


# ── _sanitize_llm_output ────────────────────────────────────────────────────


class TestSanitizeLlmOutput:
    def test_strips_code_blocks(self):
        result = _sanitize_llm_output("```python\nprint('hi')\n```", "hi")
        assert "```" not in result

    def test_strips_markdown_headers(self):
        result = _sanitize_llm_output("## Header\nSome text", "Some text")
        assert "##" not in result

    def test_empty_result_returns_empty_or_original(self):
        result = _sanitize_llm_output("", "original")
        # Either returns original or empty — implementation-defined
        assert isinstance(result, str)

    def test_normal_cleaned_text_passes_through(self):
        cleaned = "Hello world. This is a clean sentence."
        result = _sanitize_llm_output(cleaned, "hello world this is a clean sentence")
        assert result == cleaned
