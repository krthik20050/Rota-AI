import ctypes
import ctypes.wintypes
import re
import time

import pyperclip
import structlog

logger = structlog.get_logger(__name__)

_last_undo_content: str | None = None
_last_injected_text: str | None = None
_last_injected_field_info = None
_last_injected_hwnd = None
_last_injected_correlation_id: str | None = None


# SECURITY: Maximum injection length to prevent abuse
_MAX_INJECT_LENGTH = 5000  # characters

# SECURITY: Terminal process names — injecting here can execute arbitrary commands
_TERMINAL_PROCESS_NAMES = frozenset(
    {
        "cmd.exe",
        "powershell.exe",
        "pwsh.exe",
        "wt.exe",
        "windowsterminal.exe",
        "bash.exe",
        "sh.exe",
        "python.exe",
        "python3.exe",
        "pythonw.exe",
        "node.exe",
        "git-bash.exe",
        "mintty.exe",
    }
)


def _get_foreground_process_name() -> str:
    """Return the exe name of the foreground window's process (lowercase), or ''."""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return ""
        pid = ctypes.wintypes.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value
        )
        if not handle:
            return ""
        try:
            buf = ctypes.create_unicode_buffer(512)
            size = ctypes.wintypes.DWORD(512)
            ctypes.windll.kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size))
            exe = buf.value
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
        return exe.split("\\")[-1].lower() if exe else ""
    except Exception:
        return ""


"""
Text injection module — injects text into the active window via clipboard + Ctrl+V.

SECURITY CONSIDERATIONS:
- This module can inject arbitrary text into ANY application that has focus.
- If the transcription/AI pipeline is compromised (prompt injection), this becomes
  a code execution vector (terminal commands, SQL, URLs, etc.).
- Mitigations: max injection length, clipboard restore, target window validation
- TODO: Add target application allowlist, warn before injecting into terminals
"""


