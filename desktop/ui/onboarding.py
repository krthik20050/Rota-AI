"""
Rota AI — Onboarding Wizard
============================
Steps:
  0 — Welcome + Hotkey (merged — the only setup you need)
  1 — Ready (you're all set)

API key configuration and model download were moved to Settings
to get the user dictating in under 30 seconds.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
)

from ui.pages._onboarding_steps import build_step_ready, build_step_welcome
from ui.styles.onboarding_qss import ONBOARDING_QSS
from utils.window_effects import apply_blur


class OnboardingDialog(QDialog):
    """Onboarding wizard — 2 quick steps. Emits finished_signal when done."""

    finished_signal = Signal()

    _WELCOME = 0  # Welcome + Hotkey (merged)
    _READY = 1  # You're all set
    _TOTAL_STEPS = 2

    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self._config = config
        self._step = 0
        self._closing = False

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(600, 580)
        self.setStyleSheet(ONBOARDING_QSS)
        self._build_ui()
        self._show_step(0)

    # ── Build ──────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)

        self._container = QFrame()
        self._container.setObjectName("OBContainer")
        lay = QVBoxLayout(self._container)
        lay.setContentsMargins(52, 10, 52, 32)
        lay.setSpacing(0)

        # Window controls row (close + minimize)
        ctrl_row = QHBoxLayout()
        ctrl_row.setContentsMargins(0, 0, 0, 0)
        ctrl_row.setSpacing(0)
        ctrl_row.addStretch()

        self._min_btn = QPushButton("─")
        self._min_btn.setObjectName("WindowCtrlBtn")
        self._min_btn.setFixedSize(28, 28)
        self._min_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._min_btn.clicked.connect(self.showMinimized)
        ctrl_row.addWidget(self._min_btn)

        self._close_btn = QPushButton("✕")
        self._close_btn.setObjectName("WindowCloseBtn")
        self._close_btn.setFixedSize(28, 28)
        self._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_btn.clicked.connect(self._finish)
        ctrl_row.addWidget(self._close_btn)

        lay.addLayout(ctrl_row)
        lay.addSpacing(0)

        # Progress dots — 2 dots
        dot_row = QHBoxLayout()
        dot_row.setSpacing(6)
        dot_row.addStretch()
        self._dots = []
        for _ in range(self._TOTAL_STEPS):
            d = QFrame()
            d.setObjectName("DotInactive")
            d.setFixedSize(6, 6)
            self._dots.append(d)
            dot_row.addWidget(d)
        dot_row.addStretch()
        lay.addLayout(dot_row)
        lay.addSpacing(28)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: transparent;")
        self._stack.addWidget(build_step_welcome(self))   # 0: Welcome + Hotkey
        self._stack.addWidget(build_step_ready(self))      # 1: Ready
        lay.addWidget(self._stack, 1)
        lay.addSpacing(24)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self._skip_btn = QPushButton("Skip")
        self._skip_btn.setObjectName("SkipBtn")
        self._skip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._skip_btn.clicked.connect(self._finish)
        btn_row.addWidget(self._skip_btn)
        btn_row.addStretch()

        self._back_btn = QPushButton("Back")
        self._back_btn.setObjectName("BackBtn")
        self._back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._back_btn.clicked.connect(self._prev)
        btn_row.addWidget(self._back_btn)

        self._next_btn = QPushButton("Next")
        self._next_btn.setObjectName("NextBtn")
        self._next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._next_btn.clicked.connect(self._next)
        btn_row.addWidget(self._next_btn)

        lay.addLayout(btn_row)
        root.addWidget(self._container)

    # ── Navigation ─────────────────────────────────────────────────

    def _collect_step_data(self, step: int):
        """In-memory only — no disk write, no registry touch."""
        if not self._config:
            return
        try:
            if step == self._WELCOME:
                # Hotkey is already set by capture_hotkey() -> config.set("hotkey", ...)
                if not self._config.get("hotkey"):
                    self._config.set("hotkey", "tab")
        except Exception:
            pass

    def _show_step(self, idx: int):
        self._step = idx
        self._stack.setCurrentIndex(idx)
        self._back_btn.setVisible(idx > 0)
        self._skip_btn.setVisible(idx < self._READY)
        self._next_btn.setText("Get Started" if idx == self._READY else "Next")
        for i, dot in enumerate(self._dots):
            if i == idx:
                dot.setObjectName("DotActive")
                dot.setFixedSize(20, 6)
            else:
                dot.setObjectName("DotInactive")
                dot.setFixedSize(6, 6)
            dot.setStyleSheet("")

    def _next(self):
        self._collect_step_data(self._step)
        next_step = self._step + 1
        if next_step <= self._READY:
            self._show_step(next_step)
        else:
            self._finish()

    def _prev(self):
        prev_step = self._step - 1
        if prev_step >= 0:
            self._show_step(prev_step)

    def _finish(self):
        self._closing = True
        for s in range(self._TOTAL_STEPS):
            self._collect_step_data(s)
        if self._config:
            self._config.set("onboarding_complete", True)
            try:
                self._config.save()
            except Exception:
                pass
        self.accept()
        QTimer.singleShot(0, self.finished_signal.emit)

    # ── Window drag ────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._drag_pos = event.globalPosition().toPoint()

    def showEvent(self, event):
        super().showEvent(event)
        try:
            apply_blur(int(self.winId()))
        except Exception:
            pass
