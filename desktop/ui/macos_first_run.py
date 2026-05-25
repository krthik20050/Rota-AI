"""
macOS first-run setup wizard.

Shows a checklist of required dependencies and permissions.
Auto-installs what it can (PortAudio, pyobjc) and guides the user
to grant Accessibility / Input Monitoring permissions.

Usage:
    wizard = MacOSSetupWizard()
    wizard.setup_done.connect(on_setup_complete)
    wizard.show()
"""

from __future__ import annotations

import threading

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from plat.macos_setup import (
    CheckResult,
    install_portaudio,
    install_pyobjc,
    mark_setup_done,
    open_accessibility_settings,
    open_input_monitoring_settings,
    run_checks,
)

# ---------------------------------------------------------------------------
# Single checklist row
# ---------------------------------------------------------------------------


class _CheckRow(QWidget):
    """One row: status icon | label + detail | action button."""

    install_clicked = pyqtSignal(str)  # emits key
    open_settings_clicked = pyqtSignal(str)  # emits key

    def __init__(self, result: CheckResult, parent: QWidget | None = None):
        super().__init__(parent)
        self.key = result.key
        self._build()
        self.update_state(result)

    def _build(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(12)

        self._icon = QLabel()
        self._icon.setFixedWidth(20)
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        self._name = QLabel()
        self._name.setFont(QFont("", 13, QFont.Weight.Medium))
        self._detail = QLabel()
        self._detail.setWordWrap(True)
        text_col.addWidget(self._name)
        text_col.addWidget(self._detail)

        self._btn = QPushButton()
        self._btn.setFixedSize(120, 30)
        self._btn.clicked.connect(self._on_btn_clicked)

        layout.addWidget(self._icon)
        layout.addLayout(text_col, stretch=1)
        layout.addWidget(self._btn, alignment=Qt.AlignmentFlag.AlignVCenter)

    def update_state(self, result: CheckResult) -> None:
        self.key = result.key
        self._name.setText(result.label)
        self._detail.setText(result.detail)

        if result.ok:
            self._icon.setText("✓")
            self._icon.setStyleSheet("color: #4CAF50; font-size: 15px; font-weight: bold;")
            self._detail.setStyleSheet("color: #4CAF50; font-size: 12px;")
            self._btn.hide()
        else:
            self._icon.setText("●")
            self._icon.setStyleSheet("color: #E57373; font-size: 11px;")
            self._detail.setStyleSheet("color: #999; font-size: 12px;")
            if result.can_install:
                self._btn.setText("Install")
                self._btn.show()
            elif result.needs_user:
                self._btn.setText("Open Settings")
                self._btn.show()
            else:
                self._btn.hide()
            self._btn.setEnabled(True)

    def set_busy(self) -> None:
        self._icon.setText("⟳")
        self._icon.setStyleSheet("color: #FFA726; font-size: 14px;")
        self._detail.setText("Installing — this may take a few minutes…")
        self._detail.setStyleSheet("color: #FFA726; font-size: 12px;")
        self._btn.setText("Installing…")
        self._btn.setEnabled(False)

    def set_error(self, message: str) -> None:
        self._icon.setText("✗")
        self._icon.setStyleSheet("color: #EF5350; font-size: 14px;")
        self._detail.setText(f"Failed — {message[:120]}")
        self._detail.setStyleSheet("color: #EF5350; font-size: 12px;")
        self._btn.setText("Retry")
        self._btn.setEnabled(True)

    def _on_btn_clicked(self) -> None:
        text = self._btn.text()
        if text in ("Install", "Retry"):
            self.install_clicked.emit(self.key)
        elif text == "Open Settings":
            self.open_settings_clicked.emit(self.key)


# ---------------------------------------------------------------------------
# Main wizard dialog
# ---------------------------------------------------------------------------


class MacOSSetupWizard(QDialog):
    """
    First-run setup wizard for macOS.
    Emits setup_done when the user clicks Continue or Skip.
    """

    setup_done = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Set Up Rota AI")
        self.setFixedWidth(520)
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)

        self._rows: dict[str, _CheckRow] = {}
        self._results: dict[str, CheckResult] = {}

        self._build_ui()

        # Initial check after a short delay so the window renders first
        QTimer.singleShot(200, self._run_checks)

        # Re-check every 4 seconds — picks up permission grants made in System Settings
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._run_checks)
        self._poll_timer.start(4000)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 20)
        root.setSpacing(0)

        # Header
        title = QLabel("Set Up Rota AI")
        title.setFont(QFont("", 18, QFont.Weight.Bold))
        root.addWidget(title)
        root.addSpacing(6)

        subtitle = QLabel(
            "We'll install what's needed so Rota works out of the box.\n"
            "Some steps require a moment of your time to grant permissions."
        )
        subtitle.setStyleSheet("color: #888; font-size: 13px;")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)
        root.addSpacing(18)

        _divider(root, "#333")
        root.addSpacing(4)

        # Placeholder rows — populated by _apply_results
        self._rows_container = QWidget()
        self._rows_layout = QVBoxLayout(self._rows_container)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(0)

        # Loading placeholder
        self._loading_label = QLabel("Checking your system…")
        self._loading_label.setStyleSheet("color: #888; margin: 16px 0;")
        self._rows_layout.addWidget(self._loading_label)

        root.addWidget(self._rows_container)
        root.addSpacing(4)
        _divider(root, "#333")
        root.addSpacing(10)

        # Status line
        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: #888; font-size: 12px;")
        self._status_label.setWordWrap(True)
        root.addWidget(self._status_label)
        root.addSpacing(12)

        # Buttons
        btn_row = QHBoxLayout()
        self._skip_btn = QPushButton("Skip for now")
        self._skip_btn.setFlat(True)
        self._skip_btn.setStyleSheet(
            "QPushButton { color: #888; border: none; font-size: 12px; }"
            "QPushButton:hover { color: #aaa; }"
        )
        self._skip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._skip_btn.clicked.connect(self._on_skip)

        self._continue_btn = QPushButton("Continue →")
        self._continue_btn.setFixedHeight(36)
        self._continue_btn.setMinimumWidth(120)
        self._continue_btn.setEnabled(False)
        self._continue_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._continue_btn.setStyleSheet(
            "QPushButton {"
            "  background: #4CAF50; color: white; border-radius: 6px;"
            "  font-size: 13px; font-weight: bold; border: none;"
            "}"
            "QPushButton:hover { background: #43A047; }"
            "QPushButton:disabled { background: #3a3a3a; color: #666; }"
        )
        self._continue_btn.clicked.connect(self._on_continue)

        btn_row.addWidget(self._skip_btn)
        btn_row.addStretch()
        btn_row.addWidget(self._continue_btn)
        root.addLayout(btn_row)

    # ------------------------------------------------------------------
    # Check logic
    # ------------------------------------------------------------------

    def _run_checks(self) -> None:
        """Run all checks in a daemon thread, apply results on the Qt thread."""

        def _worker():
            results = run_checks()
            QTimer.singleShot(0, lambda: self._apply_results(results))

        threading.Thread(target=_worker, daemon=True).start()

    def _apply_results(self, results: list[CheckResult]) -> None:
        first_time = not self._rows

        if first_time:
            # Remove loading placeholder
            self._loading_label.setVisible(False)

        for result in results:
            self._results[result.key] = result

            if result.key not in self._rows:
                row = _CheckRow(result)
                row.install_clicked.connect(self._on_install)
                row.open_settings_clicked.connect(self._on_open_settings)
                self._rows[result.key] = row
                self._rows_layout.addWidget(row)
                # Thin separator between rows
                sep = QLabel()
                sep.setFixedHeight(1)
                sep.setStyleSheet("background: #2a2a2a; margin-left: 32px;")
                self._rows_layout.addWidget(sep)
            else:
                self._rows[result.key].update_state(result)

        self._refresh_continue_state()
        self.adjustSize()

    def _refresh_continue_state(self) -> None:
        critical_all_ok = all(r.ok for r in self._results.values() if r.critical)

        if critical_all_ok:
            self._continue_btn.setEnabled(True)
            self._status_label.setText("All required items are ready — you're good to go!")
            self._status_label.setStyleSheet("color: #4CAF50; font-size: 12px;")
        else:
            self._continue_btn.setEnabled(False)
            pending = [r.label for r in self._results.values() if r.critical and not r.ok]
            self._status_label.setText(f"Still needed: {', '.join(pending)}")
            self._status_label.setStyleSheet("color: #888; font-size: 12px;")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _on_install(self, key: str) -> None:
        row = self._rows.get(key)
        if row is None:
            return
        row.set_busy()
        # Pause polling while install is in progress
        self._poll_timer.stop()

        if key == "portaudio":
            fn = install_portaudio
        elif key == "pyobjc":
            fn = install_pyobjc
        else:
            return

        def _worker():
            ok, msg = fn()
            QTimer.singleShot(0, lambda: self._on_install_done(key, ok, msg))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_install_done(self, key: str, ok: bool, msg: str) -> None:
        row = self._rows.get(key)
        if not ok:
            if row:
                row.set_error(msg)
            self._status_label.setText(f"Install failed — {msg[:100]}")
            self._status_label.setStyleSheet("color: #E57373; font-size: 12px;")
        # Resume polling and re-check
        self._poll_timer.start(4000)
        self._run_checks()

    def _on_open_settings(self, key: str) -> None:
        if key == "accessibility":
            open_accessibility_settings()
            self._status_label.setText(
                "System Settings opened → Privacy & Security → Accessibility. "
                "Add Rota AI and toggle it on, then come back here."
            )
            self._status_label.setStyleSheet("color: #FFA726; font-size: 12px;")
        elif key == "input_monitoring":
            open_input_monitoring_settings()
            self._status_label.setText(
                "System Settings opened → Privacy & Security → Input Monitoring. "
                "Add Rota AI and toggle it on."
            )
            self._status_label.setStyleSheet("color: #FFA726; font-size: 12px;")

    def _on_continue(self) -> None:
        self._cleanup()
        mark_setup_done()
        self.setup_done.emit()
        self.accept()

    def _on_skip(self) -> None:
        self._cleanup()
        self.setup_done.emit()
        self.accept()

    def _cleanup(self) -> None:
        self._poll_timer.stop()

    def closeEvent(self, event):
        self._cleanup()
        self.setup_done.emit()
        super().closeEvent(event)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _divider(layout: QVBoxLayout, color: str) -> None:
    line = QLabel()
    line.setFixedHeight(1)
    line.setStyleSheet(f"background: {color};")
    layout.addWidget(line)
