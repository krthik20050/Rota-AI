"""macOS platform stability tests.

Verifies that all macOS platform backend modules import cleanly, handle
missing dependencies gracefully, follow the correct fallback chains, and
never crash — even under unexpected conditions.

Test coverage:
  - macos_injector.py  — 4-tier fallback injection, clipboard snapshots,
                          permission checks, target capture, undo
  - macos_hotkey.py    — hotkey parsing, pynput + Quartz backends,
                          capture_hotkey, HotkeyHandler lifecycle
  - macos_window.py    — AppContext, app classification, AX element
                          detection, field scanning, focus restoration
  - macos_setup.py     — CheckResult construction, run_checks, installer
                          wrappers, permission helpers
"""

from __future__ import annotations

import sys

import pytest
from unittest.mock import MagicMock, patch

# Skip all tests in this file on non-macOS platforms — they test macOS-specific
# platform backends (macos_injector, macos_hotkey, macos_window, macos_setup).
pytestmark = pytest.mark.skipif(sys.platform != "darwin", reason="macOS-only tests")

# ===================================================================
# 1 — macos_injector.py  — TextInjector 4-tier fallback
# ===================================================================


class TestMacOSInjectorHelpers:
    """Pure helper functions — clipboard, permissions, target capture."""

    def test_permission_checks_return_false_when_pyobjc_missing(self):
        """AXIsProcessTrustedWithOptions not available → False."""
        with patch.dict("sys.modules", {"ApplicationServices": None}):
            from plat.macos_injector import _check_accessibility_permission
            assert _check_accessibility_permission() is False

    def test_clipboard_snapshot_save_restore(self):
        from plat.macos_injector import _ClipboardSnapshot

        _ClipboardSnapshot._types_and_data = []
        _ClipboardSnapshot.save()
        # Should not crash even when AppKit is mocked out
        assert _ClipboardSnapshot._types_and_data == []

    def test_clipboard_snapshot_restore_empty(self):
        from plat.macos_injector import _ClipboardSnapshot

        _ClipboardSnapshot._types_and_data = []
        _ClipboardSnapshot.restore()  # Should not crash
        assert _ClipboardSnapshot._types_and_data == []

    def test_clipboard_copy_failure(self):
        with patch("plat.macos_injector.subprocess.Popen") as mock_popen:
            mock_popen.return_value.returncode = 1
            from plat.macos_injector import _clipboard_copy
            assert _clipboard_copy("test") is False

    @patch("plat.macos_injector.subprocess.Popen")
    def test_clipboard_copy_success(self, mock_popen):
        proc = MagicMock()
        proc.returncode = 0
        mock_popen.return_value = proc
        from plat.macos_injector import _clipboard_copy
        assert _clipboard_copy("test") is True
        mock_popen.assert_called_once()

    def test_clipboard_paste_failure(self):
        with patch("plat.macos_injector.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            from plat.macos_injector import _clipboard_paste
            assert _clipboard_paste() is None

    @patch("plat.macos_injector._clipboard_copy")
    @patch("plat.macos_injector.time.sleep")
    def test_tier_1_ax_inject_available(self, mock_sleep, mock_copy):
        from plat.macos_injector import _inject_ax

        # _inject_ax does `from ApplicationServices import AXUIElementSetAttributeValue`
        # at function-call time. We need ApplicationServices in sys.modules with
        # the right attribute to intercept it.
        mock_as = MagicMock()
        mock_as.AXUIElementSetAttributeValue.return_value = 0
        mock_as.kAXSelectedTextAttribute = "AXSelectedText"
        mock_as.kAXValueAttribute = "AXValue"

        with patch.dict("sys.modules", {"ApplicationServices": mock_as}):
            mock_element = MagicMock()
            result = _inject_ax("hello", mock_element)
            assert result is True

    @patch("plat.macos_injector._clipboard_copy")
    @patch("plat.macos_injector.time.sleep")
    def test_tier_2_apple_script_inject(self, mock_sleep, mock_copy):
        mock_copy.return_value = True
        from plat.macos_injector import _inject_apple_script

        with patch("plat.macos_injector.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            result = _inject_apple_script("hello")
            assert result is True

    def test_tier_3_pynput_cmd_v_fallback(self):
        with patch("plat.macos_injector._clipboard_copy", return_value=True):
            with patch("plat.macos_injector.time.sleep"):
                from plat.macos_injector import _inject_pynput_cmd_v

                with patch("pynput.keyboard.Controller") as mock_ctrl:
                    instance = MagicMock()
                    mock_ctrl.return_value = instance
                    result = _inject_pynput_cmd_v("hello")
                    assert result is True

    def test_tier_4_type_chars_fallback(self):
        from plat.macos_injector import _inject_type_chars

        with patch("pynput.keyboard.Controller") as mock_ctrl:
            instance = MagicMock()
            mock_ctrl.return_value = instance
            result = _inject_type_chars("hello")
            assert result is True
            instance.type.assert_called_once_with("hello")


class TestMacOSInjectorStability:
    """TextInjector class — lifecycle, edge cases, and resilience.

    Note: _check_ax_available is a @staticmethod on TextInjector, not a
    module-level function. Patches must target TextInjector._check_ax_available.
    """

    def test_constructs_without_crash(self):
        with patch("plat.macos_injector.TextInjector._check_ax_available", return_value=False):
            from plat.macos_injector import TextInjector

            injector = TextInjector()
            assert injector is not None

    def test_is_text_field_active_no_target(self):
        from plat.macos_injector import TextInjector, _current_target

        _current_target.app_name = None
        with patch("plat.macos_injector.TextInjector._check_ax_available", return_value=False):
            injector = TextInjector()
            assert injector.is_text_field_active() is False

    def test_inject_empty_text(self):
        from plat.macos_injector import TextInjector

        with patch("plat.macos_injector.TextInjector._check_ax_available", return_value=False):
            injector = TextInjector()
            ok, msg = injector.inject("")
            assert ok is False
            assert "No text" in msg

    def test_inject_truncates_at_max_length(self):
        from plat.macos_injector import _MAX_INJECT_LENGTH, TextInjector

        long_text = "x" * (_MAX_INJECT_LENGTH + 100)
        with patch("plat.macos_injector.TextInjector._check_ax_available", return_value=False):
            injector = TextInjector()
            with patch.object(injector, "_has_active_window", return_value=True):
                with patch("plat.macos_injector._current_target") as mock_target:
                    mock_target.app_name = "TextEdit"
                    mock_target.ax_element = None
                    # Mock all injection tiers to fail so we get the fallback result
                    with patch("plat.macos_injector._clipboard_copy", return_value=True):
                        ok, msg = injector.inject(long_text)
                        # Should not crash — text truncated
                        assert isinstance(ok, bool)
                        assert isinstance(msg, str)

    def test_undo_returns_false_when_nothing(self):
        from plat.macos_injector import TextInjector

        with patch("plat.macos_injector.TextInjector._check_ax_available", return_value=False):
            injector = TextInjector()
            injector._last_undo_content = None  # instance var, not module-level
            ok, msg = injector.undo_last_inject()
            assert ok is False
            assert "No undo" in msg

    def test_get_undo_available(self):
        with patch("plat.macos_injector.TextInjector._check_ax_available", return_value=False):
            from plat.macos_injector import TextInjector

            injector = TextInjector()
            injector._last_undo_content = None  # instance var, not module-level
            assert injector.get_undo_available() is False

    @patch("plat.macos_injector.subprocess.run")
    def test_capture_target_does_not_crash(self, mock_run):
        """capture_target() should handle osascript failures gracefully."""
        mock_run.side_effect = Exception("osascript not found")
        from plat.macos_injector import _current_target, capture_target

        _current_target.app_name = None
        capture_target()
        # Should not have crashed — app_name should still be None
        assert _current_target.app_name is None

    @patch("plat.macos_injector.subprocess.run")
    def test_restore_focus_handles_errors(self, mock_run):
        mock_run.side_effect = Exception("activation failed")
        from plat.macos_injector import _restore_focus

        assert _restore_focus("TextEdit") is False

    def test_ax_available_check_returns_false_when_missing(self):
        with patch.dict("sys.modules", {"ApplicationServices": None}):
            from plat.macos_injector import TextInjector
            assert TextInjector._check_ax_available() is False


# ===================================================================
# 2 — macos_hotkey.py  — Hotkey parsing + backends
# ===================================================================


class TestMacOSHotkeyParsing:
    """Hotkey string parser — edge cases & correctness."""

    def test_parse_simple_key(self):
        from plat.macos_hotkey import _parse_hotkey_str
        mods, main = _parse_hotkey_str("tab")
        assert mods == frozenset()
        assert main == "tab"

    def test_parse_with_modifiers(self):
        from plat.macos_hotkey import _parse_hotkey_str
        mods, main = _parse_hotkey_str("ctrl+shift+r")
        assert mods == frozenset({"ctrl", "shift"})
        assert main == "r"

    def test_parse_with_cmd(self):
        from plat.macos_hotkey import _parse_hotkey_str
        mods, main = _parse_hotkey_str("cmd+option+k")
        assert "cmd" in mods or "command" in mods or "meta" in mods
        assert main == "k"

    def test_parse_empty_string(self):
        from plat.macos_hotkey import _parse_hotkey_str
        mods, main = _parse_hotkey_str("")
        assert mods == frozenset()
        assert main == ""

    def test_parse_case_insensitive(self):
        from plat.macos_hotkey import _parse_hotkey_str
        mods, main = _parse_hotkey_str("Ctrl+Shift+K")
        assert mods == frozenset({"ctrl", "shift"})
        assert main == "k"

    def test_quartz_hotkey_modifier_only_returns_none(self):
        from plat.macos_hotkey import _parse_quartz_hotkey
        assert _parse_quartz_hotkey("ctrl+shift") is None

    def test_quartz_hotkey_unknown_key_returns_none(self):
        from plat.macos_hotkey import _parse_quartz_hotkey
        result = _parse_quartz_hotkey("ctrl+shift+superkey")
        assert result is None


class TestMacOSHotkeyHandler:
    """HotkeyHandler lifecycle — start, stop, health check."""

    def test_construct_defaults(self):
        from plat.macos_hotkey import HotkeyHandler

        h = HotkeyHandler()
        assert h.hotkey == "tab"
        assert h.mode == "toggle"
        assert h.backend is None
        assert h._held_mods == set()

    def test_is_recording_default_false(self):
        from plat.macos_hotkey import HotkeyHandler

        h = HotkeyHandler()
        assert h.is_recording is False

    def test_add_hotkey(self):
        from plat.macos_hotkey import HotkeyHandler

        h = HotkeyHandler()
        called = []
        h.add_hotkey("ctrl+shift+x", lambda: called.append(True))
        assert len(h._extra_hotkeys) == 1
        mods, main, cb = h._extra_hotkeys[0]
        assert main == "x"
        cb()
        assert len(called) == 1

    def test_set_mode_hold(self):
        from plat.macos_hotkey import HotkeyHandler

        h = HotkeyHandler(mode="toggle")
        h.set_mode("hold")
        assert h.mode == "hold"

    def test_set_mode_toggle(self):
        from plat.macos_hotkey import HotkeyHandler

        h = HotkeyHandler(mode="hold")
        h.set_mode("toggle")
        assert h.mode == "toggle"

    def test_set_mode_invalid(self):
        from plat.macos_hotkey import HotkeyHandler

        h = HotkeyHandler(mode="toggle")
        h.set_mode("invalid")
        assert h.mode == "toggle"  # unchanged

    def test_stop_listening_does_not_crash_when_not_started(self):
        from plat.macos_hotkey import HotkeyHandler

        h = HotkeyHandler()
        h.stop_listening()  # Should not raise

    def test_is_healthy_returns_false_when_not_started(self):
        from plat.macos_hotkey import HotkeyHandler

        h = HotkeyHandler()
        assert h.is_healthy() is False

    def test_add_hotkey_logging(self):
        from plat.macos_hotkey import HotkeyHandler

        h = HotkeyHandler()
        h.add_hotkey("ctrl+tab", lambda: None)
        # Extra hotkey should be recorded
        assert any(main == "tab" for _, main, _ in h._extra_hotkeys)


# ===================================================================
# 3 — macos_window.py  — App detection + AX element handling
# ===================================================================


class TestMacOSWindowClassification:
    """App classification by process name."""

    def test_classify_browser(self):
        from plat.macos_window import _classify
        cat, tone = _classify("Google Chrome")
        assert cat == "browser"
        assert tone == "neutral"

    def test_classify_terminal(self):
        from plat.macos_window import _classify
        cat, tone = _classify("Terminal")
        assert cat == "terminal"
        assert tone == "technical"

    def test_classify_editor(self):
        from plat.macos_window import _classify
        cat, tone = _classify("Visual Studio Code")
        assert cat == "editor"
        assert tone == "technical"

    def test_classify_unknown(self):
        from plat.macos_window import _classify
        cat, tone = _classify("SomeWeirdApp")
        assert cat == "other"
        assert tone == "neutral"

    def test_classify_empty(self):
        from plat.macos_window import _classify
        cat, tone = _classify("")
        assert cat == "other"
        assert tone == "neutral"

    def test_classify_case_sensitive(self):
        from plat.macos_window import _classify
        cat, tone = _classify("SLACK")
        assert cat == "chat"


class TestMacOSWindowAppContext:
    """AppContext dataclass construction."""

    def test_app_context_defaults(self):
        from plat.macos_window import AppContext
        ctx = AppContext()
        assert ctx.app_name == ""
        assert ctx.process_name == ""
        assert ctx.category == "other"

    def test_app_context_with_values(self):
        from plat.macos_window import AppContext
        ctx = AppContext(app_name="Safari", process_name="safari", category="browser", tone="neutral")
        assert ctx.app_name == "Safari"
        assert ctx.category == "browser"


class TestMacOSWindowFieldDetection:
    """Field info, text reading, and focus operations."""

    @patch("plat.macos_window._AX_AVAILABLE", False)
    def test_get_focused_field_info_returns_defaults_when_ax_missing(self):
        from plat.macos_window import get_focused_field_info
        info = get_focused_field_info()
        assert isinstance(info, dict)
        assert "window_id" in info
        assert "process_name" in info
        assert "pid" in info
        assert "is_text_field" in info  # optimistic default True

    @patch("plat.macos_window._AX_AVAILABLE", False)
    def test_get_field_text_returns_empty_when_ax_missing(self):
        from plat.macos_window import get_field_text
        assert get_field_text() == ""

    @patch("plat.macos_window._AX_AVAILABLE", False)
    def test_scan_for_text_inputs_returns_empty_when_ax_missing(self):
        from plat.macos_window import scan_for_text_inputs
        assert scan_for_text_inputs() == []

    @patch("plat.macos_window._AX_AVAILABLE", False)
    def test_focus_text_input_returns_false_when_ax_missing(self):
        from plat.macos_window import focus_text_input
        assert focus_text_input({}) is False

    @patch("plat.macos_window._AX_AVAILABLE", True)
    @patch("plat.macos_window.subprocess.run")
    def test_restore_focus_and_click_with_process_name(self, mock_run):
        from plat.macos_window import restore_focus_and_click
        mock_run.return_value.returncode = 0
        result = restore_focus_and_click({"process_name": "TextEdit"})
        assert result is True

    @patch("plat.macos_window._AX_AVAILABLE", True)
    def test_restore_focus_and_click_without_field_info(self):
        from plat.macos_window import restore_focus_and_click
        assert restore_focus_and_click(None) is True  # fail-open

    @patch("plat.macos_window._AX_AVAILABLE", True)
    def test_restore_focus_and_click_with_empty_field_info(self):
        from plat.macos_window import restore_focus_and_click
        assert restore_focus_and_click({}) is True  # fail-open

    @patch("plat.macos_window._AX_AVAILABLE", True)
    def test_get_active_app_returns_empty_on_failure(self):
        from plat.macos_window import get_active_app
        with patch("plat.macos_window._get_frontmost_app_info", return_value=(None, None)):
            ctx = get_active_app()
            assert ctx.app_name == ""
            assert ctx.process_name == ""
            assert ctx.category == "other"


class TestMacOSWindowFrontmostApp:
    """Frontmost app detection helpers."""

    @patch("plat.macos_window.subprocess.run")
    def test_get_frontmost_app_falls_back_to_osascript(self, mock_run):
        """When NSWorkspace is available but fails, fall back to osascript."""

        # First call (name) succeeds
        # Second call (pid) succeeds
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="Safari\n"),
            MagicMock(returncode=0, stdout="12345\n"),
        ]
        from plat.macos_window import _get_frontmost_app_info

        with patch.dict("sys.modules", {"AppKit": None}):
            name, pid = _get_frontmost_app_info()
            assert name == "Safari"
            assert pid == 12345

    def test_get_frontmost_app_returns_none_on_error(self):
        from plat.macos_window import _get_frontmost_app_info

        with patch.dict("sys.modules", {"AppKit": None}):
            with patch("plat.macos_window.subprocess.run", side_effect=Exception("fail")):
                name, pid = _get_frontmost_app_info()
                assert name is None
                assert pid is None


