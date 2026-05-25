"""
Capture focused control at hotkey press and optionally restore click+focus before paste.
Windows-only best-effort — never raises.
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes
import time
from typing import Any
from utils.log import get_logger

logger = get_logger(__name__)

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


class GUITHREADINFO(ctypes.Structure):
    """Maps to GUITHREADINFO from winuser.h for reliable cross-thread focus query."""
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


# Process names — these always have an editable text context (browser, Electron)
_BROWSER_AND_ELECTRON = frozenset(
    {
        "chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe",
        "obsidian.exe", "notion.exe", "slack.exe", "discord.exe",
        "code.exe", "cursor.exe", "teams.exe", "telegram.exe", "whatsapp.exe",
        "figma.exe", "zoom.exe", "mattermost.exe", "linear.exe",
    }
)

# Win32 class names that are clearly NOT text-input controls.
# If the focused class is one of these, we know no text field is focused.
# Everything else (including unknown classes) is treated as a potential text field.
_NON_TEXT_CLASSES = frozenset(
    {
        "button", "#32768", "#32769", "combobox", "listbox", "scrollbar",
        "static", "tooltips_class32", "toolbar", "toolbarwindow32",
        "statusbar", "msctls_statusbar32", "systreeview32", "syslistview32",
        "treeview", "listview", "tabcontrol", "systabcontrol32",
        "progressbar", "msctls_progress32", "trackbar", "msctls_trackbar32",
        "spin", "msctls_updown32", "animate_class", "sysanimate32",
        "datetimepick_class", "monthcal_class", "sysmonthcal32",
        "sysdatetimepick32", "ipaddress", "sysipaddress32",
    }
)


def get_focused_field_info() -> dict[str, Any]:
    """
    Capture the current foreground window and (best-effort) focused control.

    Strategy: assume is_text_field=True unless we positively identify a
    non-text control. This avoids false "no text field" warnings for apps
    with custom or unknown window classes.
    """
    try:
        import psutil
    except Exception:
        psutil = None  # type: ignore[assignment]

    result: dict[str, Any] = {
        "hwnd": None,
        "pid": None,
        "window_title": "",
        "exe_name": "",
        "cursor_x": 0,
        "cursor_y": 0,
        "is_text_field": True,   # optimistic default — warn only on confirmed non-text
        "focused_class": "",
        "captured_at": time.time(),
    }

    try:
        hwnd = user32.GetForegroundWindow()
        result["hwnd"] = hwnd if hwnd else None
        if not hwnd:
            result["is_text_field"] = False
            return result

        buf = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buf, 512)
        result["window_title"] = buf.value

        pid_dword = ctypes.wintypes.DWORD(0)
        foreground_tid = user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid_dword))
        result["pid"] = int(pid_dword.value)

        exe_name = ""
        if psutil:
            try:
                proc = psutil.Process(pid_dword.value)
                exe_name = proc.name().lower()
                result["exe_name"] = exe_name
            except Exception:
                pass

        point = ctypes.wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(point))
        result["cursor_x"] = int(point.x)
        result["cursor_y"] = int(point.y)

        # Browser / Electron apps always have editable content
        if exe_name in _BROWSER_AND_ELECTRON:
            result["is_text_field"] = True
            return result

        # Use GetGUIThreadInfo — more reliable than AttachThreadInput+GetFocus
        focused_hwnd = 0
        if foreground_tid:
            gti = GUITHREADINFO()
            gti.cbSize = ctypes.sizeof(GUITHREADINFO)
            if user32.GetGUIThreadInfo(foreground_tid, ctypes.byref(gti)):
                focused_hwnd = gti.hwndFocus or gti.hwndActive or 0

        if focused_hwnd:
            class_buf = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(focused_hwnd, class_buf, 256)
            class_name = class_buf.value.lower()
            result["focused_class"] = class_name

            # Only mark as NOT a text field if we positively identify a non-text class
            if class_name and any(nc == class_name or class_name.startswith(nc) for nc in _NON_TEXT_CLASSES):
                result["is_text_field"] = False
        # If focused_hwnd is 0 (e.g. UWP, sandboxed renderer), keep is_text_field=True
        # — the user likely clicked into something before pressing the hotkey.

    except Exception as e:
        logger.warning("field_detection_error", error=str(e))

    return result


def restore_focus_and_click(field_info: dict[str, Any] | None) -> bool:
    """Raise the captured window before paste."""
    try:
        if not field_info:
            return False
        hwnd = field_info.get("hwnd")
        if not hwnd:
            return False
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.02)
        return True
    except Exception as e:
        logger.warning("focus_restore_error", error=str(e))
        return False


def warn_no_text_field_banner(exe_name: str) -> None:
    """Audible + logged heads-up when no text field is detected."""
    logger.warning("no_text_field_detected", exe_name=exe_name or "unknown")
    try:
        user32.MessageBeep(0x00000030)  # MB_ICONWARNING
    except Exception:
        pass


# Win32 class names that ARE text inputs (for scanning)
_TEXT_INPUT_CLASSES = frozenset({
    "edit", "richedit20w", "richedit50w", "richeditd2dpt", "richedit20a",
    "textbox", "scintilla", "tmemo", "wxstc", "chromium_renderwidgethost",
    "mozillawindowclass",
})

# WINFUNCTYPE callback type for EnumChildWindows
_WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)


def scan_for_text_inputs(hwnd: int = 0) -> list[dict[str, Any]]:
    """
    Enumerate child windows of the active (or given) HWND and return all
    visible text-input controls, sorted by area descending.

    Returns list of dicts: {hwnd, class_name, rect, area}
    """
    if not hwnd:
        hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return []

    found: list[dict[str, Any]] = []

    def _cb(child_hwnd: int, _lparam: int) -> bool:
        try:
            # Skip invisible windows
            if not user32.IsWindowVisible(child_hwnd):
                return True

            class_buf = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(child_hwnd, class_buf, 256)
            class_name = class_buf.value.lower()

            is_text = (
                class_name in _TEXT_INPUT_CLASSES
                or "edit" in class_name
                or "text" in class_name
                or "input" in class_name
                or "scintilla" in class_name
            )
            if not is_text:
                return True

            rect = ctypes.wintypes.RECT()
            user32.GetWindowRect(child_hwnd, ctypes.byref(rect))
            w = rect.right - rect.left
            h = rect.bottom - rect.top
            if w < 20 or h < 10:
                return True

            found.append({
                "hwnd": child_hwnd,
                "class_name": class_name,
                "rect": (rect.left, rect.top, rect.right, rect.bottom),
                "area": w * h,
            })
        except Exception:
            pass
        return True

    cb = _WNDENUMPROC(_cb)
    user32.EnumChildWindows(hwnd, cb, 0)

    # Sort largest area first — the primary text field is usually the biggest
    found.sort(key=lambda x: x["area"], reverse=True)
    return found


def focus_text_input(input_info: dict[str, Any]) -> bool:
    """
    Click into a found text input control to focus it for paste.
    Returns True if focus was successfully set.
    """
    try:
        child_hwnd = input_info.get("hwnd")
        rect = input_info.get("rect")
        if not child_hwnd or not rect:
            return False

        # Bring the parent window to foreground first
        parent = user32.GetAncestor(child_hwnd, 2)  # GA_ROOT = 2
        if parent:
            user32.SetForegroundWindow(parent)
            time.sleep(0.02)

        # Click the center of the text field
        cx = (rect[0] + rect[2]) // 2
        cy = (rect[1] + rect[3]) // 2
        user32.SetCursorPos(cx, cy)
        time.sleep(0.01)
        user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
        time.sleep(0.01)
        user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
        time.sleep(0.03)

        # Verify focus landed on the right window
        focused_hwnd = user32.GetForegroundWindow()
        return bool(focused_hwnd)
    except Exception as e:
        logger.warning("focus_text_input_error", error=str(e))
        return False
