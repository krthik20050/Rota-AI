"""Animation and paint utility functions for pill overlay.

These provide finer control than QEasingCurve for specific animation scenarios,
plus standalone paint helpers extracted from PillOverlay to keep it under 500 lines.
"""

from __future__ import annotations

import math
import threading
import time

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QFontMetricsF, QPainter, QPen


# ── Easing functions ─────────────────────────────────────────────────────────

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b."""
    return a + (b - a) * t


def clamp(value: float, min_v: float, max_v: float) -> float:
    """Clamp value between min and max."""
    return max(min_v, min(max_v, value))


def ease_out_back(t: float, overshoot: float = 1.70158) -> float:
    """CSS cubic-bezier equivalent of OutBack. Used for width expand."""
    t -= 1
    return t * t * ((overshoot + 1) * t + overshoot) + 1


def ease_out_cubic(t: float) -> float:
    """Used for width collapse — no overshoot."""
    return 1 - (1 - t) ** 3


def ease_in_out_cubic(t: float) -> float:
    """Used for text opacity transitions."""
    if t < 0.5:
        return 4 * t * t * t
    return 1 - (-2 * t + 2) ** 3 / 2


def ease_in_cubic(t: float) -> float:
    """Used for exit animation."""
    return t * t * t


def spring_bounce(t: float) -> float:
    """Spring-like bounce for checkmark draw-on effect.

    scale 0.4 → 1.1 → 1.0 over the animation duration.
    """
    if t < 0.6:
        return 0.4 + 0.7 * ease_out_back(t / 0.6)
    elif t < 0.85:
        return 1.1 - 0.1 * ((t - 0.6) / 0.25)
    else:
        return 1.0 + 0.0 * ((t - 0.85) / 0.15)


# ── Haptic feedback ──────────────────────────────────────────────────────────

def play_haptic(sound_type: str) -> None:
    """Soft sine-wave tones via sounddevice (non-blocking)."""
    def _play():
        try:
            import numpy as np
            import sounddevice as sd

            sr = 22050
            vol = 0.08

            def _tone(freq: float, dur: float, fade_k: float = 30.0) -> np.ndarray:
                t = np.linspace(0.0, dur, int(sr * dur), endpoint=False)
                envelope = np.exp(-t * fade_k)
                return (np.sin(2.0 * np.pi * freq * t) * envelope * vol).astype(np.float32)

            if sound_type == "start":
                wave = _tone(880.0, 0.04, fade_k=35.0)
            elif sound_type == "stop":
                # Immediate cue on recording stop — descending two-tone
                t1 = _tone(1319.0, 0.04, fade_k=40.0)
                gap = np.zeros(int(sr * 0.025), dtype=np.float32)
                t2 = _tone(1047.0, 0.05, fade_k=35.0)
                wave = np.concatenate([t1, gap, t2])
            elif sound_type == "done":
                # Short soft confirmation chime on injection done
                wave = _tone(1100.0, 0.035, fade_k=45.0)
            elif sound_type == "error":
                wave = _tone(440.0, 0.05, fade_k=25.0)
            else:
                return

            sd.play(wave, sr, blocking=False)
        except Exception:
            pass

    threading.Thread(target=_play, daemon=True).start()


# ── DWM transparency (Windows) ───────────────────────────────────────────────

def apply_dwm_transparency(win_id: int) -> None:
    """Extend DWM glass into entire client area — eliminates white bounding rect on Windows."""
    try:
        import ctypes
        import ctypes.wintypes

        class MARGINS(ctypes.Structure):
            _fields_ = [
                ("cxLeftWidth", ctypes.c_int),
                ("cxRightWidth", ctypes.c_int),
                ("cyTopHeight", ctypes.c_int),
                ("cyBottomHeight", ctypes.c_int),
            ]

        hwnd = ctypes.c_void_p(win_id)
        # -1 in all margins = extend glass to cover entire window
        margins = MARGINS(-1, -1, -1, -1)
        ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(margins))
    except Exception:
        pass  # Silently fall back — non-DWM systems still render correctly


# ── Paint helpers ────────────────────────────────────────────────────────────

def draw_background(
    painter: QPainter,
    width: float,
    height: float,
    radius: float,
    bg_color: QColor,
) -> None:
    """Draw pill background fill and subtle inner ring."""
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(bg_color)
    painter.drawRoundedRect(QRectF(0, 0, width, height), radius, radius)
    # Subtle inner ring — gives depth without an outer shadow rectangle
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(QPen(QColor(255, 255, 255, 20), 1.0))
    painter.drawRoundedRect(
        QRectF(0.5, 0.5, width - 1, height - 1),
        radius - 0.5, radius - 0.5,
    )


def draw_idle_dot(painter: QPainter, width: float, height: float) -> None:
    """Pulsing white dot for idle state."""
    pulse = 0.30 + 0.55 * ((math.sin(time.monotonic() * (2.0 * math.pi / 2.6)) + 1.0) / 2.0)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(255, 255, 255, int(255 * pulse)))
    painter.drawEllipse(QPointF(width / 2.0, height / 2.0), 3.0, 3.0)


def draw_centered_text(
    painter: QPainter,
    text: str,
    color: QColor,
    font,
    width: float,
    height: float,
    text_opacity: float,
) -> None:
    """Draw horizontally and vertically centered text with opacity."""
    if text_opacity < 0.01:
        return
    painter.save()
    painter.setOpacity(text_opacity)
    painter.setFont(font)
    painter.setPen(color)
    metrics = QFontMetricsF(font)
    text_rect = metrics.boundingRect(text)
    x = (width - text_rect.width()) / 2.0
    y = (height + metrics.ascent() - metrics.descent()) / 2.0
    painter.drawText(QPointF(x, y), text)
    painter.restore()


def draw_done(
    painter: QPainter,
    font,
    width: float,
    height: float,
    done_scale: float,
    text_opacity: float,
    done_text_color: QColor,
) -> None:
    """Draw 'Done ✓' with bounce scale transform."""
    painter.save()
    cx = width / 2.0
    cy = height / 2.0
    painter.translate(cx, cy)
    painter.scale(done_scale, done_scale)
    painter.translate(-cx, -cy)
    draw_centered_text(painter, "Done \u2713", done_text_color, font, width, height, text_opacity)
    painter.restore()


def draw_recording_controls(painter: QPainter, width: float, height: float) -> None:
    """Draw cancel (✕) button left, stop (■) button right."""
    cy = height / 2.0
    btn_r = 12.0
    cx_cancel = height / 2.0
    cx_stop = width - height / 2.0

    # Cancel button background
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(255, 255, 255, 22))
    painter.drawEllipse(QPointF(cx_cancel, cy), btn_r, btn_r)
    # X lines
    off = 4.5
    pen = QPen(QColor(255, 255, 255, 200), 1.5)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawLine(
        QPointF(cx_cancel - off, cy - off), QPointF(cx_cancel + off, cy + off)
    )
    painter.drawLine(
        QPointF(cx_cancel + off, cy - off), QPointF(cx_cancel - off, cy + off)
    )

    # Stop button (red)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(220, 48, 48))
    painter.drawEllipse(QPointF(cx_stop, cy), btn_r, btn_r)
    # Stop square icon
    sq = 9.0
    painter.setBrush(QColor(255, 255, 255, 245))
    r = 2.0
    painter.drawRoundedRect(
        QRectF(cx_stop - sq / 2, cy - sq / 2, sq, sq), r, r
    )