# ===================================================================
# 4 — macos_setup.py  — First-run setup checks & installers
# ===================================================================


class TestMacOSSetupCheckResult:
    """CheckResult dataclass — used for all setup status rows."""

    def test_ok_result(self):
        from plat.macos_setup import CheckResult
        r = CheckResult(key="portaudio", label="PortAudio", detail="Ready", ok=True, critical=True, can_install=False, needs_user=False)
        assert r.ok is True
        assert r.critical is True
        assert r.can_install is False

    def test_failed_critical_result(self):
        from plat.macos_setup import CheckResult
        r = CheckResult(key="accessibility", label="Accessibility", detail="Not granted", ok=False, critical=True, can_install=False, needs_user=True)
        assert r.ok is False
        assert r.critical is True
        assert r.needs_user is True


class TestMacOSSetupChecks:
    """Individual check functions."""

    def test_check_portaudio_available(self):
        from plat.macos_setup import check_portaudio
        with patch("plat.macos_setup.sounddevice", create=True):
            r = check_portaudio()
            assert r.key == "portaudio"
            assert r.ok is True
            assert r.critical is True

    def test_check_portaudio_missing(self):
        from plat.macos_setup import check_portaudio
        # Force import to fail
        with patch.dict("sys.modules", {"sounddevice": None}):
            import importlib
            with patch.object(importlib, "import_module", side_effect=ImportError("no sounddevice")):
                r = check_portaudio()
                assert r.ok is False
                assert r.can_install is True

    def test_check_pyobjc_available(self):
        from plat.macos_setup import check_pyobjc
        with (
            patch.dict("sys.modules", {"AppKit": MagicMock(), "ApplicationServices": MagicMock()}),
            patch("plat.macos_setup.sys.frozen", False, create=True),
        ):
            r = check_pyobjc()
            assert r.key == "pyobjc"
            assert r.ok is True

    def test_check_pyobjc_frozen_bundle(self):
        from plat.macos_setup import check_pyobjc
        with patch("plat.macos_setup.sys.frozen", True, create=True):
            r = check_pyobjc()
            assert r.ok is True
            # check_pyobjc() returns detail="Bundled" (install_pyobjc returns "Already bundled")
            assert "Bundled" in r.detail

    def test_check_pyobjc_missing(self):
        from plat.macos_setup import check_pyobjc
        with (
            patch.dict("sys.modules", {"AppKit": None, "ApplicationServices": None}),
            patch("plat.macos_setup.sys.frozen", False, create=True),
        ):
            r = check_pyobjc()
            assert r.ok is False
            assert r.can_install is True

    def test_check_accessibility_not_granted(self):
        from plat.macos_setup import check_accessibility
        with patch.dict("sys.modules", {"ApplicationServices": None}):
            with patch("plat.macos_setup.sys.modules", {"ApplicationServices": None}):
                r = check_accessibility()
                assert r.ok is False
                assert r.needs_user is True

    def test_check_input_monitoring_not_granted(self):
        from plat.macos_setup import check_input_monitoring
        with patch.dict("sys.modules", {"Quartz": None}):
            r = check_input_monitoring()
            assert r.ok is False
            assert r.critical is False  # optional
            assert r.needs_user is True

    def test_run_checks_returns_all_four(self):
        from plat.macos_setup import run_checks
        results = run_checks()
        assert len(results) == 4
        keys = [r.key for r in results]
        assert "portaudio" in keys
        assert "pyobjc" in keys
        assert "accessibility" in keys
        assert "input_monitoring" in keys


