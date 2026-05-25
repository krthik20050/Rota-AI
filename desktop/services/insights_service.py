from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from utils.text_metrics import calculate_text_metrics


@dataclass
class SessionInsight:
    summary: str
    suggestion: str
    filler_ratio_percent: int
    clarity_score: int
    conciseness_score: int
    words: int


class InsightsService:
    """Derives short, actionable speaking insights from cleaned text."""

    def build_insight(self, text: str, metrics: Any = None) -> SessionInsight:
        """Build insight from text. Pass pre-computed metrics to avoid recalculation."""
        if metrics is None:
            metrics = calculate_text_metrics(text)
        filler_pct = int(round(metrics.filler_ratio * 100))

        if filler_pct >= 18:
            summary = f"You use {filler_pct}% filler words."
            suggestion = 'Pause instead of using fillers like "um" or "like".'
        elif filler_pct >= 10:
            summary = f"Filler words are moderate at {filler_pct}%."
            suggestion = "Try one extra beat of silence before complex phrases."
        else:
            summary = "Filler usage is low and speech is clean."
            suggestion = "Keep your current pace and pause pattern."

        return SessionInsight(
            summary=summary,
            suggestion=suggestion,
            filler_ratio_percent=filler_pct,
            clarity_score=metrics.clarity_score,
            conciseness_score=metrics.conciseness_score,
            words=metrics.total_words,
        )
