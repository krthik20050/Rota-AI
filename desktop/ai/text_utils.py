import re

import structlog

from ai.prompts import _BASE_SYSTEM_PROMPT, _CONTEXT_RULES, _MODE_PROMPTS, _SECURITY_BLOCK

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Spoken punctuation pre-processor (applied BEFORE LLM call)
# ---------------------------------------------------------------------------

_SPOKEN_PUNCTUATION = [
    (re.compile(r"\b(?:full stop|period)\b", re.I), "."),
    (re.compile(r"\bcomma\b", re.I), ","),
    (re.compile(r"\b(?:question mark)\b", re.I), "?"),
    (re.compile(r"\b(?:exclamation mark|exclamation point)\b", re.I), "!"),
    (re.compile(r"\b(?:new paragraph|next paragraph)\b", re.I), "\n\n"),
    (re.compile(r"\b(?:new line|next line)\b", re.I), "\n"),
    (re.compile(r"\b(?:open parenthesis|left parenthesis|open paren)\b", re.I), "("),
    (re.compile(r"\b(?:close parenthesis|right parenthesis|close paren)\b", re.I), ")"),
    (re.compile(r"\bcolon\b", re.I), ":"),
    (re.compile(r"\bsemicolon\b", re.I), ";"),
    (re.compile(r"\b(?:hyphen|dash)\b", re.I), "-"),
    (re.compile(r"\b(?:open quote|open quotes)\b", re.I), '"'),
    (re.compile(r"\b(?:close quote|close quotes|end quote)\b", re.I), '"'),
]

# Filler words for rule-based fallback
_FILLERS = re.compile(
    r"\b(um+|uh+|hmm+|ah+)\b,?\s*",
    re.IGNORECASE,
)
_MULTI_SPACE = re.compile(r" {2,}")

# ---------------------------------------------------------------------------
# Output sanitizer — catches LLM misbehavior (code blocks, markdown, etc.)
# ---------------------------------------------------------------------------

