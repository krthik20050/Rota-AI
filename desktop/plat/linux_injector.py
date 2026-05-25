"""
Linux text injection backend — injects text via clipboard + Ctrl+V.

Supports both X11 and Wayland sessions. Auto-detects the session type via
XDG_SESSION_TYPE and WAYLAND_DISPLAY environment variables.

External tool requirements:
  X11:   xdotool (keyboard), pyperclip or xclip (clipboard)
  Wayland: wl-copy/wl-paste (clipboard), wtype OR dotool OR ydotool (keyboard)

SECURITY CONSIDERATIONS:
- This module can inject arbitrary text into ANY application that has focus.
- If the transcription/AI pipeline is compromised (prompt injection), this becomes
  a code execution vector (terminal commands, SQL, URLs, etc.).
- Mitigations: max injection length, clipboard restore, session-type detection.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from enum import Enum

import structlog

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Module-level state (mirrors the Windows injector's globals)
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
_TERMINAL_PROCESS_NAMES = frozenset({
    "gnome-terminal", "gnome-terminal-server", "konsole", "xfce4-terminal",
    "mate-terminal", "terminator", "tilix", "alacritty", "kitty",
    "wezterm", "foot", "sakura", "terminology", "urxvt", "rxvt",
    "xterm", "st-256color", "tmux", "screen",
    "bash", "zsh", "fish", "sh", "dash",
    "python", "python3", "python3.11", "python3.12",
    "node", "docker",
})


# ---------------------------------------------------------------------------
# Session & tool detection
# ---------------------------------------------------------------------------

class SessionType(Enum):
    X11 = "x11"
    WAYLAND = "wayland"
    UNKNOWN = "unknown"


class KeyboardTool(Enum):
    WTYPE = "wtype"
    DOTOOL = "dotool"
    YDOTOOL = "ydotool"
    XDOTOOL = "xdotool"


def detect_session_type() -> SessionType:
    """Return the current display session type (X11, Wayland, or unknown)."""
    xdg = os.environ.get("XDG_SESSION_TYPE", "").lower().strip()
    wayland_display = os.environ.get("WAYLAND_DISPLAY", "")

    if xdg == "wayland" or wayland_display:
        return SessionType.WAYLAND
    if xdg == "x11" or os.environ.get("DISPLAY", ""):
        return SessionType.X11
    # Heuristic: if WAYLAND_DISPLAY is set we are almost certainly on Wayland.
    if wayland_display:
        return SessionType.WAYLAND
    logger.warning("session_type_unknown", xdg=xdg, wayland_display=bool(wayland_display))
    return SessionType.UNKNOWN


def _find_tool(name: str) -> str | None:
    """Return the full path to *name* on $PATH, or None if not found."""
    return shutil.which(name)


def detect_keyboard_tool(session: SessionType) -> KeyboardTool | None:
    """Return the best available keyboard tool for *session*."""
    if session in (SessionType.WAYLAND, SessionType.UNKNOWN):
        for tool in (KeyboardTool.WTYPE, KeyboardTool.DOTOOL, KeyboardTool.YDOTOOL):
            if _find_tool(tool.value):
                return tool
    if session in (SessionType.X11, SessionType.UNKNOWN):
        if _find_tool(KeyboardTool.XDOTOOL.value):
            return KeyboardTool.XDOTOOL
    return None


def _clipboard_copy(text: str, session: SessionType) -> bool:
    """Copy *text* to the system clipboard. Returns True on success."""
    try:
        if session == SessionType.WAYLAND:
            proc = subprocess.run(
                ["wl-copy"],
                input=text.encode("utf-8"),
                capture_output=True,
                timeout=5,
            )
            if proc.returncode == 0:
                return True
            logger.warning("wl_copy_failed", rc=proc.returncode, stderr=proc.stderr.decode(errors="replace"))

        # Fallbacks that work on both X11 and Wayland backends.
        for cmd in (["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]):
            if _find_tool(cmd[0]):
                proc = subprocess.run(
                    cmd,
                    input=text.encode("utf-8"),
                    capture_output=True,
                    timeout=5,
                )
                if proc.returncode == 0:
                    return True
                logger.warning("clipboard_cmd_failed", cmd=cmd[0], rc=proc.returncode)
                continue

        # Last resort: pyperclip (Python-only, may pull in xclip/xsel itself).
        try:
            import pyperclip
            pyperclip.copy(text)
            return True
        except Exception:
            logger.exception("pyperclip_copy_failed")

        return False
    except Exception:
        logger.exception("clipboard_copy_error")
        return False


def _clipboard_paste(session: SessionType) -> str | None:
    """Read the current clipboard contents. Returns None on failure."""
    try:
        if session == SessionType.WAYLAND:
            proc = subprocess.run(
                ["wl-paste", "--no-newline"],
                capture_output=True,
                timeout=5,
            )
            if proc.returncode == 0:
                return proc.stdout.decode("utf-8", errors="replace")
        for cmd in (["xclip", "-selection", "clipboard", "-o"], ["xsel", "--clipboard", "--output"]):
            if _find_tool(cmd[0]):
                proc = subprocess.run(cmd, capture_output=True, timeout=5)
                if proc.returncode == 0:
                    return proc.stdout.decode("utf-8", errors="replace")
        try:
            import pyperclip
            return pyperclip.paste()
        except Exception:
            logger.exception("pyperclip_paste_failed")
        return None
    except Exception:
        logger.exception("clipboard_paste_error")
        return None


def _send_ctrl_v(tool: KeyboardTool) -> bool:
    """Send Ctrl+V using *tool*. Returns True on success."""
    try:
        if tool == KeyboardTool.XDOTOOL:
            proc = subprocess.run(
                ["xdotool", "key", "--clearmodifiers", "ctrl+v"],
                capture_output=True,
                timeout=10,
            )
            if proc.returncode == 0:
                return True
            logger.warning("xdotool_ctrl_v_failed", rc=proc.returncode,
                           stderr=proc.stderr.decode(errors="replace"))

        elif tool == KeyboardTool.WTYPE:
            proc = subprocess.run(
                ["wtype", "-M", "ctrl", "v", "-m", "ctrl"],
                capture_output=True,
                timeout=10,
            )
            if proc.returncode == 0:
                return True
            logger.warning("wtype_ctrl_v_failed", rc=proc.returncode,
                           stderr=proc.stderr.decode(errors="replace"))

        elif tool == KeyboardTool.DOTOOL:
            # dotool protocol: "keydown <code>" / "keyup <code>" one per line
            # KEY_LEFTCTRL = 29, KEY_V = 47
            commands = "keydown 29\nkeydown 47\nsleep 50\nkeyup 47\nkeyup 29\n"
            proc = subprocess.run(
                ["dotool"],
                input=commands.encode("utf-8"),
                capture_output=True,
                timeout=10,
            )
            if proc.returncode == 0:
                return True
            logger.warning("dotool_ctrl_v_failed", rc=proc.returncode,
                           stderr=proc.stderr.decode(errors="replace"))

        elif tool == KeyboardTool.YDOTOOL:
            # ydotool key <keycode>:<1=press or 0=release>
            # LEFTCTRL = 29, V = 47
            base_cmd = ["ydotool", "key"]
            subprocess.run(base_cmd + ["29:1", "47:1"], capture_output=True, timeout=10)
            time.sleep(0.05)
            result = subprocess.run(base_cmd + ["47:0", "29:0"], capture_output=True, timeout=10)
            if result.returncode == 0:
                return True
            logger.warning("ydotool_ctrl_v_failed", rc=result.returncode,
                           stderr=result.stderr.decode(errors="replace"))

        return False
    except Exception:
        logger.exception("send_ctrl_v_error", tool=tool.value)
        return False


def _send_backspace_key(tool: KeyboardTool) -> bool:
    """Send a single Backspace keypress via *tool*."""
    try:
        if tool == KeyboardTool.XDOTOOL:
            proc = subprocess.run(
                ["xdotool", "key", "BackSpace"],
                capture_output=True,
                timeout=5,
            )
            return proc.returncode == 0

        elif tool == KeyboardTool.WTYPE:
            proc = subprocess.run(
                ["wtype", "-k", "BackSpace"],
                capture_output=True,
                timeout=5,
            )
            return proc.returncode == 0

        elif tool == KeyboardTool.DOTOOL:
            # KEY_BACKSPACE = 14
            commands = "keydown 14\nsleep 50\nkeyup 14\n"
            proc = subprocess.run(
                ["dotool"],
                input=commands.encode("utf-8"),
                capture_output=True,
                timeout=5,
            )
            return proc.returncode == 0

        elif tool == KeyboardTool.YDOTOOL:
            base_cmd = ["ydotool", "key"]
            subprocess.run(base_cmd + ["14:1"], capture_output=True, timeout=5)
            time.sleep(0.01)
            proc = subprocess.run(base_cmd + ["14:0"], capture_output=True, timeout=5)
            return proc.returncode == 0

        return False
    except Exception:
        logger.exception("send_backspace_error", tool=tool.value)
        return False


def _send_text_literal(tool: KeyboardTool, text: str) -> bool:
    """Type *text* literally via *tool* (character-by-character for safe chars)."""
    try:
        if tool == KeyboardTool.XDOTOOL:
            # xdotool type handles Unicode and special chars well.
            proc = subprocess.run(
                ["xdotool", "type", "--clearmodifiers", "--", text],
                capture_output=True,
                timeout=30,
            )
            if proc.returncode == 0:
                return True
            logger.warning("xdotool_type_failed", rc=proc.returncode,
                           stderr=proc.stderr.decode(errors="replace"))

        elif tool == KeyboardTool.WTYPE:
            # wtype can accept text directly.
            proc = subprocess.run(
                ["wtype", "--", text],
                capture_output=True,
                timeout=30,
            )
            if proc.returncode == 0:
                return True
            logger.warning("wtype_type_failed", rc=proc.returncode,
                           stderr=proc.stderr.decode(errors="replace"))

        elif tool == KeyboardTool.DOTOOL:
            # dotool: type each character via its keycode is complex, so
            # fall back to dotool's "type" subcommand if available, otherwise
            # delegate to xdotool. Many dotool builds don't have a "type" mode,
            # so we chunk by plain text.
            proc = subprocess.run(
                ["dotool"],
                input=f"type {text}\n".encode("utf-8"),
                capture_output=True,
                timeout=30,
            )
            if proc.returncode == 0:
                return True
            logger.warning("dotool_type_failed", rc=proc.returncode,
                           stderr=proc.stderr.decode(errors="replace"))

        elif tool == KeyboardTool.YDOTOOL:
            proc = subprocess.run(
                ["ydotool", "type", text],
                capture_output=True,
                timeout=30,
            )
            if proc.returncode == 0:
                return True
            logger.warning("ydotool_type_failed", rc=proc.returncode,
                           stderr=proc.stderr.decode(errors="replace"))

        return False
    except Exception:
        logger.exception("send_text_error", tool=tool.value, chars=len(text))
        return False


def _get_active_window_id(session: SessionType) -> str | None:
    """Return an identifier for the currently focused window, or None."""
    try:
        if session == SessionType.X11 or session == SessionType.UNKNOWN:
            if _find_tool("xdotool"):
                proc = subprocess.run(
                    ["xdotool", "getactivewindow"],
                    capture_output=True, timeout=5,
                )
                if proc.returncode == 0:
                    return proc.stdout.decode().strip()
        # Wayland does not expose a universal active-window query.
        try:
            proc = subprocess.run(
                ["xdotool", "getactivewindow"],
                capture_output=True, timeout=5,
            )
            if proc.returncode == 0:
                return proc.stdout.decode().strip()
        except Exception:
            pass
        return None
    except Exception:
        logger.exception("get_active_window_error")
        return None


def _get_focused_process_name(session: SessionType) -> str:
    """Attempt to return the process name of the focused window, or ''."""
    try:
        # Try to get window PID via xdotool / wmctrl
        for cmd in (
            ["xdotool", "getactivewindow", "getwindowpid"],
            ["xdotool", "getwindowpid"],
        ):
            try:
                proc = subprocess.run(cmd, capture_output=True, timeout=5)
                if proc.returncode == 0:
                    pid = int(proc.stdout.decode().strip())
                    try:
                        return os.readlink(f"/proc/{pid}/exe").split("/")[-1].lower()
                    except Exception:
                        comm_file = f"/proc/{pid}/comm"
                        if os.path.exists(comm_file):
                            return open(comm_file).read().strip().lower()
            except Exception:
                continue
        return ""
    except Exception:
        logger.exception("get_focused_process_error")
        return ""


# ---------------------------------------------------------------------------
# Public API — TextInjector class
# ---------------------------------------------------------------------------

class TextInjector:
    """
    Injects text into the active window via clipboard + Ctrl+V.

    WHY no caret check: On Linux there is no reliable cross-toolkit way to
    detect caret presence. Chrome, Firefox, VS Code, and Electron apps all
    use their own input models. Just paste — if nothing is focused,
    Ctrl+V is a no-op.
    """

    def __init__(self) -> None:
        self._session = detect_session_type()
        self._keyboard = detect_keyboard_tool(self._session)
        logger.info(
            "linux_injector_initialised",
            session=self._session.value,
            keyboard_tool=self._keyboard.value if self._keyboard else None,
        )
        if self._keyboard is None:
            logger.warning("no_keyboard_tool_found",
                           session=self._session.value,
                           hint="Install xdotool (X11) or wtype/dotool/ydotool (Wayland)")

    # -- Internal helpers ---------------------------------------------------

    def _has_active_window(self) -> bool:
        return _get_active_window_id(self._session) is not None

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

        # Log a warning when injecting into terminals (informational only).
        proc_name = _get_focused_process_name(self._session)
        if proc_name and proc_name.lower() in _TERMINAL_PROCESS_NAMES:
            logger.warning("injection_target_is_terminal", process=proc_name,
                           correlation_id=correlation_id)

        previous_clipboard = None
        window_before = None

        try:
            # Save current clipboard for undo capability.
            try:
                previous_clipboard = _clipboard_paste(self._session)
                _last_undo_content = previous_clipboard
            except Exception:
                previous_clipboard = None
                _last_undo_content = None

            try:
                window_before = _get_active_window_id(self._session)
            except Exception:
                window_before = None

            if not window_before:
                logger.warning("no_active_window_for_injection", correlation_id=correlation_id)
                _clipboard_copy(text, self._session)
                return False, "No active window — copied to clipboard"

            # Copy text to clipboard.
            if not _clipboard_copy(text, self._session):
                logger.warning("clipboard_copy_failed_inject", correlation_id=correlation_id)
                return False, "Failed to copy text to clipboard"

            if not use_paste_shortcut:
                return False, "Copied to clipboard"

            # Attempt focus restoration if field_info is available.
            if field_info:
                try:
                    from plat.linux_window import restore_focus_and_click
                    restored = restore_focus_and_click(field_info)
                    if not restored:
                        logger.warning("focus_restore_skipped_or_failed",
                                       correlation_id=correlation_id)
                except Exception:
                    logger.exception("focus_restore_failed", correlation_id=correlation_id)

            time.sleep(0.02)

            for attempt in range(2):
                tool = self._keyboard
                if tool is None:
                    logger.error("no_keyboard_tool_available", attempt=attempt)
                    break

                try:
                    ok = _send_ctrl_v(tool)
                    if ok:
                        time.sleep(0.08)
                        logger.info(
                            "text_injected",
                            correlation_id=correlation_id,
                            attempt=attempt + 1,
                            chars=len(text),
                            tool=tool.value,
                        )
                        _last_injected_text = text
                        _last_injected_field_info = field_info or {}
                        _last_injected_window = window_before
                        _last_injected_correlation_id = correlation_id
                        return True, "Text injected successfully."
                    else:
                        logger.warning("ctrl_v_failed", attempt=attempt + 1, tool=tool.value)
                        if attempt == 0:
                            time.sleep(0.1)
                            _clipboard_copy(text, self._session)
                except Exception:
                    logger.error("injection_attempt_failed", attempt=attempt + 1, exc_info=True)
                    if attempt == 0:
                        time.sleep(0.1)
                        _clipboard_copy(text, self._session)

            _clipboard_copy(text, self._session)
            logger.warning("paste_blocked_copied_only", correlation_id=correlation_id)
            return False, "Paste blocked - text copied to clipboard"

        except Exception:
            logger.error("text_injection_failed", correlation_id=correlation_id, exc_info=True)
            return False, "Injection failed"

        finally:
            # Restore previous clipboard.
            if previous_clipboard is not None:
                try:
                    _clipboard_copy(previous_clipboard, self._session)
                except Exception:
                    pass

    def undo_last_inject(self) -> tuple[bool, str]:
        """
        Undo the last injection by restoring the previous clipboard content.
        Returns (success, message).
        """
        global _last_undo_content
        if _last_undo_content is None:
            return False, "No undo available - nothing was copied before last injection"
        try:
            _clipboard_copy(_last_undo_content, self._session)
            _last_undo_content = None
            logger.info("undo_inject_success")
            return True, "Previous clipboard restored. Paste to recover."
        except Exception:
            logger.error("undo_inject_failed", exc_info=True)
            return False, "Undo failed"

    def get_last_injected_text(self) -> str:
        global _last_injected_text
        return _last_injected_text or ""

    def _send_backspaces(self, count: int) -> tuple[bool, str]:
        """Send *count* Backspace keypresses. Returns (success, message)."""
        if count <= 0:
            return False, "Nothing to delete"
        if count > 2000:
            return False, "Refusing to delete too much text at once"

        tool = self._keyboard
        if tool is None:
            return False, "No keyboard tool available"

        try:
            for i in range(count):
                _send_backspace_key(tool)
                time.sleep(0.005)  # 5 ms between backspaces
            return True, f"Deleted {count} characters"
        except Exception:
            logger.error("backspace_injection_failed", count=count, exc_info=True)
            return False, "Delete failed"

    def scratch_that(self, correlation_id: str | None = None) -> tuple[bool, str]:
        """Delete the last injected text by sending backspace N times."""
        global _last_injected_text, _last_injected_window, _last_injected_correlation_id
        text = (_last_injected_text or "").strip()
        if not text:
            return False, "No previous injection to scratch"
        if correlation_id is not None and _last_injected_correlation_id != correlation_id:
            return False, "Scratch that is only allowed for the active recording session"

        # Verify we are still targeting the same window.
        try:
            current_win = _get_active_window_id(self._session)
        except Exception:
            current_win = None
        if _last_injected_window is not None and current_win != _last_injected_window:
            return False, "Scratch that is only allowed in the original target window"

        ok, msg = self._send_backspaces(len(text))
        if ok:
            _last_injected_text = None
            _last_injected_window = None
            _last_injected_correlation_id = None
        return ok, msg

    def replace_last_injected(
        self, old: str, new: str, correlation_id: str | None = None
    ) -> tuple[bool, str]:
        """
        Apply voice edit command: change *old* to *new* on the last injected text.
        Replaces first case-insensitive match, rewrites text in-place.
        """
        global _last_injected_text, _last_injected_correlation_id
        import re as _re

        current = (_last_injected_text or "").strip()
        if not current:
            return False, "No previous injection to edit"
        if not old.strip():
            return False, "Missing source text for change command"
        if correlation_id is not None and _last_injected_correlation_id != correlation_id:
            return False, "Edit is only allowed for the active recording session"

        pattern = _re.compile(_re.escape(old.strip()), _re.IGNORECASE)
        if not pattern.search(current):
            return False, f"Could not find '{old}' in last text"

        rewritten = pattern.sub(new.strip(), current, count=1)

        last_win = _last_injected_window
        last_field = _last_injected_field_info

        if last_win is None:
            return False, "No reliable context for edit — please edit manually"

        original = current
        try:
            # Attempt focus restoration.
            restored = True
            if last_field:
                try:
                    from plat.linux_window import restore_focus_and_click
                    restored = restore_focus_and_click(last_field)
                except Exception:
                    restored = False

            try:
                current_win = _get_active_window_id(self._session)
            except Exception:
                current_win = None

            if not restored or current_win != last_win:
                return False, "Could not restore focus to original target — manual edit required"

            ok, msg = self._send_backspaces(len(current))
            if not ok:
                return False, msg

            try:
                current_win = _get_active_window_id(self._session)
            except Exception:
                current_win = None
            if current_win != last_win:
                return False, "Target window changed during edit — manual edit required"

            inject_ok, inject_msg = self.inject(
                rewritten, correlation_id=correlation_id, field_info=last_field
            )
            if not inject_ok:
                try:
                    self.inject(original, correlation_id=None, field_info=last_field)
                except Exception:
                    pass
                return False, inject_msg

            return True, "Applied change command"
        except Exception:
            logger.exception("replace_last_injected_failed")
            return False, "Edit failed"

    def get_undo_available(self) -> bool:
        """Check if undo is available."""
        global _last_undo_content
        return _last_undo_content is not None
