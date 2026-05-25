"""
macOS window detection backend using Apple Accessibility (AXUIElement) + NSWorkspace.

Provides:
  - Frontmost application detection (name + PID)
  - Focused UI element capture (for smart text injection)
  - Window focus restoration
  - App classification (browser, editor, terminal, chat, etc.)
  - Text field scanning

Required Python packages:
  - pyobjc-framework-ApplicationServices (for AXUIElement)
  - pyobjc-framework-AppKit (for NSWorkspace)

Reference: VoiceType macOS backend (Honeybee1023/VoiceType)
"""

from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from typing import Any

from utils.log import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# AppContext dataclass — mirrors Windows/Linux versions
# ---------------------------------------------------------------------------

@dataclass
class AppContext:
    app_name: str = ""
    process_name: str = ""
    category: str = "other"
    tone: str = "neutral"


# ---------------------------------------------------------------------------
# Process name -> category mapping (macOS app names)
# ---------------------------------------------------------------------------

_PROCESS_CATEGORY: dict[str, str] = {
    # Browsers
    "google chrome": "browser", "chrome": "browser",
    "firefox": "browser", "safari": "browser",
    "microsoft edge": "browser", "brave browser": "browser",
    "opera": "browser", "vivaldi": "browser", "arc": "browser",
    "orion": "browser", "floorp": "browser",
    # Editors
    "visual studio code": "editor", "code": "editor",
    "cursor": "editor", "sublime text": "editor",
    "textedit": "editor", "bbedit": "editor",
    "vim": "editor", "neovim": "editor", "emacs": "editor",
    "xcode": "editor", "android studio": "editor",
    "intellij idea": "editor", "pycharm": "editor",
    "webstorm": "editor", "phpstorm": "editor",
    "zed": "editor", "nova": "editor",
    # Terminals
    "terminal": "terminal", "iterm2": "terminal", "iterm": "terminal",
    "alacritty": "terminal", "kitty": "terminal", "wezterm": "terminal",
    "hyper": "terminal", "warp": "terminal", "tabby": "terminal",
    "ghostty": "terminal",
    # Chat / Communication
    "slack": "chat", "discord": "chat", "telegram": "chat",
    "messages": "chat", "signal": "chat", "wechat": "chat",
    "whatsapp": "chat", "zoom": "chat", "microsoft teams": "chat",
    "element": "chat", "imessage": "chat",
    # Email
    "mail": "email", "microsoft outlook": "email",
    "thunderbird": "email", "mimestream": "email",
    "spark": "email", "airmail": "email",
    # Notes
    "obsidian": "notes", "notion": "notes", "logseq": "notes",
    "bear": "notes", "craft": "notes", "apple notes": "notes",
    "typora": "notes", "upnote": "notes",
    # Office
    "microsoft word": "office", "microsoft excel": "office",
    "microsoft powerpoint": "office", "libreoffice": "office",
    "pages": "office", "numbers": "office", "keynote": "office",
    # Media
    "music": "media", "spotify": "media", "vlc": "media",
    "quicktime player": "media", "iina": "media", "mpv": "media",
    "podcasts": "media", "apple tv": "media",
    # Design
    "figma": "media", "sketch": "media", "affinity designer": "media",
    "affinity photo": "media", "gimp": "media", "inkscape": "media",
}

_CATEGORY_TONE: dict[str, str] = {
    "browser": "neutral", "editor": "technical", "terminal": "technical",
    "chat": "casual", "email": "formal", "office": "formal",
    "notes": "neutral", "media": "neutral", "other": "neutral",
}


def _classify(process_name: str) -> tuple[str, str]:
    """Classify a macOS app name into (category, tone)."""
    stem = process_name.lower().strip() if process_name else ""
    category = _PROCESS_CATEGORY.get(stem, "other")
    tone = _CATEGORY_TONE.get(category, "neutral")
    return category, tone


