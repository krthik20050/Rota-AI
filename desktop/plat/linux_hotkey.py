"""
Linux global-hotkey backend using evdev.

Reads keyboard events directly from /dev/input devices via the evdev library.
Works on both X11 and Wayland since evdev operates at the kernel input layer.

Requires:
    - pip install evdev
    - The user must have read access to /dev/input/event* (usually via the
      'input' group, or running as root).

Interface matches the Windows HotkeyHandler so it can be swapped in directly.
"""
from __future__ import annotations

import glob
import os
import threading
import time
from typing import Callable

import structlog

logger = structlog.get_logger(__name__)

try:
    import evdev
    from evdev import ecodes, InputDevice, list_devices
except ImportError:
    evdev = None  # type: ignore[assignment]

try:
    import pynput as _pynput_available
except ImportError:
    _pynput_available = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# pynput key → canonical name mapping
# ---------------------------------------------------------------------------

def _build_pynput_key_map() -> dict:
    """Build {pynput.Key.xxx: canonical_name} mapping."""
    if _pynput_available is None:
        return {}
    from pynput.keyboard import Key
    m: dict = {
        Key.ctrl: "ctrl", Key.ctrl_l: "ctrl", Key.ctrl_r: "ctrl",
        Key.shift: "shift", Key.shift_l: "shift", Key.shift_r: "shift",
        Key.alt: "alt", Key.alt_l: "alt", Key.alt_r: "alt",
        Key.alt_gr: "alt", Key.cmd: "meta", Key.cmd_l: "meta", Key.cmd_r: "meta",
        Key.tab: "tab", Key.space: "space", Key.enter: "enter",
        Key.backspace: "backspace", Key.esc: "esc",
        Key.delete: "delete", Key.insert: "insert",
        Key.home: "home", Key.end: "end",
        Key.page_up: "pageup", Key.page_down: "pagedown",
        Key.up: "up", Key.down: "down", Key.left: "left", Key.right: "right",
        Key.caps_lock: "capslock", Key.num_lock: "numlock",
        Key.scroll_lock: "scrolllock", Key.pause: "pause",
        Key.print_screen: "sysrq",
    }
    for i in range(1, 25):
        fkey = getattr(Key, f"f{i}", None)
        if fkey is not None:
            m[fkey] = f"f{i}"
    return m


_PYNPUT_KEY_MAP: dict = {}


def _pynput_key_name(key) -> str | None:
    """Convert a pynput key event to a canonical name string."""
    global _PYNPUT_KEY_MAP
    if not _PYNPUT_KEY_MAP:
        _PYNPUT_KEY_MAP = _build_pynput_key_map()
    name = _PYNPUT_KEY_MAP.get(key)
    if name:
        return name
    # Regular character key
    if _pynput_available is not None:
        from pynput.keyboard import KeyCode
        if isinstance(key, KeyCode) and key.char:
            return key.char.lower()
    return None

# ---------------------------------------------------------------------------
# evdev key-code → canonical name mapping
# We only map the keys we care about for hotkey matching, not the entire
# ecodes table.
# ---------------------------------------------------------------------------

def _build_key_lookup() -> dict[int, str]:
    """Build {evdev_key_code: lowercase_name} for keys referenced in hotkeys."""
    lookup: dict[int, str] = {}
    # Modifier keys (left and right)
    for prefix, base in [
        ("KEY_LEFTCTRL", "ctrl"), ("KEY_RIGHTCTRL", "ctrl"),
        ("KEY_LEFTSHIFT", "shift"), ("KEY_RIGHTSHIFT", "shift"),
        ("KEY_LEFTALT", "alt"), ("KEY_RIGHTALT", "alt"),
        ("KEY_LEFTMETA", "meta"), ("KEY_RIGHTMETA", "meta"),
    ]:
        code = getattr(ecodes, prefix, None)
        if code is not None:
            lookup[code] = base
    # Function keys F1-F24
    for i in range(1, 25):
        code = getattr(ecodes, f"KEY_F{i}", None)
        if code is not None:
            lookup[code] = f"f{i}"
    # Common named keys
    for name in (
        "KEY_SPACE", "KEY_TAB", "KEY_ENTER", "KEY_BACKSPACE", "KEY_ESC",
        "KEY_DELETE", "KEY_INSERT", "KEY_HOME", "KEY_END", "KEY_PAGEUP",
        "KEY_PAGEDOWN", "KEY_UP", "KEY_DOWN", "KEY_LEFT", "KEY_RIGHT",
        "KEY_CAPSLOCK", "KEY_NUMLOCK", "KEY_SCROLLLOCK",
        "KEY_SYSRQ", "KEY_PAUSE", "KEY_COMPOSE",
    ):
        code = getattr(ecodes, name, None)
        if code is not None:
            lookup[code] = name[4:].lower()  # strip KEY_ prefix
    # Letters a-z
    for i in range(26):
        code = getattr(ecodes, f"KEY_{chr(ord('A') + i)}", None)
        if code is not None:
            lookup[code] = chr(ord('a') + i)
    # Digits 0-9
    for i in range(10):
        code = getattr(ecodes, f"KEY_{i}", None)
        if code is not None:
            lookup[code] = str(i)
    # Numpad digits
    for i in range(10):
        code = getattr(ecodes, f"KEY_KP{i}", None)
        if code is not None:
            lookup[code] = str(i)
    return lookup


