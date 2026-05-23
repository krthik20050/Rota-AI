"""
DEPRECATED: Legacy cleanup module.

All cleanup logic has been consolidated into ai.ai_processor.AIProcessor.
This module is kept only for backward compatibility with tests.
The _has_trigger and clean_text functions are no longer used in the pipeline.
"""

import os
import warnings

from groq import Groq

warnings.warn(
    "ai.cleanup is deprecated. Use ai.ai_processor.AIProcessor instead.",
    DeprecationWarning,
    stacklevel=2,
)

_TRIGGER_WORDS = {"change", "replace", "actually", "scratch", "delete", "wait", "meant", "sorry"}

_SYSTEM_PROMPT = (
    "You process voice dictation. The text contains voice correction commands. "
    "Execute each command on the surrounding text: "
    "'change X to Y' / 'replace X with Y' — swap the phrase; "
    "'scratch that' / 'delete that' — remove the preceding sentence; "
    "'actually [content]' / 'no wait [content]' — replace preceding sentence with content; "
    "'I meant X' — replace last word/phrase with X. "
    "Remove the command phrases. Return only the corrected text, nothing else."
)

_MODEL = "llama-3.1-8b-instant"


def _has_trigger(text: str) -> bool:
    words = text.lower().split()
    return bool(_TRIGGER_WORDS.intersection(words))


def clean_text(raw: str) -> str:
    """Deprecated: Use AIProcessor.process_text() instead."""
    if not _has_trigger(raw):
        return raw

    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return raw

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": raw},
        ],
        temperature=0,
        max_tokens=512,
    )
    return response.choices[0].message.content.strip()
