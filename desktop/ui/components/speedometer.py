"""
Semi-circle speedometer widget for words-today visualization.
"""

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRectF, Qt, pyqtProperty
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class SpeedometerWidget(QWidget):
    """Paints a semi-circle arc speedometer with value + label."""

    def __init__(self, max_value: int = 3000, parent=None):
        super().__init__(parent)
        self._value = 0
        self._display_value = 0
        self._max = max_value
        self._anim = None
        self.setFixedSize(220, 130)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)

    @pyqtProperty(int)
    def display_value(self) -> int:
        return self._display_value

    @display_value.setter
    def display_value(self, v: int):
        self._display_value = max(0, min(int(v), self._max))
        self.update()

    def set_value(self, v: int):
        """Instant update — used by periodic metrics refresh (non-insights)."""
        self._value = min(int(v), self._max)
        if self._anim and self._anim.state() == QPropertyAnimation.State.Running:
            return  # don't interrupt a running animation
        self._display_value = self._value
        self.update()

    def set_value_animated(self, v: int, duration: int = 950):
        """Sweep arc from 0 to v with ease-out cubic — called on page entry."""
        self._value = min(int(v), self._max)
        if self._anim and self._anim.state() == QPropertyAnimation.State.Running:
            self._anim.stop()
        self._display_value = 0  # always start arc from zero
        anim = QPropertyAnimation(self, b"display_value", self)
        anim.setStartValue(0)
        anim.setEndValue(self._value)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self._anim = anim

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        r = min(w // 2, h) - 14
        cx, cy = w // 2, h - 8

        rect = QRectF(cx - r, cy - r, r * 2, r * 2)
        pct = min(1.0, self._display_value / max(1, self._max))

        # Track (left→right clockwise = negative span in Qt)
        pen = QPen(QColor("#1A2220"), 13)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawArc(rect, 180 * 16, -180 * 16)

        # Filled arc
        if pct > 0.005:
            pen = QPen(QColor("#86EFAC"), 13)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawArc(rect, 180 * 16, int(-pct * 180 * 16))

        # Value text — monospace for data feel
        p.setPen(QColor("#F0F0F2"))
        f = QFont("Courier New", 22)
        f.setWeight(QFont.Weight.Bold)
        p.setFont(f)
        p.drawText(
            QRectF(0, cy - r * 0.72, w, r * 0.48),
            Qt.AlignmentFlag.AlignCenter,
            f"{self._display_value:,}",
        )

        # Sub-label
        p.setPen(QColor("#5A5A60"))
        p.setFont(QFont("Segoe UI", 10))
        p.drawText(
            QRectF(0, cy - r * 0.26, w, r * 0.26), Qt.AlignmentFlag.AlignCenter, "words today"
        )
