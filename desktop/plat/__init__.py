"""
Platform abstraction layer for Rota AI.

Provides OS-specific implementations for:
- Hotkey capture
- Text injection
- Window/app detection
- Secret storage
- Startup registration
- Single-instance guard

Usage:
    from plat import get_hotkey_handler, get_injector, get_window_detector

Each function returns the appropriate backend for the current OS.
"""

import sys

IS_LINUX = sys.platform.startswith("linux")
IS_WINDOWS = sys.platform == "win32"


def get_hotkey_handler():
    """Return the OS-appropriate HotkeyHandler class."""
    if IS_LINUX:
        from plat.linux_hotkey import HotkeyHandler
        return HotkeyHandler
    else:
        from audio.hotkey import HotkeyHandler
        return HotkeyHandler


def get_injector():
    """Return the OS-appropriate TextInjector class."""
    if IS_LINUX:
        from plat.linux_injector import TextInjector
        return TextInjector
    else:
        from injection.injector import TextInjector
        return TextInjector


def get_window_detector():
    """Return the OS-appropriate window detector module."""
    if IS_LINUX:
        from plat import linux_window
        return linux_window
    else:
        from injection import field_detector
        return field_detector


def get_field_reader():
    """Return the OS-appropriate field reader module."""
    if IS_LINUX:
        from plat import linux_window
        return linux_window
    else:
        from injection import field_reader
        return field_reader


def get_app_detector():
    """Return the OS-appropriate app detector module."""
    if IS_LINUX:
        from plat import linux_window
        return linux_window
    else:
        from injection import app_detector
        return app_detector