_KEY_LOOKUP: dict[int, str] | None = None


def _get_key_lookup() -> dict[int, str]:
    global _KEY_LOOKUP
    if _KEY_LOOKUP is None:
        _KEY_LOOKUP = _build_key_lookup()
    return _KEY_LOOKUP


# ---------------------------------------------------------------------------
# Hotkey string parser  (same convention as the Windows backend)
# ---------------------------------------------------------------------------

def _parse_hotkey_str(hotkey: str) -> tuple[frozenset[str], str]:
    """Parse 'ctrl+shift+r' → (frozenset({'ctrl','shift'}), 'r')."""
    known_mods = {"ctrl", "shift", "alt", "meta"}
    parts = hotkey.lower().strip().split("+")
    mods = frozenset(p for p in parts if p in known_mods)
    main = next((p for p in parts if p not in known_mods), "")
    return mods, main


def _capture_hotkey_pynput(timeout: float = 8.0) -> str | None:
    """Record next key combo using pynput (X11, no input-group needed)."""
    if _pynput_available is None:
        return None
    from pynput import keyboard as pynput_kb

    result: dict = {"hotkey": None}
    done = threading.Event()
    held_mods: set[str] = set()

    def on_press(key):
        name = _pynput_key_name(key)
        if name is None:
            return
        if name == "esc":
            done.set()
            return False
        is_mod = name in ("ctrl", "shift", "alt", "meta")
        if is_mod:
            held_mods.add(name)
            return
        parts = [m for m in ("ctrl", "shift", "alt", "meta") if m in held_mods]
        parts.append(name)
        result["hotkey"] = "+".join(parts)
        done.set()
        return False

    def on_release(key):
        if done.is_set():
            return False
        name = _pynput_key_name(key)
        if name in ("ctrl", "shift", "alt", "meta"):
            held_mods.discard(name)

    listener = pynput_kb.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    done.wait(timeout=timeout)
    try:
        listener.stop()
    except Exception:
        pass
    return result["hotkey"]


