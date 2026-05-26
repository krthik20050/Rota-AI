"""
macOS text injection backend — 4-tier fallback system.

Injection priority:
  1. AXUIElementSetAttributeValue (kAXSelectedTextAttribute / kAXValueAttribute)
     Directly sets text on the focused Accessibility element.
     No clipboard side effects. Requires Accessibility permission.
  2. NSPasteboard + AppleScript Cmd+V
     Copies text to clipboard, then uses osascript to send Cmd+V.
     Restores previous clipboard after paste.
     Requires Accessibility + Automation permissions.
  3. pynput CGEvent Cmd+V
     Copies text to clipboard, then uses pynput to send Cmd+V.
     Requires Accessibility permission.
  4. pynput character-by-character typing
     Last resort for problematic apps (Terminal, iTerm2, WeChat).
     Slow but universal.

Required Python packages:
  - pyobjc-framework-ApplicationServices (for AXUIElement)
  - pyobjc-framework-Cocoa (for NSPasteboard)
  - pynput (for keyboard simulation)

Reference: VoiceType macOS backend (Honeybee1023/VoiceType)
"""

from __future__ import annotations

import subprocess
import time

import structlog

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Module-level state (mirrors the Windows and Linux injector globals)
# ---------------------------------------------------------------------------
_last_undo_content: str | None = None
_last_injected_text: str | None = None
_last_injected_field_info = None
_last_injected_window = None
_last_injected_correlation_id: str | None = None

# SECURITY: Maximum injection length to prevent abuse
_MAX_INJECT_LENGTH = 5000  # characters

# SECURITY: Terminal / shell process names — injecting here can execute commands.
# Only used for informational warnings; injection is not blocked.
_TERMINAL_PROCESS_NAMES = frozenset(
    {
        "terminal",
        "iterm2",
        "alacritty",
        "kitty",
        "wezterm",
        "hyper",
        "warp",
        "tabby",
        "ghostty",
        "bash",
        "zsh",
        "fish",
        "sh",
        "dash",
        "tcsh",
        "python",
        "python3",
        "node",
        "irb",
        "rails",
    }
)

# Apps that don't respond well to AX injection or Cmd+V — use direct typing instead
_DIRECT_TYPE_APPS = frozenset(
    {
        "terminal",
        "iterm2",
        "iterm",
        "wechat",
        "微信",
        "alacritty",
    }
)


# ---------------------------------------------------------------------------
# macOS permission checks
# ---------------------------------------------------------------------------


def _check_accessibility_permission() -> bool:
    """Check if the process has Accessibility permission."""
    try:
        from ApplicationServices import (
            AXIsProcessTrustedWithOptions,
        )

        # Prompt=False — just check, don't show dialog
        return bool(AXIsProcessTrustedWithOptions(None))
    except Exception:
        return False


def _check_input_monitoring_permission() -> bool:
    """Check if the process has Input Monitoring permission (Quartz CGEventTap)."""
    try:
        from Quartz import CGEventTapCreate, kCGHeadInsertEventTap, kCGSessionEventTap

        tap = CGEventTapCreate(
            kCGSessionEventTap,
            kCGHeadInsertEventTap,
            1,  # active — actually test if we can tap
            0,  # mask=0 — we're just testing creation
            lambda _proxy, _type, _event, _refcon: _event,
            None,
        )
        if tap:
            # Release the test tap
            from Quartz import CFRelease

            CFRelease(tap)
            return True
        return False
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Clipboard helpers (NSPasteboard snapshot + restore)
# ---------------------------------------------------------------------------