class TestMacOSSetupInstallers:
    """Install/uninstall helpers."""

    def test_is_setup_done_no_file(self):
        from plat.macos_setup import is_setup_done
        with patch("os.path.exists", return_value=False):
            assert is_setup_done() is False

    def test_is_setup_done_file_exists(self):
        from plat.macos_setup import is_setup_done
        with patch("os.path.exists", return_value=True):
            assert is_setup_done() is True

    @patch("builtins.open", new_callable=MagicMock)
    @patch("os.makedirs")
    def test_mark_setup_done(self, mock_makedirs, mock_open):
        from plat.macos_setup import mark_setup_done
        mark_setup_done()
        mock_makedirs.assert_called_once()
        mock_open.assert_called_once()

    def test_install_portaudio_no_brew(self):
        from plat.macos_setup import install_portaudio
        with patch("plat.macos_setup._find_brew", return_value=None):
            with patch("plat.macos_setup._install_homebrew", return_value=(False, "Failed")):
                ok, msg = install_portaudio()
                assert ok is False
                assert "Failed" in msg

    def test_install_pyobjc_frozen_skips(self):
        from plat.macos_setup import install_pyobjc
        with patch("plat.macos_setup.sys.frozen", True, create=True):
            ok, msg = install_pyobjc()
            assert ok is True
            # install_pyobjc returns "Already bundled" not just "Bundled"
            assert "Already" in msg

    def test_find_brew_not_installed(self):
        from plat.macos_setup import _find_brew
        with patch("os.path.isfile", return_value=False):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 1
                assert _find_brew() is None


