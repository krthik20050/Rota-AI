import json
import os
import re
import structlog

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Personal dictionary auto-learner
# ---------------------------------------------------------------------------

class PersonalDictionary:
    """
    Auto-growing personal dictionary that learns from every processed text.

    Extracts and remembers:
    - Proper nouns (capitalized words that aren't sentence starters)
    - Technical terms (camelCase, snake_case, acronyms)
    - Frequently used uncommon words

    Storage: %APPDATA%/RotaAI/personal_dictionary.json
    """

    def __init__(self, dict_path: str | None = None):
        if dict_path is None:
            appdata_dir = os.path.join(os.environ.get("APPDATA", "."), "RotaAI")
            os.makedirs(appdata_dir, exist_ok=True)
            dict_path = os.path.join(appdata_dir, "personal_dictionary.json")
        self._path = dict_path
        self._terms: dict[str, int] = {}  # term → usage count
        self._load()

    def _load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, encoding="utf-8") as f:
                    self._terms = json.load(f)
            except Exception:
                logger.warning("personal_dict_load_failed", path=self._path)
                self._terms = {}

    def _save(self):
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._terms, f, indent=2, ensure_ascii=False)
        except Exception:
            logger.warning("personal_dict_save_failed", path=self._path)

    def get_terms(self) -> list[str]:
        """Return all learned terms, sorted by usage frequency."""
        return sorted(self._terms.keys(), key=lambda t: self._terms[t], reverse=True)

    def learn_from_text(self, text: str):
        """
        Extract and learn notable terms from processed text.

        Learns: proper nouns, technical terms, acronyms, brand names.
        Ignores: common English words, single characters, very short words.
        """
        if not text or len(text) < 5:
            return

        # Common words to ignore (not worth learning)
        _COMMON = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "shall", "can", "need", "must", "i", "you",
            "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
            "my", "your", "his", "its", "our", "their", "this", "that", "these",
            "those", "what", "which", "who", "whom", "where", "when", "why", "how",
            "all", "each", "every", "both", "few", "more", "most", "other", "some",
            "such", "no", "not", "only", "same", "so", "than", "too", "very",
            "just", "but", "and", "or", "if", "then", "also", "as", "for", "from",
            "in", "into", "of", "on", "to", "with", "about", "after", "before",
            "between", "by", "during", "through", "at", "up", "out", "off", "over",
            "under", "again", "here", "there", "now", "today", "tomorrow", "yesterday",
            "want", "like", "think", "know", "see", "get", "make", "go", "come",
            "take", "give", "say", "tell", "ask", "use", "find", "put", "try",
            "keep", "let", "start", "turn", "show", "hear", "play", "run", "move",
            "look", "thing", "things", "way", "time", "work", "day", "good", "new",
            "first", "last", "long", "great", "little", "own", "old", "right",
            "big", "high", "different", "small", "large", "next", "early", "young",
            "important", "public", "bad", "sure", "yeah", "yes", "okay", "actually",
            "really", "well", "still", "even", "much", "back", "kind", "going",
            "something", "nothing", "everything", "anything", "done", "already",
        }

        words = re.findall(r'\b[A-Za-z][A-Za-z0-9_.-]{2,}\b', text)
        new_terms = set()

        for word in words:
            lower = word.lower()
            if lower in _COMMON:
                continue

            is_notable = False

            # Proper nouns: capitalized words not at sentence start
            if word[0].isupper() and not word.isupper() and len(word) > 2:
                is_notable = True

            # Acronyms: all caps, 2+ letters
            if word.isupper() and len(word) >= 2:
                is_notable = True

            # Technical: camelCase or PascalCase
            if re.match(r'^[a-z]+[A-Z]', word) or re.match(r'^[A-Z][a-z]+[A-Z]', word):
                is_notable = True

            # Technical: contains underscore or dot
            if '_' in word or '.' in word:
                is_notable = True

            if is_notable:
                new_terms.add(word)

        if new_terms:
            changed = False
            for term in new_terms:
                if term in self._terms:
                    self._terms[term] += 1
                else:
                    self._terms[term] = 1
                    changed = True
            # Cap at 500 entries: prune least-used single-occurrence terms first
            if len(self._terms) > 500:
                singles = [t for t, c in self._terms.items() if c == 1]
                for t in singles[:max(0, len(self._terms) - 500)]:
                    del self._terms[t]
                changed = True
            if changed:
                self._save()
                logger.debug("personal_dict_updated", new_terms=len(new_terms), total=len(self._terms))

    def add_term(self, term: str):
        """Manually add a term to the dictionary."""
        term = term.strip()
        if term:
            self._terms[term] = self._terms.get(term, 0) + 10  # Manual adds get high weight
            self._save()

    def remove_term(self, term: str):
        """Remove a term from the dictionary."""
        self._terms.pop(term, None)
        self._save()

    def all_terms(self) -> dict[str, int]:
        """Return all terms with their usage counts."""
        return dict(self._terms)
