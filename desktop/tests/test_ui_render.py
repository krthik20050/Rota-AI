"""Tests for UI rendering stability — ensures all major UI widgets
instantiate, lay out, and render without crashes.

Tests cover:
  - MacOSSetupWizard (first-run dialog, check rows)
  - OnboardingDialog (wizard steps, navigation, model download)
  - PillOverlay (state transitions, animations, audio levels)
  - Toast (notification popup with click callback)
  - RotaTrayIcon (system tray menu creation)
  - DebugWindow (debug UI, state updates, text display)

Test strategy: verify construction, property defaults, state transitions,
and that styled widgets accept QSS without errors. No real display needed
since QWidget construction is independent of show().
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent

# ---------------------------------------------------------------------------
# Prevent Qt from crashing on headless CI
# ---------------------------------------------------------------------------

_QT_APP = None


def _ensure_app():
    global _QT_APP
    if _QT_APP is None:
        from PySide6.QtWidgets import QApplication

        _QT_APP = QApplication.instance() or QApplication([])
    return _QT_APP


def _cleanup_app():
    """Force-clean singleton so each test class can re-init if needed."""
    global _QT_APP
    _QT_APP = None


# ===================================================================
# 1 — macOS first-run wizard
# ===================================================================


class TestMacOSCheckRow:
    """_CheckRow widget — single row in the setup checklist."""

    def test_constructs_with_result(self):
        _ensure_app()
        from plat.macos_setup import CheckResult
        from ui.macos_first_run import _CheckRow

        result = CheckResult(
            key="portaudio",
            label="PortAudio",
            detail="Not found",
            ok=False,
            critical=True,
            can_install=True,
            needs_user=False,
        )
        row = _CheckRow(result)
        assert row.key == "portaudio"
        # Icon + name + detail + button should be visible
        assert row._icon is not None
        assert row._btn is not None
        assert row._btn.text() in ("Install",)

    def test_update_state_ok_hides_button(self):
        _ensure_app()
        from plat.macos_setup import CheckResult
        from ui.macos_first_run import _CheckRow

        row = _CheckRow(
            CheckResult(key="portaudio", label="P", detail="Ready", ok=True, critical=True, can_install=False, needs_user=False)
        )
        assert row._icon.text() == "✓"
        assert row._btn.isHidden()

    def test_update_state_failed_shows_action(self):
        _ensure_app()
        from plat.macos_setup import CheckResult
        from ui.macos_first_run import _CheckRow

        row = _CheckRow(
            CheckResult(key="pyobjc", label="PyObjC", detail="Missing", ok=False, critical=True, can_install=True, needs_user=False)
        )
        assert row._icon.text() == "●"
        # Use isHidden() instead of isVisible() — child widgets need a shown parent
        assert not row._btn.isHidden()
        assert row._btn.text() == "Install"

    def test_set_busy_and_error(self):
        _ensure_app()
        from plat.macos_setup import CheckResult
        from ui.macos_first_run import _CheckRow

        row = _CheckRow(
            CheckResult(key="portaudio", label="P", detail="Not found", ok=False, critical=True, can_install=True, needs_user=False)
        )
        row.set_busy()
        assert "⟳" in row._icon.text()
        assert not row._btn.isEnabled()

        row.set_error("Something broke")
        assert "✗" in row._icon.text()
        assert row._btn.isEnabled()
        assert "Retry" in row._btn.text()


class TestMacOSSetupWizard:
    """MacOSSetupWizard dialog — full checklist with polling."""

    def test_constructs_with_defaults(self):
        _ensure_app()
        from ui.macos_first_run import MacOSSetupWizard

        wizard = MacOSSetupWizard()
        assert wizard.windowTitle() == "Set Up Rota AI"
        assert wizard.isModal()
        assert wizard._poll_timer is not None
        assert wizard._poll_timer.interval() == 4000

    def test_skip_button_emits_done(self):
        _ensure_app()
        from ui.macos_first_run import MacOSSetupWizard

        wizard = MacOSSetupWizard()
        emitted = []

        def _done():
            emitted.append(True)

        wizard.setup_done.connect(_done)
        wizard._on_skip()
        assert len(emitted) == 1

    def test_close_event_cleanup(self):
        _ensure_app()
        from ui.macos_first_run import MacOSSetupWizard

        wizard = MacOSSetupWizard()
        assert wizard._poll_timer.isActive()
        emitted = []

        def _done():
            emitted.append(True)

        wizard.setup_done.connect(_done)

        # Use a real QCloseEvent — MagicMock fails PySide6 type checking
        event = QCloseEvent()
        wizard.closeEvent(event)
        assert not wizard._poll_timer.isActive()
        assert len(emitted) == 1


# ===================================================================
# 2 — Onboarding wizard
# ===================================================================


def _make_onboarding_config():
    """Create a MagicMock config that returns valid defaults for OnboardingDialog."""
    config = MagicMock()
    config.get.return_value = "base.en"  # model_size must not be None
    return config


class TestOnboardingDialog:
    """OnboardingDialog — multi-step setup wizard."""

    def test_constructs_with_defaults(self):
        _ensure_app()
        from ui.onboarding import OnboardingDialog

        dialog = OnboardingDialog(config=None)
        assert dialog._step == 0
        assert dialog._TOTAL_STEPS == 5
        assert not dialog._closing
        assert dialog._stack is not None

    def test_navigation_forward_and_back(self):
        _ensure_app()
        from ui.onboarding import OnboardingDialog

        config = _make_onboarding_config()
        dialog = OnboardingDialog(config=config)
        assert dialog._step == 0
        dialog._next()
        assert dialog._step == 1
        dialog._next()
        assert dialog._step == 2
        dialog._prev()
        assert dialog._step == 1

    def test_navigation_to_ready(self):
        _ensure_app()
        from ui.onboarding import OnboardingDialog

        config = _make_onboarding_config()
        dialog = OnboardingDialog(config=config)
        for _ in range(dialog._READY):
            dialog._next()
        assert dialog._step == dialog._READY

    def test_skip_button(self):
        _ensure_app()
        from PySide6.QtWidgets import QApplication

        from ui.onboarding import OnboardingDialog

        config = _make_onboarding_config()
        dialog = OnboardingDialog(config=config)
        emitted = []

        def _done():
            emitted.append(True)

        dialog.finished_signal.connect(_done)
        dialog._finish()
        # _finish() uses QTimer.singleShot(0, ...) — process events to fire it
        QApplication.processEvents()
        assert config.set.called
        assert config.save.called
        assert len(emitted) == 1

    @patch("ui.onboarding.os.environ", {"GEMINI_API_KEY": "fake-key"})
    def test_ready_summary_with_env_keys(self):
        _ensure_app()
        from ui.onboarding import OnboardingDialog

        config = _make_onboarding_config()
        dialog = OnboardingDialog(config=config)
        # Navigate to ready step
        for _ in range(dialog._READY):
            dialog._next()
        assert dialog._step == dialog._READY

    def test_mouse_drag_events(self):
        _ensure_app()
        from ui.onboarding import OnboardingDialog

        dialog = OnboardingDialog(config=None)
        from PySide6.QtCore import QPoint
        # Simulate mouse press + move (should not crash)
        event_press = MagicMock()
        event_press.button.return_value = Qt.MouseButton.LeftButton
        pos_mock = MagicMock()
        pos_mock.y.return_value = 10.0  # Within title bar (y < 42)
        event_press.position.return_value = pos_mock
        event_press.globalPosition.return_value.toPoint.return_value = QPoint(100, 100)
        dialog.mousePressEvent(event_press)
        event_move = MagicMock()
        event_move.buttons.return_value = Qt.MouseButton.LeftButton
        event_move.globalPosition.return_value.toPoint.return_value = QPoint(120, 120)
        dialog.mouseMoveEvent(event_move)
        # mouseMoveEvent updates _drag_pos to the new position for window dragging
        assert dialog._drag_pos == QPoint(120, 120)


# ===================================================================
# 3 — Pill overlay
# ===================================================================


class TestPillOverlay:
    """Floating pill overlay — state machine with animations."""

    def test_constructs_idle(self):
        _ensure_app()
        from ui.overlay.pill_overlay import PillOverlay
        from ui.overlay.pill_state import PillState

        pill = PillOverlay()
        assert pill.get_state() == PillState.IDLE
        assert pill._entry_scale == 1.0
        assert pill._exit_scale == 1.0
        assert pill._waveform.isHidden()

    def test_state_transition_recording(self):
        _ensure_app()
        from ui.overlay.pill_overlay import PillOverlay
        from ui.overlay.pill_state import PillState

        pill = PillOverlay()
        pill.set_state(PillState.RECORDING)
        assert pill.get_state() == PillState.RECORDING
        # Use isHidden() — child widget visibility requires a shown parent
        assert not pill._waveform.isHidden()
        assert pill._waveform._active is True
        # Mouse events should be enabled during recording
        assert not pill.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def test_state_transition_transcribing(self):
        _ensure_app()
        from ui.overlay.pill_overlay import PillOverlay
        from ui.overlay.pill_state import PillState

        pill = PillOverlay()
        pill.set_state(PillState.RECORDING)
        pill._audio_level = 0.5
        pill.set_state(PillState.TRANSCRIBING)
        assert pill.get_state() == PillState.TRANSCRIBING
        # Mouse events should be disabled after recording
        assert pill.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def test_state_transition_done(self):
        _ensure_app()
        from ui.overlay.pill_overlay import PillOverlay
        from ui.overlay.pill_state import PillState

        pill = PillOverlay()
        pill.set_state(PillState.RECORDING)
        pill.set_state(PillState.TRANSCRIBING)
        pill.set_state(PillState.DONE)
        assert pill.get_state() == PillState.DONE
        assert pill._waveform.isHidden()
        # Done timer should auto-return to idle
        assert pill._done_timer.isActive()
        assert pill._done_timer.remainingTime() > 0

    def test_audio_level_smoothing(self):
        _ensure_app()
        from ui.overlay.pill_overlay import PillOverlay

        pill = PillOverlay()
        pill.on_audio_level(0.0)
        assert pill._audio_level == 0.0
        pill.on_audio_level(1.0)
        # Smoothed: 0.0*0.6 + min(1.0, 1.0*18.0)*0.4 = 0.0 + 0.4 = 0.4
        assert pill._audio_level == 0.4
        # Waveform should update
        assert pill._waveform._audio_level == 0.4

    def test_set_partial_text(self):
        _ensure_app()
        from ui.overlay.pill_overlay import PillOverlay

        pill = PillOverlay()
        pill.set_partial_text("Hello world")
        assert pill._partial_text == "Hello world"

    def test_show_error(self):
        _ensure_app()
        from ui.overlay.pill_overlay import PillOverlay
        from ui.overlay.pill_state import PillState

        pill = PillOverlay()
        pill.show_error("Something went wrong")
        assert pill.get_state() == PillState.ERROR
        assert "Something went wrong" in pill._truncated_partial_text()

    @patch("ui.overlay.pill_overlay.play_haptic")
    def test_show_success_triggers_haptic(self, mock_haptic):
        _ensure_app()
        from ui.overlay.pill_overlay import PillOverlay

        pill = PillOverlay()
        pill.show_success("Done!")
        mock_haptic.assert_called_with("done")

    def test_cancel_and_stop_signals(self):
        _ensure_app()
        from ui.overlay.pill_overlay import PillOverlay
        from ui.overlay.pill_state import PillState

        pill = PillOverlay()
        cancel_fired = []
        stop_fired = []

        pill.cancel_requested.connect(lambda: cancel_fired.append(True))
        pill.stop_requested.connect(lambda: stop_fired.append(True))

        pill.set_state(PillState.RECORDING)

        # Simulate click in cancel zone (left)
        from unittest.mock import MagicMock
        event = MagicMock()
        event.position.return_value.x.return_value = 5
        pill.mousePressEvent(event)
        assert len(cancel_fired) == 1

        # Simulate click in stop zone (right)
        event2 = MagicMock()
        event2.position.return_value.x.return_value = pill.width() - 5
        pill.mousePressEvent(event2)
        assert len(stop_fired) == 1


# ===================================================================
# 4 — Toast notification
# ===================================================================


class TestToast:
    """Toast overlay notification."""

    def test_constructs(self):
        _ensure_app()
        from ui.toast import Toast

        toast = Toast("Hello world", duration_ms=5000)
        assert toast._message == "Hello world"
        assert not toast._warning

    def test_constructs_warning(self):
        _ensure_app()
        from ui.toast import Toast

        toast = Toast("Warning", warning=True, duration_ms=5000)
        assert toast._warning
        assert toast._message == "Warning"

    def test_on_click_callback(self):
        _ensure_app()
        from ui.toast import Toast

        clicked = []

        def _on_click():
            clicked.append(True)

        toast = Toast("Click me", on_click=_on_click, duration_ms=5000)
        from unittest.mock import MagicMock
        event = MagicMock()
        toast.mousePressEvent(event)
        assert len(clicked) == 1

    def test_timer_closes(self):
        _ensure_app()
        from PySide6.QtWidgets import QApplication

        from ui.toast import Toast

        toast = Toast("Auto close", duration_ms=100)
        toast.show()  # Toast must be shown before isVisible() returns True
        assert toast.isVisible()
        # Process Qt events so the QTimer.singleShot(100, close) actually fires
        import time
        deadline = time.monotonic() + 3.0
        while toast.isVisible() and time.monotonic() < deadline:
            QApplication.processEvents()
        assert not toast.isVisible()


# ===================================================================
# 5 — System tray icon
# ===================================================================


# ===================================================================
# 5 — Backend fallback toast classification
# ===================================================================


class TestBackendFallbackToasts:
    """Tests for _maybe_notify_backend_fallback error message classification.

    Tests that each error category produces the correct toast message
    without making network calls or needing a full application instance.
    """

    @staticmethod
    def _make_mock_app():
        """Create a mock that can receive the mixin method bound to it."""
        from unittest.mock import MagicMock

        app = MagicMock()
        app.transcriber = MagicMock()
        return app

    def _bind_method(self, app):
        """Bind _maybe_notify_backend_fallback to the mock app."""
        import types

        from app.processing_pipeline_mixin import ProcessingPipelineMixin

        app._maybe_notify_backend_fallback = types.MethodType(
            ProcessingPipelineMixin._maybe_notify_backend_fallback, app
        )
        return app

    def test_no_transcriber_skips(self):
        app = self._make_mock_app()
        app.transcriber = None
        self._bind_method(app)
        app._maybe_notify_backend_fallback()
        app.show_toast.assert_not_called()

    def test_no_event_skips(self):
        app = self._make_mock_app()
        app.transcriber.consume_backend_event.return_value = ("", "")
        self._bind_method(app)
        app._maybe_notify_backend_fallback()
        app.show_toast.assert_not_called()

    def test_non_local_backend_ignored(self):
        app = self._make_mock_app()
        app.transcriber.consume_backend_event.return_value = ("groq", "all good")
        self._bind_method(app)
        app._maybe_notify_backend_fallback()
        app.show_toast.assert_not_called()

    def test_latency_fallback(self):
        app = self._make_mock_app()
        self._bind_method(app)
        app.transcriber.consume_backend_event.return_value = ("local", "latency=4.2")
        app._maybe_notify_backend_fallback()
        app.show_toast.assert_called_once()
        msg = app.show_toast.call_args[0][0]
        assert "slow" in msg.lower()

    def test_rate_limit_detected(self):
        app = self._make_mock_app()
        self._bind_method(app)
        for reason in ["429 Too Many Requests", "rate limit hit", "quota exceeded", "too many requests from this"]:
            app.transcriber.consume_backend_event.return_value = ("local", reason)
            app.show_toast.reset_mock()
            app._maybe_notify_backend_fallback()
            app.show_toast.assert_called_once()
            msg = app.show_toast.call_args[0][0]
            assert any(t in msg.lower() for t in ("rate limit", "too many", "quota")), f"Failed for reason: {reason}"

    def test_invalid_key_detected(self):
        app = self._make_mock_app()
        self._bind_method(app)
        for reason in ["401 Unauthorized", "unauthorized", "invalid api key"]:
            app.transcriber.consume_backend_event.return_value = ("local", reason)
            app.show_toast.reset_mock()
            app._maybe_notify_backend_fallback()
            app.show_toast.assert_called_once()
            msg = app.show_toast.call_args[0][0]
            assert any(t in msg.lower() for t in ("invalid", "unauthorized")), f"Failed for reason: {reason}"

    def test_invalid_key_shows_warning(self):
        app = self._make_mock_app()
        self._bind_method(app)
        app.transcriber.consume_backend_event.return_value = ("local", "invalid key")
        app._maybe_notify_backend_fallback()
        kwargs = app.show_toast.call_args[1]
        assert kwargs.get("warning") is True

    def test_timeout_detected(self):
        app = self._make_mock_app()
        self._bind_method(app)
        for reason in ["timeout error", "connection timed out"]:
            app.transcriber.consume_backend_event.return_value = ("local", reason)
            app.show_toast.reset_mock()
            app._maybe_notify_backend_fallback()
            app.show_toast.assert_called_once()
            msg = app.show_toast.call_args[0][0]
            assert "time" in msg.lower()

    def test_generic_fallback(self):
        app = self._make_mock_app()
        self._bind_method(app)
        app.transcriber.consume_backend_event.return_value = ("local", "some unknown error occurred")
        app._maybe_notify_backend_fallback()
        app.show_toast.assert_called_once()
        msg = app.show_toast.call_args[0][0]
        assert "unavailable" in msg.lower()


# ===================================================================
# 6 — System tray icon
# ===================================================================


class TestRotaTrayIcon:
    """System tray icon with dark context menu."""

    def test_constructs(self):
        _ensure_app()
        from ui.tray import RotaTrayIcon

        tray = RotaTrayIcon()
        assert tray.menu is not None
        assert tray.open_action is not None
        assert tray.settings_action is not None
        assert tray.mode_action is not None
        assert tray.ai_action is not None
        assert tray.report_action is not None
        assert tray.exit_action is not None
        assert tray.toolTip() == "Rota: Ready"

    def test_update_status(self):
        _ensure_app()
        from ui.tray import RotaTrayIcon

        tray = RotaTrayIcon()
        tray.update_status("hold", True)
        assert "Hold to Record" in tray.mode_action.text()
        assert "ON" in tray.ai_action.text()

        tray.update_status("toggle", False)
        assert "Toggle Mode" in tray.mode_action.text()
        assert "OFF" in tray.ai_action.text()

    def test_update_runtime_state(self):
        _ensure_app()
        from ui.tray import RotaTrayIcon

        tray = RotaTrayIcon()
        tray.update_runtime_state("LISTENING")
        assert "Recording" in tray.toolTip()
        tray.update_runtime_state("PROCESSING")
        assert "Processing" in tray.toolTip()
        tray.update_runtime_state("ERROR")
        assert "Error" in tray.toolTip()
        tray.update_runtime_state("IDLE")
        assert "Ready" in tray.toolTip()


# ===================================================================
# 6 — Debug window
# ===================================================================


class TestDebugWindow:
    """Minimal dark debug UI with live state display."""

    def test_constructs(self):
        _ensure_app()
        from ui.debug_window import DebugWindow

        win = DebugWindow(on_start_clicked=lambda: None, on_stop_clicked=lambda: None)
        assert win.windowTitle() == "Rota Debug"
        assert "IDLE" in win.state_label.text()

    def test_update_state(self):
        _ensure_app()
        from ui.debug_window import DebugWindow

        win = DebugWindow(on_start_clicked=lambda: None, on_stop_clicked=lambda: None)
        win.update_state("LISTENING", "sess-123")
        assert "LISTENING" in win.state_label.text()
        assert "sess-123" in win.session_label.text()

    def test_update_text_results(self):
        _ensure_app()
        from ui.debug_window import DebugWindow

        win = DebugWindow(on_start_clicked=lambda: None, on_stop_clicked=lambda: None)
        win.update_text_results("hello world", "Hello World")
        assert win.raw_text.toPlainText() == "hello world"
        assert win.cleaned_text.toPlainText() == "Hello World"

    def test_update_timings(self):
        _ensure_app()
        from ui.debug_window import DebugWindow

        win = DebugWindow(on_start_clicked=lambda: None, on_stop_clicked=lambda: None)
        win.update_timings({"audio_ms": 1200, "transcribe_ms": 3400})
        assert "audio_ms" in win.timings_text.toPlainText()

    def test_update_timings_none(self):
        _ensure_app()
        from ui.debug_window import DebugWindow

        win = DebugWindow(on_start_clicked=lambda: None, on_stop_clicked=lambda: None)
        win.update_timings({})
        assert "No timings yet" in win.timings_text.toPlainText()

    def test_update_logs(self):
        _ensure_app()
        from ui.debug_window import DebugWindow

        win = DebugWindow(on_start_clicked=lambda: None, on_stop_clicked=lambda: None)
        win.update_logs(["line1", "line2"])
        assert "line1\nline2" in win.logs_text.toPlainText()

    def test_buttons_connected(self):
        _ensure_app()
        from ui.debug_window import DebugWindow

        start_calls = []
        stop_calls = []

        def _start():
            start_calls.append(True)

        def _stop():
            stop_calls.append(True)

        win = DebugWindow(on_start_clicked=_start, on_stop_clicked=_stop)
        win.start_button.click()
        assert len(start_calls) == 1
        win.stop_button.click()
        assert len(stop_calls) == 1
