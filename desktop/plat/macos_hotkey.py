"""
macOS global-hotkey backend — dual backend (pynput + Quartz CGEventTap).

Provides two hotkey listening strategies:
  1. pynput backend — Uses pynput's keyboard.Listener + keyboard.HotKey.
     Simpler, works for most hotkeys. Requires Accessibility permission.
  2. Quartz CGEventTap backend — Uses Quartz event taps for lower-level capture.
     More reliable for complex key combos. Requires Input Monitoring permission.

Interface matches the Windows HotkeyHandler and Linux HotkeyHandler.

Reference: VoiceType macOS backend (Honeybee1023/VoiceType)
           pynput macOS backend (pynput/keyboard/_darwin.py)
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable

import structlog

logger = structlog.get_logger(__name__)

try:
    from pynput import keyboard as pynput_keyboard
except Exception:
    pynput_keyboard = None


# ---------------------------------------------------------------------------
# Quartz CGEventTap backend
# ---------------------------------------------------------------------------

# USB HID keycode mapping (same as VoiceType's keycode_map)
_KEYCODE_MAP: dict[str, int] = {
    "a": 0,
    "s": 1,
    "d": 2,
    "f": 3,
    "h": 4,
    "g": 5,
    "z": 6,
    "x": 7,
    "c": 8,
    "v": 9,
    "b": 11,
    "q": 12,
    "w": 13,
    "e": 14,
    "r": 15,
    "y": 16,
    "t": 17,
    "1": 18,
    "2": 19,
    "3": 20,
    "4": 21,
    "6": 22,
    "5": 23,
    "=": 24,
    "9": 25,
    "7": 26,
    "-": 27,
    "8": 28,
    "0": 29,
    "]": 30,
    "o": 31,
    "u": 32,
    "[": 33,
    "i": 34,
    "p": 35,
    "l": 37,
    "j": 38,
    "'": 39,
    "k": 40,
    ";": 41,
    "\\": 42,
    ",": 43,
    "/": 44,
    "n": 45,
    "m": 46,
    ".": 47,
    "`": 50,
    # Additional keys
    "tab": 48,
    "space": 49,
    "enter": 36,
    "return": 36,
    "backspace": 51,
    "delete": 51,
    "esc": 53,
    "escape": 53,
    "up": 126,
    "down": 125,
    "left": 123,
    "right": 124,
    "home": 115,
    "end": 119,
    "pageup": 116,
    "pagedown": 121,
}
# F1-F12 (correct Quartz virtual keycodes)
_KEYCODE_MAP["f1"] = 0x7A  # 122
_KEYCODE_MAP["f2"] = 0x78  # 120
_KEYCODE_MAP["f3"] = 0x63  # 99
_KEYCODE_MAP["f4"] = 0x76  # 118
_KEYCODE_MAP["f5"] = 0x60  # 96
_KEYCODE_MAP["f6"] = 0x61  # 97
_KEYCODE_MAP["f7"] = 0x62  # 98
_KEYCODE_MAP["f8"] = 0x64  # 100
_KEYCODE_MAP["f9"] = 0x65  # 101
_KEYCODE_MAP["f10"] = 0x6D  # 109
_KEYCODE_MAP["f11"] = 0x67  # 103
_KEYCODE_MAP["f12"] = 0x6F  # 111


def _parse_hotkey_str(hotkey: str) -> tuple[frozenset[str], str]:
    """Parse 'ctrl+shift+r' -> (frozenset({'ctrl','shift'}), 'r')."""
    known_mods = {"ctrl", "shift", "alt", "meta", "cmd", "command", "option"}
    parts = hotkey.lower().strip().split("+")
    mods = frozenset(p.strip() for p in parts if p.strip() in known_mods)
    main = next((p.strip() for p in parts if p.strip() not in known_mods), "")
    return mods, main


def _parse_quartz_hotkey(hotkey: str) -> tuple[int, int] | None:
    """
    Parse a hotkey string like '<ctrl>+<shift>+r' into (Quartz modifier flags, keycode).
    Returns None if the hotkey can't be parsed.
    """
    parts = [p.strip().lower() for p in hotkey.split("+") if p.strip()]
    if not parts:
        return None

    required_flags = 0
    key_part = None

    for part in parts:
        # Strip angle brackets if present (<ctrl> -> ctrl)
        if part.startswith("<") and part.endswith(">"):
            part = part[1:-1]

        if part in {"ctrl", "control"}:
            required_flags |= 1 << 18  # kCGEventFlagMaskControl (0x40000)
        elif part == "shift":
            required_flags |= 1 << 17  # kCGEventFlagMaskShift (0x20000)
        elif part in {"cmd", "command", "meta"}:
            required_flags |= 1 << 20  # kCGEventFlagMaskCommand (0x100000)
        elif part in {"alt", "option"}:
            required_flags |= 1 << 19  # kCGEventFlagMaskAlternate (0x80000)
        else:
            key_part = part

    if key_part is None:
        return None

    keycode = _KEYCODE_MAP.get(key_part)
    if keycode is None:
        logger.warning("quartz_hotkey: unknown key '%s'", key_part)
        return None

    return required_flags, keycode


def _quartz_hotkey_loop(
    hotkey: str,
    on_trigger: Callable[[], None],
    stop_event: threading.Event | None = None,
) -> None:
    """
    Run a Quartz CGEventTap hotkey listener on the current thread.
    This blocks — it runs a CFRunLoop. Call it on a dedicated thread.
    stop_event: set it to request a clean shutdown.
    """
    try:
        import Quartz
    except ImportError as exc:
        logger.error("Quartz not available (install pyobjc-framework-Quartz): %s", exc)
        return

    parsed = _parse_quartz_hotkey(hotkey)
    if parsed is None:
        logger.error("Quartz hotkey: cannot parse hotkey '%s'", hotkey)
        return

    required_flags, target_keycode = parsed
    _fired = threading.Event()

    def callback(_proxy, event_type, event, _refcon):
        if event_type == Quartz.kCGEventKeyDown:
            flags = Quartz.CGEventGetFlags(event)
            if (flags & required_flags) == required_flags:
                event_keycode = Quartz.CGEventGetIntegerValueField(
                    event, Quartz.kCGKeyboardEventKeycode
                )
                if event_keycode == target_keycode:
                    _fired.set()
        return event

    mask = Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown)
    tap = Quartz.CGEventTapCreate(
        Quartz.kCGSessionEventTap,
        Quartz.kCGHeadInsertEventTap,
        Quartz.kCGEventTapOptionListenOnly,
        mask,
        callback,
        None,
    )
    if tap is None:
        logger.error(
            "Quartz hotkey: CGEventTapCreate failed. "
            "Check Input Monitoring permission in System Settings."
        )
        return

    run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
    Quartz.CFRunLoopAddSource(
        Quartz.CFRunLoopGetCurrent(),
        run_loop_source,
        Quartz.kCFRunLoopCommonModes,
    )
    Quartz.CGEventTapEnable(tap, True)

    logger.info("Quartz hotkey listener started for '%s'", hotkey)
    while stop_event is None or not stop_event.is_set():
        Quartz.CFRunLoopRunInMode(Quartz.kCFRunLoopDefaultMode, 0.1, False)
        if _fired.is_set():
            _fired.clear()
            try:
                on_trigger()
            except Exception:
                logger.exception("quartz_hotkey_callback_failed")

    Quartz.CGEventTapEnable(tap, False)
    logger.info("Quartz hotkey listener stopped for '%s'", hotkey)


# ---------------------------------------------------------------------------
# capture_hotkey — record the next key combination the user presses
# ---------------------------------------------------------------------------


def capture_hotkey(timeout: float = 8.0) -> str | None:
    """
    Record the next key combination the user presses.
    Temporarily installs a pynput keyboard listener, waits for a key press,
    and returns the canonical hotkey string (e.g. 'ctrl+shift+k', 'tab').

    Pressing Escape cancels and returns None.

    Args:
        timeout: Seconds to wait before giving up.

    Returns:
        Hotkey string like 'ctrl+k', 'tab', 'f9', or None if cancelled/timeout.
    """
    if pynput_keyboard is None:
        logger.error("capture_hotkey: pynput not available")
        return None

    result = {"hotkey": None}
    done = threading.Event()
    held_mods: set[str] = set()

    def _key_name(key) -> str | None:
        """Convert a pynput key to its canonical name."""
        try:
            # Named special keys
            special = {
                pynput_keyboard.Key.tab: "tab",
                pynput_keyboard.Key.space: "space",
                pynput_keyboard.Key.enter: "enter",
                pynput_keyboard.Key.backspace: "backspace",
                pynput_keyboard.Key.esc: "esc",
                pynput_keyboard.Key.delete: "delete",
                pynput_keyboard.Key.home: "home",
                pynput_keyboard.Key.end: "end",
                pynput_keyboard.Key.page_up: "pageup",
                pynput_keyboard.Key.page_down: "pagedown",
                pynput_keyboard.Key.up: "up",
                pynput_keyboard.Key.down: "down",
                pynput_keyboard.Key.left: "left",
                pynput_keyboard.Key.right: "right",
                pynput_keyboard.Key.caps_lock: "capslock",
                pynput_keyboard.Key.cmd: "cmd",
                pynput_keyboard.Key.cmd_l: "cmd",
                pynput_keyboard.Key.cmd_r: "cmd",
                pynput_keyboard.Key.ctrl: "ctrl",
                pynput_keyboard.Key.ctrl_l: "ctrl",
                pynput_keyboard.Key.ctrl_r: "ctrl",
                pynput_keyboard.Key.shift: "shift",
                pynput_keyboard.Key.shift_l: "shift",
                pynput_keyboard.Key.shift_r: "shift",
                pynput_keyboard.Key.alt: "alt",
                pynput_keyboard.Key.alt_l: "alt",
                pynput_keyboard.Key.alt_r: "alt",
                pynput_keyboard.Key.alt_gr: "alt",
            }
            if key in special:
                return special[key]
            # Function keys
            for i in range(1, 25):
                fk = getattr(pynput_keyboard.Key, f"f{i}", None)
                if key == fk:
                    return f"f{i}"
            # Character key
            char = getattr(key, "char", None)
            if char:
                return char.lower()
        except Exception:
            pass
        return None

    def on_press(key):
        name = _key_name(key)
        if name is None:
            return True
        if name == "esc":
            result["hotkey"] = None
            done.set()
            return False
        is_mod = name in {"ctrl", "shift", "alt", "cmd", "meta"}
        if is_mod:
            held_mods.add(name)
            return True
        # Main key found — build hotkey string
        parts = []
        for mod in ("ctrl", "shift", "alt", "cmd"):
            if mod in held_mods:
                parts.append(mod)
        parts.append(name)
        result["hotkey"] = "+".join(parts)
        done.set()
        return False

    def on_release(key):
        name = _key_name(key)
        if name in {"ctrl", "shift", "alt", "cmd", "meta"}:
            held_mods.discard(name)

    try:
        listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.daemon = True
        listener.start()
        done.wait(timeout=timeout)
        listener.stop()
    except Exception:
        logger.exception("capture_hotkey failed")

    return result["hotkey"]


# ---------------------------------------------------------------------------
# HotkeyHandler — drop-in compatible with Windows/Linux HotkeyHandler
# ---------------------------------------------------------------------------


class HotkeyHandler:
    """
    macOS global-hotkey handler.

    Supports dual backends selected at construction time:
      backend="pynput" — Uses pynput keyboard.Listener (default).
      backend="quartz" — Uses Quartz CGEventTap.
      backend="both"   — Starts both (redundant but maximum reliability).

    Drop-in compatible with the Windows HotkeyHandler and Linux HotkeyHandler.
    """

    MODE_TOGGLE = "toggle"
    MODE_HOLD = "hold"

    HOLD_COMPAT_THRESHOLD = 3.0  # seconds; hold longer → keep recording on release

    def __init__(
        self,
        hotkey: str = "tab",
        mode: str = MODE_TOGGLE,
        backend: str = "pynput",
        start_callback: Callable[[], None] | None = None,
        stop_callback: Callable[[], None] | None = None,
        error_callback: Callable[[Exception], None] | None = None,
    ):
        self.hotkey = (hotkey or "tab").lower()
        self._hotkey_mods, self._hotkey_main = _parse_hotkey_str(self.hotkey)
        self.mode = mode
        self._backend = backend
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.error_callback = error_callback

        self.backend = None
        self._listener_thread: threading.Thread | None = None
        self._listener_stop = threading.Event()

        self._is_recording = False
        self._is_key_pressed = False
        self._press_time: float | None = None
        self._started_this_press = False
        self._lock = threading.Lock()

        self._pynput_listener = None
        self._held_mods: set[str] = set()
        self._extra_hotkeys: list[tuple[frozenset[str], str, Callable[[], None]]] = []

    @property
    def is_recording(self) -> bool:
        with self._lock:
            return self._is_recording

    def add_hotkey(self, hotkey_str: str, callback: Callable[[], None]) -> None:
        mods, main = _parse_hotkey_str(hotkey_str.lower())
        self._extra_hotkeys.append((mods, main, callback))
        logger.info("extra_hotkey_added", hotkey=hotkey_str)

    def set_mode(self, mode: str) -> None:
        if mode not in (self.MODE_HOLD, self.MODE_TOGGLE):
            return
        action = None
        with self._lock:
            if self._is_recording:
                self._is_recording = False
                action = self.stop_callback
            self._is_key_pressed = False
            self.mode = mode
        if action:
            action()

    # ------------------------------------------------------------------
    # pynput backend
    # ------------------------------------------------------------------

    def _matches_pynput_key(self, key) -> bool:
        """True if key is the trigger key AND all required modifiers are held."""
        mods, main = self._hotkey_mods, self._hotkey_main

        matched_main = False
        named = getattr(pynput_keyboard.Key, main, None)
        if named is not None:
            matched_main = key == named
        else:
            matched_main = (getattr(key, "char", None) or "").lower() == main

        if not matched_main:
            return False
        return self._held_mods >= mods

    def _get_pynput_mod_map(self) -> dict[str, set]:
        if pynput_keyboard is None:
            return {}
        Key = pynput_keyboard.Key
        return {
            "ctrl": {Key.ctrl, Key.ctrl_l, Key.ctrl_r},
            "shift": {Key.shift, Key.shift_l, Key.shift_r},
            "alt": {Key.alt, Key.alt_l, Key.alt_r, Key.alt_gr},
            "cmd": {Key.cmd, Key.cmd_l, Key.cmd_r},
        }

    def _pynput_mod_name(self, key) -> str | None:
        mod_map = self._get_pynput_mod_map()
        for name, key_set in mod_map.items():
            if key in key_set:
                return name
        return None

    def _handle_press(self):
        action = None
        with self._lock:
            if self._is_key_pressed:
                return
            self._is_key_pressed = True
            self._press_time = time.monotonic()

            if self.mode == self.MODE_HOLD:
                if not self._is_recording:
                    self._is_recording = True
                    action = self.start_callback
            elif self.mode == self.MODE_TOGGLE:
                if not self._is_recording:
                    self._is_recording = True
                    self._started_this_press = True
                    action = self.start_callback
                else:
                    self._started_this_press = False
        if action:
            action()

    def _handle_release(self):
        action = None
        with self._lock:
            self._is_key_pressed = False
            press_time = self._press_time
            self._press_time = None

            if self.mode == self.MODE_HOLD:
                if self._is_recording:
                    self._is_recording = False
                    action = self.stop_callback
            elif self.mode == self.MODE_TOGGLE:
                if self._started_this_press:
                    self._started_this_press = False
                elif self._is_recording:
                    held = (time.monotonic() - press_time) if press_time is not None else 0.0
                    if held >= self.HOLD_COMPAT_THRESHOLD:
                        logger.debug("hold_compat: ignoring release, recording stays on")
                    else:
                        self._is_recording = False
                        action = self.stop_callback
        if action:
            action()

    def _on_pynput_press(self, key):
        try:
            mod_name = self._pynput_mod_name(key)
            if mod_name:
                self._held_mods.add(mod_name)
            if self._matches_pynput_key(key):
                self._handle_press()
            # Fire extra hotkeys
            for mods, main, callback in self._extra_hotkeys:
                if not (self._held_mods >= mods):
                    continue
                named = getattr(pynput_keyboard.Key, main, None)
                if named is not None:
                    matched = key == named
                else:
                    matched = (getattr(key, "char", None) or "").lower() == main
                if matched:
                    try:
                        callback()
                    except Exception:
                        logger.exception("extra_hotkey_callback_failed")
        except Exception as exc:
            if self.error_callback:
                self.error_callback(exc)

    def _on_pynput_release(self, key):
        try:
            if self._matches_pynput_key(key):
                self._handle_release()
            mod_name = self._pynput_mod_name(key)
            if mod_name:
                self._held_mods.discard(mod_name)
        except Exception as exc:
            if self.error_callback:
                self.error_callback(exc)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start_listening(self) -> None:
        """Start listening for the global hotkey."""
        self.stop_listening()
        errors = []

        if self._backend in ("pynput", "both"):
            if pynput_keyboard is not None:
                try:
                    self._pynput_listener = pynput_keyboard.Listener(
                        on_press=self._on_pynput_press,
                        on_release=self._on_pynput_release,
                    )
                    self._pynput_listener.daemon = True
                    self._pynput_listener.start()
                    self.backend = "pynput"
                    logger.info("global_hotkey_started", backend="pynput", hotkey=self.hotkey)
                except Exception as exc:
                    errors.append(exc)
                    logger.exception("pynput_hotkey_start_failed")

        if self._backend in ("quartz", "both"):
            try:
                self._listener_stop.clear()
                self._listener_thread = threading.Thread(
                    target=_quartz_hotkey_loop,
                    args=(
                        self.hotkey,
                        lambda: self._handle_press()
                        if not self.is_recording
                        else self._handle_release(),
                        self._listener_stop,
                    ),
                    daemon=True,
                )
                self._listener_thread.start()
                if self.backend is None:
                    self.backend = "quartz"
                else:
                    self.backend = "both"
                logger.info("global_hotkey_started", backend="quartz", hotkey=self.hotkey)
            except Exception as exc:
                errors.append(exc)
                logger.exception("quartz_hotkey_start_failed")

        if self.backend is None:
            raise RuntimeError(
                f"Global hotkey listener could not start on macOS "
                f"(tried: {self._backend}). "
                f"Ensure Accessibility (pynput) and/or Input Monitoring (Quartz) permissions are granted."
            ) from (errors[-1] if errors else None)

    def stop_listening(self) -> None:
        """Stop listening for the global hotkey."""
        if self._pynput_listener is not None:
            try:
                self._pynput_listener.stop()
            except Exception:
                logger.exception("pynput_hotkey_stop_failed")
            self._pynput_listener = None

        self._listener_stop.set()
        self._listener_thread = None

        self.backend = None
        self._held_mods.clear()
        self._extra_hotkeys.clear()
        with self._lock:
            self._is_key_pressed = False
            self._is_recording = False
            self._press_time = None
            self._started_this_press = False

    def is_healthy(self) -> bool:
        if self.backend == "pynput" and self._pynput_listener is not None:
            return bool(self._pynput_listener.running)
        if self.backend == "quartz" and self._listener_thread is not None:
            return self._listener_thread.is_alive()
        if self.backend == "both":
            pynput_ok = self._pynput_listener is not None and self._pynput_listener.running
            quartz_ok = self._listener_thread is not None and self._listener_thread.is_alive()
            return pynput_ok or quartz_ok
        return False

    @classmethod
    def capture_hotkey(cls, timeout: float = 8.0) -> str | None:
        """Classmethod wrapper for cross-platform API compatibility."""
        return capture_hotkey(timeout=timeout)
