import re
from dataclasses import dataclass, field

FILLER_WORDS = (
    "um",
    "uh",
    "like",
    "basically",
    "actually",
    "you know",
    "i mean",
    "so",
)

HEDGING_WORDS = (
    "just",
    "kind of",
    "sort of",
    "maybe",
    "perhaps",
    "probably",
    "i think",
    "i guess",
    "i suppose",
    "like",
    "might",
    "could be",
    "not sure",
)

DEFAULT_PHRASES = (
    "thank you",
    "you're welcome",
    "good morning",
    "good afternoon",
    "how are you",
    "nice to meet you",
    "please help",
    "let me know",
    "i think",
    "in my opinion",
    "i believe",
    "for sure",
    "absolutely",
    "certainly",
    "definitely",
)


@dataclass
class TextMetrics:
    total_words: int
    filler_count: int
    filler_ratio: float
    clarity_score: int
    conciseness_score: int
    phrases: dict[str, int] = field(default_factory=dict)
    pause_efficiency: float = 100.0
    cadence_variety: float = 0.0
    gunning_fog: float = 0.0
    grade_level: str = "Standard Conversational"
    tone_ratios: dict[str, float] = field(default_factory=dict)
    hedging_count: int = 0
    hedging_rate: float = 0.0
    hesitation_rate: float = 0.0
    pacing_label: str = "Optimal"


def _word_tokens(text: str) -> list[str]:
    return re.findall(r"\b[\w']+\b", (text or "").lower())


def count_syllables(word: str) -> int:
    """Robust pure-Python syllable-counting helper to find complex words."""
    word = (word or "").lower().strip()
    if not word:
        return 0
    word = re.sub(r"[^a-z]", "", word)
    if not word:
        return 0

    vowels = "aeiouy"
    count = 0
    prev_is_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel

    if word.endswith("e"):
        if len(word) >= 3 and word[-2] == "l" and word[-3] not in vowels:
            pass
        else:
            count -= 1

    return max(1, count)


def _extract_phrases(text: str) -> dict[str, int]:
    text_lower = (text or "").lower()
    phrase_counts: dict[str, int] = {}
    for phrase in DEFAULT_PHRASES:
        count = len(re.findall(rf"\b{re.escape(phrase)}\b", text_lower))
        if count > 0:
            phrase_counts[phrase] = count
    return phrase_counts