# ---------------------------------------------------------------------------
# AXUIElement availability check
# ---------------------------------------------------------------------------

_AX_AVAILABLE = False
try:
    from ApplicationServices import (
        AXUIElementCreateSystemWide,
        AXUIElementCopyAttributeValue,
        kAXFocusedUIElementAttribute,
    )
    _AX_AVAILABLE = True
except ImportError:
    logger.warning("pyobjc-framework-ApplicationServices not available; AX detection disabled")


# ---------------------------------------------------------------------------
# Public API — mirrors Windows field_detector + Linux linux_window interface
# ---------------------------------------------------------------------------

def get_focused_field_info() -> dict[str, Any]:
    """
    Capture the current focused window and (best-effort) focused control.

    Strategy on macOS:
      1. Use NSWorkspace to get the frontmost app name + PID
      2. Use AXUIElement to get the focused UI element
      3. Fall back to osascript if AX is unavailable

    Note on cursor_x / cursor_y:
      macOS does not expose global cursor position via AXUIElement.
      We use AppleScript to get it, but it may return 0,0 in some cases.
      The injector does not use these coordinates for targeting.
    """
    result: dict[str, Any] = {
        "window_id": None,
        "pid": None,
        "window_title": "",
        "process_name": "",
        "cursor_x": 0,
        "cursor_y": 0,
        "is_text_field": True,  # optimistic default
        "focused_class": "",
        "captured_at": time.time(),
    }

    # Get frontmost app info via NSWorkspace or osascript
    app_name, pid = _get_frontmost_app_info()
    if app_name:
        result["process_name"] = app_name
        result["window_title"] = app_name
    if pid:
        result["pid"] = pid

    # Get cursor position via AppleScript
    try:
        cursor_result = subprocess.run(
            ["osascript", "-e",
             "tell application \"System Events\" to get (mouse location)"],
            capture_output=True, text=True, timeout=3,
        )
        if cursor_result.returncode == 0:
            # Parse "{x, y}" format from AppleScript list
            loc = cursor_result.stdout.strip()
            if "," in loc:
                parts = loc.split(",")
                result["cursor_x"] = int(parts[0].strip().strip("{"))
                result["cursor_y"] = int(parts[1].strip().strip("}"))
    except Exception:
        pass

    # Get focused AX element
    if _AX_AVAILABLE:
        try:
            system = AXUIElementCreateSystemWide()
            err, focused = AXUIElementCopyAttributeValue(
                system, kAXFocusedUIElementAttribute, None
            )
            if err == 0 and focused is not None:
                # Try to get the role (class) of the focused element
                try:
                    from ApplicationServices import (
                        AXUIElementCopyAttributeValue as _copyAttr,
                        kAXRoleAttribute,
                    )
                    err2, role = _copyAttr(focused, kAXRoleAttribute, None)
                    if err2 == 0 and role:
                        result["focused_class"] = str(role).lower()
                        # Determine if it's a text field based on role
                        text_roles = {
                            "axtextfield", "axtextarea", "axsearchfield",
                            "axsecuretextfield", "axwebarea", "axscrollarea",
                        }
                        result["is_text_field"] = str(role).lower() in text_roles
                except Exception:
                    pass
        except Exception as exc:
            logger.debug("ax_role_read_failed", error=str(exc))
    return result


def _capture_ax_element():
    """Capture the currently focused AX UI Element, or None."""
    if not _AX_AVAILABLE:
        return None
    try:
        from ApplicationServices import (
            AXUIElementCreateSystemWide,
            AXUIElementCopyAttributeValue,
            kAXFocusedUIElementAttribute,
        )
        system = AXUIElementCreateSystemWide()
        err, focused = AXUIElementCopyAttributeValue(
            system, kAXFocusedUIElementAttribute, None
        )
        if err == 0 and focused is not None:
            return focused
    except Exception:
        pass
    return None