class _ClipboardSnapshot:
    """Save and restore macOS clipboard contents."""

    _types_and_data: list[tuple[str, bytes]] = []

    @classmethod
    def save(cls) -> None:
        """Snapshot the current clipboard for later restore."""
        cls._types_and_data = []
        try:
            from AppKit import NSPasteboard

            pb = NSPasteboard.generalPasteboard()
            for t in pb.types():
                data = pb.dataForType_(t)
                if data:
                    cls._types_and_data.append((str(t), bytes(data)))
        except Exception as exc:
            logger.warning("clipboard_snapshot_failed", error=str(exc))

    @classmethod
    def restore(cls) -> None:
        """Restore the clipboard to its previous contents."""
        if not cls._types_and_data:
            return
        try:
            from AppKit import NSPasteboard

            pb = NSPasteboard.generalPasteboard()
            pb.clearContents()
            for t, raw in cls._types_and_data:
                pb.setData_forType_(raw, t)
        except Exception as exc:
            logger.warning("clipboard_restore_failed", error=str(exc))
        finally:
            cls._types_and_data = []


def _clipboard_copy(text: str) -> bool:
    """Copy text to clipboard. Returns True on success."""
    try:
        proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        proc.communicate(text.encode("utf-8"), timeout=5)
        return proc.returncode == 0
    except Exception as exc:
        logger.warning("pbcopy_failed", error=str(exc))
        return False