class TextInjector:
    """
    Injects text into the active window via clipboard + Ctrl+V.

    WHY no caret check: GetGUIThreadInfo only detects Win32 carets.
    Chrome, Firefox, VS Code, Electron, and Windows Terminal all use
    their own text models — hwndCaret is always 0 in those apps.
    Checking for it silently blocks injection in 90% of real targets.
    Instead we just paste. If nothing is focused, Ctrl+V is a no-op.
    """

    def _has_active_window(self):
        try:
            return bool(ctypes.windll.user32.GetForegroundWindow())
        except Exception:
            logger.exception("foreground_window_check_failed")
            return False

    def is_text_field_active(self):
        """Compatibility method for diagnostic tools. Returns True if any window is active."""
        return self._has_active_window()

    def inject(
        self,
        text: str,
        correlation_id: str | None = None,
        field_info: dict | None = None,
        use_paste_shortcut: bool = True,
    ) -> tuple[bool, str]:
        """
        Attempts to inject text into the currently active window.
        Returns (success: bool, message: str).
        """
        if not text:
            return False, "No text to inject"

        # SECURITY: Enforce maximum injection length
        if len(text) > _MAX_INJECT_LENGTH:
            logger.warning("injection_too_long", length=len(text), max=_MAX_INJECT_LENGTH)
            text = text[:_MAX_INJECT_LENGTH]

        # Log a warning when injecting into terminals (informational only — not blocked).
        proc = _get_foreground_process_name()
        if proc in _TERMINAL_PROCESS_NAMES:
            logger.warning(
                "injection_target_is_terminal", process=proc, correlation_id=correlation_id
            )

        previous_clipboard = None
        hwnd_before = None
        try:
            global \
                _last_undo_content, \
                _last_injected_text, \
                _last_injected_field_info, \
                _last_injected_hwnd, \
                _last_injected_correlation_id

            # Save current clipboard for undo capability.
            try:
                previous_clipboard = pyperclip.paste()
                _last_undo_content = previous_clipboard
            except Exception:
                previous_clipboard = None
                _last_undo_content = None

            try:
                hwnd_before = ctypes.windll.user32.GetForegroundWindow()
            except Exception:
                hwnd_before = None
            if not hwnd_before:
                logger.warning("no_active_window_for_injection", correlation_id=correlation_id)
                pyperclip.copy(text)
                return False, "No active window — copied to clipboard"

            pyperclip.copy(text)

            if not use_paste_shortcut:
                return False, "Copied to clipboard"

            if field_info:
                try:
                    from injection.field_detector import restore_focus_and_click

                    restored = restore_focus_and_click(field_info)
                    if not restored:
                        logger.warning(
                            "focus_restore_skipped_or_failed", correlation_id=correlation_id
                        )
                except Exception:
                    logger.exception("focus_restore_failed", correlation_id=correlation_id)

            time.sleep(0.01)

            for attempt in range(2):
                try:
                    # Send Ctrl+V using native Windows keybd_event.
                    # WHY: Avoids importing/using python-keyboard package which initializes
                    # its own low-level hook thread and causes 0x8001010d / access violation crashes.
                    VK_CONTROL = 0x11
                    VK_V = 0x56
                    KEYEVENTF_KEYUP = 0x0002
                    ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(VK_V, 0, 0, 0)
                    time.sleep(0.01)
                    ctypes.windll.user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
                    ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
                    time.sleep(0.05)
                    logger.info(
                        "text_injected",
                        correlation_id=correlation_id,
                        attempt=attempt + 1,
                        chars=len(text),
                    )
                    _last_injected_text = text
                    _last_injected_field_info = field_info or {}
                    _last_injected_hwnd = hwnd_before
                    _last_injected_correlation_id = correlation_id
                    return True, "Text injected successfully."
                except Exception:
                    logger.error(
                        "ctrl_v_injection_failed",
                        correlation_id=correlation_id,
                        attempt=attempt + 1,
                        exc_info=True,
                    )
                    if attempt == 0:
                        time.sleep(0.1)
                        pyperclip.copy(text)

            pyperclip.copy(text)
            logger.warning("paste_blocked_copied_only", correlation_id=correlation_id)
            return False, "Paste blocked - text copied to clipboard"

        except Exception:
            logger.error("text_injection_failed", correlation_id=correlation_id, exc_info=True)
            return False, "Injection failed"

        finally:
            # Restore previous clipboard. Wait an additional 100 ms here so
            # slow apps (Electron, browsers) have time to process the Ctrl+V
            # message before we overwrite the clipboard contents.
            if previous_clipboard is not None:
                try:
                    time.sleep(0.1)
                    pyperclip.copy(previous_clipboard)
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
            pyperclip.copy(_last_undo_content)
            _last_undo_content = None  # Clear after use
            logger.info("undo_inject_success")
            return True, "Previous clipboard restored. Paste to recover."
        except Exception as e:
            logger.error("undo_inject_failed", error=str(e))
            return False, f"Undo failed: {e}"

    def get_last_injected_text(self) -> str:
        global _last_injected_text
        return _last_injected_text or ""

    def _send_backspaces(self, count: int) -> tuple[bool, str]:
        if count <= 0:
            return False, "Nothing to delete"
        if count > 2000:
            return False, "Refusing to delete too much text at once"
        try:
            # Send Backspace events using native Windows keybd_event.
            # WHY: Lightweight, synchronous keystroke simulation with zero hook conflicts.
            VK_BACK = 0x08
            KEYEVENTF_KEYUP = 0x0002
            for _ in range(count):
                ctypes.windll.user32.keybd_event(VK_BACK, 0, 0, 0)
                time.sleep(0.002)
                ctypes.windll.user32.keybd_event(VK_BACK, 0, KEYEVENTF_KEYUP, 0)
                time.sleep(0.005)  # 5ms delay between backspaces for reliability
            return True, f"Deleted {count} characters"
        except Exception as e:
            logger.error("backspace_injection_failed", error=str(e))
            return False, f"Delete failed: {e}"

    def scratch_that(self, correlation_id: str | None = None) -> tuple[bool, str]:
        """Delete the last injected text by sending backspace N times."""
        global _last_injected_text, _last_injected_hwnd, _last_injected_correlation_id
        text = (_last_injected_text or "").strip()
        if not text:
            return False, "No previous injection to scratch"
        if correlation_id is not None and _last_injected_correlation_id != correlation_id:
            return False, "Scratch that is only allowed for the active recording session"

        try:
            current_hwnd = ctypes.windll.user32.GetForegroundWindow()
        except Exception:
            current_hwnd = None
        if _last_injected_hwnd is not None and current_hwnd != _last_injected_hwnd:
            return False, "Scratch that is only allowed in the original target window"

        ok, msg = self._send_backspaces(len(text))
        if ok:
            _last_injected_text = None
            _last_injected_hwnd = None
            _last_injected_correlation_id = None
        return ok, msg

    def replace_last_injected(
        self, old: str, new: str, correlation_id: str | None = None
    ) -> tuple[bool, str]:
        """
        Apply voice edit command: change X to Y on the last injected text.
        Replaces first case-insensitive match, rewrites text in-place.
        """
        global _last_injected_text, _last_injected_correlation_id
        current = (_last_injected_text or "").strip()
        if not current:
            return False, "No previous injection to edit"
        if not old.strip():
            return False, "Missing source text for change command"
        if correlation_id is not None and _last_injected_correlation_id != correlation_id:
            return False, "Edit is only allowed for the active recording session"

        pattern = re.compile(re.escape(old.strip()), re.IGNORECASE)
        if not pattern.search(current):
            return False, f"Could not find '{old}' in last text"

        rewritten = pattern.sub(new.strip(), current, count=1)

        # SECURITY: only perform destructive replace if we can restore focus
        # to the same window the last injection targeted. This prevents
        # cross-window data loss when focus has moved.
        last_hwnd = _last_injected_hwnd
        last_field = _last_injected_field_info

        if last_hwnd is None:
            return False, "No reliable context for edit — please edit manually"

        original = current
        try:
            # Attempt to restore focus to the original field if we have info.
            restored = True
            if last_field:
                try:
                    from injection.field_detector import restore_focus_and_click

                    restored = restore_focus_and_click(last_field)
                except Exception:
                    restored = False

            try:
                current_hwnd = ctypes.windll.user32.GetForegroundWindow()
            except Exception:
                current_hwnd = None

            if not restored or current_hwnd != last_hwnd:
                return False, "Could not restore focus to original target — manual edit required"

            ok, msg = self._send_backspaces(len(current))
            if not ok:
                return False, msg

            try:
                current_hwnd = ctypes.windll.user32.GetForegroundWindow()
            except Exception:
                current_hwnd = None
            if current_hwnd != last_hwnd:
                return False, "Target window changed during edit — manual edit required"

            inject_ok, inject_msg = self.inject(
                rewritten, correlation_id=correlation_id, field_info=last_field
            )
            if not inject_ok:
                try:
                    pyperclip.copy(original)
                    self.inject(original, correlation_id=None, field_info=last_field)
                except Exception:
                    pass
                return False, inject_msg

            return True, "Applied change command"
        except Exception as exc:
            logger.exception("replace_last_injected_failed")
            return False, f"Edit failed: {exc}"

    def get_undo_available(self) -> bool:
        """Check if undo is available."""
        global _last_undo_content
        return _last_undo_content is not None
