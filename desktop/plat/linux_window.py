"""
Linux window detection backend using AT-SPI (Accessibility Service Provider Interface).

Works on both X11 and Wayland via the D-Bus accessibility bus.

AT-SPI is the standard Linux accessibility framework used by screen readers.
It provides access to:
- Focused element detection
- Element roles and properties
- Text content of input fields
- Application identification

Falls back gracefully when AT-SPI is not available.

Reference: https://www.freedesktop.org/wiki/Accessibility/AT-SPI2/
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

from utils.log import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# AppContext dataclass -- mirrors the Windows version
# ---------------------------------------------------------------------------


@dataclass
class AppContext:
    app_name: str = ""
    process_name: str = ""
    category: str = "other"
    tone: str = "neutral"


# ---------------------------------------------------------------------------
# Process name -> category mapping (same as Windows version)
# ---------------------------------------------------------------------------

_PROCESS_CATEGORY: dict[str, str] = {
    "chrome": "browser",
    "firefox": "browser",
    "msedge": "browser",
    "brave": "browser",
    "opera": "browser",
    "vivaldi": "browser",
    "code": "editor",
    "cursor": "editor",
    "sublime_text": "editor",
    "notepad": "editor",
    "xed": "editor",
    "gedit": "editor",
    "kate": "editor",
    "neovim": "editor",
    "vim": "editor",
    "emacs": "editor",
    "gnome-terminal": "terminal",
    "konsole": "terminal",
    "alacritty": "terminal",
    "kitty": "terminal",
    "wezterm": "terminal",
    "foot": "terminal",
    "tilix": "terminal",
    "terminator": "terminal",
    "xfce4-terminal": "terminal",
    "slack": "chat",
    "discord": "chat",
    "telegramdesktop": "chat",
    "signal": "chat",
    "thunderbird": "email",
    "evolution": "email",
    "obsidian": "notes",
    "notion": "notes",
    "logseq": "notes",
    "libreoffice": "office",
    "soffice": "office",
    "vlc": "media",
    "spotify": "media",
    "mpv": "media",
    "gimp": "media",
    "inkscape": "media",
}

_CATEGORY_TONE: dict[str, str] = {
    "browser": "neutral",
    "editor": "technical",
    "terminal": "technical",
    "chat": "casual",
    "email": "formal",
    "office": "formal",
    "notes": "neutral",
    "media": "neutral",
    "other": "neutral",
}


def _classify(process_name: str) -> tuple[str, str]:
    stem = process_name.lower().removesuffix(".exe") if process_name else ""
    # Handle snap/flatpak style names
    for prefix in ["snap.", "app."]:
        if stem.startswith(prefix):
            stem = stem[len(prefix) :]
    category = _PROCESS_CATEGORY.get(stem, "other")
    tone = _CATEGORY_TONE.get(category, "neutral")
    return category, tone


# ---------------------------------------------------------------------------
# AT-SPI availability check
# ---------------------------------------------------------------------------

_ATSPI_AVAILABLE = False
try:
    import pyatspi

    _ATSPI_AVAILABLE = True
except ImportError:
    logger.warning("pyatspi not available; window detection will be limited")


# ---------------------------------------------------------------------------
# Public API -- mirrors the Windows field_detector interface
# ---------------------------------------------------------------------------


def get_focused_field_info() -> dict[str, Any]:
    """
    Capture the current focused window and (best-effort) focused control.

    Strategy on Linux:
      1. Use AT-SPI to get the focused application and element
      2. Fall back to _NET_ACTIVE_WINDOW via python-xlib on X11
      3. Fall back to empty info if both fail

    Note on cursor_x / cursor_y:
      On X11: filled by python-xlib query_pointer().
      On Wayland: always 0,0 — Wayland has no global cursor position API
      without compositor-specific protocols. The injector does not use these
      coordinates for targeting, so 0,0 is a safe sentinel value.
    """
    result: dict[str, Any] = {
        "window_id": None,
        "pid": None,
        "window_title": "",
        "process_name": "",
        "cursor_x": 0,  # 0,0 on Wayland — intentional, see docstring
        "cursor_y": 0,
        "is_text_field": True,  # optimistic default
        "focused_class": "",
        "captured_at": time.time(),
    }

    _on_wayland = bool(
        os.environ.get("WAYLAND_DISPLAY")
        or os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"
    )

    # Strategy 1: AT-SPI
    if _ATSPI_AVAILABLE:
        try:
            _fill_via_atspi(result)
            # AT-SPI doesn't expose cursor position; fill it from xlib on X11
            if not _on_wayland and os.environ.get("DISPLAY") and result["cursor_x"] == 0:
                _fill_cursor_via_xlib(result)
            return result
        except Exception as e:
            logger.debug("atspi_focus_detection_failed", error=str(e))

    # Strategy 2: python-xlib on X11
    if os.environ.get("DISPLAY"):
        try:
            _fill_via_xlib(result)
            return result
        except Exception as e:
            logger.debug("xlib_focus_detection_failed", error=str(e))

    if _on_wayland:
        logger.debug("wayland_cursor_pos_unavailable")

    return result


def get_field_text() -> str:
    """
    Read existing text from the currently focused input field.

    Uses AT-SPI text interfaces (Text pattern, then Value pattern).
    Returns empty string on any failure.
    """
    if not _ATSPI_AVAILABLE:
        return ""

    try:
        desktop = pyatspi.Registry.getDesktop(0)
        for app in desktop:
            try:
                for child in app:
                    try:
                        if not child.getState().contains(pyatspi.STATE_FOCUSED):
                            continue

                        # Try Text pattern (rich text controls)
                        try:
                            text_iface = child.queryText()
                            if text_iface:
                                text = text_iface.getText(0, -1)
                                if text and text.strip():
                                    return text.strip()[-500:]  # last 500 chars
                        except Exception:
                            pass

                        # Try Value pattern (simple text inputs)
                        try:
                            value_iface = child.queryValue()
                            if value_iface:
                                val = str(value_iface.currentValue)
                                if val and val.strip():
                                    return val.strip()[-500:]
                        except Exception:
                            pass

                    except Exception:
                        continue
            except Exception:
                continue
    except Exception as e:
        logger.debug("atspi_field_text_read_failed", error=str(e))

    return ""


def scan_for_text_inputs(window_id: int = 0) -> list[dict[str, Any]]:
    """
    Enumerate accessible text-input controls in the active window.

    Returns list of dicts: {window_id, class_name, rect, area}
    Sorted by area descending (largest first).
    """
    if not _ATSPI_AVAILABLE:
        return []

    results: list[dict[str, Any]] = []

    TEXT_INPUT_ROLES = {
        "text",
        "entry",
        "text box",
        "text area",
        "password text",
        "terminal",
        "document text",
        "edit bar",
        "combo box",
    }

    try:
        desktop = pyatspi.Registry.getDesktop(0)
        # Prefer the active application; fall back to scanning all apps
        active_apps = []
        other_apps = []
        for app in desktop:
            try:
                if app.getState().contains(pyatspi.STATE_ACTIVE):
                    active_apps.append(app)
                else:
                    other_apps.append(app)
            except Exception:
                other_apps.append(app)

        scan_order = active_apps + other_apps
        for app in scan_order:
            try:
                _scan_children(app, TEXT_INPUT_ROLES, results, depth=0, max_depth=10)
                # Stop after finding inputs in the active app
                if active_apps and app in active_apps and results:
                    break
            except Exception:
                continue
    except Exception as e:
        logger.debug("atspi_scan_failed", error=str(e))

    results.sort(key=lambda x: x.get("area", 0), reverse=True)
    return results


def focus_text_input(input_info: dict[str, Any]) -> bool:
    """
    Attempt to focus a found text input control via AT-SPI.

    Strategy:
      1. Call pyatspi grab_focus() on the stored node reference.
      2. Try the accessible Action interface for a "focus" action.
      3. Fall back to xdotool click at the element's centre point.
    Returns True if any method succeeded (best-effort).
    """
    node = input_info.get("_atspi_node") if input_info else None

    if node is not None and _ATSPI_AVAILABLE:
        # Strategy 1: grab_focus via the Component interface
        try:
            component = node.queryComponent()
            if component and component.grabFocus():
                logger.debug("focus_text_input_grab_focus_ok")
                return True
        except Exception:
            pass

        # Strategy 2: Action interface — look for "focus" or "activate" action
        try:
            action = node.queryAction()
            n_actions = action.get_n_actions() if action else 0
            for i in range(n_actions):
                name = (action.get_name(i) or "").lower()
                if name in ("focus", "activate", "click"):
                    action.do_action(i)
                    logger.debug("focus_text_input_action_ok", action=name)
                    return True
        except Exception:
            pass

    # Strategy 3: xdotool click at element centre (X11 only)
    rect = input_info.get("rect") if input_info else None
    if rect and os.environ.get("DISPLAY"):
        try:
            import shutil
            import subprocess

            if shutil.which("xdotool"):
                x1, y1, x2, y2 = rect
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                subprocess.run(
                    ["xdotool", "mousemove", str(cx), str(cy), "click", "1"],
                    timeout=3,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                logger.debug("focus_text_input_xdotool_click", cx=cx, cy=cy)
                return True
        except Exception as e:
            logger.debug("focus_text_input_xdotool_failed", error=str(e))

    # Strategy 4: ydotool click at element centre (Wayland via /dev/uinput)
    # Requires: ydotool installed + /dev/uinput accessible (udev rule in setup-linux.sh)
    if rect:
        try:
            import shutil
            import subprocess

            if shutil.which("ydotool"):
                x1, y1, x2, y2 = rect
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                # Move mouse to element centre
                subprocess.run(
                    ["ydotool", "mousemove", "--absolute", "--", str(cx), str(cy)],
                    timeout=3,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                time.sleep(0.02)
                # Click left button (0xC0 = press + release in one command)
                result = subprocess.run(
                    ["ydotool", "click", "0xC0"],
                    timeout=3,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if result.returncode == 0:
                    logger.debug("focus_text_input_ydotool_click", cx=cx, cy=cy)
                    return True
        except Exception as e:
            logger.debug("focus_text_input_ydotool_failed", error=str(e))

    logger.debug("focus_text_input_no_method_succeeded")
    return False


def restore_focus_and_click(field_info: dict[str, Any] | None) -> bool:
    """
    Raise the captured window before paste.

    Strategy order:
      1. xdotool windowactivate  (X11)
      2. swaymsg [pid=N] focus   (Wayland / Sway / wlroots compositors)
      3. hyprctl dispatch focuswindow pid:N  (Hyprland)
      4. AT-SPI grab_focus on focused element  (Wayland fallback, best-effort)
    Never raises — returns True even if no strategy worked, so injection is
    not blocked by a focus failure.
    """
    try:
        import shutil
        import subprocess

        window_id = field_info.get("window_id") if field_info else None
        pid = field_info.get("pid") if field_info else None

        _on_wayland = bool(
            os.environ.get("WAYLAND_DISPLAY")
            or os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"
        )

        # Strategy 1: xdotool (X11 or XWayland)
        if window_id and shutil.which("xdotool"):
            result = subprocess.run(
                ["xdotool", "windowactivate", str(window_id)],
                timeout=3,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if result.returncode == 0:
                time.sleep(0.05)
                return True

        # Strategy 2: Sway / wlroots (WAYLAND_DISPLAY + SWAYSOCK)
        if pid and _on_wayland and os.environ.get("SWAYSOCK") and shutil.which("swaymsg"):
            result = subprocess.run(
                ["swaymsg", f'[pid="{pid}"] focus'],
                timeout=3,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if result.returncode == 0:
                time.sleep(0.05)
                return True
            logger.debug("swaymsg_focus_failed", rc=result.returncode)

        # Strategy 3: Hyprland
        if (
            pid
            and _on_wayland
            and os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
            and shutil.which("hyprctl")
        ):
            result = subprocess.run(
                ["hyprctl", "dispatch", "focuswindow", f"pid:{pid}"],
                timeout=3,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if result.returncode == 0:
                time.sleep(0.05)
                return True
            logger.debug("hyprctl_focus_failed", rc=result.returncode)

        # Strategy 4: AT-SPI grab_focus on the focused element in the target app.
        # Works on Wayland when the compositor exposes no window management API.
        if pid and _ATSPI_AVAILABLE:
            try:
                desktop = pyatspi.Registry.getDesktop(0)
                for app in desktop:
                    try:
                        if app.get_process_id() != pid:
                            continue
                        focused = _find_focused_element(app)
                        if focused:
                            comp = focused.queryComponent()
                            if comp and comp.grabFocus():
                                time.sleep(0.05)
                                logger.debug("restore_focus_atspi_grab_ok", pid=pid)
                                return True
                    except Exception:
                        continue
            except Exception as e:
                logger.debug("atspi_restore_focus_failed", error=str(e))

        # No strategy succeeded; return True so injection still proceeds.
        return True
    except Exception as e:
        logger.warning("focus_restore_error", error=str(e))
        return False


def warn_no_text_field_banner(process_name: str) -> None:
    """Audible + logged heads-up when no text field is detected."""
    logger.warning("no_text_field_detected", process_name=process_name or "unknown")


def get_active_app() -> AppContext:
    """
    Returns AppContext for the current foreground window.
    Never raises -- returns empty AppContext on any failure.
    """
    try:
        if _ATSPI_AVAILABLE:
            return _active_app_via_atspi()
        elif os.environ.get("DISPLAY"):
            return _active_app_via_xlib()
    except Exception as e:
        logger.warning("active_app_detection_failed", error=str(e))
    return AppContext()


# ---------------------------------------------------------------------------
# Internal: AT-SPI implementations
# ---------------------------------------------------------------------------


def _find_focused_element(node, depth: int = 0, max_depth: int = 12):
    """Recursively find the first AT-SPI node with STATE_FOCUSED."""
    if depth > max_depth:
        return None
    try:
        if node.getState().contains(pyatspi.STATE_FOCUSED):
            return node
    except Exception:
        return None
    try:
        for i in range(node.childCount):
            try:
                child = node.getChildAtIndex(i)
                found = _find_focused_element(child, depth + 1, max_depth)
                if found is not None:
                    return found
            except Exception:
                continue
    except Exception:
        pass
    return None


def _fill_via_atspi(result: dict[str, Any]) -> None:
    """Fill result dict using AT-SPI accessibility queries (recursive search)."""
    desktop = pyatspi.Registry.getDesktop(0)
    for app in desktop:
        try:
            app_name = app.name or ""
            focused = _find_focused_element(app)
            if focused is None:
                continue

            result["process_name"] = _process_name_from_atspi(app)
            result["window_title"] = app_name
            result["focused_class"] = focused.getRoleName() or ""

            role = (focused.getRoleName() or "").lower()
            text_roles = {"text", "entry", "text box", "text area", "terminal"}
            try:
                is_editable = focused.getState().contains(pyatspi.STATE_EDITABLE)
            except Exception:
                is_editable = False
            result["is_text_field"] = role in text_roles or is_editable

            try:
                pid = app.get_process_id()
                if pid and pid > 0:
                    result["pid"] = pid
            except Exception:
                pass

            return
        except Exception:
            continue


def _active_app_via_atspi() -> AppContext:
    """Get active application info via AT-SPI."""
    desktop = pyatspi.Registry.getDesktop(0)
    for app in desktop:
        try:
            if app.getState().contains(pyatspi.STATE_ACTIVE):
                process_name = _process_name_from_atspi(app)
                category, tone = _classify(process_name)
                return AppContext(
                    app_name=app.name or "",
                    process_name=process_name,
                    category=category,
                    tone=tone,
                )
        except Exception:
            continue
    return AppContext()


def _process_name_from_atspi(app) -> str:
    """Extract the process name from an AT-SPI application handle."""
    try:
        pid = app.get_process_id()
        if pid and pid > 0:
            # Read /proc/PID/comm for the process name
            try:
                with open(f"/proc/{pid}/comm") as f:
                    return f.read().strip()
            except Exception:
                pass
            # Fallback: read /proc/PID/cmdline
            try:
                with open(f"/proc/{pid}/cmdline") as f:
                    cmdline = f.read().split("\x00")[0]
                    return cmdline.split("/")[-1] if cmdline else ""
            except Exception:
                pass
    except Exception:
        pass
    return ""


def _scan_children(node, text_roles: set, results: list, depth: int, max_depth: int):
    """Recursively scan AT-SPI tree for text input controls."""
    if depth > max_depth:
        return

    try:
        role = (node.getRoleName() or "").lower()
        try:
            is_editable = node.getState().contains(pyatspi.STATE_EDITABLE)
        except Exception:
            is_editable = False
        if role in text_roles or is_editable:
            try:
                extents = node.queryComponent().getExtents(pyatspi.WINDOW_COORDS)
                if extents:
                    x, y, w, h = extents
                    if w >= 20 and h >= 10:
                        results.append(
                            {
                                "window_id": id(node),
                                "_atspi_node": node,  # live reference for focus_text_input
                                "class_name": role,
                                "rect": (x, y, x + w, y + h),
                                "area": w * h,
                            }
                        )
            except Exception:
                pass

        # Recurse into children
        try:
            for i in range(node.childCount):
                try:
                    child = node.getChildAtIndex(i)
                    _scan_children(child, text_roles, results, depth + 1, max_depth)
                except Exception:
                    continue
        except Exception:
            pass
    except Exception:
        return


# ---------------------------------------------------------------------------
# Internal: python-xlib fallback (X11 only)
# ---------------------------------------------------------------------------


def _fill_cursor_via_xlib(result: dict[str, Any]) -> None:
    """Fill cursor_x / cursor_y using python-xlib query_pointer (X11 only)."""
    try:
        from Xlib import display

        d = display.Display()
        pointer = d.screen().root.query_pointer()
        result["cursor_x"] = pointer.root_x
        result["cursor_y"] = pointer.root_y
        d.close()
    except Exception:
        pass  # non-fatal; 0,0 is acceptable sentinel


def _fill_via_xlib(result: dict[str, Any]) -> None:
    """Fill result dict using python-xlib on X11."""
    try:
        from Xlib import X, display
    except ImportError:
        logger.debug("python-xlib not available")
        return

    try:
        d = display.Display()
        root = d.screen().root

        # Get active window
        active = root.get_full_property(d.intern_atom("_NET_ACTIVE_WINDOW"), X.AnyPropertyType)
        if not active or not active.value:
            return

        window_id = active.value[0]
        result["window_id"] = window_id

        win = d.create_resource_object("window", window_id)

        # Get window title
        try:
            title = win.get_full_property(d.intern_atom("_NET_WM_NAME"), X.AnyPropertyType)
            if title and title.value:
                result["window_title"] = title.value.decode("utf-8", errors="replace")
            else:
                name = win.get_wm_name()
                if name:
                    result["window_title"] = name
        except Exception:
            pass

        # Get PID
        try:
            pid_prop = win.get_full_property(d.intern_atom("_NET_WM_PID"), X.AnyPropertyType)
            if pid_prop and pid_prop.value:
                pid = pid_prop.value[0]
                result["pid"] = pid
                # Read process name
                try:
                    with open(f"/proc/{pid}/comm") as f:
                        result["process_name"] = f.read().strip()
                except Exception:
                    pass
        except Exception:
            pass

        # Get mouse position
        try:
            pointer = root.query_pointer()
            result["cursor_x"] = pointer.root_x
            result["cursor_y"] = pointer.root_y
        except Exception:
            pass

        d.close()

    except Exception as e:
        logger.debug("xlib_fill_error", error=str(e))


def _active_app_via_xlib() -> AppContext:
    """Get active application info via python-xlib."""
    ctx = AppContext()

    try:
        from Xlib import X, display

        d = display.Display()
        root = d.screen().root

        active = root.get_full_property(d.intern_atom("_NET_ACTIVE_WINDOW"), X.AnyPropertyType)
        if not active or not active.value:
            d.close()
            return ctx

        win = d.create_resource_object("window", active.value[0])

        # Window title
        try:
            title = win.get_full_property(d.intern_atom("_NET_WM_NAME"), X.AnyPropertyType)
            if title and title.value:
                ctx.app_name = title.value.decode("utf-8", errors="replace")
        except Exception:
            pass

        # PID -> process name
        try:
            pid_prop = win.get_full_property(d.intern_atom("_NET_WM_PID"), X.AnyPropertyType)
            if pid_prop and pid_prop.value:
                pid = pid_prop.value[0]
                try:
                    with open(f"/proc/{pid}/comm") as f:
                        ctx.process_name = f.read().strip()
                except Exception:
                    pass
        except Exception:
            pass

        d.close()

    except Exception as e:
        logger.debug("xlib_active_app_error", error=str(e))

    ctx.category, ctx.tone = _classify(ctx.process_name)
    return ctx