def _clipboard_paste() -> str | None:
    """Read current clipboard contents. Returns None on failure."""
    try:
        result = subprocess.run(["pbpaste"], capture_output=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.decode("utf-8", errors="replace")
        return None
    except Exception as exc:
        logger.warning("pbpaste_failed", error=str(exc))
        return None


# ---------------------------------------------------------------------------
# Target app info (captured at recording start)
# ---------------------------------------------------------------------------


class _TargetInfo:
    """Holds the captured target app/window state for the current recording session."""

    app_name: str | None = None
    pid: int | None = None
    ax_element: object | None = None
    click_pos: tuple[int, int] | None = None


_current_target = _TargetInfo()


def capture_target() -> None:
    """Capture the current frontmost app and focused element before recording starts."""
    try:
        # Get frontmost app name
        result = subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "System Events" to get name of first process whose frontmost is true',
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        _current_target.app_name = result.stdout.strip() or None

        # Get frontmost app PID
        result = subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "System Events" to get unix id of (first process whose frontmost is true)',
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        try:
            _current_target.pid = int(result.stdout.strip())
        except (ValueError, TypeError):
            _current_target.pid = None

        # Capture focused AX element
        try:
            from ApplicationServices import (
                AXUIElementCopyAttributeValue,
                AXUIElementCreateSystemWide,
                kAXFocusedUIElementAttribute,
            )

            system = AXUIElementCreateSystemWide()
            err, focused = AXUIElementCopyAttributeValue(system, kAXFocusedUIElementAttribute, None)
            if err == 0 and focused is not None:
                _current_target.ax_element = focused
                logger.info("macos_injector: captured focused AX element")
            else:
                _current_target.ax_element = None
                logger.debug("macos_injector: no focused AX element (err=%d)", err)
        except Exception as exc:
            _current_target.ax_element = None
            logger.debug("macos_injector: AX capture failed: %s", exc)

    except Exception as exc:
        logger.warning("macos_injector: target capture failed: %s", exc)


def clear_target() -> None:
    """Clear captured target info after injection."""
    _current_target.app_name = None
    _current_target.pid = None
    _current_target.ax_element = None
    _current_target.click_pos = None


# ---------------------------------------------------------------------------
# Tier 1: AXUIElement injection (fastest, no clipboard side effects)
# ---------------------------------------------------------------------------


def _inject_ax(text: str, element) -> bool:
    """
    Set text directly on an AXUIElement via Accessibility API.
    Tries kAXSelectedTextAttribute first, then kAXValueAttribute.
    Returns True on success.
    """
    try:
        from ApplicationServices import (
            AXUIElementSetAttributeValue,
            kAXSelectedTextAttribute,
            kAXValueAttribute,
        )

        # Try kAXSelectedTextAttribute (replaces selected text / inserts at cursor)
        err = AXUIElementSetAttributeValue(element, kAXSelectedTextAttribute, text)
        if err == 0:
            logger.info("macos_injector: AX inject success via kAXSelectedTextAttribute")
            return True

        # Try kAXValueAttribute (replaces entire field value)
        err = AXUIElementSetAttributeValue(element, kAXValueAttribute, text)
        if err == 0:
            logger.info("macos_injector: AX inject success via kAXValueAttribute")
            return True

        logger.debug("macos_injector: AX inject failed (err=%d)", err)
        return False
    except Exception as exc:
        logger.debug("macos_injector: AX inject exception: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Tier 2: AppleScript Cmd+V (works in virtually all apps)
# ---------------------------------------------------------------------------


def _inject_apple_script(text: str) -> bool:
    """Inject via clipboard + AppleScript Cmd+V. Returns True on success."""
    if not _clipboard_copy(text):
        return False
    time.sleep(0.02)
    try:
        result = subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "System Events" to keystroke "v" using command down',
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            logger.info("macos_injector: AppleScript Cmd+V success")
            return True
        logger.warning(
            "macos_injector: AppleScript paste failed (rc=%d): %s",
            result.returncode,
            result.stderr[:200],
        )
        return False
    except Exception as exc:
        logger.warning("macos_injector: AppleScript paste exception: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Tier 3: pynput CGEvent Cmd+V (fallback if osascript fails)
# ---------------------------------------------------------------------------


def _inject_pynput_cmd_v(text: str) -> bool:
    """Inject via clipboard + pynput Cmd+V. Returns True on success."""
    try:
        from pynput.keyboard import Controller, Key
    except ImportError:
        logger.warning("macos_injector: pynput not available for Cmd+V")
        return False

    if not _clipboard_copy(text):
        return False
    time.sleep(0.02)
    try:
        kb = Controller()
        with kb.pressed(Key.cmd):
            kb.press("v")
            kb.release("v")
        logger.info("macos_injector: pynput Cmd+V success")
        return True
    except Exception as exc:
        logger.warning("macos_injector: pynput Cmd+V exception: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Tier 4: character-by-character typing (last resort)
# ---------------------------------------------------------------------------


def _inject_type_chars(text: str) -> bool:
    """Type text character-by-character via pynput. Slow but universal."""
    try:
        from pynput.keyboard import Controller
    except ImportError:
        logger.warning("macos_injector: pynput not available for typing")
        return False
    try:
        kb = Controller()
        kb.type(text)
        logger.info("macos_injector: character typing success (%d chars)", len(text))
        return True
    except Exception as exc:
        logger.warning("macos_injector: character typing exception: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Focus restoration
# ---------------------------------------------------------------------------


def _restore_focus(app_name: str | None) -> bool:
    """Bring the target app to foreground before injection."""
    if not app_name:
        return False
    try:
        result = subprocess.run(
            ["osascript", "-e", f'tell application "{app_name}" to activate'],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            time.sleep(0.08)
            return True
        return False
    except Exception as exc:
        logger.debug("macos_injector: focus restore failed: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Public API — TextInjector class (matches Windows/Linux injector interface)
# ---------------------------------------------------------------------------


class TextInjector:
    """
    Injects text into the active window on macOS using a 4-tier fallback system.

    Interface matches the Windows TextInjector and Linux TextInjector.
    """

    def __init__(self) -> None:
        self._ax_available = self._check_ax_available()
        logger.info(
            "macos_injector_initialised",
            ax_available=self._ax_available,
            accessibility=_check_accessibility_permission(),
        )

    @staticmethod
    def _check_ax_available() -> bool:
        try:
            import ApplicationServices  # noqa: F401

            return True
        except ImportError:
            logger.warning(
                "pyobjc-framework-ApplicationServices not available; AX injection disabled"
            )
            return False

    # -- Internal helpers ---------------------------------------------------

    def _has_active_window(self) -> bool:
        return _current_target.app_name is not None

    # -- Public interface (matches Windows TextInjector) ---------------------

    def is_text_field_active(self) -> bool:
        """Compatibility method. Returns True if any window is active."""
        return self._has_active_window()

    def inject(
        self,
        text: str,
        correlation_id: str | None = None,
        field_info: dict | None = None,
        use_paste_shortcut: bool = True,
    ) -> tuple[bool, str]:
        """
        Attempts to inject text into the currently focused window.
        Returns (success: bool, message: str).
        """
        global _last_undo_content, _last_injected_text
        global _last_injected_field_info, _last_injected_window, _last_injected_correlation_id

        if not text:
            return False, "No text to inject"

        # SECURITY: Enforce maximum injection length.
        if len(text) > _MAX_INJECT_LENGTH:
            logger.warning("injection_too_long", length=len(text), max=_MAX_INJECT_LENGTH)
            text = text[:_MAX_INJECT_LENGTH]

        # Log a warning when injecting into terminals.
        proc_name = (_current_target.app_name or "").lower()
        if proc_name in _TERMINAL_PROCESS_NAMES:
            logger.warning(
                "injection_target_is_terminal", process=proc_name, correlation_id=correlation_id
            )

        target_app = _current_target.app_name
        ax_element = _current_target.ax_element

        # Check if we should force direct typing for this app
        if target_app and any(ta in target_app.lower() for ta in _DIRECT_TYPE_APPS):
            logger.info("macos_injector: direct typing forced for app=%s", target_app)
            _restore_focus(target_app)
            ok = _inject_type_chars(text)
            if ok:
                _last_injected_text = text
                _last_injected_field_info = field_info or {}
                _last_injected_correlation_id = correlation_id
                return True, "Text typed directly"
            return False, "Direct typing failed"

        # Save clipboard for undo
        try:
            _last_undo_content = _clipboard_paste()
        except Exception:
            _last_undo_content = None

        # Take a snapshot for restore
        _ClipboardSnapshot.save()

        try:
            # Restore focus to target app
            _restore_focus(target_app)

            # Tier 1: AXUIElement injection (no clipboard side effects)
            if ax_element is not None and self._ax_available:
                if _inject_ax(text, ax_element):
                    _last_injected_text = text
                    _last_injected_field_info = field_info or {}
                    _last_injected_correlation_id = correlation_id
                    return True, "Text injected via AXUIElement"

            if not use_paste_shortcut:
                _clipboard_copy(text)
                return False, "Copied to clipboard"

            # Tier 2: AppleScript Cmd+V
            if _inject_apple_script(text):
                _last_injected_text = text
                _last_injected_field_info = field_info or {}
                _last_injected_correlation_id = correlation_id
                return True, "Text injected via AppleScript"

            # Tier 3: pynput Cmd+V
            if _inject_pynput_cmd_v(text):
                _last_injected_text = text
                _last_injected_field_info = field_info or {}
                _last_injected_correlation_id = correlation_id
                return True, "Text injected via pynput"

            # Tier 4: character-by-character typing
            if _inject_type_chars(text):
                _last_injected_text = text
                _last_injected_field_info = field_info or {}
                _last_injected_correlation_id = correlation_id
                return True, "Text typed character by character"

            return False, "All injection methods failed"

        except Exception as exc:
            logger.error("text_injection_failed", correlation_id=correlation_id, exc_info=True)
            return False, f"Injection failed: {exc}"

        finally:
            # Always restore the clipboard snapshot if one was taken, so stale
            # snapshot data never leaks into the next injection call.
            had_rich_data = bool(_ClipboardSnapshot._types_and_data)
            if had_rich_data:
                try:
                    time.sleep(0.1)
                    _ClipboardSnapshot.restore()
                except Exception:
                    _ClipboardSnapshot._types_and_data = []
            if _last_undo_content is not None and not had_rich_data:
                try:
                    time.sleep(0.1)
                    _clipboard_copy(_last_undo_content)
                except Exception:
                    pass

    def undo_last_inject(self) -> tuple[bool, str]:
        """Undo the last injection by restoring the previous clipboard content."""
        global _last_undo_content
        if _last_undo_content is None:
            return False, "No undo available"
        try:
            _clipboard_copy(_last_undo_content)
            _last_undo_content = None
            return True, "Previous clipboard restored. Paste to recover."
        except Exception as exc:
            return False, f"Undo failed: {exc}"

    def get_last_injected_text(self) -> str:
        global _last_injected_text
        return _last_injected_text or ""

    def get_undo_available(self) -> bool:
        return _last_undo_content is not None
