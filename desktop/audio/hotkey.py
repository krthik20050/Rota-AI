from utils.log import get_logger
import threading
import time

try:
    from pynput import keyboard as pynput_keyboard
except Exception:
    pynput_keyboard = None

keyboard_hook = None

logger = get_logger(__name__)


class HotkeyHandler:
    """
    Handles the global recording hotkey.
    Uses pynput first on Windows because it is more reliable for ordinary desktop apps,
    with the existing keyboard package kept as a fallback.
    """
    MODE_TOGGLE = "toggle"
    MODE_HOLD = "hold"

    HOLD_COMPAT_THRESHOLD = 3.0  # seconds; hold longer → keep recording on release

    # Map modifier names to pynput Key objects
    _PYNPUT_MOD_MAP = None  # populated lazily
    _KEY_NAME_REVERSE_MAP = None  # populated lazily: {pynput_key_obj: "f9", "tab", "a", ...}

    @classmethod
    def _get_pynput_mod_map(cls):
        if cls._PYNPUT_MOD_MAP is None and pynput_keyboard is not None:
            cls._PYNPUT_MOD_MAP = {
                "ctrl":  {pynput_keyboard.Key.ctrl, pynput_keyboard.Key.ctrl_l, pynput_keyboard.Key.ctrl_r},
                "shift": {pynput_keyboard.Key.shift, pynput_keyboard.Key.shift_l, pynput_keyboard.Key.shift_r},
                "alt":   {pynput_keyboard.Key.alt, pynput_keyboard.Key.alt_l, pynput_keyboard.Key.alt_r},
            }
        return cls._PYNPUT_MOD_MAP or {}

    @classmethod
    def _get_key_name_reverse_map(cls):
        """Build {pynput_key_obj: name} reverse lookup for capture_hotkey."""
        if cls._KEY_NAME_REVERSE_MAP is not None:
            return cls._KEY_NAME_REVERSE_MAP
        rev = {}
        if pynput_keyboard is None:
            return rev
        # Named special keys: tab, space, enter, esc, delete, home, end, etc.
        for attr in dir(pynput_keyboard.Key):
            if attr.startswith('_'):
                continue
            key_obj = getattr(pynput_keyboard.Key, attr, None)
            if key_obj is not None and isinstance(key_obj, pynput_keyboard.Key):
                rev[key_obj] = attr.lower()
        # Function keys are already in dir(Key): f1, f2, ..., f12
        # Characters are handled via key.char, not in Key enum
        cls._KEY_NAME_REVERSE_MAP = rev
        return rev

    @classmethod
    def _key_to_name(cls, key) -> str | None:
        """Convert a pynput key object to its canonical name string."""
        if pynput_keyboard is None:
            return None
        # Check named keys (tab, f1, space, enter, etc.)
        rev = cls._get_key_name_reverse_map()
        if key in rev:
            return rev[key]
        # Check modifier keys
        mod_map = cls._get_pynput_mod_map()
        for name, key_set in mod_map.items():
            if key in key_set:
                return name
        # Character key
        char = getattr(key, 'char', None)
        if char:
            return char.lower()
        return None

    @classmethod
    def _names_to_hotkey_str(cls, mods: set, main_name: str = "") -> str:
        """Convert captured modifier set + main key name to canonical hotkey string.
        
        Example: ({'ctrl', 'shift'}, 'k') → 'ctrl+shift+k'
                 ({}, 'tab') → 'tab'
                 ({'ctrl', 'alt'}, 'space') → 'ctrl+alt+space'
        """
        parts = []
        # Always put modifiers in canonical order
        for mod in ('ctrl', 'shift', 'alt'):
            if mod in mods:
                parts.append(mod)
        if main_name:
            parts.append(main_name.lower())
        return '+'.join(parts) if parts else ''

    @classmethod
    def capture_hotkey(cls, timeout: float = 8.0) -> str | None:
        """Record the next key combination the user presses.
        
        Temporarily installs a global keyboard listener, waits for a key press,
        and returns the canonical hotkey string (e.g. 'ctrl+shift+k', 'tab', 'f9').
        
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
        held_mods: set = set()

        def capture_press(key):
            # Escape cancels
            if key == pynput_keyboard.Key.esc:
                result["hotkey"] = None
                done.set()
                return False  # stop listener
            main_name = cls._key_to_name(key)
            if main_name is None:
                return True  # skip unrecognized keys
            # Ignore press events for modifier-only (wait for main key)
            known_mods = {"ctrl", "shift", "alt"}
            if main_name in known_mods:
                held_mods.add(main_name)
                return True
            # Main key found - build hotkey string
            hotkey_str = cls._names_to_hotkey_str(held_mods, main_name)
            result["hotkey"] = hotkey_str
            done.set()
            return False  # stop listener

        def capture_release(key):
            name = cls._key_to_name(key)
            if name in ("ctrl", "shift", "alt"):
                held_mods.discard(name)

        try:
            listener = pynput_keyboard.Listener(
                on_press=capture_press,
                on_release=capture_release,
            )
            listener.daemon = True
            listener.start()
            done.wait(timeout=timeout)
            listener.stop()
        except Exception:
            logger.exception("capture_hotkey failed")

        return result["hotkey"]

    @classmethod
    def _parse_hotkey_str(cls, hotkey: str):
        """Parse 'ctrl+shift+r' → (frozenset({'ctrl','shift'}), 'r')."""
        parts = hotkey.lower().split("+")
        known_mods = {"ctrl", "shift", "alt"}
        mods = frozenset(p for p in parts if p in known_mods)
        main = next((p for p in parts if p not in known_mods), "")
        return mods, main

    def __init__(self, hotkey="tab", mode=MODE_TOGGLE, start_callback=None, stop_callback=None, error_callback=None):
        self.hotkey = (hotkey or "tab").lower()
        self._hotkey_mods, self._hotkey_main = self._parse_hotkey_str(self.hotkey)
        self.mode = mode
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.error_callback = error_callback

        self.backend = None
        self._is_recording = False
        self._is_key_pressed = False
        self._press_time = None
        self._started_this_press = False
        self._lock = threading.Lock()
        self._listener = None
        self._press_hook = None
        self._release_hook = None
        self._held_mods: set = set()  # currently held modifier names
        # Extra hotkeys: list of (mods: frozenset, main: str, callback)
        self._extra_hotkeys: list = []
        # Modifier-only chord state (used when hotkey has no main key, e.g. "ctrl+shift")
        self._modifier_chord_active: bool = False   # all required mods are currently held
        self._modifier_chord_dirty: bool = False    # a non-required key was pressed during chord

    def _get_keyboard_hook(self):
        """Lazy-loads the fallback python-keyboard hook engine.
        
        WHY: The 'keyboard' library immediately registers a system-wide LL hook 
        upon import, spawning a Win32 thread which conflicts with pynput's hook 
        and throws 0x8001010d / access violations. Deferring the import ensures 
        this hook thread is never spawned as long as the primary pynput backend works.
        """
        global keyboard_hook
        if keyboard_hook is None:
            try:
                import keyboard as keyboard_hook
            except Exception:
                pass
        return keyboard_hook

    @property
    def is_recording(self):
        with self._lock:
            return self._is_recording

    def _pynput_key_to_name(self, key) -> str | None:
        """Return the canonical name of a pynput key, or None if not a modifier."""
        mod_map = self._get_pynput_mod_map()
        for name, key_set in mod_map.items():
            if key in key_set:
                return name
        return None

    def _matches_pynput_key(self, key) -> bool:
        """True if key is the trigger key AND all required modifiers are held."""
        mods, main = self._hotkey_mods, self._hotkey_main

        # Check main key
        matched_main = False
        if pynput_keyboard is not None:
            # Try named function key (f1-f12, space, tab, etc.)
            named = getattr(pynput_keyboard.Key, main, None)
            if named is not None:
                matched_main = (key == named)
            else:
                # Single character key
                matched_main = (getattr(key, "char", None) or "").lower() == main

        if not matched_main:
            return False

        # Check modifiers
        return self._held_mods >= mods  # all required mods must be held

    def _update_held_mod_press(self, key):
        name = self._pynput_key_to_name(key)
        if name:
            self._held_mods.add(name)

    def _update_held_mod_release(self, key):
        name = self._pynput_key_to_name(key)
        if name:
            self._held_mods.discard(name)

    def _matches_keyboard_event(self, event):
        """Match event for keyboard-hook backend. Supports simple names and modifier combos."""
        name = getattr(event, "name", "").lower()
        if not self._hotkey_mods:
            return name == self._hotkey_main
        # For modifier combos, check both the main key name and that modifiers are pressed
        if name != self._hotkey_main:
            return False
        kh = self._get_keyboard_hook()
        if kh is None:
            return False
        try:
            for mod in self._hotkey_mods:
                if not kh.is_pressed(mod):
                    return False
            return True
        except Exception:
            return False

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
                    # Start immediately on press; release of THIS keydown won't stop
                    self._is_recording = True
                    self._started_this_press = True
                    action = self.start_callback
                else:
                    # Already recording
                    if self._hotkey_main:
                        # Standard key: defer stop decision to release
                        # (3s hold compat — see _handle_release)
                        self._started_this_press = False
                    else:
                        # Modifier-only chord: stop immediately on second chord press
                        # (no separate release event used for stop)
                        self._is_recording = False
                        action = self.stop_callback

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
                    # This keydown STARTED recording; release should not stop it
                    self._started_this_press = False
                elif self._is_recording:
                    held = (time.monotonic() - press_time) if press_time is not None else 0.0
                    if held >= self.HOLD_COMPAT_THRESHOLD:
                        # Held 3s+ → backward compat hold-to-record; keep recording ON
                        logger.debug("hold_compat: ignoring release, recording stays on")
                    else:
                        # Normal second press → stop
                        self._is_recording = False
                        action = self.stop_callback

        if action:
            action()

    def add_hotkey(self, hotkey_str: str, callback) -> None:
        """Register an additional hotkey dispatched through the active pynput listener.

        Must be called after start_listening(). Has no effect when the keyboard
        fallback backend is active (the caller's try/except should handle that).
        """
        mods, main = self._parse_hotkey_str(hotkey_str.lower())
        self._extra_hotkeys.append((mods, main, callback))

    def _fire_extra_hotkeys(self, key) -> None:
        """Check whether key + held mods match any extra hotkey; fire its callback."""
        if not self._extra_hotkeys or pynput_keyboard is None:
            return
        for mods, main, callback in self._extra_hotkeys:
            if not (self._held_mods >= mods):
                continue
            named = getattr(pynput_keyboard.Key, main, None)
            if named is not None:
                matched = (key == named)
            else:
                matched = (getattr(key, "char", None) or "").lower() == main
            if matched:
                try:
                    callback()
                except Exception:
                    logger.exception("extra_hotkey_callback_failed hotkey=%s+%s", mods, main)

    def _on_pynput_press(self, key):
        try:
            self._update_held_mod_press(key)
            if not self._hotkey_main and self._hotkey_mods:
                # Modifier-only hotkey (e.g. "ctrl+shift")
                mod_name = self._pynput_key_to_name(key)
                if self._held_mods >= self._hotkey_mods and not self._modifier_chord_active:
                    # Chord just completed — mark active and clean
                    self._modifier_chord_active = True
                    self._modifier_chord_dirty = False
                    if self.mode == self.MODE_HOLD:
                        # Hold mode: start recording immediately on chord press
                        self._handle_press()
                elif self._modifier_chord_active and mod_name not in self._hotkey_mods:
                    # A key outside the required set was pressed while chord is held
                    self._modifier_chord_dirty = True
            else:
                if self._matches_pynput_key(key):
                    self._handle_press()
            self._fire_extra_hotkeys(key)
        except Exception as exc:
            logger.exception("hotkey_press_callback_failed")
            if self.error_callback:
                self.error_callback(exc)

    def _on_pynput_release(self, key):
        try:
            if not self._hotkey_main and self._hotkey_mods:
                # Modifier-only hotkey
                mod_name = self._pynput_key_to_name(key)
                if mod_name in self._hotkey_mods and self._modifier_chord_active:
                    was_dirty = self._modifier_chord_dirty
                    self._modifier_chord_active = False
                    self._modifier_chord_dirty = False
                    with self._lock:
                        self._is_key_pressed = False  # allow next chord to fire
                    if self.mode == self.MODE_HOLD:
                        self._handle_release()
                    elif not was_dirty:
                        # Toggle: fire start/stop on clean chord release
                        self._handle_press()
            else:
                if self._matches_pynput_key(key):
                    self._handle_release()
            self._update_held_mod_release(key)
        except Exception as exc:
            logger.exception("hotkey_release_callback_failed")
            if self.error_callback:
                self.error_callback(exc)

    def _on_keyboard_press(self, event):
        try:
            if self._matches_keyboard_event(event):
                self._handle_press()
        except Exception as exc:
            logger.exception("keyboard_press_callback_failed")
            if self.error_callback:
                self.error_callback(exc)

    def _on_keyboard_release(self, event):
        try:
            if self._matches_keyboard_event(event):
                self._handle_release()
        except Exception as exc:
            logger.exception("keyboard_release_callback_failed")
            if self.error_callback:
                self.error_callback(exc)

    def start_listening(self):
        """Starts listening for the global hotkey."""
        self.stop_listening()
        errors = []

        if pynput_keyboard is not None:
            try:
                self._listener = pynput_keyboard.Listener(
                    on_press=self._on_pynput_press,
                    on_release=self._on_pynput_release,
                )
                self._listener.daemon = True
                self._listener.start()
                self.backend = "pynput"
                logger.info("global_hotkey_started", extra={"backend": self.backend, "hotkey": self.hotkey})
                return True
            except Exception as exc:
                errors.append(exc)
                logger.exception("pynput_hotkey_start_failed")

        kh = self._get_keyboard_hook()
        if kh is not None:
            try:
                self._press_hook = kh.on_press(self._on_keyboard_press)
                self._release_hook = kh.on_release(self._on_keyboard_release)
                self.backend = "keyboard"
                logger.info("global_hotkey_started", extra={"backend": self.backend, "hotkey": self.hotkey})
                return True
            except Exception as exc:
                errors.append(exc)
                logger.exception("keyboard_hotkey_start_failed")

        raise RuntimeError("Global hotkey listener could not start") from (errors[-1] if errors else None)

    def stop_listening(self):
        """Stops listening for the global hotkey."""
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception:
                logger.exception("pynput_hotkey_stop_failed")
            self._listener = None

        # Use the already-loaded module-level var — do NOT call _get_keyboard_hook()
        # here. That function triggers an import which spawns a competing
        # WH_KEYBOARD_LL hook thread, causing 0x8001010d / access-violation crashes
        # when pynput is the active backend.
        kh = keyboard_hook
        if kh is not None:
            if self._press_hook is not None:
                kh.unhook(self._press_hook)
                self._press_hook = None
            if self._release_hook is not None:
                kh.unhook(self._release_hook)
                self._release_hook = None

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

    def set_mode(self, mode):
        """Changes the hotkey mode."""
        if mode not in [self.MODE_HOLD, self.MODE_TOGGLE]:
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

    def is_healthy(self):
        if self.backend == "pynput" and self._listener is not None:
            return bool(self._listener.running)
        if self.backend == "keyboard":
            return self._press_hook is not None and self._release_hook is not None
        return False


if __name__ == "__main__":
    def on_start():
        print("Recording...  [press F9 again to stop]")

    def on_stop():
        print("Stopped. Pipeline triggered.")

    handler = HotkeyHandler(start_callback=on_start, stop_callback=on_stop)
    handler.start_listening()
    print(f"Toggle mode active (backend: pending). Press F9 to start/stop. Ctrl+C to quit.")
    print(f"Hold F9 3s+ = backward-compat hold (stays on until next quick press).")
    try:
        while True:
            time.sleep(0.5)
            # Print state every 2s so tester can see current recording flag
    except KeyboardInterrupt:
        handler.stop_listening()
        print("Done.")