def capture_hotkey(timeout: float = 8.0) -> str | None:
    """Record the next key combination the user presses (Linux/evdev version).
    
    Temporarily grabs all keyboard devices, waits for a key press, and returns
    the canonical hotkey string (e.g. 'ctrl+shift+k', 'tab', 'f9').
    
    Pressing Escape cancels and returns None.
    
    Args:
        timeout: Seconds to wait before giving up.
        
    Returns:
        Hotkey string like 'ctrl+k', 'tab', 'f9', or None if cancelled/timeout.
    """
    try:
        from evdev import ecodes, InputDevice, list_devices, categorize
        import glob
        import select
    except ImportError:
        logger.warning("capture_hotkey: evdev not available, trying pynput")
        if os.environ.get("DISPLAY") and _pynput_available is not None:
            return _capture_hotkey_pynput(timeout=timeout)
        logger.error("capture_hotkey: no backend available")
        return None

    # Discover keyboard devices
    keyboards = []
    for path_dev in sorted(glob.glob("/dev/input/event*")):
        try:
            dev = InputDevice(path_dev)
        except (OSError, PermissionError):
            continue
        try:
            caps = dev.capabilities(verbose=False)
            ev_key_caps = caps.get(ecodes.EV_KEY, [])
        except Exception:
            continue
        if not ev_key_caps:
            continue
        # Check for letter keys (keyboard, not mouse/button)
        if ecodes.KEY_A in ev_key_caps:
            keyboards.append(dev)

    if not keyboards:
        logger.warning("capture_hotkey: no evdev keyboard devices found, trying pynput")
        if os.environ.get("DISPLAY") and _pynput_available is not None:
            return _capture_hotkey_pynput(timeout=timeout)
        logger.error("capture_hotkey: no backend available")
        return None

    # Build reverse lookup: evdev key code → name
    key_lookup = _get_key_lookup()  # {code: "tab", "f9", "a", ...}

    # Known modifier key codes
    mod_codes = {
        ecodes.KEY_LEFTCTRL: "ctrl", ecodes.KEY_RIGHTCTRL: "ctrl",
        ecodes.KEY_LEFTSHIFT: "shift", ecodes.KEY_RIGHTSHIFT: "shift",
        ecodes.KEY_LEFTALT: "alt", ecodes.KEY_RIGHTALT: "alt",
        ecodes.KEY_LEFTMETA: "meta", ecodes.KEY_RIGHTMETA: "meta",
    }

    held_mods: set = set()
    result = {"hotkey": None}
    deadline = time.time() + timeout

    try:
        # Use select() to poll all keyboard devices with timeout
        while time.time() < deadline:
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            r, _, _ = select.select(keyboards, [], [], min(remaining, 0.2))
            for dev in r:
                try:
                    events = dev.read()
                except OSError:
                    continue
                for event in events:
                    if event.type != ecodes.EV_KEY:
                        continue
                    code = event.code
                    value = event.value  # 0=up, 1=down, 2=hold
                    if value == 0:  # release
                        if code in mod_codes:
                            mod_name = mod_codes[code]
                            held_mods.discard(mod_name)
                        continue
                    if value != 1:  # skip repeat
                        continue
                    # Press event
                    if code == ecodes.KEY_ESC:
                        result["hotkey"] = None
                        return None
                    if code in mod_codes:
                        held_mods.add(mod_codes[code])
                        continue
                    main_name = key_lookup.get(code, "")
                    if not main_name:
                        continue
                    # Build hotkey string
                    parts = []
                    for mod in ("ctrl", "shift", "alt", "meta"):
                        if mod in held_mods:
                            parts.append(mod)
                    parts.append(main_name)
                    result["hotkey"] = "+".join(parts)
                    return result["hotkey"]
    except Exception:
        logger.exception("capture_hotkey failed")

    return result["hotkey"]


# ---------------------------------------------------------------------------
# Keyboard device discovery
# ---------------------------------------------------------------------------

def _discover_keyboard_devices() -> list[InputDevice]:
    """
    Return /dev/input/event* devices that look like keyboards.

    Heuristic: the device must support EV_KEY and at least one of KEY_A..KEY_D
    (very conservative — avoids mice, gamepads, power buttons, etc.).
    """
    if evdev is None:
        return []

    keyboards: list[InputDevice] = []
    key_lookup = _get_key_lookup()
    permission_denied_count = 0

    for path in sorted(glob.glob("/dev/input/event*")):
        try:
            dev = InputDevice(path)
        except PermissionError:
            permission_denied_count += 1
            continue
        except OSError:
            continue

        try:
            caps = dev.capabilities(verbose=False)
            ev_key_caps = caps.get(evdev.ecodes.EV_KEY, [])
        except Exception:
            continue

        # Must support some key events
        if not ev_key_caps:
            continue

        # Check for at least a few letter keys to distinguish from mice/buttons
        letter_codes = {ecodes.KEY_A, ecodes.KEY_B, ecodes.KEY_C, ecodes.KEY_D}
        if not any(c in ev_key_caps for c in letter_codes):
            continue

        keyboards.append(dev)
        logger.debug("hotkey_device_found", path=path, name=dev.name)

    # If the heuristic is too strict and found nothing, fall back to any
    # device that supports KEY_A specifically.
    if not keyboards:
        for path in sorted(glob.glob("/dev/input/event*")):
            try:
                dev = InputDevice(path)
                caps = dev.capabilities(verbose=False)
                ev_key_caps = caps.get(evdev.ecodes.EV_KEY, [])
            except Exception:
                continue
            if ecodes.KEY_A in ev_key_caps:
                keyboards.append(dev)
                logger.debug("hotkey_device_fallback", path=path, name=dev.name)

    # Surface a clear, actionable error when permission is the problem.
    # This happens when setup-linux.sh ran but the user hasn't logged out/in
    # yet — the 'input' group membership hasn't propagated to the session.
    if not keyboards and permission_denied_count > 0:
        import grp
        try:
            input_group = grp.getgrnam("input")
            import os
            in_group = os.getlogin() in input_group.gr_mem or input_group.gr_gid in os.getgroups()
        except Exception:
            in_group = False

        if not in_group:
            logger.error(
                "evdev_permission_denied_not_in_input_group",
                hint=(
                    "Your user is NOT in the 'input' group. "
                    "Run: sudo usermod -aG input $USER  then log out and back in. "
                    "Or run Rota AI with: newgrp input to apply the group without logging out."
                ),
            )
        else:
            logger.error(
                "evdev_permission_denied_session_stale",
                hint=(
                    "Your user is in the 'input' group but the current session "
                    "doesn't reflect it yet. Log out and back in, or restart with: "
                    "newgrp input"
                ),
            )

    return keyboards


