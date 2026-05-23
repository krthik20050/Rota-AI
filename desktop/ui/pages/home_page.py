"""
Rota AI — Home Page Widget
===========================
Two-column layout: history timeline (left) | stats panel (right).
Extracted from main_window.py to keep MainWindow under 500 lines.
"""
from __future__ import annotations

import random
import re
import time
from collections import Counter
from datetime import datetime, date as Date, timedelta, timezone

import pyperclip
import structlog
from PyQt6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from ui.components.history_item import HistoryItemWidget
from ui.styles.main_window_qss import (
    CLR_ACCENT, CLR_ERROR, CLR_WARNING,
    STATS_PANEL_W,
)

logger = structlog.get_logger(__name__)


class HomePage(QWidget):
    """Home page: history list + stats panel. Self-contained — no MainWindow coupling."""

    def __init__(self, history_manager, ai_processor, config, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.ai_processor = ai_processor
        self._config = config

        self._history_signature = None
        self._history_scroll_animation = None
        self._date_headers: list[tuple[str, QLabel]] = []

        # Stats animation — fires only on first data load
        self._stats_initialized = False
        self._stats_targets = [0, 0, 0]   # [wpm, words_today, lifetime]
        self._stats_anim_start = 0.0
        self._stats_anim_duration = 1.4
        self._stats_anim_timer = QTimer(self)
        self._stats_anim_timer.setInterval(14)
        self._stats_anim_timer.timeout.connect(self._stats_tick)

        # Section-label slot-machine rotation — fires once at startup
        self._label_anim_frame = 0
        self._label_anim_total = 20          # 20 × 55 ms ≈ 1.1 s
        self._label_anim_timer = QTimer(self)
        self._label_anim_timer.setInterval(55)
        self._label_anim_timer.timeout.connect(self._label_rotation_tick)

        self._build_ui()

    # ──────────────────────────────────────────────────────────
    # Layout
    # ──────────────────────────────────────────────────────────
    def _build_ui(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lay.addWidget(self._build_history_column(), 1)
        lay.addWidget(self._build_stats_panel())

    def _build_history_column(self) -> QWidget:
        col = QWidget()
        lay = QVBoxLayout(col)
        lay.setContentsMargins(24, 20, 14, 20)
        lay.setSpacing(0)

        # Header row
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 10)

        self._date_label = QLabel("TODAY")
        self._date_label.setObjectName("SectionLabel")
        header.addWidget(self._date_label)
        header.addStretch()

        daily_btn = QPushButton("ⓘ")
        daily_btn.setObjectName("IconBtn")
        daily_btn.setFixedSize(26, 26)
        daily_btn.setToolTip("Daily voice output summary")
        daily_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        daily_btn.clicked.connect(self._show_daily_summary)
        header.addWidget(daily_btn)

        refresh_btn = QPushButton("↻")
        refresh_btn.setObjectName("IconBtn")
        refresh_btn.setFixedSize(26, 26)
        refresh_btn.setToolTip("Refresh")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.refresh_history)
        header.addWidget(refresh_btn)
        lay.addLayout(header)

        # Scroll area
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.history_scroll.setObjectName("HistoryScroll")
        self.history_scroll.verticalScrollBar().setSingleStep(40)
        self.history_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setContentsMargins(0, 0, 6, 0)
        self.history_layout.setSpacing(2)
        self.history_scroll.setWidget(self.history_container)
        self.history_scroll.verticalScrollBar().valueChanged.connect(self._update_date_label)
        lay.addWidget(self.history_scroll, 1)

        return col

    def _build_stats_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("StatsPanel")
        panel.setMinimumWidth(160)
        panel.setMaximumWidth(STATS_PANEL_W)
        panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        lay = QVBoxLayout(panel)
        lay.setContentsMargins(20, 28, 20, 28)
        lay.setSpacing(16)

        def _section(text: str) -> QLabel:
            lbl = QLabel(text)
            lbl.setObjectName("PanelSection")
            return lbl

        def _divider() -> QFrame:
            d = QFrame()
            d.setFixedHeight(1)
            d.setStyleSheet("background: rgba(255, 255, 255, 0.05); border: none;")
            return d

        self._status_compact = QLabel("● Ready")
        self._status_compact.setObjectName("VoiceProfilePill")
        lay.addWidget(self._status_compact)

        lay.addWidget(_divider())
        self._lbl_sec_wpm = _section("WORDS / MIN")
        lay.addWidget(self._lbl_sec_wpm)
        self._lbl_wpm = QLabel("0")
        self._lbl_wpm.setObjectName("HomeStatBig")
        lay.addWidget(self._lbl_wpm)

        lay.addWidget(_divider())
        self._lbl_sec_words = _section("WORDS TODAY")
        lay.addWidget(self._lbl_sec_words)
        self._lbl_words = QLabel("0")
        self._lbl_words.setObjectName("HomeStatBig")
        lay.addWidget(self._lbl_words)

        lay.addWidget(_divider())
        self._lbl_sec_lifetime = _section("ALL TIME")
        lay.addWidget(self._lbl_sec_lifetime)
        self._lbl_lifetime = QLabel("0")
        self._lbl_lifetime.setObjectName("HomeStatBig")
        lay.addWidget(self._lbl_lifetime)

        lay.addStretch()
        return panel

    # ──────────────────────────────────────────────────────────
    # Public API — called by MainWindow
    # ──────────────────────────────────────────────────────────
    def update_status(self, text: str, color: str, compact_style: str = "") -> None:
        """Update the compact status pill in the stats panel."""
        if not compact_style:
            compact_style = (
                f"color: {color}; font-size: 11px; font-weight: 600;"
                f"background: rgba(134, 239, 172, 0.08);"
                f"border: 1px solid rgba(134, 239, 172, 0.18);"
                f"border-radius: 6px; padding: 4px 10px;"
            )
        self._status_compact.setText(text)
        self._status_compact.setStyleSheet(compact_style)

    def set_history_font(self, font) -> None:
        """Apply a font to the history item container."""
        self.history_container.setFont(font)

    def update_stats(self, wpm: int, words_today: int, lifetime_words: int) -> None:
        """Update the three home-page stat numbers with optional entry animation."""
        has_data = wpm > 0 or words_today > 0 or lifetime_words > 0
        if not self._stats_initialized:
            if has_data:
                self._stats_initialized = True
                self._stats_targets = [wpm, words_today, lifetime_words]
                # Keep labels at "0" and delay the animation so it starts after
                # the window is fully rendered and visible to the user.
                self._lbl_wpm.setText("0")
                self._lbl_words.setText("0")
                self._lbl_lifetime.setText("0")
                QTimer.singleShot(300, self._start_initial_anim)
            # No data yet — keep labels at "0" and wait for the next call
            return
        # Already initialized — update targets; don't interrupt a running animation
        self._stats_targets = [wpm, words_today, lifetime_words]
        if not self._stats_anim_timer.isActive():
            self._lbl_wpm.setText(str(wpm))
            self._lbl_words.setText(f"{words_today:,}")
            self._lbl_lifetime.setText(f"{lifetime_words:,}")

    def _start_initial_anim(self):
        """Start the count-up animation (called 300 ms after first real data)."""
        self._stats_anim_start = time.monotonic()
        self._stats_anim_timer.start()
        self._label_anim_frame = 0
        self._label_anim_timer.start()

    def refresh_history(self, highlight_latest: bool = False) -> None:
        history_days = int(self._config.get("history_days", 2)) if self._config else 2
        all_rows = self.history_manager.get_entries()[:200]

        if history_days > 0:
            cutoff = Date.today() - timedelta(days=history_days - 1)
            rows = [r for r in all_rows if (self._parse_date(str(r[1])) or Date.min) >= cutoff]
        else:
            rows = all_rows

        sig = tuple(r[0] for r in rows)
        if not highlight_latest and sig == self._history_signature:
            return
        self._history_signature = sig

        self._clear_history_layout()

        if not rows:
            self._show_empty_state()
            return

        self._date_headers = []
        current_date = None
        for idx, (entry_id, timestamp, raw, cleaned, is_prompt) in enumerate(rows):
            entry_date = self._parse_date(str(timestamp))
            date_key = entry_date or Date.min

            if date_key != current_date:
                current_date = date_key
                if self.history_layout.count() > 0:
                    self.history_layout.addSpacing(12)
                date_str = self._format_date(entry_date)
                marker = QLabel("")
                marker.setObjectName("DateGroupMarker")
                marker.setFixedHeight(0)
                self.history_layout.addWidget(marker)
                self._date_headers.append((date_str, marker))

            is_latest = highlight_latest and idx == 0
            item = HistoryItemWidget(
                entry_id, timestamp, raw, cleaned, is_prompt, is_latest=is_latest
            )
            item.copy_requested.connect(pyperclip.copy)
            item.copy_raw_requested.connect(pyperclip.copy)
            item.delete_requested.connect(self._on_delete)
            item.undo_requested.connect(self._on_undo)
            item.retry_requested.connect(self._on_retry)
            item.extract_audio_requested.connect(self._on_extract_audio)
            self.history_layout.addWidget(item)

        self.history_layout.addStretch()

        if self._date_headers:
            self._date_label.setText(self._date_headers[0][0])

        if highlight_latest:
            QTimer.singleShot(0, self._scroll_to_top)

    # ──────────────────────────────────────────────────────────
    # History helpers
    # ──────────────────────────────────────────────────────────
    def _clear_history_layout(self):
        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _show_empty_state(self):
        lbl = QLabel("No dictations yet")
        lbl.setObjectName("EmptyTitle")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.history_layout.addSpacing(60)
        self.history_layout.addWidget(lbl)
        self.history_layout.addStretch()

    def _scroll_to_top(self):
        bar = self.history_scroll.verticalScrollBar()
        if bar.value() == bar.minimum():
            return
        anim = QPropertyAnimation(bar, b"value")
        anim.setDuration(480)
        anim.setStartValue(bar.value())
        anim.setEndValue(bar.minimum())
        anim.setEasingCurve(QEasingCurve.Type.OutQuart)
        anim.start()
        self._history_scroll_animation = anim  # keep reference alive

    def _update_date_label(self):
        if not self._date_headers:
            return
        scroll_y = self.history_scroll.verticalScrollBar().value()
        current = self._date_headers[0][0]
        for date_str, widget in self._date_headers:
            if widget.y() <= scroll_y + 10:
                current = date_str
        self._date_label.setText(current)

    def _show_daily_summary(self):
        rows = self.history_manager.get_entries()[:200]
        today = Date.today()
        today_rows = [r for r in rows if (self._parse_date(str(r[1])) or Date.min) == today]

        total_words = 0
        all_words: list[str] = []
        for _, _, raw, cleaned, _ in today_rows:
            text = cleaned or raw or ""
            words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
            all_words.extend(words)
            total_words += len(text.split())

        top_words = Counter(all_words).most_common(5)
        lines = [f"Sessions today: {len(today_rows)}", f"Words today: {total_words:,}"]
        if top_words:
            lines.append("Most used words:")
            for word, cnt in top_words:
                lines.append(f"  {word} ({cnt}×)")

        popup = QWidget(self, Qt.WindowType.Popup)
        popup.setObjectName("DailySummaryPopup")
        popup.setStyleSheet("""
            QWidget#DailySummaryPopup {
                background: #1C2320;
                border: 1px solid rgba(134, 239, 172, 0.25);
                border-radius: 10px;
            }
            QLabel { color: #E8E8EA; font-size: 12px; background: transparent; }
            QLabel#PopupTitle { font-size: 13px; font-weight: 700; color: #86EFAC; }
        """)
        lay = QVBoxLayout(popup)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(6)
        title = QLabel("Daily Voice Output")
        title.setObjectName("PopupTitle")
        lay.addWidget(title)
        for line in lines:
            lay.addWidget(QLabel(line))
        popup.adjustSize()

        btn = self.sender()
        if btn:
            pos = btn.mapToGlobal(QPoint(0, btn.height() + 4))
            popup.move(pos)
        popup.show()
        popup.raise_()

    # ──────────────────────────────────────────────────────────
    # Entry actions
    # ──────────────────────────────────────────────────────────
    def _on_delete(self, entry_id: int):
        self.history_manager.delete_entry(entry_id)
        self._history_signature = None
        self.refresh_history()

    def _on_undo(self, entry_id: int):
        row = self.history_manager.get_entry(entry_id)
        if row is None:
            return
        _, _, raw_text, _, _ = row
        self.history_manager.update_entry(entry_id, raw_text)
        self._history_signature = None
        self.refresh_history()

    def _on_retry(self, entry_id: int):
        from PyQt6.QtWidgets import QMessageBox
        row = self.history_manager.get_entry(entry_id)
        if row is None:
            return
        _, _, raw_text, _, _ = row
        if self.ai_processor is None:
            QMessageBox.information(
                self, "Retry",
                "Smart formatting engine not available. Enable Smart Formatting in Settings."
            )
            return
        try:
            cleaned = self.ai_processor.process_text(raw_text)
            self.history_manager.update_entry(entry_id, cleaned)
            self._history_signature = None
            self.refresh_history()
        except Exception as exc:
            QMessageBox.warning(self, "Retry failed", f"Formatting failed:\n{exc}")

    def _on_extract_audio(self, entry_id: int):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self, "Extract Audio",
            "Audio is not stored for past recordings.\n\n"
            "Rota keeps text transcriptions only. Audio extraction is not available."
        )

    # ──────────────────────────────────────────────────────────
    # Date / time helpers
    # ──────────────────────────────────────────────────────────
    def _parse_date(self, timestamp: str) -> Date | None:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                dt_utc = datetime.strptime(timestamp.split(".")[0], fmt).replace(
                    tzinfo=timezone.utc
                )
                return dt_utc.astimezone().date()
            except ValueError:
                continue
        return None

    def _format_date(self, d: Date | None) -> str:
        if d is None:
            return "UNKNOWN DATE"
        mode = (self._config.get("date_display", "relative") if self._config else "relative")
        if mode == "relative":
            delta = (Date.today() - d).days
            if delta == 0:
                return "TODAY"
            if delta == 1:
                return "YESTERDAY"
            return d.strftime("%B %d, %Y").upper()
        return d.strftime("%Y-%m-%d")

    # ──────────────────────────────────────────────────────────
    # Stats animation
    # ──────────────────────────────────────────────────────────
    _SLOT_WORDS = [
        "VELOCITY", "OUTPUT", "SPEED", "RATE", "COUNT",
        "FLOW", "DATA", "PACE", "TOTAL", "WORDS",
        "VOLUME", "METRIC", "SCORE", "TRACK", "PULSE",
    ]

    def _label_rotation_tick(self):
        self._label_anim_frame += 1
        if self._label_anim_frame >= self._label_anim_total:
            self._label_anim_timer.stop()
            self._lbl_sec_wpm.setText("WORDS / MIN")
            self._lbl_sec_words.setText("WORDS TODAY")
            self._lbl_sec_lifetime.setText("ALL TIME")
            return
        for lbl in (self._lbl_sec_wpm, self._lbl_sec_words, self._lbl_sec_lifetime):
            lbl.setText(random.choice(self._SLOT_WORDS))

    def _stats_tick(self):
        elapsed = time.monotonic() - self._stats_anim_start
        t = min(1.0, elapsed / self._stats_anim_duration)
        ease = 1.0 - (1.0 - t) ** 3
        if t >= 1.0:
            self._stats_anim_timer.stop()
        wpm, words, lifetime = self._stats_targets
        self._lbl_wpm.setText(str(int(wpm * ease)))
        self._lbl_words.setText(f"{int(words * ease):,}")
        self._lbl_lifetime.setText(f"{int(lifetime * ease):,}")
