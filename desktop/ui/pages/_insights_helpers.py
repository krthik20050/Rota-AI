from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout


class _FastInfoLabel(QLabel):
    def __init__(self, tooltip_text: str, parent=None):
        super().__init__("ⓘ", parent)
        self._tooltip_text = tooltip_text
        self._popup = None
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._show_popup)
        self.setObjectName("InfoBtn")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def enterEvent(self, event):
        self._timer.start(80)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._timer.stop()
        self._close_popup()
        super().leaveEvent(event)

    def _close_popup(self):
        if self._popup:
            self._popup.hide()
            self._popup.deleteLater()
            self._popup = None

    def _show_popup(self):
        self._close_popup()
        from PyQt6.QtWidgets import QFrame as QF
        from PyQt6.QtCore import QPoint
        win = self.window()
        popup = QF(win)
        popup.setObjectName("InfoPopup")
        lay = QVBoxLayout(popup)
        lay.setContentsMargins(12, 10, 12, 10)
        lbl = QLabel(self._tooltip_text)
        lbl.setWordWrap(True)
        lbl.setMaximumWidth(300)
        lbl.setStyleSheet("color: #E8E8EA; font-size: 12px; background: transparent; line-height: 1.5;")
        lay.addWidget(lbl)
        popup.adjustSize()
        pos = self.mapTo(win, QPoint(self.width() + 8, -4))
        if pos.x() + popup.width() > win.width():
            pos = self.mapTo(win, QPoint(-popup.width() - 8, -4))
        popup.move(pos)
        popup.show()
        popup.raise_()
        self._popup = popup


def build_drill_slide(page, icon, title, subtitle, drill, metric_name, metric_value, target):
    """Build a single vocal-drill carousel slide. Returns dict of labelled widgets."""
    frame = QFrame()
    frame.setObjectName("InsightCard")
    frame.setStyleSheet(
        "QFrame#InsightCard { background: rgba(255, 255, 255, 0.05); "
        "border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; }"
    )
    lay = QVBoxLayout(frame)
    lay.setContentsMargins(16, 14, 16, 14)
    lay.setSpacing(8)

    header = QHBoxLayout()
    icon_lbl = QLabel(icon)
    icon_lbl.setStyleSheet("font-size: 20px; background: transparent;")
    header.addWidget(icon_lbl)
    title_lbl = QLabel(title)
    title_lbl.setStyleSheet("font-size: 12px; font-weight: 700; color: #E8E8EA; background: transparent;")
    header.addWidget(title_lbl, 1)
    lay.addLayout(header)

    subtitle_lbl = QLabel(subtitle)
    subtitle_lbl.setObjectName("Subtitle")
    subtitle_lbl.setStyleSheet("font-size: 10px; color: #8E8E93; background: transparent;")
    lay.addWidget(subtitle_lbl)

    drill_lbl = QLabel(drill)
    drill_lbl.setObjectName("InsightText")
    drill_lbl.setWordWrap(True)
    drill_lbl.setStyleSheet("font-size: 10px; color: #AEAEB2; line-height: 1.5; background: transparent;")
    lay.addWidget(drill_lbl, 1)

    footer = QHBoxLayout()
    metric_lbl = QLabel(f"{metric_name}: {metric_value}")
    metric_lbl.setStyleSheet("font-size: 10px; color: #86EFAC; font-weight: 600; background: transparent;")
    target_lbl = QLabel(target)
    target_lbl.setStyleSheet("font-size: 9px; color: #636366; background: transparent;")
    footer.addWidget(metric_lbl)
    footer.addStretch()
    footer.addWidget(target_lbl)
    lay.addLayout(footer)

    return {
        "frame": frame, "icon_lbl": icon_lbl, "title_lbl": title_lbl,
        "subtitle_lbl": subtitle_lbl, "drill_lbl": drill_lbl,
        "metric_lbl": metric_lbl, "target_lbl": target_lbl,
    }