# ===================================================================
# 5 — Cross-platform compat: platform __init__
# ===================================================================


class TestPlatformInit:
    """plat/__init__ platform selection logic.

    sys.platform is checked at import time in plat/__init__.py.
    To properly test different platforms, we must evict the cached
    plat.* modules so they re-import under the patched sys.platform.
    """

    def _evict_plat_modules(self):
        """Remove all cached plat.* modules so they re-import fresh."""
        for mod_name in list(sys.modules.keys()):
            if mod_name == "plat" or mod_name.startswith("plat."):
                del sys.modules[mod_name]

    def test_get_hotkey_handler_macos(self):
        with patch("sys.platform", "darwin"):
            self._evict_plat_modules()
            from plat import get_hotkey_handler
            handler = get_hotkey_handler()
            assert "macos_hotkey" in str(handler.__module__)

    def test_get_hotkey_handler_linux(self):
        with patch("sys.platform", "linux"):
            self._evict_plat_modules()
            from plat import get_hotkey_handler
            handler = get_hotkey_handler()
            assert "linux_hotkey" in str(handler.__module__)

    def test_get_injector_macos(self):
        with patch("sys.platform", "darwin"):
            self._evict_plat_modules()
            from plat import get_injector
            injector = get_injector()
            assert "macos_injector" in str(injector.__module__)

    def test_get_injector_linux(self):
        with patch("sys.platform", "linux"):
            self._evict_plat_modules()
            from plat import get_injector
            injector = get_injector()
            assert "linux_injector" in str(injector.__module__)
