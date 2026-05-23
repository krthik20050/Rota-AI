"""
GitHub-style contribution heatmap — enlarged, dynamic sizing.
"""
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush, QFont
from PyQt6.QtWidgets import QWidget, QSizePolicy
from datetime import datetime, timedelta


class HeatmapGrid(QWidget):
    """
    Enlarged activity heatmap — 18 weeks, scales with available width.
    Color intensity based on word count per day.
    """
    WEEKS = 18

    def __init__(self, daily_counts: dict = None, parent=None):
        super().__init__(parent)
        self.daily_counts = daily_counts or {}
        self.setMinimumSize(440, 128)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(148)

    def setDailyCounts(self, daily_counts: dict):
        self.daily_counts = daily_counts or {}
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        COLS, ROWS = self.WEEKS, 7
        x_off = 32
        y_off = 22

        avail_w = w - x_off - 4
        avail_h = h - y_off - 4
        cell = max(8, min(avail_w // COLS, avail_h // ROWS) - 2)
        gap  = 3

        now        = datetime.now()
        start_date = now - timedelta(days=COLS * 7 - 1)
        # Align to preceding Sunday
        days_back  = (start_date.weekday() + 1) % 7
        aligned    = start_date - timedelta(days=days_back)

        # Day labels
        painter.setPen(QColor("#5A5A60"))
        f = QFont("Segoe UI", 7)
        painter.setFont(f)
        for idx, name in enumerate(["", "Mon", "", "Wed", "", "Fri", ""]):
            if name:
                y = y_off + idx * (cell + gap) + cell // 2 + 3
                painter.drawText(QRectF(2, y - 7, x_off - 4, 12),
                                 Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                                 name)

        # Month labels
        last_month = None
        for col in range(COLS):
            d = aligned + timedelta(weeks=col)
            m = d.strftime("%b")
            if m != last_month:
                last_month = m
                x = x_off + col * (cell + gap)
                painter.setPen(QColor("#5A5A60"))
                painter.drawText(QRectF(x, 4, 28, 12),
                                 Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, m)

        # Cells
        COLORS = [
            QColor(255, 255, 255, 10),     # 0 — empty
            QColor(134, 239, 172, 40),     # < 100 words
            QColor(134, 239, 172, 100),    # < 300 words
            QColor(134, 239, 172, 175),    # < 700 words
            QColor(134, 239, 172, 255),    # >= 700 words
        ]
        for col in range(COLS):
            for day in range(ROWS):
                d     = aligned + timedelta(weeks=col, days=day)
                wc    = self.daily_counts.get(d.strftime("%Y-%m-%d"), 0)
                ci    = 0 if wc == 0 else (1 if wc < 100 else (2 if wc < 300 else (3 if wc < 700 else 4)))
                x     = x_off + col * (cell + gap)
                y     = y_off + day * (cell + gap)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(COLORS[ci]))
                painter.drawRoundedRect(x, y, cell, cell, 2, 2)
