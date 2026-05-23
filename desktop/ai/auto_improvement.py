"""
Auto-Improvement System for Rota AI.

Tracks injected text vs. post-injection user edits, extracts word-level
corrections, and automatically updates the Personal Dictionary.
"""
import os
import json
import structlog
import time
import difflib
from pathlib import Path

logger = structlog.get_logger(__name__)

class AutoImprovementSystem:
    """
    Tracks and learns from user corrections post-injection.
    
    1. Stores the last injected texts.
    2. When the next recording starts, inspects the field text for edits.
    3. Uses diffing to find word-level corrections.
    4. Feeds corrections back into the Personal Dictionary & saves correction logs.
    """

    def __init__(self, log_path: str | None = None, personal_dict=None):
        if log_path is None:
            appdata_dir = os.path.join(os.environ.get("APPDATA", "."), "RotaAI")
            os.makedirs(appdata_dir, exist_ok=True)
            log_path = os.path.join(appdata_dir, "auto_improvement_log.json")
        self._path = log_path
        self.personal_dict = personal_dict
        self._recent_injections: list[dict] = []  # items: {"session_id": str, "text": str, "timestamp": float}
        self._corrections: list[dict] = []  # items: {"original": str, "corrected": str, "timestamp": float}
        self._load()

    def _load(self):
        """Loads historical corrections from file."""
        if os.path.exists(self._path):
            try:
                with open(self._path, encoding="utf-8") as f:
                    data = json.load(f)
                    self._corrections = data.get("corrections", [])
            except Exception:
                logger.warning("auto_improvement_load_failed", path=self._path)
                self._corrections = []

    def _save(self):
        """Saves historical corrections to file."""
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump({"corrections": self._corrections}, f, indent=2, ensure_ascii=False)
        except Exception:
            logger.warning("auto_improvement_save_failed", path=self._path)

    def track_injection(self, session_id: str, text: str):
        """Records an injected text for future diff tracking."""
        if not text or not text.strip():
            return
        
        # Keep only the last 10 injections to save memory
        self._recent_injections = [inj for inj in self._recent_injections if time.time() - inj["timestamp"] < 300][-9:]
        self._recent_injections.append({
            "session_id": session_id,
            "text": text.strip(),
            "timestamp": time.time()
        })
        logger.info("tracked_injection", session_id=session_id, length=len(text))

    def analyze_field_for_corrections(self, current_field_text: str) -> list[tuple[str, str]]:
        """
        Compares the current field text against the last injected text to detect edits.
        
        Returns:
            List of tuples of (original_word, corrected_word)
        """
        if not current_field_text or not current_field_text.strip():
            return []
        
        if not self._recent_injections:
            return []

        # Compare against the most recent injection
        last_inj = self._recent_injections[-1]
        original_text = last_inj["text"]

        # If they are exactly the same, no corrections made
        if original_text == current_field_text.strip():
            return []

        # Find word-level differences
        orig_words = original_text.split()
        curr_words = current_field_text.strip().split()

        # If length or structure is vastly different (e.g. user cleared the field), ignore it
        if abs(len(orig_words) - len(curr_words)) > max(5, len(orig_words) * 0.5):
            return []

        matcher = difflib.SequenceMatcher(None, orig_words, curr_words)
        corrections = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            # "replace" means a block of words in orig was replaced by a block of words in curr
            if tag == 'replace':
                orig_block = orig_words[i1:i2]
                curr_block = curr_words[j1:j2]
                
                # We specifically look for single-word corrections (names, terms) to keep it high precision
                if len(orig_block) == 1 and len(curr_block) == 1:
                    orig_w = orig_block[0].strip(".,?!:;\"'")
                    curr_w = curr_block[0].strip(".,?!:;\"'")
                    
                    if orig_w != curr_w and len(curr_w) > 1:
                        corrections.append((orig_w, curr_w))

        # Learn and log the corrections
        for orig, corrected in corrections:
            self._log_correction(orig, corrected)
            
        return corrections

    def _log_correction(self, original: str, corrected: str):
        """Logs a correction and automatically learns it."""
        # Avoid duplicate learning of the same correction
        if any(c["original"] == original and c["corrected"] == corrected for c in self._corrections):
            return

        self._corrections.append({
            "original": original,
            "corrected": corrected,
            "timestamp": time.time()
        })
        self._save()
        
        logger.info("auto_learned_correction", original=original, corrected=corrected)

        # Feed back to personal dictionary if provided
        if self.personal_dict is not None:
            # Add to personal dictionary UI / memory
            if hasattr(self.personal_dict, "add_term"):
                self.personal_dict.add_term(corrected)
            elif hasattr(self.personal_dict, "learn_from_text"):
                # fallback or direct learning method
                self.personal_dict.learn_from_text(corrected)

    def get_corrections(self) -> list[dict]:
        """Returns all recorded corrections, newest first."""
        return sorted(self._corrections, key=lambda c: c["timestamp"], reverse=True)
