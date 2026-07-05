"""
Per-user writing style profile.

Stored as a JSON file at data/profiles/default.json.
Loaded before every AI call and injected into the system prompt
as an extra block of formatting preferences.

The profile learns from user corrections over time:
- If the user keeps adding Oxford commas, we learn to use them
- If the user keeps capitalizing a term, we learn the correct capitalization
- If the user keeps making text more casual, we shift formality

Thread-safe (uses file locking via atomic write).
"""

from __future__ import annotations

import json
import os
import sys
import threading
from dataclasses import asdict, dataclass, field


def _default_profile_path() -> str:
    """Platform-specific data directory for the profile."""
    if sys.platform == "darwin":
        base = os.path.join(os.path.expanduser("~/Library/Application Support"), "RotaAI")
    elif sys.platform.startswith("linux"):
        xdg = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        base = os.path.join(xdg, "rota-ai")
    else:
        base = os.path.join(os.environ.get("APPDATA", "."), "RotaAI")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "style_profile.json")


@dataclass
class StyleProfile:
    """Persistent writing style preferences, learned from user corrections."""

    # ── Punctuation style ──
    oxford_comma: bool = True
    """Whether to use the Oxford comma (A, B, and C vs A, B and C)."""

    sentence_period: bool = True
    """Always end sentences with periods."""

    exclamation_frequency: float = 0.3
    """How often to use exclamation marks (0.0 = never, 1.0 = always)."""

    # ── Vocabulary ──
    formality_score: float = 0.5
    """Writing formality (0.0 = very casual, 1.0 = very formal)."""

    contraction_preference: float = 0.7
    """Preference for contractions (0.0 = avoid, 1.0 = always use)."""

    # ── Capitalization ──
    proper_nouns: dict[str, str] = field(default_factory=dict)
    """Known proper noun spellings: {'rota ai': 'Rota AI', 'gpt': 'GPT'}"""

    # ── Learning ──
    correction_pairs: list[dict] = field(default_factory=list)
    """Historical correction pairs for analysis: [{original, corrected, count}]"""

    # ── Internal ──
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _path: str = ""
    _dirty: bool = False

    def to_prompt_injection(self) -> str:
        """Convert style preferences to a system prompt block."""
        parts = []

        # Formality
        if self.formality_score > 0.7:
            parts.append("- Formality: Formal — use complete sentences, avoid contractions")
        elif self.formality_score < 0.3:
            parts.append("- Formality: Casual — conversational, use contractions naturally")
        else:
            parts.append("- Formality: Neutral — match the speaker's natural register")

        # Punctuation
        if self.oxford_comma:
            parts.append("- Use the Oxford comma (A, B, and C)")

        if self.exclamation_frequency < 0.2:
            parts.append("- Avoid exclamation marks — use periods instead")
        elif self.exclamation_frequency > 0.7:
            parts.append("- Use exclamation marks freely — match enthusiastic tone")

        # Proper nouns
        if self.proper_nouns:
            names = ", ".join(f"{k} → {v}" for k, v in sorted(self.proper_nouns.items()))
            parts.append(f"- Preserve these capitalizations: {names}")

        if not parts:
            return ""

        return "## USER'S WRITING STYLE\n" + "\n".join(parts)

    def learn_from_correction(self, original_word: str, corrected_word: str) -> bool:
        """
        Learn from a single word-level correction.

        Returns True if the profile was meaningfully updated.
        """
        with self._lock:
            updated = False

            # Track correction pair
            existing = None
            for pair in self.correction_pairs:
                if pair["original"] == original_word and pair["corrected"] == corrected_word:
                    existing = pair
                    break

            if existing:
                existing["count"] = existing.get("count", 1) + 1
            else:
                self.correction_pairs.append(
                    {
                        "original": original_word,
                        "corrected": corrected_word,
                        "count": 1,
                    }
                )
                updated = True
                self._dirty = True

            # Learn proper noun capitalization
            # If the correction changes capitalization (e.g., "rota" → "Rota"),
            # add it to the proper nouns dictionary
            if original_word.lower() == corrected_word.lower():
                # Only capitalization changed
                if original_word != corrected_word:
                    self.proper_nouns[original_word.lower()] = corrected_word
                    updated = True
                    self._dirty = True
            else:
                # Word itself changed — add corrected version to proper nouns
                # if it looks like a proper noun (capitalized, not in common dict)
                if corrected_word[0].isupper() and len(corrected_word) > 1:
                    self.proper_nouns[corrected_word.lower()] = corrected_word
                    updated = True
                    self._dirty = True

            # Adjust formality based on correction patterns
            if corrected_word in {
                "cannot",
                "will not",
                "do not",
                "is not",
                "are not",
                "was not",
                "were not",
                "has not",
                "have not",
            }:
                self.formality_score = min(1.0, self.formality_score + 0.05)
                updated = True
                self._dirty = True
            elif corrected_word in {
                "can't",
                "won't",
                "don't",
                "isn't",
                "aren't",
                "wasn't",
                "weren't",
                "hasn't",
                "haven't",
            }:
                self.formality_score = max(0.0, self.formality_score - 0.05)
                updated = True
                self._dirty = True

            return updated

    def learn_from_texts(self, original: str, corrected: str) -> int:
        """
        Diff two texts and learn from all word-level corrections.

        Returns the number of corrections learned.
        """
        import difflib

        orig_words = original.split()
        corr_words = corrected.split()

        if abs(len(orig_words) - len(corr_words)) > max(5, len(orig_words) * 0.5):
            return 0  # Too different — likely the user rewrote everything

        matcher = difflib.SequenceMatcher(None, orig_words, corr_words)
        corrections_found = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "replace" and (i2 - i1) == 1 and (j2 - j1) == 1:
                orig_w = orig_words[i1].strip(".,?!:;\"'")
                corr_w = corr_words[j1].strip(".,?!:;\"'")
                if orig_w != corr_w and len(corr_w) > 1:
                    if self.learn_from_correction(orig_w, corr_w):
                        corrections_found += 1

        return corrections_found

    # ── Persistence ──

    def save(self, path: str | None = None) -> None:
        """Save profile to disk. Thread-safe (atomic write).

        Skips disk I/O if the profile hasn't been modified since last
        save (checked via _dirty flag) — avoids unnecessary writes
        on every AI call when no corrections were learned.
        """
        with self._lock:
            if not self._dirty:
                return

            target = path or self._path
            if not target:
                target = _default_profile_path()
                self._path = target

            data = asdict(self)
            data.pop("_lock", None)
            data.pop("_path", None)
            data.pop("correction_pairs", None)

            try:
                tmp = target + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                os.replace(tmp, target)
                self._dirty = False  # Only reset after successful write
            except Exception:
                pass

    @classmethod
    def load(cls, path: str | None = None) -> StyleProfile:
        """Load profile from disk, or return defaults if not found."""
        target = path or _default_profile_path()
        try:
            with open(target, encoding="utf-8") as f:
                data = json.load(f)
            # Filter to only known fields
            known = {k for k in cls.__dataclass_fields__ if not k.startswith("_")}
            filtered = {k: v for k, v in data.items() if k in known}
            profile = cls(**filtered)
            profile._path = target
            return profile
        except (FileNotFoundError, json.JSONDecodeError, TypeError):
            profile = cls()
            profile._path = target
            return profile
