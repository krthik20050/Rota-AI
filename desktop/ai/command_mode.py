import os
import re
from typing import Optional

from groq import Groq

_COMMAND_PATTERNS = [
    (r"\bmake\s+this\s+(?:an?\s+)?(\w+)\b", "transform"),
    (r"\bconvert\s+(this\s+)?to\s+(bullet\s+points?|list)\b", "bullets"),
    (r"\bformat\s+(this\s+)?as\s+(?:an?\s+)?(\w+)\b", "transform"),
    (r"\bturn\s+(this\s+)?into\s+(?:an?\s+)?(\w+)\b", "transform"),
    (r"\brewrite\s+(this\s+)?as\s+(?:an?\s+)?(\w+)\b", "transform"),
    (r"\bsummarize\s+(this|that)\b", "summarize"),
    (r"\bmake\s+(this|that)\s+(shorter|longer|concise|brief)\b", "shorten"),
]

_TARGET_PROMPTS = {
    "email": "Format this as a professional email with subject line and body.",
    "tweet": "Convert to a concise tweet under 280 characters.",
    "tweets": "Convert to a concise tweet under 280 characters.",
    "bullet": "Convert to a clear bullet point list.",
    "bullets": "Convert to a clear bullet point list.",
    "list": "Convert to a clear bullet point list.",
    "summary": "Create a brief summary of the key points.",
    "shorter": "Condense the text while preserving the key meaning.",
    "concise": "Make the text more concise and direct.",
    "brief": "Summarize into a brief version.",
    "professional": "Rewrite in a professional business tone.",
    "casual": "Rewrite in a casual friendly tone.",
    "code": "Format as clean code if applicable.",
    "message": "Format as a short message.",
    "notes": "Format as quick notes.",
    "paragraph": "Format as a clean paragraph.",
}


def detect_command(text: str) -> Optional[tuple[str, str]]:
    """
    Detect voice command in text.
    Returns (command_type, target) or None if no command detected.
    """
    text_lower = text.lower()
    
    for pattern, cmd_type in _COMMAND_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            if cmd_type == "transform":
                # Extract target from match group
                target = None
                for g in match.groups():
                    if g and g.strip():
                        target = g.strip()
                        break
                if target and target in _TARGET_PROMPTS:
                    return ("transform", target)
            elif cmd_type == "bullets":
                return ("transform", "bullets")
            elif cmd_type == "summarize":
                return ("transform", "summary")
            elif cmd_type == "shorten":
                return ("shorten", match.group(1) if match.lastindex else "shorter")
    
    return None


def strip_command(text: str) -> str:
    """Remove command phrase from text, leaving only the content to transform."""
    text_lower = text.lower()
    
    patterns_to_strip = [
        r"\bmake\s+this\s+(?:an?\s+)?\w+\b",
        r"\bconvert\s+(this\s+)?to\s+(?:bullet\s+points?|list)\b",
        r"\bformat\s+(this\s+)?as\s+(?:an?\s+)?\w+",
        r"\bturn\s+(this\s+)?into\s+(?:an?\s+)?\w+",
        r"\brewrite\s+(this\s+)?as\s+(?:an?\s+)?\w+",
        r"\bsummarize\s+(this|that)\b",
        r"\bmake\s+(this|that)\s+(?:shorter|longer|concise|brief)\b",
    ]
    
    result = text
    for pattern in patterns_to_strip:
        result = re.sub(pattern, "", result, flags=re.IGNORECASE).strip()
    
    # Clean up any leading punctuation
    result = result.lstrip("-*:. ")
    return result


def transform_text(text: str, command: str, target: str) -> str:
    """Apply transformation to text using LLM."""
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return text
    
    prompt = _TARGET_PROMPTS.get(target, f"Transform this text as requested: {target}")
    
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
        temperature=0.3,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()


_MAX_INPUT_LENGTH = 10000  # Prevent abuse


def process_with_command_mode(text: str) -> tuple[str, bool]:
    """
    Process text through command mode if command detected.
    Returns (processed_text, was_command_applied).
    """
    if not text or len(text) > _MAX_INPUT_LENGTH:
        return text, False

    command = detect_command(text)
    if not command:
        return text, False

    cmd_type, target = command
    content = strip_command(text)

    if not content.strip():
        return text, False

    try:
        transformed = transform_text(content, cmd_type, target)
        return transformed, True
    except Exception:
        return text, False