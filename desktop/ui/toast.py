from __future__ import annotations

import sys
from collections.abc import Callable

from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QPainter, QPainterPath
from PySide6.QtWidgets import QApplication, QWidget

# Singleton: track the currently visible toast so overlapping notifications
# are closed before showing a new one. Prevents toast stacking when multiple
# events fire in rapid succession (e.g. "No speech detected" + fallback).
_toast_instance: QWidget | None = None

_RADIUS = 20.0
_PAD_H = 22.0  # horizontal padding
_PAD_V = 12.0  # vertical padding
_BORDER_ALPHA = 30  # subtle inner ring alpha


def _close_existing_toast() -> None:
    """Close any currently visible toast before showing a new one."""
    global _toast_instance
    if _toast_instance is not None:
        try:
            _toast_instance.close()
        except Exception:
            pass
        _toast_instance = None


class Toast(QWidget):
    """
    Pill-shaped toast notification.

    Fully self-painted (no QLabel child) so the rounded shape is crisp at
    the OS level — no rectangular background artefact on Windows.

    Each Toast closes the previously visible Toast on creation, preventing
    overlapping notification stacking.
    """

    def __init__(
        self,
        message: str,
        parent=None,
        warning: bool = False,
        on_click: Callable | None = None,
        duration_ms: int = 3500,
    ):
        # Close any existing toast before showing this one
        _close_existing_toast()

        super().__init__(parent)
        self._message = message
        self._warning = warning
        self._on_click = on_click

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAutoFillBackground(False)
        if on_click is not None:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._font = QFont("Segoe UI")
        self._font.setPointSizeF(10.5)
        self._font.setWeight(QFont.Weight.DemiBold)

        if warning:
            self._bg = QColor("#D97706")
            self._fg = QColor("#000000")
        else:
            self._bg = QColor("#2A2A2E")
            self._fg = QColor("#F0F0F2")

        # Size the window to fit the text
        fm = QFontMetricsF(self._font)
        text_w = fm.horizontalAdvance(message)
        text_h = fm.height()
        w = int(text_w + _PAD_H * 2 + 1)
        h = int(text_h + _PAD_V * 2 + 1)
        self.resize(w, h)

        screen = QApplication.primaryScreen()
        if screen is not None:
            geo = screen.availableGeometry()
            self.move((geo.width() - w) // 2, geo.bottom() - 110)

        # Register this as the active toast instance
        global _toast_instance
        _toast_instance = self

        QTimer.singleShot(duration_ms, self._on_toast_expired)

    # ── Windows DWM glass (eliminates white/accent-colour bounding rect) ──

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if sys.platform == "win32":
            try:
                import ctypes

                class MARGINS(ctypes.Structure):
                    _fields_ = [
                        ("cxLeftWidth", ctypes.c_int),
                        ("cxRightWidth", ctypes.c_int),
                        ("cyTopHeight", ctypes.c_int),
                        ("cyBottomHeight", ctypes.c_int),
                    ]

                ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(
                    ctypes.c_void_p(int(self.winId())),
                    ctypes.byref(MARGINS(-1, -1, -1, -1)),
                )
            except Exception:
                pass

    # ── Custom painting — no QLabel, no rectangular artefact ─────────────

    def paintEvent(self, event) -> None:
        w, h = self.width(), self.height()
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # 1. Punch fully transparent so DWM glass shows through empty areas
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 0))
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

            # 2. Pill background clipped to rounded path — no rectangular leak
            path = QPainterPath()
            path.addRoundedRect(QRectF(0, 0, w, h), _RADIUS, _RADIUS)
            painter.setClipPath(path)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self._bg)
            painter.drawRoundedRect(QRectF(0, 0, w, h), _RADIUS, _RADIUS)

            # 3. Subtle inner ring
            painter.setClipping(False)
            from PySide6.QtGui import QPen

            painter.setBrush(Qt.BrushStyle.NoBrush)
            ring_color = QColor(255, 255, 255, _BORDER_ALPHA)
            painter.setPen(QPen(ring_color, 1.0))
            painter.drawRoundedRect(QRectF(0.5, 0.5, w - 1, h - 1), _RADIUS - 0.5, _RADIUS - 0.5)

            # 4. Text centered
            painter.setPen(self._fg)
            painter.setFont(self._font)
            fm = QFontMetricsF(self._font)
            tx = (w - fm.horizontalAdvance(self._message)) / 2.0
            ty = (h + fm.ascent() - fm.descent()) / 2.0
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, self._message)
            _ = tx, ty  # kept for reference
        finally:
            painter.end()

    def _on_toast_expired(self) -> None:
        """Called when the toast auto-dismiss timer fires. Clears singleton ref."""
        global _toast_instance
        if _toast_instance is self:
            _toast_instance = None
        self.close()

    def mousePressEvent(self, event) -> None:
        if self._on_click is not None:
            self._on_click()
            self._on_toast_expired()
        else:
            super().mousePressEvent(event)
