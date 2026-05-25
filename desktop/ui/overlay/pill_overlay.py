"""Floating pill overlay for Rota AI dictation."""

from __future__ import annotations

import sys

from PyQt6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QRect,
    Qt,
    QTimer,
    QVariantAnimation,
    pyqtSignal,
    pyqtSlot,
)
from PyQt6.QtGui import QColor, QCursor, QFont, QPainter
from PyQt6.QtWidgets import QApplication, QWidget

from ui.overlay.animation_utils import (
    apply_dwm_transparency,
    draw_background,
    draw_centered_text,
    draw_done,
    draw_idle_dot,
    draw_recording_controls,
    play_haptic,
)
from ui.overlay.pill_state import PillState
from ui.overlay.waveform_widget import WaveformWidget


class PillOverlay(QWidget):
    """Frameless, transparent, always-on-top overlay with explicit state transitions."""

    hidden_after_exit = pyqtSignal()
    cancel_requested = pyqtSignal()
    stop_requested = pyqtSignal()

    HEIGHT = 38
    RADIUS = 19
    MARGIN_BOTTOM = 26

    STATE_WIDTHS = {
        PillState.IDLE: 42,
        PillState.RECORDING: 152,  # room for X + waveform + stop button
        PillState.TRANSCRIBING: 150,
        PillState.PROCESSING: 150,
        PillState.DONE: 118,
        PillState.ERROR: 124,
    }

    BG_COLOR = QColor(18, 18, 20, 235)
    TEXT_COLOR = QColor(255, 255, 255, 210)
    DONE_TEXT_COLOR = QColor(110, 210, 110, 230)
    ERROR_TEXT_COLOR = QColor(240, 100, 100, 230)

    def __init__(self):
        super().__init__()
        self._state = PillState.IDLE
        self._audio_level = 0.0
        self._entry_scale = 1.0
        self._exit_scale = 1.0
        self._text_opacity = 0.0
        self._done_scale = 1.0
        self._partial_text = ""
        self._ellipsis_index = 0
        self._ellipsis_frames = [" ", ". ", ".. ", "..."]
        self._active_animations: list[QAbstractAnimation] = []

        self._setup_window()
        self._font = QFont("Segoe UI")
        self._font.setPointSizeF(10.5)
        self._font.setWeight(QFont.Weight.Medium)
        self._font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.2)

        self._waveform = WaveformWidget(self)
        self._waveform.hide()

        self._ellipsis_timer = QTimer(self)
        self._ellipsis_timer.setInterval(500)
        self._ellipsis_timer.timeout.connect(self._tick_ellipsis)

        self._done_timer = QTimer(self)
        self._done_timer.setSingleShot(True)
        self._done_timer.timeout.connect(lambda: self.set_state(PillState.IDLE))

        self._pulse_timer = QTimer(self)
        self._pulse_timer.setInterval(33)
        self._pulse_timer.timeout.connect(self.update)

        self._geometry_anim = QVariantAnimation(self)
        self._geometry_anim.valueChanged.connect(self._apply_animated_geometry)

        self._position_on_screen(self.STATE_WIDTHS[PillState.IDLE])
        self._sync_waveform_geometry()

    def _setup_window(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        # Start transparent to mouse — enabled only during RECORDING
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAutoFillBackground(False)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setMinimumHeight(self.HEIGHT)
        self.setMaximumHeight(self.HEIGHT)
        self.resize(self.STATE_WIDTHS[PillState.IDLE], self.HEIGHT)

    def _screen_geometry(self):
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        return screen.geometry() if screen is not None else None

    def _target_rect(self, width: int) -> QRect:
        screen_geo = self._screen_geometry()
        if screen_geo is None:
            return QRect(self.x(), self.y(), width, self.HEIGHT)
        x = screen_geo.center().x() - width // 2
        y = screen_geo.bottom() - self.HEIGHT - self.MARGIN_BOTTOM
        return QRect(x, y, width, self.HEIGHT)

    def _position_on_screen(self, width: int | None = None) -> None:
        self.setGeometry(self._target_rect(width or self.width()))

    def _sync_waveform_geometry(self) -> None:
        x = int((self.width() - self._waveform.width()) / 2)
        y = int((self.height() - self._waveform.height()) / 2)
        self._waveform.move(x, y)

    def resizeEvent(self, event) -> None:
        self._sync_waveform_geometry()
        super().resizeEvent(event)

    @pyqtSlot(float)
    def on_audio_level(self, raw_rms: float) -> None:
        amplified = min(1.0, max(0.0, float(raw_rms)) * 18.0)
        self._audio_level = self._audio_level * 0.6 + amplified * 0.4
        self._waveform.set_audio_level(self._audio_level)

    def get_state(self) -> PillState:
        return self._state

    def set_state(self, new_state: PillState) -> None:
        if new_state == self._state:
            return

        old_state = self._state
        self._state = new_state
        self._done_timer.stop()

        if old_state == PillState.IDLE and new_state == PillState.RECORDING:
            self._transition_idle_to_recording()
        elif old_state == PillState.RECORDING and new_state == PillState.TRANSCRIBING:
            self._transition_recording_to_transcribing()
        elif new_state == PillState.PROCESSING:
            self._transition_to_processing()
        elif new_state == PillState.DONE:
            self._transition_to_done()
        elif new_state == PillState.IDLE:
            self._transition_to_idle()
        else:
            self._animate_width(self.STATE_WIDTHS[new_state])
            self.update()

    # ── State transitions ────────────────────────────────────────────────────

    def _transition_idle_to_recording(self) -> None:
        self._partial_text = ""
        self._text_opacity = 0.0
        self._ellipsis_timer.stop()
        self._waveform.set_active(True)
        self._waveform.set_bar_opacity(1.0)
        self._waveform.show()
        self._waveform.start()
        self._animate_width(self.STATE_WIDTHS[PillState.RECORDING], QEasingCurve.Type.OutBack, 360)
        play_haptic("start")
        # Enable mouse events for cancel/stop buttons
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.update()

    def _transition_recording_to_transcribing(self) -> None:
        # Audio cue fires IMMEDIATELY when recording stops
        play_haptic("stop")
        # Disable mouse events — no buttons visible after recording
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._waveform.set_active(False)
        self._animate_width(
            self.STATE_WIDTHS[PillState.TRANSCRIBING], QEasingCurve.Type.OutCubic, 260
        )
        self._ellipsis_index = 0
        self._ellipsis_timer.start(500)
        self._text_opacity = 0.0

        bar_fade = QVariantAnimation(self)
        bar_fade.setStartValue(1.0)
        bar_fade.setEndValue(0.0)
        bar_fade.setDuration(550)
        bar_fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        bar_fade.valueChanged.connect(lambda v: self._waveform.set_bar_opacity(float(v)))
        bar_fade.finished.connect(self._waveform.stop)
        self._start_tracked_animation(bar_fade)
        QTimer.singleShot(140, self._start_text_fade_in)

    def _transition_to_processing(self) -> None:
        self._animate_width(
            self.STATE_WIDTHS[PillState.PROCESSING], QEasingCurve.Type.OutCubic, 260
        )
        self._waveform.set_active(False)
        self._waveform.set_bar_opacity(0.0)
        self._waveform.stop()
        self._ellipsis_index = 0
        self._ellipsis_timer.start(500)
        self._text_opacity = 0.0
        self._start_text_fade_in()
        self.update()

    def _transition_to_done(self) -> None:
        self._ellipsis_timer.stop()
        self._waveform.set_active(False)
        self._waveform.set_bar_opacity(0.0)
        self._waveform.stop()
        self._waveform.hide()
        self._animate_width(self.STATE_WIDTHS[PillState.DONE], QEasingCurve.Type.OutCubic, 220)
        self._text_opacity = 0.0
        self._start_text_fade_in()
        self._start_done_bounce()
        play_haptic("done")
        self._done_timer.start(900)

    def _transition_to_idle(self) -> None:
        self._partial_text = ""
        self._ellipsis_timer.stop()
        self._waveform.set_active(False)
        self._waveform.set_bar_opacity(0.0)
        self._waveform.stop()
        self._waveform.hide()
        self._text_opacity = 0.0
        self._done_scale = 1.0
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.hide_overlay()

    # ── Animation helpers ────────────────────────────────────────────────────

    def _animate_width(
        self,
        target_width: int,
        easing: QEasingCurve.Type | None = None,
        duration: int | None = None,
    ) -> None:
        start_rect = self.geometry()
        end_rect = self._target_rect(target_width)
        if start_rect == end_rect:
            return

        if not self.isVisible():
            self.setGeometry(end_rect)
            return

        expanding = target_width > start_rect.width()
        curve = easing or (QEasingCurve.Type.OutBack if expanding else QEasingCurve.Type.OutCubic)
        ms = duration or (300 if expanding else 200)
        if not expanding:
            curve = QEasingCurve.Type.OutCubic
            ms = 200

        self._geometry_anim.stop()
        self._geometry_anim.setStartValue(start_rect)
        self._geometry_anim.setEndValue(end_rect)
        self._geometry_anim.setDuration(ms)
        self._geometry_anim.setEasingCurve(curve)
        self._geometry_anim.start()

    def _apply_animated_geometry(self, value) -> None:
        if isinstance(value, QRect):
            self.setGeometry(value)

    def _start_text_fade_in(self) -> None:
        if self._state not in (PillState.TRANSCRIBING, PillState.PROCESSING, PillState.DONE):
            return
        anim = QVariantAnimation(self)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setDuration(380)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        anim.valueChanged.connect(self._set_text_opacity)
        self._start_tracked_animation(anim)

    def _set_text_opacity(self, value) -> None:
        self._text_opacity = float(value)
        self.update()

    def _start_done_bounce(self) -> None:
        anim = QVariantAnimation(self)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setDuration(420)
        anim.setEasingCurve(QEasingCurve.Type.Linear)
        anim.valueChanged.connect(self._set_done_progress)
        self._start_tracked_animation(anim)

    def _set_done_progress(self, value) -> None:
        t = float(value)
        if t < 0.68:
            local = t / 0.68
            self._done_scale = 0.5 + 0.6 * (1 - (1 - local) ** 3)
        else:
            local = (t - 0.68) / 0.32
            self._done_scale = 1.08 + (1.0 - 1.08) * (1 - (1 - local) ** 3)
        self.update()

    def _start_tracked_animation(self, anim: QAbstractAnimation) -> None:
        anim.stop()

        def cleanup(animation=anim):
            if animation in self._active_animations:
                self._active_animations.remove(animation)

        anim.finished.connect(cleanup)
        self._active_animations.append(anim)
        anim.start()

    def _tick_ellipsis(self) -> None:
        self._ellipsis_index = (self._ellipsis_index + 1) % len(self._ellipsis_frames)
        self.update()

    # ── Show / hide ──────────────────────────────────────────────────────────

    def show_overlay(self) -> None:
        self._position_on_screen(self.width())
        if not self.isVisible():
            self._entry_scale = 0.72
            self._exit_scale = 1.0
            self.setWindowOpacity(0.0)
            self.show()
            self._pulse_timer.start()
            self._start_entry_animation()

    def _start_entry_animation(self) -> None:
        opacity = QVariantAnimation(self)
        opacity.setStartValue(0.0)
        opacity.setEndValue(1.0)
        opacity.setDuration(380)
        opacity.setEasingCurve(QEasingCurve.Type.OutCubic)
        opacity.valueChanged.connect(lambda v: self.setWindowOpacity(float(v)))
        self._start_tracked_animation(opacity)

        scale = QVariantAnimation(self)
        scale.setStartValue(0.72)
        scale.setEndValue(1.0)
        scale.setDuration(380)
        scale.setEasingCurve(QEasingCurve.Type.OutBack)
        scale.valueChanged.connect(self._set_entry_scale)
        self._start_tracked_animation(scale)

    def _set_entry_scale(self, value) -> None:
        self._entry_scale = float(value)
        self.update()

    def hide_overlay(self) -> None:
        if not self.isVisible():
            return
        for anim in list(self._active_animations):
            anim.stop()
        self._active_animations.clear()
        self._geometry_anim.stop()
        self._ellipsis_timer.stop()
        self._done_timer.stop()

        opacity = QVariantAnimation(self)
        opacity.setStartValue(float(self.windowOpacity()))
        opacity.setEndValue(0.0)
        opacity.setDuration(210)
        opacity.setEasingCurve(QEasingCurve.Type.InCubic)
        opacity.valueChanged.connect(lambda v: self.setWindowOpacity(float(v)))
        self._start_tracked_animation(opacity)

        scale = QVariantAnimation(self)
        scale.setStartValue(1.0)
        scale.setEndValue(0.84)
        scale.setDuration(210)
        scale.setEasingCurve(QEasingCurve.Type.InCubic)
        scale.valueChanged.connect(self._set_exit_scale)
        scale.finished.connect(self._hide_after_exit)
        self._start_tracked_animation(scale)

    def _set_exit_scale(self, value) -> None:
        self._exit_scale = float(value)
        self.update()

    def _hide_after_exit(self) -> None:
        self._pulse_timer.stop()
        self._waveform.stop()
        self._waveform.hide()
        self.hide()
        self.setWindowOpacity(1.0)
        self._entry_scale = 1.0
        self._exit_scale = 1.0
        self.hidden_after_exit.emit()

    # ── Platform transparency ─────────────────────────────────────────────────

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if sys.platform == "win32":
            apply_dwm_transparency(int(self.winId()))
        # macOS/Linux: transparency handled by the compositor/WM

    # ── Mouse events (active only in RECORDING state) ─────────────────────────

    def mousePressEvent(self, event) -> None:
        if self._state != PillState.RECORDING:
            event.ignore()
            return
        x = event.position().x()
        # Cancel zone: left HEIGHT pixels
        if x <= self.HEIGHT:
            self.cancel_requested.emit()
        # Stop zone: right HEIGHT pixels
        elif x >= self.width() - self.HEIGHT:
            self.stop_requested.emit()
        event.accept()

    # ── Painting ─────────────────────────────────────────────────────────────

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Clear to fully transparent — prevents white rect artifact
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 0))
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

            painter.save()
            scale = min(self._entry_scale, self._exit_scale)
            if abs(scale - 1.0) > 0.001:
                cx = self.width() / 2.0
                cy = self.height() / 2.0
                painter.translate(cx, cy)
                painter.scale(scale, scale)
                painter.translate(-cx, -cy)

            draw_background(painter, self.width(), self.height(), self.RADIUS, self.BG_COLOR)
            self._draw_content(painter)
            painter.restore()
        finally:
            painter.end()

    def _draw_content(self, painter: QPainter) -> None:
        w, h = self.width(), self.height()
        s = self._state
        if s == PillState.IDLE:
            draw_idle_dot(painter, w, h)
        elif s == PillState.RECORDING:
            draw_recording_controls(painter, w, h)
        elif s in (PillState.TRANSCRIBING, PillState.PROCESSING):
            label = "Transcribing" if s == PillState.TRANSCRIBING else "Processing"
            text = label + self._ellipsis_frames[self._ellipsis_index]
            draw_centered_text(painter, text, self.TEXT_COLOR, self._font, w, h, self._text_opacity)
        elif s == PillState.DONE:
            draw_done(
                painter,
                self._font,
                w,
                h,
                self._done_scale,
                self._text_opacity,
                self.DONE_TEXT_COLOR,
            )
        elif s == PillState.ERROR:
            text = self._truncated_partial_text() or "Error"
            draw_centered_text(
                painter, text, self.ERROR_TEXT_COLOR, self._font, w, h, self._text_opacity
            )

    def set_partial_text(self, text: str) -> None:
        self._partial_text = (text or "").strip()
        self.update()

    def _truncated_partial_text(self) -> str:
        text = self._partial_text
        if len(text) <= 44:
            return text
        return text[-44:]

    # ── Public API ────────────────────────────────────────────────────────────

    def show_success(self, message: str = "Done") -> None:
        self.set_state(PillState.DONE)
        self.show_overlay()

    def show_error(self, message: str = "Error") -> None:
        self._partial_text = message
        play_haptic("error")
        self.set_state(PillState.ERROR)
        self.show_overlay()

    def show_listening(self) -> None:
        self.set_state(PillState.RECORDING)
        self.show_overlay()
