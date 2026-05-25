from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.components.circular_progress import CircularProgress
from ui.components.heatmap_grid import HeatmapGrid
from ui.components.speedometer import SpeedometerWidget
from ui.components.trend_chart import SpeechTrendChart


def build_usage_tab(page) -> QScrollArea:
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    container = QWidget()
    container.setObjectName("TabContainer")
    lay = QVBoxLayout(container)
    lay.setContentsMargins(0, 0, 0, 10)
    lay.setSpacing(16)

    stats = QHBoxLayout()
    stats.setSpacing(12)
    page.total_words_card = page._stat_card(
        "Words Today",
        "0",
        "Sum of all words dictated today (resets at local midnight).\n"
        "Counts tokens in the cleaned and formatted output text.",
    )
    page.wpm_card = page._stat_card(
        "avg pace (wpm)",
        "0",
        "Words Per Minute = total words \u00f7 total active mic time today.\n"
        "Only counts time the microphone was actively capturing speech.",
    )
    page.session_card = page._stat_card(
        "Lifetime Words",
        "0",
        "Cumulative word count across all dictation sessions since first use.",
    )
    page.streak_card = page._stat_card(
        "Daily Streak",
        "0 days",
        "Consecutive days with at least one completed dictation.\n"
        "Resets if you skip a full calendar day.",
    )
    stats.addWidget(page.total_words_card)
    stats.addWidget(page.wpm_card)
    stats.addWidget(page.session_card)
    stats.addWidget(page.streak_card)
    lay.addLayout(stats)

    speedo_card = QFrame()
    speedo_card.setObjectName("InsightCard")
    speedo_lay = QHBoxLayout(speedo_card)
    speedo_lay.setContentsMargins(24, 20, 24, 20)
    speedo_lay.setSpacing(32)
    speedo_text = QVBoxLayout()
    speedo_text.setSpacing(6)
    speedo_title = QLabel("Daily Voice Output")
    speedo_title.setObjectName("SectionTitle")
    speedo_sub = QLabel("Words dictated today vs. your 3,000-word daily target")
    speedo_sub.setObjectName("Subtitle")
    speedo_sub.setWordWrap(True)
    speedo_text.addWidget(speedo_title)
    speedo_text.addWidget(speedo_sub)
    speedo_text.addStretch()
    speedo_lay.addLayout(speedo_text, 1)
    page._insights_speedometer = SpeedometerWidget(max_value=3000)
    page._insights_speedometer.setFixedSize(260, 156)
    speedo_lay.addWidget(page._insights_speedometer, 0, Qt.AlignmentFlag.AlignVCenter)
    lay.addWidget(speedo_card)

    mid_row = QHBoxLayout()
    mid_row.setSpacing(16)

    page.app_breakdown_card = QFrame()
    page.app_breakdown_card.setObjectName("InsightCard")
    ab_lay = QVBoxLayout(page.app_breakdown_card)
    ab_lay.setContentsMargins(20, 18, 20, 18)
    ab_lay.setSpacing(10)
    ab_lay.addWidget(_lbl("Workflow Integrations", "SectionTitle"))
    ab_lay.addWidget(_lbl("Dictation activity by application", "Subtitle"))
    page.app_breakdown_layout = QVBoxLayout()
    page.app_breakdown_layout.setSpacing(8)
    page.app_empty_lbl = QLabel("No application usage tracked yet.")
    page.app_empty_lbl.setObjectName("InsightText")
    page.app_breakdown_layout.addWidget(page.app_empty_lbl)
    ab_lay.addLayout(page.app_breakdown_layout)
    ab_lay.addStretch()
    mid_row.addWidget(page.app_breakdown_card, 1)

    trends_card = QFrame()
    trends_card.setObjectName("InsightCard")
    tr_lay = QVBoxLayout(trends_card)
    tr_lay.setContentsMargins(20, 18, 20, 18)
    tr_lay.setSpacing(12)
    tr_hdr = QHBoxLayout()
    tr_txt = QVBoxLayout()
    tr_txt.setSpacing(2)
    tr_txt.addWidget(_lbl("Speech Trends", "SectionTitle"))
    tr_txt.addWidget(_lbl("Average speed and clarity over time", "Subtitle"))
    tr_hdr.addLayout(tr_txt)
    tr_hdr.addStretch()
    page.trend_chart = SpeechTrendChart()
    tr_lay.addLayout(tr_hdr)
    tr_lay.addWidget(page.trend_chart, 1)
    mid_row.addWidget(trends_card, 1)
    lay.addLayout(mid_row)

    heatmap_card = QFrame()
    heatmap_card.setObjectName("InsightCard")
    hm_lay = QVBoxLayout(heatmap_card)
    hm_lay.setContentsMargins(20, 18, 20, 18)
    hm_lay.setSpacing(10)
    hm_hdr = QHBoxLayout()
    hm_txt = QVBoxLayout()
    hm_txt.setSpacing(2)
    hm_txt.addWidget(_lbl("Activity Heatmap", "SectionTitle"))
    hm_txt.addWidget(_lbl("18-week voice contribution history", "Subtitle"))
    hm_hdr.addLayout(hm_txt)
    hm_hdr.addStretch()
    page.heatmap_grid = HeatmapGrid()
    hm_lay.addLayout(hm_hdr)
    hm_lay.addWidget(page.heatmap_grid)
    lay.addWidget(heatmap_card)

    page.daily_challenge_desc = QLabel()
    page.daily_challenge_progress = QLabel()
    page.daily_challenge_ring = CircularProgress("", 0.0)

    insight_card = QFrame()
    insight_card.setObjectName("InsightCard")
    ic_lay = QVBoxLayout(insight_card)
    ic_lay.setContentsMargins(20, 18, 20, 18)
    ic_lay.setSpacing(8)
    ic_lay.addWidget(_lbl("Latest Dictation Feedback", "SectionTitle"))
    page._insight_text = QLabel("Start a dictation to see insights here.")
    page._insight_text.setObjectName("InsightText")
    page._insight_text.setWordWrap(True)
    page._suggestion_text = QLabel("")
    page._suggestion_text.setObjectName("SuggestionText")
    page._suggestion_text.setWordWrap(True)
    page._suggestion_text.setVisible(False)
    ic_lay.addWidget(page._insight_text)
    ic_lay.addWidget(page._suggestion_text)
    lay.addWidget(insight_card)

    scroll.setWidget(container)
    return scroll


def _lbl(text, obj_name):
    lbl = QLabel(text)
    lbl.setObjectName(obj_name)
    return lbl