# ---------------------------------------------------------------------------
# HotkeyHandler
# ---------------------------------------------------------------------------

class HotkeyHandler:
    """
    Linux global-hotkey handler using evdev keyboard events.

    Evdev reads the physical device node, so it works regardless of the
    display server (X11 / Wayland). The caller is responsible for ensuring
    the process has read permission on /dev/input/event*.

    Drop-in compatible with the Windows HotkeyHandler.
    """

    MODE_TOGGLE = "toggle"
    MODE_HOLD = "hold"

    HOLD_COMPAT_THRESHOLD = 3.0  # seconds; hold longer → keep recording on release

    def __init__(
        self,
        hotkey: str = "tab",
        mode: str = MODE_TOGGLE,
        start_callback: Callable[[], None] | None = None,
        stop_callback: Callable[[], None] | None = None,
        error_callback: Callable[[Exception], None] | None = None,
    ):
        self.hotkey = (hotkey or "f9").lower()
        self._hotkey_mods, self._hotkey_main = _parse_hotkey_str(self.hotkey)
        self.mode = mode
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

        # Currently held canonical modifier names (ctrl, shift, alt, meta)
        self._held_mods: set[str] = set()

        # Extra hotkeys: list of (mods: frozenset, main: str, callback)
        self._extra_hotkeys: list[tuple[frozenset[str], str, Callable[[], None]]] = []

        # Modifier-only chord state (used when hotkey has no main key)
        self._modifier_chord_active: bool = False
        self._modifier_chord_dirty: bool = False

        # Pre-discover devices so we don't have to re-do it each time
        self._devices: list[InputDevice] = []

        # pynput listener (used as fallback when evdev is unavailable)
        self._pynput_listener = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def is_recording(self) -> bool:
        with self._lock:
            return self._is_recording

    def add_hotkey(self, hotkey_str: str, callback: Callable[[], None]) -> None:
        """Register an additional hotkey dispatched through the evdev listener."""
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

    def start_listening(self) -> bool:
        """Start the evdev listener thread, with pynput fallback on X11.

        Returns True on success.  If evdev cannot open any keyboard device
        (user not in the 'input' group) AND we are on an X11 session,
        automatically falls back to pynput which works without extra setup.
        """
        self.stop_listening()

        # --- Try evdev first ---
        evdev_ok = False
        if evdev is not None:
            try:
                self._devices = _discover_keyboard_devices()
            except Exception:
                logger.exception("hotkey_device_discovery_failed")
                self._devices = []
            evdev_ok = bool(self._devices)

        if not evdev_ok:
            # --- pynput fallback (X11 only) ---
            if os.environ.get("DISPLAY") and _pynput_available is not None:
                logger.info(
                    "evdev_unavailable_falling_back_to_pynput",
                    hint=(
                        "Hotkey running via pynput (X11). Works without input-group membership. "
                        "Wayland users: add yourself to the 'input' group for evdev support."
                    ),
                )
                return self._start_pynput_listener()

            # No backend available — surface a clear error
            logger.error(
                "no_keyboard_devices_found",
                hint=(
                    "No keyboard devices could be opened. "
                    "Ensure your user is in the 'input' group and you have logged out/in since setup. "
                    "Run: groups  — you should see 'input' listed. "
                    "If not: sudo usermod -aG input $USER  then log out and back in."
                ),
            )
            if self.error_callback:
                try:
                    self.error_callback(
                        PermissionError(
                            "Cannot access keyboard devices (/dev/input/event*).\n"
                            "Fix: sudo usermod -aG input $USER  then log out and back in.\n"
                            "Quick fix without logout: run Rota AI via:  newgrp input"
                        )
                    )
                except Exception:
                    pass
            return False

        # Grab exclusive access on all discovered keyboard devices so events
        # are not also delivered to the display server (prevents e.g. the key
        # press that triggered recording from typing into a text field).
        grabbed: list[InputDevice] = []
        try:
            for dev in self._devices:
                try:
                    dev.grab()
                    grabbed.append(dev)
                    logger.debug("hotkey_device_grabbed", path=dev.path, name=dev.name)
                except Exception:
                    logger.warning("hotkey_device_grab_failed", path=dev.path, name=dev.name)
        except Exception:
            logger.exception("hotkey_device_grab_unexpected")
            # Release any we already grabbed
            for dev in grabbed:
                try:
                    dev.ungrab()
                except Exception:
                    pass
            return False

        if not grabbed:
            logger.error("hotkey_no_devices_grabbed")
            return False

        self._devices = grabbed
        self._listener_stop.clear()
        self._listener_thread = threading.Thread(
            target=self._listener_loop,
            name="hotkey-evdev-listener",
            daemon=True,
        )
        self._listener_thread.start()
        self.backend = "evdev"
        logger.info(
            "global_hotkey_started",
            extra={"backend": self.backend, "hotkey": self.hotkey},
            devices=[d.path for d in grabbed],
        )
        return True

    def _start_pynput_listener(self) -> bool:
        """Start a pynput keyboard listener (X11 fallback, no input-group needed)."""
        if _pynput_available is None:
            logger.error("pynput_not_installed")
            return False
        from pynput import keyboard as pynput_kb

        self._listener_stop.clear()

        def on_press(key):
            if self._listener_stop.is_set():
                return False
            name = _pynput_key_name(key)
            if name is None:
                return
            is_mod = name in ("ctrl", "shift", "alt", "meta")
            if is_mod:
                self._held_mods.add(name)

            if not self._hotkey_main and self._hotkey_mods:
                if self._held_mods >= self._hotkey_mods and not self._modifier_chord_active:
                    self._modifier_chord_active = True
                    self._modifier_chord_dirty = False
                    if self.mode == self.MODE_HOLD:
                        self._handle_press()
                elif self._modifier_chord_active and not is_mod:
                    self._modifier_chord_dirty = True
            else:
                if name == self._hotkey_main and self._held_mods >= self._hotkey_mods:
                    self._handle_press()

            # Extra hotkeys
            if self._extra_hotkeys:
                for mods, main, callback in self._extra_hotkeys:
                    if self._held_mods >= mods and name == main:
                        try:
                            callback()
                        except Exception:
                            logger.exception("extra_hotkey_callback_failed_pynput")

        def on_release(key):
            if self._listener_stop.is_set():
                return False
            name = _pynput_key_name(key)
            if name is None:
                return
            is_mod = name in ("ctrl", "shift", "alt", "meta")

            if not self._hotkey_main and self._hotkey_mods:
                if is_mod and name in self._hotkey_mods and self._modifier_chord_active:
                    was_dirty = self._modifier_chord_dirty
                    self._modifier_chord_active = False
                    self._modifier_chord_dirty = False
                    with self._lock:
                        self._is_key_pressed = False
                    if self.mode == self.MODE_HOLD:
                        self._handle_release()
                    elif not was_dirty:
                        self._handle_press()
            else:
                if name == self._hotkey_main and self._held_mods >= self._hotkey_mods:
                    self._handle_release()

            if is_mod:
                self._held_mods.discard(name)

        try:
            listener = pynput_kb.Listener(on_press=on_press, on_release=on_release)
            listener.start()
            self._pynput_listener = listener
            self.backend = "pynput"
            logger.info("global_hotkey_started", extra={"backend": "pynput", "hotkey": self.hotkey})
            return True
        except Exception:
            logger.exception("pynput_listener_start_failed")
            return False

    def stop_listening(self) -> None:
        """Stop the listener and ungrab devices."""
        self._listener_stop.set()

        if self._pynput_listener is not None:
            try:
                self._pynput_listener.stop()
            except Exception:
                pass
            self._pynput_listener = None

        if self._listener_thread is not None:
            try:
                self._listener_thread.join(timeout=3.0)
            except Exception:
                logger.exception("hotkey_thread_join_failed")
            if self._listener_thread.is_alive():
                logger.warning("hotkey_thread_did_not_exit")
            self._listener_thread = None

        for dev in self._devices:
            try:
                dev.ungrab()
            except Exception:
                logger.debug("hotkey_ungrab_failed", path=dev.path)
        self._devices = []

        self.backend = None
        self._held_mods.clear()
        self._extra_hotkeys.clear()
        self._modifier_chord_active = False
        self._modifier_chord_dirty = False

        with self._lock:
            self._is_key_pressed = False
            self._is_recording = False
            self._press_time = None
            self._started_this_press = False

        logger.info("global_hotkey_stopped")

    def is_healthy(self) -> bool:
        if self.backend == "pynput":
            return (
                self._pynput_listener is not None
                and self._pynput_listener.is_alive()
            )
        if self.backend == "evdev":
            return (
                self._listener_thread is not None
                and self._listener_thread.is_alive()
            )
        return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _key_code_to_name(code: int) -> str | None:
        return _get_key_lookup().get(code)

    def _matches_hotkey(self, code: int) -> bool:
        """True if key code matches the hotkey's main key AND all required
        modifiers are currently held."""
        expected_name = self._key_code_to_name(code)
        if expected_name != self._hotkey_main:
            return False
        return self._held_mods >= self._hotkey_mods

    def _fire_extra_hotkeys(self, code: int) -> None:
        """Check if code + held mods match any extra hotkey."""
        if not self._extra_hotkeys:
            return
        code_name = self._key_code_to_name(code)
        for mods, main, callback in self._extra_hotkeys:
            if not (self._held_mods >= mods):
                continue
            if code_name == main:
                try:
                    callback()
                except Exception:
                    logger.exception(
                        "extra_hotkey_callback_failed",
                        mods=mods,
                        main=main,
                    )

    # ------------------------------------------------------------------
    # Press / release semantics  (mirrors Windows backend)
    # ------------------------------------------------------------------

    def _handle_press(self) -> None:
        """Called when the trigger hotkey combination is detected."""
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
                    if self._hotkey_main:
                        # Standard key: defer stop decision to release
                        self._started_this_press = False
                    else:
                        # Modifier-only chord: stop immediately
                        self._is_recording = False
                        action = self.stop_callback

        if action:
            action()

    def _handle_release(self) -> None:
        """Called when the trigger hotkey combination is released."""
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
                    # This keydown started recording; release should not stop it
                    self._started_this_press = False
                elif self._is_recording:
                    held = (
                        (time.monotonic() - press_time)
                        if press_time is not None
                        else 0.0
                    )
                    if held >= self.HOLD_COMPAT_THRESHOLD:
                        logger.debug("hold_compat: ignoring release, recording stays on")
                    else:
                        self._is_recording = False
                        action = self.stop_callback

        if action:
            action()

    # ------------------------------------------------------------------
    # Event dispatch
    # ------------------------------------------------------------------

    def _on_key_event(self, event) -> None:
        """Process a single EV_KEY event."""
        from evdev import ecodes as e_ecodes

        if event.type != e_ecodes.EV_KEY:
            return

        code = event.code
        key_state = event.value  # 0=up, 1=down, 2=repeat

        name = self._key_code_to_name(code)
        is_mod = name in ("ctrl", "shift", "alt", "meta")

        if key_state == 1:  # key down
            if is_mod:
                self._held_mods.add(name)

            # --- Modifier-only hotkey handling ---
            if not self._hotkey_main and self._hotkey_mods:
                if self._held_mods >= self._hotkey_mods and not self._modifier_chord_active:
                    self._modifier_chord_active = True
                    self._modifier_chord_dirty = False
                    if self.mode == self.MODE_HOLD:
                        self._handle_press()
                elif self._modifier_chord_active and not is_mod:
                    self._modifier_chord_dirty = True
            else:
                if name == self._hotkey_main and self._held_mods >= self._hotkey_mods:
                    self._handle_press()

            self._fire_extra_hotkeys(code)

        elif key_state == 0:  # key up
            # --- Modifier-only hotkey handling ---
            if not self._hotkey_main and self._hotkey_mods:
                if is_mod and name in self._hotkey_mods and self._modifier_chord_active:
                    was_dirty = self._modifier_chord_dirty
                    self._modifier_chord_active = False
                    self._modifier_chord_dirty = False
                    with self._lock:
                        self._is_key_pressed = False
                    if self.mode == self.MODE_HOLD:
                        self._handle_release()
                    elif not was_dirty:
                        # Toggle on clean chord release
                        self._handle_press()
            else:
                if name == self._hotkey_main and self._held_mods >= self._hotkey_mods:
                    self._handle_release()

            if is_mod:
                self._held_mods.discard(name)

        # key_state == 2 (repeat) — we already handled the press on the first
        # down, so we just fire extra hotkeys on repeat.
        elif key_state == 2:
            self._fire_extra_hotkeys(code)

    # ------------------------------------------------------------------
    # Listener thread
    # ------------------------------------------------------------------

    def _listener_loop(self) -> None:
        """Main loop run in the daemon thread.

        Uses select() over all grabbed keyboard devices, dispatching events
        to _on_key_event.
        """
        import selectors

        sel = selectors.DefaultSelector()
        for dev in self._devices:
            try:
                sel.register(dev, selectors.EVENT_READ)
            except Exception:
                logger.exception("hotkey_select_register_failed", path=dev.path)

        logger.info("hotkey_listener_loop_started")

        try:
            while not self._listener_stop.is_set():
                # Use a timeout so we can check _listener_stop periodically
                events = sel.select(timeout=0.25)
                if not events:
                    continue

                for key, _mask in events:
                    dev = key.fileobj  # type: ignore[assignment]
                    try:
                        for event in dev.read():
                            try:
                                self._on_key_event(event)
                            except Exception:
                                logger.exception("hotkey_event_handler_failed")
                    except (OSError, IOError) as exc:
                        logger.warning(
                            "hotkey_device_read_error",
                            path=getattr(dev, "path", "?"),
                            error=str(exc),
                        )
                        # If a device disappears, it might be unplugged.
                        # Remove it and keep going with the others.
                        try:
                            sel.unregister(dev)
                        except Exception:
                            pass
                        continue
                    except Exception:
                        logger.exception("hotkey_device_read_unexpected")
        except Exception:
            logger.exception("hotkey_listener_loop_crash")
            if self.error_callback:
                try:
                    self.error_callback(
                        RuntimeError("Hotkey listener loop crashed")
                    )
                except Exception:
                    pass
        finally:
            try:
                sel.close()
            except Exception:
                pass
            logger.info("hotkey_listener_loop_exited")

    @classmethod
    def capture_hotkey(cls, timeout: float = 8.0) -> str | None:
        """Classmethod wrapper so callers can use HotkeyHandler.capture_hotkey()
        consistently across platforms (matches Windows HotkeyHandler API)."""
        return capture_hotkey(timeout=timeout)


# Pre-compute modifier key codes for fast lookup
_MODIFIER_CODES: set[int] = set()
if evdev is not None:
    for name in (
        "KEY_LEFTCTRL", "KEY_RIGHTCTRL",
        "KEY_LEFTSHIFT", "KEY_RIGHTSHIFT",
        "KEY_LEFTALT", "KEY_RIGHTALT",
        "KEY_LEFTMETA", "KEY_RIGHTMETA",
    ):
        code = getattr(ecodes, name, None)
        if code is not None:
            _MODIFIER_CODES.add(code)


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    def on_start() -> None:
        print("Recording...  [press hotkey again to stop]")

    def on_stop() -> None:
        print("Stopped. Pipeline triggered.")

    handler = HotkeyHandler(start_callback=on_start, stop_callback=on_stop)
    ok = handler.start_listening()
    if not ok:
        print("ERROR: Could not start hotkey listener (evdev missing / no device access).")
        raise SystemExit(1)

    print(f"Listening (backend: {handler.backend}). Press Ctrl+C to quit.")
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        handler.stop_listening()
        print("Done.")