def get_field_text() -> str:
    """
    Read existing text from the currently focused input field.
    Uses AXUIElement Value attribute. Returns empty string on failure.
    """
    if not _AX_AVAILABLE:
        return ""

    try:
        from ApplicationServices import (
            AXUIElementCreateSystemWide,
            AXUIElementCopyAttributeValue,
            kAXFocusedUIElementAttribute,
            kAXValueAttribute,
        )
        system = AXUIElementCreateSystemWide()
        err, focused = AXUIElementCopyAttributeValue(
            system, kAXFocusedUIElementAttribute, None
        )
        if err != 0 or focused is None:
            return ""

        err2, value = AXUIElementCopyAttributeValue(focused, kAXValueAttribute, None)
        if err2 == 0 and value:
            text = str(value)
            return text[-500:] if len(text) > 500 else text
    except Exception as exc:
        logger.debug("ax_field_text_read_failed", error=str(exc))

    return ""


def scan_for_text_inputs(window_id: int = 0) -> list[dict[str, Any]]:
    """
    Enumerate accessible text-input controls in the active window.
    On macOS, we use AXUIElement to traverse the accessibility tree.

    Returns list of dicts: {window_id, class_name, rect, area}
    Sorted by area descending (largest first).
    """
    if not _AX_AVAILABLE:
        return []

    results: list[dict[str, Any]] = []
    TEXT_INPUT_ROLES = {
        "axtextfield", "axtextarea", "axsearchfield",
        "axsecuretextfield", "axwebarea",
    }

    try:
        from ApplicationServices import (
            AXUIElementCreateSystemWide,
            AXUIElementCopyAttributeValue,
            kAXFocusedUIElementAttribute,
            kAXChildrenAttribute,
            kAXRoleAttribute,
            kAXPositionAttribute,
            kAXSizeAttribute,
        )
        system = AXUIElementCreateSystemWide()
        err, focused = AXUIElementCopyAttributeValue(
            system, kAXFocusedUIElementAttribute, None
        )
        if err != 0 or focused is None:
            return []

        # Walk up to find the window, then scan children
        # For simplicity, we just check the focused element and its siblings
        _scan_ax_element(focused, TEXT_INPUT_ROLES, results, depth=0, max_depth=5)
    except Exception as exc:
        logger.debug("ax_scan_failed", error=str(exc))

    results.sort(key=lambda x: x.get("area", 0), reverse=True)
    return results


def _scan_ax_element(element, text_roles: set, results: list, depth: int, max_depth: int):
    """Recursively scan AXUIElement children for text inputs."""
    if depth > max_depth:
        return
    try:
        from ApplicationServices import (
            AXUIElementCopyAttributeValue as _copyAttr,
            kAXRoleAttribute,
            kAXChildrenAttribute,
            kAXPositionAttribute,
            kAXSizeAttribute,
        )
        err, role = _copyAttr(element, kAXRoleAttribute, None)
        if err == 0 and role and str(role).lower() in text_roles:
            # Get position and size
            err_pos, pos = _copyAttr(element, kAXPositionAttribute, None)
            err_size, size = _copyAttr(element, kAXSizeAttribute, None)
            if err_pos == 0 and err_size == 0 and pos and size:
                x = pos.x if hasattr(pos, 'x') else 0
                y = pos.y if hasattr(pos, 'y') else 0
                w = size.width if hasattr(size, 'width') else 0
                h = size.height if hasattr(size, 'height') else 0
                if w > 20 and h > 10:
                    results.append({
                        "window_id": None,
                        "class_name": str(role),
                        "rect": (int(x), int(y), int(x + w), int(y + h)),
                        "area": int(w * h),
                    })

        err, children = _copyAttr(element, kAXChildrenAttribute, None)
        if err == 0 and children:
            for child in children:
                _scan_ax_element(child, text_roles, results, depth + 1, max_depth)
    except Exception:
        pass


