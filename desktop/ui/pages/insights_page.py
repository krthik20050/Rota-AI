from __future__ import annotations

import time

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.pages._insights_helpers import _FastInfoLabel, build_drill_slide
from ui.pages._insights_updater import update_advanced_coaching as _do_advanced_coaching
from ui.pages._insights_updater import update_from_dashboard as _do_update

CLR_ACCENT = "#86EFAC"
CLR_BORDER = "rgba(255, 255, 255, 0.05)"
CLR_CARD = "#191E1C"
CLR_TEXT_PRIMARY = "#F0F0F2"
CLR_TEXT_SECONDARY = "#A0A0A5"
CLR_TEXT_MUTED = "#5A5A60"


class InsightsPage(QWidget):
    def __init__(self, config, history_db, session_store=None, parent=None):
        super().__init__(parent)
        self.config = config
        self.history_db = history_db
        self.session_store = session_store

        self._insights_targets = [0, 0, 0, 0]
        self._insights_anim_start = 0.0
        self._insights_anim_duration = 1.6
        self._insights_anim_timer = QTimer(self)
        self._insights_anim_timer.setInterval(14)
        self._insights_anim_timer.timeout.connect(self._insights_tick)

        self._setup_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        page_lay = QVBoxLayout(self)
        page_lay.setContentsMargins(20, 18, 20, 18)
        page_lay.setSpacing(16)

        header = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(2)
        title = QLabel("Insights")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Unlock the secrets of your voice performance")
        subtitle.setObjectName("Subtitle")
        header_text.addWidget(title)
        header_text.addWidget(subtitle)
        header.addLayout(header_text, 1)

        self.segmented_control = QFrame()
        self.segmented_control.setObjectName("SegmentedControl")
        seg_lay = QHBoxLayout(self.segmented_control)
        seg_lay.setContentsMargins(4, 4, 4, 4)
        seg_lay.setSpacing(4)

        self.btn_usage = QPushButton("Usage & Productivity")
        self.btn_usage.setObjectName("TabToggleBtn")
        self.btn_usage.setCheckable(True)
        self.btn_usage.setChecked(True)
        self.btn_usage.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_speech = QPushButton("Speech & Style")
        self.btn_speech.setObjectName("TabToggleBtn")
        self.btn_speech.setCheckable(True)
        self.btn_speech.setCursor(Qt.CursorShape.PointingHandCursor)

        seg_lay.addWidget(self.btn_usage)
        seg_lay.addWidget(self.btn_speech)
        header.addWidget(self.segmented_control, 0, Qt.AlignmentFlag.AlignVCenter)

        self.btn_usage.clicked.connect(self._show_usage_tab)
        self.btn_speech.clicked.connect(self._show_speech_tab)
        page_lay.addLayout(header)

        self.insights_stack = QStackedWidget()
        self.insights_stack.setStyleSheet("background: transparent;")
        self.insights_stack.addWidget(self._build_usage_tab())
        self.insights_stack.addWidget(self._build_speech_tab())
        page_lay.addWidget(self.insights_stack, 1)
        self._update_tab_btn_styles()

    def _section_title_row(self, text: str, tooltip: str = "") -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(5)
        lbl = QLabel(text)
        lbl.setObjectName("SectionTitle")
        row.addWidget(lbl)
        if tooltip:
            info = _FastInfoLabel(tooltip)
            info.setFixedSize(16, 16)
            row.addWidget(info)
        row.addStretch()
        return row

    def _stat_card(self, title: str, value: str, tooltip: str = ""):
        card = QFrame()
        card.setObjectName("StatCard")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(6)
        title_row = QHBoxLayout()
        title_row.setSpacing(5)
        t = QLabel(title)
        t.setObjectName("StatTitle")
        title_row.addWidget(t)
        if tooltip:
            info = _FastInfoLabel(tooltip)
            info.setFixedSize(16, 16)
            title_row.addWidget(info)
        title_row.addStretch()
        v = QLabel(value)
        v.setObjectName("StatValue")
        lay.addLayout(title_row)
        lay.addWidget(v)
        card.value_label = v
        return card

    def _build_usage_tab(self):
        from ui.pages._insights_usage_tab import build_usage_tab

        return build_usage_tab(self)

    def _build_speech_tab(self):
        from ui.pages._insights_speech_tab import build_speech_tab

        return build_speech_tab(self)

    def _build_drill_slide(self, icon, title, subtitle, drill, metric_name, metric_value, target):
        return build_drill_slide(
            self, icon, title, subtitle, drill, metric_name, metric_value, target
        )

    # ------------------------------------------------------------------
    # Carousel navigation
    # ------------------------------------------------------------------

    def _carousel_prev(self):
        if not hasattr(self, "drill_carousel"):
            return
        idx = self.drill_carousel.currentIndex()
        new_idx = (idx - 1) % self.drill_carousel.count()
        self.drill_carousel.setCurrentIndex(new_idx)
        if hasattr(self, "carousel_page_lbl"):
            self.carousel_page_lbl.setText(f"{new_idx + 1} / {self.drill_carousel.count()}")

    def _carousel_next(self):
        if not hasattr(self, "drill_carousel"):
            return
        idx = self.drill_carousel.currentIndex()
        new_idx = (idx + 1) % self.drill_carousel.count()
        self.drill_carousel.setCurrentIndex(new_idx)
        if hasattr(self, "carousel_page_lbl"):
            self.carousel_page_lbl.setText(f"{new_idx + 1} / {self.drill_carousel.count()}")

    # ------------------------------------------------------------------
    # Tab switching
    # ------------------------------------------------------------------

    def _show_usage_tab(self):
        self.btn_usage.setChecked(True)
        self.btn_speech.setChecked(False)
        self.insights_stack.setCurrentIndex(0)
        self._update_tab_btn_styles()

    def _show_speech_tab(self):
        self.btn_usage.setChecked(False)
        self.btn_speech.setChecked(True)
        self.insights_stack.setCurrentIndex(1)
        self._update_tab_btn_styles()

    def _update_tab_btn_styles(self):
        self.btn_usage.style().polish(self.btn_usage)
        self.btn_speech.style().polish(self.btn_speech)

    # ------------------------------------------------------------------
    # Animation
    # ------------------------------------------------------------------

    def animate_entry(self):
        self._insights_anim_timer.stop()
        if hasattr(self, "total_words_card"):
            self.total_words_card.value_label.setText("0")
        if hasattr(self, "wpm_card"):
            self.wpm_card.value_label.setText("0")
        if hasattr(self, "session_card"):
            self.session_card.value_label.setText("0")
        if hasattr(self, "streak_card"):
            self.streak_card.value_label.setText("0 days")
        words = getattr(self, "_last_today_words", 0)
        if hasattr(self, "_insights_speedometer"):
            self._insights_speedometer.set_value_animated(words, duration=1400)
        if hasattr(self, "trend_chart"):
            labels = getattr(self, "_trend_labels", [])
            wpm = getattr(self, "_trend_wpm", [])
            clarity = getattr(self, "_trend_clarity", [])
            self.trend_chart.setTrendDataAnimated(labels, wpm, clarity)
        self._insights_anim_start = time.monotonic()
        self._insights_anim_timer.start()

    def _insights_tick(self):
        elapsed = time.monotonic() - self._insights_anim_start
        t = min(1.0, elapsed / self._insights_anim_duration)
        ease = 1.0 - (1.0 - t) ** 3
        if t >= 1.0:
            self._insights_anim_timer.stop()
        words, wpm, lifetime, streak = self._insights_targets
        if hasattr(self, "total_words_card"):
            self.total_words_card.value_label.setText(f"{int(words * ease):,}")
        if hasattr(self, "wpm_card"):
            self.wpm_card.value_label.setText(str(int(wpm * ease)))
        if hasattr(self, "session_card"):
            self.session_card.value_label.setText(f"{int(lifetime * ease):,}")
        if hasattr(self, "streak_card"):
            sv = int(streak * ease)
            self.streak_card.value_label.setText(f"{sv} {'day' if sv == 1 else 'days'}")

    def tick(self):
        self._insights_tick()

    # ------------------------------------------------------------------
    # Public API — called by MainWindow
    # ------------------------------------------------------------------

    def update_from_dashboard(self, words_or_dashboard, wpm=None):
        """Update all InsightsPage widgets from a dashboard dict or raw values."""
        _do_update(self, words_or_dashboard, wpm)

    def _update_advanced_coaching(self, adv: dict):
        """Update advanced speech coaching widgets from the coaching dict."""
        _do_advanced_coaching(self, adv)

    def update_insight(self, summary: str, suggestion: str, clarity: float, conciseness: float):
        """Update the latest session insight text."""
        if hasattr(self, "_insight_text") and summary:
            self._insight_text.setText(summary)
        if hasattr(self, "_suggestion_text") and suggestion:
            self._suggestion_text.setText(f"💡 {suggestion}")
            self._suggestion_text.setVisible(True)
