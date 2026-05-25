"""
Read text from the currently focused input field using Windows UI Automation.

Used to provide continuity context to the AI cleanup LLM — so it knows what
the user has already typed and can continue naturally from that point.

Architecture:
  - Uses the IUIAutomation COM interface via comtypes
  - Falls back to reading clipboard + selected text if UIA fails
  - Never raises — returns empty string on any failure
  - Best-effort: works well with native Win32 controls, Electron apps,
    and most browsers. Some custom controls may not expose text.
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes

from utils.log import get_logger

logger = get_logger(__name__)

user32 = ctypes.windll.user32


def get_field_text() -> str:
    """
    Read existing text from the currently focused input field.

    Returns the text currently in the field (what the user has already typed),
    or empty string if unable to read.

    This context is sent to the LLM so it can maintain writing continuity
    and match the user's existing style/tone.
    """
    # Strategy 1: Try Windows UI Automation (most reliable for modern apps)
    text = _try_uia_text()
    if text:
        return text

    # Strategy 2: Try WM_GETTEXT for classic Win32 Edit controls
    text = _try_wm_gettext()
    if text:
        return text

    return ""


def _try_uia_text() -> str:
    """Read text using IUIAutomation COM interface."""
    try:
        import comtypes.client

        # Do NOT call CoInitialize/CoUninitialize here.
        # comtypes manages COM initialization internally per-thread.
        # Calling CoUninitialize while COM objects are still alive in local
        # scope causes access violations on the next COM call.

        # Create UI Automation instance
        uia = comtypes.client.CreateObject(
            "{ff48dba4-60ef-4201-aa87-54103eef594e}",  # CUIAutomation CLSID
            interface=None,
        )

        # Get the focused element
        focused = uia.GetFocusedElement()
        if focused is None:
            return ""

        # Try to get the Value pattern (works for text inputs)
        try:
            # UIA_ValuePatternId = 10002
            value_pattern = focused.GetCurrentPattern(10002)
            if value_pattern is not None:
                import comtypes.gen.UIAutomationClient

                val = value_pattern.QueryInterface(
                    comtypes.gen.UIAutomationClient.IUIAutomationValuePattern
                )
                text = val.CurrentValue or ""
                if text.strip():
                    logger.debug("uia_value_read", length=len(text))
                    return text.strip()
        except Exception:
            pass

        # Try to get the Text pattern (works for rich text controls)
        try:
            # UIA_TextPatternId = 10014
            text_pattern = focused.GetCurrentPattern(10014)
            if text_pattern is not None:
                import comtypes.gen.UIAutomationClient

                txt = text_pattern.QueryInterface(
                    comtypes.gen.UIAutomationClient.IUIAutomationTextPattern
                )
                doc_range = txt.DocumentRange
                text = doc_range.GetText(-1) or ""
                if text.strip():
                    logger.debug("uia_text_read", length=len(text))
                    return text.strip()
        except Exception:
            pass

        return ""

    except ImportError:
        logger.debug("comtypes_not_available")
        return ""
    except Exception as exc:
        logger.debug("uia_read_failed", error=str(exc))
        return ""


def _try_wm_gettext() -> str:
    """Read text using WM_GETTEXT message for classic Win32 controls."""
    try:
        # Get the foreground window and its focused control
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ""

        # Get the thread of the foreground window
        foreground_tid = user32.GetWindowThreadProcessId(hwnd, None)
        current_tid = ctypes.windll.kernel32.GetCurrentThreadId()

        focused_hwnd = None

        # Attach to foreground thread to get its focused control
        if foreground_tid != current_tid:
            attached = user32.AttachThreadInput(current_tid, foreground_tid, True)
            if attached:
                try:
                    focused_hwnd = user32.GetFocus()
                finally:
                    user32.AttachThreadInput(current_tid, foreground_tid, False)
        else:
            focused_hwnd = user32.GetFocus()

        if not focused_hwnd:
            return ""

        # Check the control class to see if it's a text control
        class_buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(focused_hwnd, class_buf, 256)
        class_name = class_buf.value.lower()

        # Only read from known text control classes
        text_classes = ("edit", "richedit", "richedit20", "richedit50w", "scintilla")
        if not any(tc in class_name for tc in text_classes):
            return ""

        # WM_GETTEXTLENGTH = 0x000E, WM_GETTEXT = 0x000D
        length = user32.SendMessageW(focused_hwnd, 0x000E, 0, 0)
        # SECURITY: Reduce cap from 10000 to 2000 chars to limit data exposure
        if length <= 0 or length > 2000:
            return ""

        buf = ctypes.create_unicode_buffer(length + 1)
        user32.SendMessageW(focused_hwnd, 0x000D, length + 1, buf)
        text = buf.value or ""

        if text.strip():
            logger.debug("wm_gettext_read", length=len(text), control_class=class_name)
            # Return only the last 500 chars for context (don't overwhelm the LLM)
            return text.strip()[-500:]

        return ""

    except Exception as exc:
        logger.debug("wm_gettext_failed", error=str(exc))
        return ""
