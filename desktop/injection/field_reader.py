"""
Field text reader — reads existing text from the focused window before injection.

Uses a layered approach (best → fallback):
1. UIA via pywin32 (Chrome, VS Code, Electron, WPF — modern apps)
2. WM_GETTEXT via ctypes (Notepad, terminals, Qt/WinForms — standard controls)
3. Empty string (graceful degradation)

All wrapped in try/except so failure never blocks the pipeline.
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes
import sys

# WM_GETTEXT constant
WM_GETTEXT = 0x000D

_user32 = None


def _ensure_user32():
    global _user32
    if _user32 is None and sys.platform == "win32":
        try:
            _user32 = ctypes.windll.user32
        except Exception:
            pass
    return _user32


def read_focused_field_text(max_chars: int = 500) -> str:
    """
    Read the existing text from the currently focused text field.

    Strategy (tried in order):
    1. UIA via pywin32 (Chrome, VS Code, Electron, WPF — modern apps)
    2. WM_GETTEXT via ctypes (Notepad, terminals, Qt/WinForms — standard controls)
    3. Returns empty string (graceful degradation)

    Args:
        max_chars: Maximum characters to read (default 500, capped for safety)

    Returns:
        The text content of the focused field, or empty string.
    """
    if sys.platform != "win32":
        return ""

    # Layer 1: UIA (Chrome, VS Code, Electron, WPF — the modern web)
    result = _read_focused_field_text_uia(max_chars)
    if result:
        return result

    # Layer 2: WM_GETTEXT (standard Win32 controls)
    return _read_focused_field_text_wm(max_chars)


def _read_focused_field_text_uia(max_chars: int = 500) -> str:
    """
    Read field text using UI Automation (Chrome, VS Code, Electron, WPF).

    Uses pywin32's win32com.client to access the UIA COM API.
    Returns empty string on any failure so callers fall back to WM_GETTEXT.

    Args:
        max_chars: Maximum characters to read.

    Returns:
        The text content, or empty string.
    """
    if sys.platform != "win32":
        return ""

    try:
        from win32com.client import Dispatch

        automation = Dispatch("UIAutomation.UIAutomationClient.CUIAutomation")
        if automation is None:
            return ""

        focused = automation.GetFocusedElement()
        if focused is None:
            return ""

        # Try ValuePattern (plain text inputs — most common)
        try:
            value_pattern = focused.GetCurrentPattern(10002)
            if value_pattern:
                text = value_pattern.CurrentValue
                if text and text.strip():
                    return text.strip()[:max_chars]
        except Exception:
            pass

        # Try TextPattern (rich text editors, code editors)
        try:
            text_pattern = focused.GetCurrentPattern(10014)
            if text_pattern:
                doc_range = text_pattern.DocumentRange
                if doc_range:
                    text = doc_range.GetText(max_chars)
                    if text and text.strip():
                        return text.strip()[:max_chars]
        except Exception:
            pass

        # Try Name property (some controls expose content here)
        try:
            name = focused.CurrentName
            if name and name.strip() and len(name) > 5:
                return name.strip()[:max_chars]
        except Exception:
            pass

        return ""

    except Exception:
        return ""


def _read_focused_field_text_wm(max_chars: int = 500) -> str:
    """
    Read field text using WM_GETTEXT via ctypes (standard Win32 controls).

    Covers Notepad, WordPad, Outlook compose, terminals, many Qt/WinForms
    apps that use standard EDIT/RichEdit controls.

    Args:
        max_chars: Maximum characters to read (default 500, capped at 1000)

    Returns:
        The text content, or empty string.
    """
    user32 = _ensure_user32()
    if user32 is None:
        return ""

    try:
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ""

        foreground_tid = user32.GetWindowThreadProcessId(hwnd, None)
        if not foreground_tid:
            return ""

        class GUITHREADINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", ctypes.wintypes.DWORD),
                ("flags", ctypes.wintypes.DWORD),
                ("hwndActive", ctypes.wintypes.HWND),
                ("hwndFocus", ctypes.wintypes.HWND),
                ("hwndCapture", ctypes.wintypes.HWND),
                ("hwndMenuOwner", ctypes.wintypes.HWND),
                ("hwndMoveSize", ctypes.wintypes.HWND),
                ("hwndCaret", ctypes.wintypes.HWND),
                ("rcCaret", ctypes.wintypes.RECT),
            ]

        gti = GUITHREADINFO()
        gti.cbSize = ctypes.sizeof(GUITHREADINFO)
        if not user32.GetGUIThreadInfo(foreground_tid, ctypes.byref(gti)):
            return ""

        focused_hwnd = gti.hwndFocus
        if not focused_hwnd:
            return ""

        buf_size = min(max_chars + 1, 1001)
        buf = ctypes.create_unicode_buffer(buf_size)
        chars_copied = user32.SendMessageW(focused_hwnd, WM_GETTEXT, buf_size, buf)

        if chars_copied > 0:
            text = buf.value.strip()
            if text:
                return text

        title_buf = ctypes.create_unicode_buffer(buf_size)
        chars_copied = user32.GetWindowTextW(focused_hwnd, title_buf, buf_size)
        if chars_copied > 0:
            text = title_buf.value.strip()
            if text:
                return text

        return ""
    except Exception:
        return ""
