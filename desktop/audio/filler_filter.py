import re

from utils.log import get_logger

logger = get_logger(__name__)

# Phrases before single words — longer match wins
_FILLERS_ORDERED = [
    "okay so",
    "so yeah",
    "you know",
    "i mean",
    "um",
    "uh",
    "like",
    "basically",
    "literally",
    "actually",
    "right",
]


def _build_pattern(filler: str) -> re.Pattern:
    parts = [re.escape(w) for w in filler.split()]
    return re.compile(r"\b" + r"\s+".join(parts) + r"\b", re.IGNORECASE)


_COMPILED: list[tuple[str, re.Pattern]] = [(fw, _build_pattern(fw)) for fw in _FILLERS_ORDERED]


def remove_fillers(text: str) -> str:
    """
    Remove filler words/phrases from transcribed speech.
    Cleans up leftover commas and whitespace after removal.
    """
    if not text:
        return text

    result = text
    for _, pattern in _COMPILED:
        # Replace filler with a null marker to avoid word-merging
        result = pattern.sub("\x00", result)

    # Absorb comma+space on either side of the marker
    result = re.sub(r",?\s*\x00\s*,?", " ", result)
    # Fix double commas: ", ," → ","
    result = re.sub(r",\s*,", ",", result)
    # Remove space before sentence-ending punctuation
    result = re.sub(r"\s+([,!?.;:])", r"\1", result)
    # Normalize whitespace
    result = re.sub(r" {2,}", " ", result)
    # Strip leading/trailing commas and spaces
    result = re.sub(r"^[\s,]+|[\s,]+$", "", result)
    return result.strip()


def count_fillers(text: str) -> dict[str, int]:
    """
    Count occurrences of each filler word/phrase.
    Returns only entries with count > 0.
    """
    if not text:
        return {}
    counts: dict[str, int] = {}
    for filler, pattern in _COMPILED:
        n = len(pattern.findall(text))
        if n:
            counts[filler] = n
    return counts


if __name__ == "__main__":
    cases = [
        # (input, expected_output)
        ("Um, I think so", "I think so"),
        ("It was, like, a good idea", "It was a good idea"),
        ("You know, that's basically right", "that's"),
        ("I mean, okay so let's go", "let's go"),
        ("So yeah, that's it", "that's it"),
        ("Actually literally the best", "the best"),
        ("Um uh you know I mean right", ""),
        ("Hello world", "Hello world"),  # no fillers
        ("", ""),  # empty
    ]

    print("=== remove_fillers tests ===")
    all_pass = True
    for text, expected in cases:
        result = remove_fillers(text)
        status = "[PASS]" if result == expected else "[FAIL]"
        if result != expected:
            all_pass = False
        print(f"{status}  in : {text!r}")
        if result != expected:
            print(f"       out: {result!r}")
            print(f"       exp: {expected!r}")

    print("\n=== count_fillers tests ===")
    sample = "Um, I like, you know, basically um the same thing"
    counts = count_fillers(sample)
    print(f"Input : {sample!r}")
    print(f"Counts: {counts}")
    assert counts.get("um") == 2, f"expected um=2, got {counts.get('um')}"
    assert counts.get("like") == 1
    assert counts.get("you know") == 1
    assert counts.get("basically") == 1
    print("[PASS] count_fillers assertions")

    if all_pass:
        print("\nAll remove_fillers tests passed.")
    else:
        print("\nSome tests FAILED.")
