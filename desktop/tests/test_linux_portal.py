"""Tests for the Wayland XDG Desktop Portal global shortcut backend."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Test hotkey format conversion helpers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("mods", "main", "expected"),
    [
        (frozenset(), "f9", "F9"),
        (frozenset({"ctrl"}), "f9", "<Control>F9"),
        (frozenset({"ctrl", "shift"}), "r", "<Control><Shift>R"),
        (frozenset({"alt"}), "tab", "<Alt>Tab"),
        (frozenset({"meta"}), "space", "<Super>Space"),
        (frozenset({"ctrl", "alt"}), "delete", "<Control><Alt>Delete"),
        (frozenset(), "a", "A"),
        (frozenset({"shift"}), "f1", "<Shift>F1"),
    ],
)
def test_hotkey_to_portal_preference(mods, main, expected):
    from plat.linux_portal import _hotkey_to_portal_preference

    result = _hotkey_to_portal_preference(mods, main)
    assert result == expected, f"{mods}+{main} -> {result} (expected {expected})"


@pytest.mark.parametrize(
    ("pref", "expected"),
    [
        ("F9", "f9"),
        ("<Control>F9", "ctrl+f9"),
        ("<Control><Shift>R", "ctrl+shift+r"),
        ("<Alt>Tab", "alt+tab"),
        ("<Super>Space", "meta+space"),
        ("<Control><Alt>Delete", "ctrl+alt+delete"),
        ("A", "a"),
        ("<Shift>F1", "shift+f1"),
    ],
)
def test_portal_preference_to_hotkey(pref, expected):
    from plat.linux_portal import _portal_preference_to_hotkey

    result = _portal_preference_to_hotkey(pref)
    assert result == expected, f"{pref} -> {result} (expected {expected})"


# Roundtrip test
@pytest.mark.parametrize(
    ("mods", "main"),
    [
        (frozenset(), "f9"),
        (frozenset({"ctrl"}), "f9"),
        (frozenset({"ctrl", "shift"}), "r"),
        (frozenset({"alt"}), "tab"),
        (frozenset({"meta"}), "space"),
        (frozenset(), "a"),
        (frozenset({"ctrl", "alt", "shift"}), "delete"),
    ],
)
def test_hotkey_portal_roundtrip(mods, main):
    """Converting to portal format and back should yield the original mods+main."""
    from plat.linux_portal import _hotkey_to_portal_preference, _portal_preference_to_hotkey

    pref = _hotkey_to_portal_preference(mods, main)
    result = _portal_preference_to_hotkey(pref)

    # Reconstruct expected format from the roundtrip
    parts = result.split("+")
    known_mods = {"ctrl", "shift", "alt", "meta"}
    result_mods = frozenset(p for p in parts if p in known_mods)
    result_main = next((p for p in parts if p not in known_mods), "")
    assert result_mods == mods, f"mods mismatch: {result_mods} != {mods}"
    assert result_main == main, f"main mismatch: {result_main} != {main}"


# ---------------------------------------------------------------------------
# Test PortalShortcutHandler start/stop (without real DBus)
# ---------------------------------------------------------------------------


def test_portal_handler_start_skips_non_wayland():
    """Handler.start() should return False when not on Wayland."""
    from plat.linux_portal import PortalShortcutHandler

    handler = PortalShortcutHandler(
        hotkey_str="f9",
        start_callback=lambda: None,
        stop_callback=lambda: None,
    )

    with patch.dict(os.environ, {"XDG_SESSION_TYPE": "x11", "DISPLAY": ":0"}):
        result = handler.start()

    assert result is False, "Should not start on X11"


def test_portal_handler_start_fails_without_jeepney():
    """Handler.start() should return False when jeepney is not installed."""
    from plat.linux_portal import PortalShortcutHandler

    handler = PortalShortcutHandler(
        hotkey_str="f9",
        start_callback=lambda: None,
        stop_callback=lambda: None,
    )

    with patch.dict(os.environ, {"XDG_SESSION_TYPE": "wayland"}):
        with patch("plat.linux_portal.jeepney", None):
            result = handler.start()

    assert result is False, "Should not start without jeepney"


def test_portal_handler_stop_safe_when_not_started():
    """Handler.stop() should not raise when handler was never started."""
    from plat.linux_portal import PortalShortcutHandler

    handler = PortalShortcutHandler(
        hotkey_str="f9",
        start_callback=lambda: None,
        stop_callback=lambda: None,
    )

    # Should not raise
    handler.stop()
    assert handler.is_running is False


def test_portal_handler_toggle_recording():
    """_toggle_recording should toggle state correctly."""
    from plat.linux_portal import PortalShortcutHandler

    calls = []
    handler = PortalShortcutHandler(
        hotkey_str="f9",
        start_callback=lambda: calls.append("start"),
        stop_callback=lambda: calls.append("stop"),
        mode="toggle",
    )

    # First toggle: should start
    handler._toggle_recording()
    assert calls == ["start"]
    assert handler._is_recording is True

    # Second toggle: should stop
    calls.clear()
    handler._toggle_recording()
    assert calls == ["stop"]
    assert handler._is_recording is False


def test_portal_handler_hold_mode():
    """Hold mode should alternate start/stop on key-press/key-release."""
    from plat.linux_portal import PortalShortcutHandler

    calls = []
    handler = PortalShortcutHandler(
        hotkey_str="f9",
        start_callback=lambda: calls.append("start"),
        stop_callback=lambda: calls.append("stop"),
        mode="hold",
    )

    # Simulate key press
    handler._toggle_recording()
    assert calls == ["start"]
    assert handler._is_key_pressed is True

    # Simulate key release (another toggle in hold mode)
    calls.clear()
    handler._toggle_recording()
    assert calls == ["stop"]
    assert handler._is_key_pressed is False
