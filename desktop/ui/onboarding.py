"""
Rota AI — Onboarding Wizard
============================
Steps:
  0 — Welcome
  1 — API Keys  (Gemini + Groq)
  2 — Whisper Model  (choose + download)
  3 — Hotkey  (interactive picker)
  4 — Ready
"""
from __future__ import annotations

import os
import threading

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QPushButton,
    QStackedWidget, QVBoxLayout,
)

from utils.window_effects import apply_blur
from ui.styles.onboarding_qss import ONBOARDING_QSS
from ui.pages._onboarding_steps import (
    build_step_welcome,
    build_step_api_keys,
    build_step_model,
    build_step_hotkey,
    build_step_ready,
)


class OnboardingDialog(QDialog):
    """Full onboarding wizard. Emits finished_signal when done or skipped."""

    finished_signal = pyqtSignal()
    _download_result = pyqtSignal(bool, str)   # success, error_msg — thread-safe

    # Step indices: 0=Welcome, 1=API Keys, 2=Model, 3=Hotkey, 4=Ready
    _WELCOME = 0
    _API_KEYS = 1
    _MODEL = 2
    _HOTKEY = 3
    _READY = 4
    _TOTAL_STEPS = 5  # always 5 widgets in stack, but we may skip one

    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self._config = config
        self._step = 0
        self._download_done = False
        self._download_error = ""
        self._closing = False
        self._spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self._spinner_idx = 0
        self._spinner_timer = QTimer(self)
        self._spinner_timer.setInterval(80)
        self._spinner_timer.timeout.connect(self._spin)
        self._download_result.connect(self._download_finished)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(600, 580)
        self.setStyleSheet(ONBOARDING_QSS)
        self._build_ui()
        self._show_step(0)

    # ── Build ──────────────────────────────────────────────────────────────

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

        self._min_btn  = QPushButton("─")
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

        # Progress dots
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
        self._stack.addWidget(build_step_welcome(self))
        self._stack.addWidget(build_step_api_keys(self))
        self._stack.addWidget(build_step_model(self))
        self._stack.addWidget(build_step_hotkey(self))
        self._stack.addWidget(build_step_ready(self))
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

    # ── Hotkey pill sync ────────────────────────────────────────────────────

    # ── Model download ──────────────────────────────────────────────────────

    def _start_download(self):
        self._download_btn.setEnabled(False)
        self._download_done = False
        self._download_error = ""
        model_size = self._model_combo.currentData() or "base.en"
        self._spinner_timer.start()
        self._download_status.setObjectName("StatusLabel")
        self._download_status.setText("⠋ Downloading…")
        t = threading.Thread(target=self._download_worker, args=(model_size,), daemon=True)
        t.start()

    def _auto_start_download(self):
        """Called automatically when the model step is shown.
        Starts the download without user clicking the button."""
        # Guard: don't re-download if already done or in progress
        if self._download_done or self._download_error:
            return
        if self._spinner_timer.isActive():
            return
        self._download_btn.setEnabled(False)
        self._download_done = False
        self._download_error = ""
        model_size = self._model_combo.currentData() or "base.en"
        self._spinner_timer.start()
        self._download_status.setObjectName("StatusLabel")
        self._download_status.setText("⠋ Downloading fallback model…")
        t = threading.Thread(target=self._download_worker, args=(model_size,), daemon=True)
        t.start()

    def _download_worker(self, model_size: str):
        """Runs in background thread — only emits a signal, never touches Qt widgets."""
        try:
            from faster_whisper import WhisperModel
            WhisperModel(model_size, device="cpu", compute_type="int8")
            self._download_result.emit(True, "")
        except Exception as exc:
            self._download_result.emit(False, str(exc)[:80])

    def _spin(self):
        if not self._download_done and not self._download_error and not self._closing:
            self._spinner_idx = (self._spinner_idx + 1) % len(self._spinner_chars)
            self._download_status.setText(f"{self._spinner_chars[self._spinner_idx]} Downloading…")

    def _download_finished(self, success: bool, error: str):
        self._spinner_timer.stop()
        if self._closing:
            return
        self._download_done = success
        self._download_error = error
        if error:
            self._download_status.setObjectName("StatusErr")
            self._download_status.setText(f"✕ {error}")
            self._download_btn.setEnabled(True)
        else:
            self._download_status.setObjectName("StatusOk")
            self._download_status.setText("✓ Model ready")
            self._download_btn.setText("Downloaded ✓")
        self._download_status.setStyleSheet("")   # force style refresh

    # ── Navigation ──────────────────────────────────────────────────────────

    def _collect_step_data(self, step: int):
        """In-memory only — no disk write, no registry touch."""
        if not self._config:
            return
        try:
            if step == 1:
                self._config.set("gemini_api_key", self._gemini_input.text().strip())
                self._config.set("groq_api_key",   self._groq_input.text().strip())
            elif step == 2:
                self._config.set("model_size", self._model_combo.currentData() or "base.en")
            elif step == 3:
                # Hotkey is already set by capture_hotkey() -> config.set("hotkey", ...)
                # Just ensure a fallback is present
                if not self._config.get("hotkey"):
                    self._config.set("hotkey", "tab")
        except Exception:
            pass   # never block navigation on a UI read error

    def _show_step(self, idx: int):
        self._step = idx
        self._stack.setCurrentIndex(idx)
        self._back_btn.setVisible(idx > 0)
        self._skip_btn.setVisible(idx < self._READY)
        self._next_btn.setText("Get Started" if idx == self._READY else "Next")
        if idx == self._READY:
            self._build_ready_summary()
        for i, dot in enumerate(self._dots):
            if i == idx:
                dot.setObjectName("DotActive")
                dot.setFixedSize(20, 6)
            else:
                dot.setObjectName("DotInactive")
                dot.setFixedSize(6, 6)
            dot.setStyleSheet("")

        # Auto-download model when reaching the model step (only if not already cached)
        if idx == self._MODEL and not self._download_done and not self._download_error:
            if not getattr(self, "_model_already_cached", False):
                QTimer.singleShot(300, self._auto_start_download)

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

    def _build_ready_summary(self):
        if not hasattr(self, "_ready_summary"):
            return
        lines = []
        try:
            from ui.pages._onboarding_steps import _hotkey_display_name
            hk_val = _hotkey_display_name(self._config.get("hotkey", "tab") or "tab")
            lines.append(f"● Hotkey: {hk_val}")
            mdl = getattr(self, "_model_combo", None)
            mdl_val = (mdl.currentData() if mdl else None) or self._config.get("model_size", "base.en")
            lines.append(f"● Model: {mdl_val}")
            gem = getattr(self, "_gemini_input", None)
            grq = getattr(self, "_groq_input",   None)
            has_gemini = bool(gem and gem.text().strip()) or bool(os.environ.get("GEMINI_API_KEY"))
            has_groq   = bool(grq and grq.text().strip()) or bool(os.environ.get("GROQ_API_KEY"))
            ai = []
            if has_gemini: ai.append("Gemini")
            if has_groq:   ai.append("Groq")
            lines.append("● Formatting: " + (", ".join(ai) if ai else "Not configured (add in Settings)"))
        except Exception:
            pass
        self._ready_summary.setText("\n".join(lines))

    def _finish(self):
        self._closing = True
        self._spinner_timer.stop()
        for s in range(self._TOTAL_STEPS):
            self._collect_step_data(s)
        if self._config:
            self._config.set("onboarding_complete", True)
            try:
                self._config.save()          # single disk write at the very end
            except Exception:
                pass
        self.accept()
        QTimer.singleShot(0, self.finished_signal.emit)

    # ── Window drag ─────────────────────────────────────────────────────────

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