def focus_text_input(input_info: dict[str, Any]) -> bool:
    """
    Attempt to focus a found text input control.
    On macOS, we use AXUIElementSetAttributeValue to set focus.
    """
    if not _AX_AVAILABLE:
        return False

    try:
        from ApplicationServices import (
            AXUIElementCreateSystemWide,
            AXUIElementCopyAttributeValue,
            kAXFocusedUIElementAttribute,
        )
        system = AXUIElementCreateSystemWide()
        err, focused = AXUIElementCopyAttributeValue(
            system, kAXFocusedUIElementAttribute, None
        )
        if err == 0 and focused is not None:
            # Try to set focus via the AX API
            try:
                from ApplicationServices import (
                    AXUIElementSetAttributeValue,
                    kAXFocusedAttribute,
                )
                AXUIElementSetAttributeValue(focused, kAXFocusedAttribute, True)
                return True
            except Exception:
                pass
    except Exception as exc:
        logger.debug("focus_text_input_error", error=str(exc))

    return False


def restore_focus_and_click(field_info: dict[str, Any] | None) -> bool:
    """
    Raise the captured window before paste.
    On macOS, we use AppleScript to activate the target app.
    Never raises — returns True even if no strategy worked.
    """
    try:
        if not field_info:
            return True  # fail-open

        process_name = field_info.get("process_name")
        if process_name:
            subprocess.run(
                ["osascript", "-e", f'tell application "{process_name}" to activate'],
                timeout=3, capture_output=True,
            )
            time.sleep(0.08)
            return True

        pid = field_info.get("pid")
        if pid:
            # Try to activate by PID
            subprocess.run(
                ["osascript", "-e",
                 f'tell application "System Events" to set frontmost of (first process whose unix id is {pid}) to true'],
                timeout=3, capture_output=True,
            )
            time.sleep(0.08)
            return True

        return True  # fail-open
    except Exception as exc:
        logger.warning("focus_restore_error", error=str(exc))
        return True  # fail-open


def warn_no_text_field_banner(process_name: str) -> None:
    """Audible + logged heads-up when no text field is detected."""
    logger.warning("no_text_field_detected", process_name=process_name or "unknown")
    try:
        # macOS system beep
        subprocess.run(["afplay", "/System/Library/Sounds/Tink.aiff"],
                       timeout=2, capture_output=True)
    except Exception:
        pass


def get_active_app() -> AppContext:
    """
    Returns AppContext for the current foreground window.
    Never raises — returns empty AppContext on any failure.
    """
    try:
        app_name, pid = _get_frontmost_app_info()
        if app_name:
            category, tone = _classify(app_name)
            return AppContext(
                app_name=app_name,
                process_name=app_name.lower(),
                category=category,
                tone=tone,
            )
    except Exception as exc:
        logger.warning("active_app_detection_failed", error=str(exc))
    return AppContext()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_frontmost_app_info() -> tuple[str | None, int | None]:
    """Get the frontmost app name and PID. Returns (name, pid) or (None, None)."""
    # Try NSWorkspace first (more reliable)
    try:
        from AppKit import NSWorkspace
        app = NSWorkspace.sharedWorkspace().frontmostApplication()
        if app:
            name = app.localizedName()
            pid = app.processIdentifier()
            return (str(name) if name else None, int(pid) if pid else None)
    except Exception:
        pass

    # Fallback: osascript
    try:
        result = subprocess.run(
            ["osascript", "-e",
             'tell application "System Events" to get name of first process whose frontmost is true'],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            name = result.stdout.strip() or None
            pid = None
            # Also get PID
            pid_result = subprocess.run(
                ["osascript", "-e",
                 'tell application "System Events" to get unix id of (first process whose frontmost is true)'],
                capture_output=True, text=True, timeout=5,
            )
            if pid_result.returncode == 0:
                try:
                    pid = int(pid_result.stdout.strip())
                except (ValueError, TypeError):
                    pass
            return name, pid
    except Exception:
        pass

    return None, None
