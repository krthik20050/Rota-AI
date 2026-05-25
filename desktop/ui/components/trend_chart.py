import time

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QWidget


class SpeechTrendChart(QWidget):
    """
    A premium, glassmorphic line chart using QPainter to plot speaking speed (WPM)
    and Clarity (%) trend lines over recent dictation sessions.
    Uses smooth anti-aliased paths, color gradients, and glowing data nodes.
    """

    def __init__(self, labels: list = None, wpm: list = None, clarity: list = None, parent=None):
        super().__init__(parent)
        self.labels = labels or []
        self.wpm = wpm or []
        self.clarity = clarity or []
        self.setMinimumSize(320, 160)
        self.setMaximumSize(600, 220)

        self._full_wpm = []
        self._full_clarity = []
        self._anim_start = 0.0
        self._anim_duration = 1.3
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(14)
        self._anim_timer.timeout.connect(self._tick)

    def setTrendData(self, labels: list, wpm: list, clarity: list):
        self._anim_timer.stop()
        self.labels = labels or []
        self.wpm = wpm or []
        self.clarity = clarity or []
        self._full_wpm = list(self.wpm)
        self._full_clarity = list(self.clarity)
        self.update()

    def setTrendDataAnimated(self, labels: list, wpm: list, clarity: list):
        self.labels = labels or []
        self._full_wpm = list(wpm or [])
        self._full_clarity = list(clarity or [])
        self.wpm = [0.0] * len(self._full_wpm)
        self.clarity = [0.0] * len(self._full_clarity)
        self._anim_start = time.monotonic()
        self._anim_timer.start()

    def _tick(self):
        elapsed = time.monotonic() - self._anim_start
        t = elapsed / self._anim_duration
        if t >= 1.0:
            t = 1.0
            self._anim_timer.stop()
        ease = 1.0 - (1.0 - t) ** 3
        self.wpm = [v * ease for v in self._full_wpm]
        self.clarity = [v * ease for v in self._full_clarity]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw a beautiful dark acrylic card back panel
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(28, 28, 31, 140))
        rect_bg = QRectF(0, 0, self.width(), self.height())
        painter.drawRoundedRect(rect_bg, 8, 8)

        # Draw a subtle top border line for glassmorphic shine
        shine_pen = QPen(QColor(255, 255, 255, 12))
        shine_pen.setWidth(1)
        painter.setPen(shine_pen)
        painter.drawLine(8, 0, self.width() - 8, 0)

        # Geometry setup
        padding_left = 40
        padding_right = 40
        padding_top = 25
        padding_bottom = 25

        graph_width = self.width() - padding_left - padding_right
        graph_height = self.height() - padding_top - padding_bottom

        if not self.wpm or len(self.wpm) < 2:
            # Draw elegant Empty State message
            painter.setPen(QColor("#8E8E93"))
            font = QFont("Segoe UI", 10)
            painter.setFont(font)
            painter.drawText(
                QRectF(0, 0, self.width(), self.height()),
                Qt.AlignmentFlag.AlignCenter,
                "Start dictating to generate trend metrics.",
            )
            return

        # Grid lines (draw 3 horizontal divider lines)
        grid_pen = QPen(QColor(255, 255, 255, 10))
        grid_pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        for i in range(4):
            y = padding_top + (graph_height / 3) * i
            painter.drawLine(padding_left, int(y), padding_left + graph_width, int(y))

        # Scalers
        max_wpm = max(180, max(self.wpm))
        min_wpm = 0
        wpm_range = max_wpm - min_wpm

        max_clarity = 100
        min_clarity = 0
        clarity_range = max_clarity - min_clarity

        num_points = len(self.wpm)
        dx = graph_width / (num_points - 1)

        # ----------------------------------------------------
        # Draw WPM trend area + line (Vibrant Vital Blue-Green)
        # ----------------------------------------------------
        wpm_points = []
        for i in range(num_points):
            x = padding_left + i * dx
            # Invert Y as QPainter origin is top-left
            y = padding_top + graph_height - ((self.wpm[i] - min_wpm) / wpm_range) * graph_height
            wpm_points.append(QPointF(x, y))

        # WPM Area Path (Gradient fill)
        area_path = QPainterPath()
        area_path.moveTo(wpm_points[0].x(), padding_top + graph_height)
        for pt in wpm_points:
            area_path.lineTo(pt.x(), pt.y())
        area_path.lineTo(wpm_points[-1].x(), padding_top + graph_height)
        area_path.closeSubpath()

        area_gradient = QLinearGradient(0, padding_top, 0, padding_top + graph_height)
        area_gradient.setColorAt(0.0, QColor(93, 197, 253, 50))  # Light blue glow
        area_gradient.setColorAt(1.0, QColor(93, 197, 253, 0))
        painter.fillPath(area_path, QBrush(area_gradient))

        # WPM Line Path
        line_path = QPainterPath()
        line_path.moveTo(wpm_points[0])
        for pt in wpm_points[1:]:
            line_path.lineTo(pt)

        wpm_pen = QPen(QColor("#93C5FD"))
        wpm_pen.setWidth(2)
        painter.setPen(wpm_pen)
        painter.drawPath(line_path)

        # ----------------------------------------------------
        # Draw Clarity Trend Line (Calm Accent Vital Green)
        # ----------------------------------------------------
        clarity_points = []
        for i in range(num_points):
            x = padding_left + i * dx
            y = (
                padding_top
                + graph_height
                - ((self.clarity[i] - min_clarity) / clarity_range) * graph_height
            )
            clarity_points.append(QPointF(x, y))

        clarity_line_path = QPainterPath()
        clarity_line_path.moveTo(clarity_points[0])
        for pt in clarity_points[1:]:
            clarity_line_path.lineTo(pt)

        clarity_pen = QPen(QColor("#86EFAC"))
        clarity_pen.setWidth(2)
        painter.setPen(clarity_pen)
        painter.drawPath(clarity_line_path)

        # ----------------------------------------------------
        # Draw Glowing Nodes
        # ----------------------------------------------------
        for pt in wpm_points:
            # WPM Dot
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(147, 197, 253, 60))  # outer glow
            painter.drawEllipse(pt, 6.0, 6.0)
            painter.setBrush(QColor("#93C5FD"))  # solid core
            painter.drawEllipse(pt, 3.0, 3.0)

        for pt in clarity_points:
            # Clarity Dot
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(134, 239, 172, 60))  # outer glow
            painter.drawEllipse(pt, 6.0, 6.0)
            painter.setBrush(QColor("#86EFAC"))  # solid core
            painter.drawEllipse(pt, 3.0, 3.0)

        # ----------------------------------------------------
        # Labels and Axes
        # ----------------------------------------------------
        painter.setPen(QColor("#8E8E93"))
        font_axis = QFont("Segoe UI", 7)
        painter.setFont(font_axis)

        # X-Axis labels
        for i in range(num_points):
            lbl = self.labels[i]
            pt = wpm_points[i]
            painter.drawText(
                QRectF(pt.x() - 15, padding_top + graph_height + 4, 30, 12),
                Qt.AlignmentFlag.AlignCenter,
                lbl,
            )

        # Left WPM Axis values (Draw 0, 90, 180)
        painter.setPen(QColor("#93C5FD"))
        painter.drawText(
            QRectF(8, padding_top - 6, 28, 12), Qt.AlignmentFlag.AlignRight, f"{max_wpm}"
        )
        painter.drawText(
            QRectF(8, padding_top + graph_height / 2 - 6, 28, 12),
            Qt.AlignmentFlag.AlignRight,
            f"{max_wpm // 2}",
        )
        painter.drawText(
            QRectF(8, padding_top + graph_height - 6, 28, 12), Qt.AlignmentFlag.AlignRight, "0"
        )

        # Right Clarity Axis values (Draw 100%, 50%, 0%)
        painter.setPen(QColor("#86EFAC"))
        painter.drawText(
            QRectF(self.width() - 36, padding_top - 6, 28, 12), Qt.AlignmentFlag.AlignLeft, "100%"
        )
        painter.drawText(
            QRectF(self.width() - 36, padding_top + graph_height / 2 - 6, 28, 12),
            Qt.AlignmentFlag.AlignLeft,
            "50%",
        )
        painter.drawText(
            QRectF(self.width() - 36, padding_top + graph_height - 6, 28, 12),
            Qt.AlignmentFlag.AlignLeft,
            "0%",
        )

        # Legend at top
        painter.setPen(QColor("#E8E8EA"))
        font_legend = QFont("Segoe UI", 7, QFont.Weight.Bold)
        painter.setFont(font_legend)

        # WPM indicator
        painter.setBrush(QColor("#93C5FD"))
        painter.drawEllipse(padding_left + 10, 8, 5, 5)
        painter.setPen(QColor("#8E8E93"))
        painter.drawText(padding_left + 20, 4, 60, 12, Qt.AlignmentFlag.AlignLeft, "Speed (WPM)")

        # Clarity indicator
        painter.setBrush(QColor("#86EFAC"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(padding_left + 90, 8, 5, 5)
        painter.setPen(QColor("#8E8E93"))
        painter.drawText(padding_left + 100, 4, 60, 12, Qt.AlignmentFlag.AlignLeft, "Clarity (%)")