def calculate_text_metrics(text: str) -> TextMetrics:
    words = _word_tokens(text)
    total_words = len(words)
    if total_words == 0:
        return TextMetrics(
            total_words=0,
            filler_count=0,
            filler_ratio=0.0,
            clarity_score=100,
            conciseness_score=100,
            phrases={},
            pause_efficiency=100.0,
            cadence_variety=0.0,
            gunning_fog=0.0,
            grade_level="Conversational",
            tone_ratios={"confident": 40.0, "thoughtful": 30.0, "warm": 20.0, "technical": 10.0},
        )

    # 1. Filler counting
    filler_count = 0
    lowered = (text or "").lower()
    for filler in FILLER_WORDS:
        if " " in filler:
            filler_count += len(re.findall(rf"\b{re.escape(filler)}\b", lowered))
        else:
            filler_count += sum(1 for token in words if token == filler)

    filler_ratio = filler_count / max(1, total_words)
    clarity_score = max(0, min(100, int(round(100 - (filler_ratio * 220)))))

    avg_word_len = sum(len(w) for w in words) / total_words
    length_penalty = max(0.0, (avg_word_len - 5.8) * 8.0)
    conciseness_score = max(0, min(100, int(round(100 - length_penalty - (filler_ratio * 70)))))

    phrases = _extract_phrases(text)

    # 2. Pause Efficiency (based on punctuation count proxy)
    punctuation_count = len(re.findall(r"[.,!?;:]", text or ""))
    pause_efficiency = (punctuation_count / max(1, punctuation_count + filler_count)) * 100.0

    # 3. Readability & Gunning Fog Index
    # Split text into sentences using standard punctuation splits
    sentences = [s.strip() for s in re.split(r"[.!?]+", text or "") if s.strip()]
    total_sentences = max(1, len(sentences))

    complex_words_count = sum(1 for w in words if count_syllables(w) >= 3)
    avg_sentence_len = total_words / total_sentences
    pct_complex_words = (complex_words_count / total_words) * 100.0
    gunning_fog = 0.4 * (avg_sentence_len + pct_complex_words)

    # Readability grade mapping
    if gunning_fog >= 16.0:
        grade_level = "Academic / Dense"
    elif gunning_fog >= 12.0:
        grade_level = "Executive / Advanced"
    elif gunning_fog >= 8.0:
        grade_level = "Clear Professional"
    elif gunning_fog >= 5.0:
        grade_level = "Standard Conversational"
    else:
        grade_level = "Simple / Direct"

    # 4. Speaking Cadence Variety
    # Standard deviation of words per sentence
    if len(sentences) > 1:
        lengths = [len(re.findall(r"\b[\w']+\b", s)) for s in sentences]
        mean_len = sum(lengths) / len(sentences)
        variance = sum((x - mean_len) ** 2 for x in lengths) / len(sentences)
        cadence_variety = variance**0.5
    else:
        cadence_variety = 0.0

    # 5. Speaking Tone Classification (keywords mapping)
    tone_keywords = {
        "confident": [
            "absolutely",
            "definitely",
            "certainly",
            "will",
            "must",
            "guarantee",
            "resolve",
            "decide",
            "execute",
            "vital",
            "critical",
            "proven",
            "clearly",
            "ensure",
        ],
        "thoughtful": [
            "think",
            "believe",
            "opinion",
            "perhaps",
            "consider",
            "suggest",
            "ponder",
            "reflect",
            "maybe",
            "hypothesize",
            "wonder",
            "evaluate",
            "speculate",
        ],
        "warm": [
            "team",
            "together",
            "help",
            "thank",
            "welcome",
            "please",
            "appreciate",
            "collaborate",
            "share",
            "glad",
            "kind",
            "great",
            "support",
            "us",
            "we",
            "our",
        ],
        "technical": [
            "basically",
            "actually",
            "essentially",
            "verify",
            "audit",
            "metrics",
            "database",
            "analytics",
            "refactor",
            "system",
            "structure",
            "data",
            "logical",
            "process",
            "code",
        ],
    }

    tone_counts = {"confident": 0, "thoughtful": 0, "warm": 0, "technical": 0}
    for word in words:
        for tone, keywords_list in tone_keywords.items():
            if word in keywords_list:
                tone_counts[tone] += 1

    total_tone_matches = sum(tone_counts.values())
    if total_tone_matches > 0:
        tone_ratios = {
            tone: round((count / total_tone_matches) * 100.0, 1)
            for tone, count in tone_counts.items()
        }
    else:
        # Balanced default conversational ratios
        tone_ratios = {"confident": 40.0, "thoughtful": 30.0, "warm": 20.0, "technical": 10.0}

    # 6. Hedging Words detection
    hedging_count = 0
    for hedge in HEDGING_WORDS:
        if " " in hedge:
            hedging_count += len(re.findall(rf"\b{re.escape(hedge)}\b", lowered))
        else:
            hedging_count += sum(1 for token in words if token == hedge)
    hedging_rate = (hedging_count / max(1, total_words)) * 100.0

    # 7. Speech Hesitation Rate (filler-to-pause ratio)
    hesitation_rate = (filler_count / max(1, punctuation_count + filler_count)) * 100.0

    # 8. Pacing Label based on WPM proxy (words per sentence as proxy)
    if avg_sentence_len > 25:
        pacing_label = "Fast"
    elif avg_sentence_len >= 12:
        pacing_label = "Optimal"
    else:
        pacing_label = "Slow"

    return TextMetrics(
        total_words=total_words,
        filler_count=filler_count,
        filler_ratio=filler_ratio,
        clarity_score=clarity_score,
        conciseness_score=conciseness_score,
        phrases=phrases,
        pause_efficiency=pause_efficiency,
        cadence_variety=cadence_variety,
        gunning_fog=gunning_fog,
        grade_level=grade_level,
        tone_ratios=tone_ratios,
        hedging_count=hedging_count,
        hedging_rate=round(hedging_rate, 1),
        hesitation_rate=round(hesitation_rate, 1),
        pacing_label=pacing_label,
    )