# Patterns that indicate the LLM generated code or markdown instead of cleaning text
_CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```", re.MULTILINE)
_MARKDOWN_HEADER = re.compile(r"^#{1,6}\s", re.MULTILINE)
_MARKDOWN_BOLD = re.compile(r"\*\*(.+?)\*\*")
_MARKDOWN_ITALIC = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
_NUMBERED_LIST = re.compile(r"^\d+\.\s+\*?\*?", re.MULTILINE)
_BULLET_LIST = re.compile(r"^[\-\*]\s+", re.MULTILINE)
_PREAMBLE_PATTERNS = [
    re.compile(
        r"^Here(?:'s| is)\s+(?:the\s+)?(?:cleaned\s+|polished\s+|updated\s+|formatted\s+)?(?:and\s+)?(?:formatted\s+|polished\s+)?(?:text|version|output)\s*[:.]?\s*",
        re.IGNORECASE,
    ),
    re.compile(r"^(?:Sure|Of course|Certainly)[!,.]?\s*", re.IGNORECASE),
    re.compile(
        r"^I(?:'ve| have)\s+(?:cleaned|processed|updated|polished)\s+(?:the\s+)?(?:text|version|output)?\s*[:.]?\s*",
        re.IGNORECASE,
    ),
    re.compile(
        r"^The\s+(?:cleaned|polished|updated|formatted)\s+(?:text|version|output)\s*[:.]\s*",
        re.IGNORECASE,
    ),
]


def _preprocess_spoken_punctuation(text: str) -> str:
    """Convert explicitly spoken punctuation words into actual characters."""
    for pattern, replacement in _SPOKEN_PUNCTUATION:
        text = pattern.sub(replacement, text)
    # Clean up spacing around injected punctuation
    text = re.sub(r"\s+([.,?!;:)\"])", r"\1", text)
    text = re.sub(r'([\(\""])\s+', r"\1", text)
    return text.strip()


def _sanitize_llm_output(result: str, original: str) -> str:
    """
    Post-process LLM output to strip code blocks, markdown, and preambles.

    Safety net for when the AI ignores anti-hallucination rules and generates
    code, markdown formatting, or treats the input as an instruction.

    If the output is wildly different from the input (e.g., the AI generated
    a full code file), falls back to rule-based cleaning of the original.
    """
    if not result:
        return result

    # Strip triple-quotes, trailing notes, and LLM preambles iteratively/recursively
    while True:
        prev_result = result
        result = result.strip()

        # Strip triple-quotes if the model returned them
        if result.startswith('"""') and result.endswith('"""'):
            result = result[3:-3].strip()
        elif result.startswith("'''") and result.endswith("'''"):
            result = result[3:-3].strip()

        # Strip any trailing notes or explanations
        result = re.sub(r"(?i)\n*Note:\s*.*$", "", result, flags=re.DOTALL).strip()
        result = re.sub(r"(?i)\n*Explanation:\s*.*$", "", result, flags=re.DOTALL).strip()

        # Strip LLM preambles ("Here's the cleaned text:", "Sure!", etc.)
        for pattern in _PREAMBLE_PATTERNS:
            result = pattern.sub("", result, count=1).strip()

        if result == prev_result:
            break

    # Check if output contains code blocks — if so, the AI generated code
    if _CODE_BLOCK_PATTERN.search(result):
        logger.warning("sanitizer_stripped_code_blocks")
        # If the MAJORITY of the output is inside code blocks, reject entirely
        without_code = _CODE_BLOCK_PATTERN.sub("", result).strip()
        if len(without_code) < len(original) * 0.3:
            # Almost all output was code — LLM hallucinated, use rule-based
            return _rule_based_clean(original)
        result = without_code

    # Strip markdown headers (## Title, # Header, etc.)
    if _MARKDOWN_HEADER.search(result):
        result = _MARKDOWN_HEADER.sub("", result)

    # Strip bold markdown (**text** → text)
    result = _MARKDOWN_BOLD.sub(r"\1", result)

    # NOTE: Do NOT strip numbered list (1. 2. 3.) or bullet (• ) markers here.
    # The smart-structure rules in _BASE_SYSTEM_PROMPT explicitly produce these
    # formats when the content warrants them. Stripping them would destroy valid output.
    # The _NUMBERED_LIST / _BULLET_LIST patterns are kept as utilities for other callers
    # but must NOT be applied to clean LLM output.

    # Sanity check: if the cleaned output is 3x longer than input, the AI
    # likely generated new content. Fall back to rule-based clean.
    if len(result) > len(original) * 3 and len(original) > 20:
        logger.warning("sanitizer_output_too_long", input_len=len(original), output_len=len(result))
        return _rule_based_clean(original)

    return result.strip()


def _is_too_different(candidate: str, original: str) -> bool:
    """
    Detect true AI hallucinations — only reject if the output is clearly wrong.

    WHAT we catch:
      - Empty or near-empty output (AI returned nothing)
      - Output 5x longer than input (AI generated new content)
      - Zero word overlap AND output is tiny (AI swapped topic entirely)
      - Huge input reduced to very few words (AI summarized/deleted content)
    WHAT we ALLOW:
      - Normal rephrasing, restructuring, punctuation additions
      - Adding articles/prepositions the speaker skipped
      - Changing sentence order for flow
      - Splitting/merging sentences
    WHY: LLMs legitimately rewrite speech significantly. The old strict
    thresholds (15% coverage, 85% new-word ratio) were rejecting good AI
    cleanup from the 8b fallback model, forcing rule-based fallback.
    """
    if not candidate or not original:
        return False

    candidate_words = set(re.findall(r"[A-Za-z0-9]+", candidate.lower()))
    original_words = set(re.findall(r"[A-Za-z0-9]+", original.lower()))
    overlap_count = len(candidate_words & original_words)

    # Count total words (not unique) for length-based guards
    original_word_count = len(re.findall(r"[A-Za-z0-9]+", original))
    candidate_word_count = len(re.findall(r"[A-Za-z0-9]+", candidate))

    # Guard 1: Output is drastically longer (5x) — AI likely hallucinated new content
    if len(candidate) > len(original) * 5 and len(original) > 20:
        return True

    # Guard 2: Zero word overlap AND very short output — completely different topic
    if overlap_count == 0 and candidate_word_count <= 3 and original_word_count > 5:
        return True

    # Guard 3: Tiny output when long input — AI summarized/deleted user's content
    if original_word_count >= 10 and candidate_word_count < 3:
        return True

    return False


def _rule_based_clean(text: str) -> str:
    """Fallback cleanup using regex — no API calls needed."""
    text = text.strip()
    if not text:
        return text

    # Apply spoken punctuation conversion
    text = _preprocess_spoken_punctuation(text)

    text = _FILLERS.sub("", text)
    text = _MULTI_SPACE.sub(" ", text).strip()

    if not text:
        return text

    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s[:1].upper() + s[1:] if s else s for s in sentences]
    text = " ".join(sentences)
    text = text[:1].upper() + text[1:]

    if len(text.split()) > 3 and text[-1] not in ".!?":
        text += "."

    return text


# Window title substrings → override category for browser/web apps
_TITLE_CONTEXT_OVERRIDES: list[tuple[str, str]] = [
    ("gmail", "email"),
    ("outlook", "email"),
    ("mail", "email"),
    ("inbox", "email"),
    ("superhuman", "email"),
    ("hey.com", "email"),
    ("slack", "chat"),
    ("discord", "chat"),
    ("whatsapp", "chat"),
    ("telegram", "chat"),
    ("messenger", "chat"),
    ("teams", "chat"),
    ("github", "editor"),
    ("gitlab", "editor"),
    ("linear", "editor"),
    ("jira", "editor"),
    ("notion", "document"),
    ("obsidian", "document"),
    ("docs.google", "document"),
    ("google docs", "document"),
    ("word", "document"),
]

# Map categories that don't have explicit _CONTEXT_RULES keys
_CATEGORY_CONTEXT_MAP: dict[str, str] = {
    "office": "document",
    "notes": "document",
    "media": "other",
}


def _build_dynamic_prompt(
    writing_mode: str,
    app_context=None,
    field_text: str = "",
    personal_terms: list[str] | None = None,
) -> str:
    """
    Build a context-aware system prompt dynamically for each dictation.

    This is the key differentiator vs generic prompts — WisprFlow's secret sauce
    is that the LLM knows WHERE the user is typing and adapts formatting accordingly.
    """
    # For non-clean modes, use the dedicated mode prompt (already self-contained)
    mode_prompt = _MODE_PROMPTS.get(writing_mode)
    if mode_prompt is not None:
        return mode_prompt

    # Build the full dynamic prompt for "clean" mode
    parts = [_BASE_SYSTEM_PROMPT]

    # Inject app context rules
    if app_context is not None:
        category = getattr(app_context, "category", "other") or "other"
        app_name = getattr(app_context, "app_name", "") or ""
        tone = getattr(app_context, "tone", "neutral") or "neutral"

        # Override category based on window title for browser/Electron apps
        title_lower = app_name.lower()
        for title_hint, override_category in _TITLE_CONTEXT_OVERRIDES:
            if title_hint in title_lower:
                category = override_category
                break

        # Map categories without explicit _CONTEXT_RULES entries
        category = _CATEGORY_CONTEXT_MAP.get(category, category)

        context_rules = _CONTEXT_RULES.get(category, _CONTEXT_RULES["other"])
        parts.append(context_rules)

        if app_name:
            parts.append(f"\nThe user is currently typing in: **{app_name}**")
        if tone and tone != "neutral":
            parts.append(f"Expected tone: **{tone}**")

    # Inject field context (surrounding text for continuity)
    if field_text and field_text.strip():
        truncated = field_text.strip()[:500]  # Limit context size
        parts.append(
            f"\n## EXISTING TEXT IN FIELD\n"
            f"The user has already typed the following text before this dictation. "
            f"Continue naturally from where they left off — match their style, "
            f"maintain sentence continuity, and do NOT repeat what's already written:\n"
            f'"""\n{truncated}\n"""'
        )

    # Inject personal dictionary terms
    if personal_terms:
        terms_str = ", ".join(personal_terms[:100])  # Cap at 100 terms
        parts.append(
            f"\n## PERSONAL VOCABULARY\n"
            f"The user frequently uses these specific terms. Preserve their exact "
            f"spelling and capitalization when they appear in the transcript:\n{terms_str}"
        )

    # Always append the security block — no mode should miss it
    parts.append(_SECURITY_BLOCK)

    return "\n\n".join(parts)
