"""Audio-reactive waveform bars for the pill overlay."""

from __future__ import annotations

import time

import numpy as np
from PyQt6.QtCore import QRectF, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QPainter
from PyQt6.QtWidgets import QWidget


class WaveformWidget(QWidget):
    """Fixed-size waveform with asymmetric rise/fall smoothing."""

    BAR_COUNT = 9
    BAR_W = 3
    BAR_GAP = 4
    MIN_H = 4.0
    MAX_H = 34.0
    RISE = 0.42
    FALL = 0.70

    def __init__(self, parent=None):
        super().__init__(parent)
        self._audio_level = 0.0
        self._active = False
        self._bar_opacity = 1.0

        self._phases = np.array([i * 0.85 for i in range(self.BAR_COUNT)], dtype=np.float64)
        self._targets = np.full(self.BAR_COUNT, self.MIN_H, dtype=np.float64)
        self._display = np.full(self.BAR_COUNT, self.MIN_H, dtype=np.float64)
        self._noise = np.zeros(self.BAR_COUNT, dtype=np.float64)
        self._rising = np.zeros(self.BAR_COUNT, dtype=bool)
        self._delta = np.zeros(self.BAR_COUNT, dtype=np.float64)
        self._speed = np.zeros(self.BAR_COUNT, dtype=np.float64)

        total_w = self.BAR_COUNT * self.BAR_W + (self.BAR_COUNT - 1) * self.BAR_GAP
        self.setFixedSize(total_w, int(self.MAX_H) + 4)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._timer = QTimer(self)
        self._timer.setInterval(33)
        self._timer.timeout.connect(self._tick)

    def set_audio_level(self, level: float) -> None:
        self._audio_level = max(0.0, min(1.0, float(level)))

    def set_active(self, active: bool) -> None:
        self._active = active

    def start(self) -> None:
        if not self._timer.isActive():
            self._timer.start(33)

    def stop(self) -> None:
        if self._timer.isActive():
            self._timer.stop()

    def set_bar_opacity(self, opacity: float) -> None:
        self._bar_opacity = max(0.0, min(1.0, float(opacity)))
        self.update()

    def _tick(self) -> None:
        if not self.isVisible() and self._bar_opacity <= 0.01:
            return

        t = time.monotonic()
        if self._active:
            np.sin(t * 5.0 + self._phases, out=self._noise)
            self._noise += 1.0
            self._noise *= 0.5
            self._targets[:] = self.MIN_H + (
                self._audio_level * (self.MAX_H - self.MIN_H) * (0.5 + self._noise * 0.5)
            )
        else:
            np.sin(t * 1.1 + self._phases * 0.4, out=self._noise)
            self._noise += 1.0
            self._noise *= 0.5
            self._targets[:] = self.MIN_H + self._noise * 9.0

        np.greater(self._targets, self._display, out=self._rising)
        np.subtract(self._targets, self._display, out=self._delta)
        np.multiply(self._rising, self.RISE - self.FALL, out=self._speed)
        self._speed += self.FALL
        np.multiply(self._speed, self._delta, out=self._delta)
        self._display += self._delta
        self.update()

    def paintEvent(self, event) -> None:
        if self._bar_opacity < 0.01:
            return

        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setOpacity(self._bar_opacity)
            # White bars with slight transparency for a softer look
            painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
            painter.setPen(Qt.PenStyle.NoPen)

            cy = self.height() / 2.0
            for i, h in enumerate(self._display):
                x = i * (self.BAR_W + self.BAR_GAP)
                y = cy - h / 2.0
                painter.drawRoundedRect(QRectF(x, y, self.BAR_W, float(h)), 1.5, 1.5)
        finally:
            painter.end()
