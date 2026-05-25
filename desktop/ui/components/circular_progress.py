from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class CircularProgress(QWidget):
    """
    An elegant, color-graded Circular Progress widget using QPainter.
    Ideal for displaying metric percentages like Clarity, Conciseness, etc.
    """

    def __init__(
        self, title: str, percentage: float = 0.0, accent_color_hex: str = "#86EFAC", parent=None
    ):
        super().__init__(parent)
        self.title = title
        self.percentage = percentage
        self.accent_color_hex = accent_color_hex
        self.setMinimumSize(120, 120)
        self.setMaximumSize(160, 160)

    def setPercentage(self, percentage: float):
        self.percentage = max(0.0, min(100.0, percentage))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        size = min(width, height)

        # Calculations for circular track
        margin = 12
        radius = size - 2 * margin
        x = (width - radius) / 2
        y = (height - radius) / 2
        rect = QRectF(x, y, radius, radius)

        # Draw background track
        bg_pen = QPen(QColor(255, 255, 255, 10))
        bg_pen.setWidth(8)
        bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(rect, 0, 360 * 16)

        # Draw progress arc (start from top, i.e., 90 degrees or 90 * 16 units)
        accent_color = QColor(self.accent_color_hex)
        fg_pen = QPen(accent_color)
        fg_pen.setWidth(8)
        fg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(fg_pen)

        start_angle = 90 * 16
        span_angle = -int((self.percentage / 100.0) * 360 * 16)
        painter.drawArc(rect, start_angle, span_angle)

        # Center Text - Percentage
        painter.setPen(QColor("#E8E8EA"))
        font_pct = QFont("Segoe UI", 16, QFont.Weight.Bold)
        painter.setFont(font_pct)
        pct_text = f"{int(round(self.percentage))}%"
        painter.drawText(
            QRectF(x, y + radius / 2 - 20, radius, 30), Qt.AlignmentFlag.AlignCenter, pct_text
        )

        # Center Text - Title underneath
        painter.setPen(QColor("#8E8E93"))
        font_title = QFont("Segoe UI", 8, QFont.Weight.Normal)
        painter.setFont(font_title)
        painter.drawText(
            QRectF(x - 10, y + radius / 2 + 10, radius + 20, 20),
            Qt.AlignmentFlag.AlignCenter,
            self.title,
        )
