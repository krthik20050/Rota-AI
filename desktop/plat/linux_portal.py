"""
Wayland global-hotkey backend via XDG Desktop Portal GlobalShortcuts.

Uses org.freedesktop.portal.GlobalShortcuts DBus interface to register
a global hotkey through the desktop compositor. This is the **correct**
approach on Wayland — No evdev grab, no keyboard freeze, no X11 hack.

Requires:
    - pip install jeepney
    - A desktop environment that supports the GlobalShortcuts portal
      (GNOME 42+, KDE Plasma 5.25+, Sway 1.8+, Hyprland).

The portal shows a permission dialog on first registration so the user
explicitly approves the shortcut.
"""

from __future__ import annotations

import os
import threading
import time
import uuid
from collections.abc import Callable

import structlog

logger = structlog.get_logger(__name__)

try:
    import jeepney
    import jeepney.io.blocking as dbus_blocking
    from jeepney import DBusAddress, HeaderFields, MessageType, new_method_call
    from jeepney.bus import get_bus
except ImportError:
    jeepney = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# DBus constants for the GlobalShortcuts portal
# ---------------------------------------------------------------------------

_PORTAL_BUS_NAME = "org.freedesktop.portal.Desktop"
_PORTAL_OBJECT_PATH = "/org/freedesktop/portal/desktop"
_PORTAL_IFACE = "org.freedesktop.portal.GlobalShortcuts"
_REQUEST_IFACE = "org.freedesktop.portal.Request"
_SESSION_IFACE = "org.freedesktop.portal.Session"


# ---------------------------------------------------------------------------
# Shortcut to key mapping (portal → our canonical names)
# ---------------------------------------------------------------------------


# Map portal shortcut preference strings to our hotkey format.
# The portal uses accelerator strings like "<Control>F9" or "F9".
# We store the reverse mapping from our internal format.
def _hotkey_to_portal_preference(mods: frozenset[str], main: str) -> str:
    """Convert our canonical hotkey to portal shortcut preference format.

    Example: frozenset({'ctrl'}), 'f9' → '<Control>F9'
             frozenset({'ctrl','shift'}), 'r' → '<Control><Shift>R'
             frozenset(), 'tab' → 'Tab'
    """
    mod_map = {
        "ctrl": "<Control>",
        "shift": "<Shift>",
        "alt": "<Alt>",
        "meta": "<Super>",
    }
    parts = []
    for mod_name in ("ctrl", "shift", "alt", "meta"):
        if mod_name in mods:
            parts.append(mod_map.get(mod_name, mod_name))
    if main:
        # Capitalize first letter for portal format
        if len(main) == 1:
            parts.append(main.upper())
        else:
            parts.append(main.capitalize())
    return "".join(parts)


def _portal_preference_to_hotkey(pref: str) -> str:
    """Convert a portal shortcut preference back to our canonical format.

    Example: '<Control>F9' → 'ctrl+f9'
             '<Control><Shift>R' → 'ctrl+shift+r'
             'Tab' → 'tab'
             'F9' → 'f9'
    """
    mod_reverse = {
        "<Control>": "ctrl",
        "<Shift>": "shift",
        "<Alt>": "alt",
        "<Super>": "meta",
        "<Meta>": "meta",
    }
    mods = []
    remaining = pref
    for tag, name in sorted(mod_reverse.items(), key=lambda x: -len(x[0])):
        if tag in remaining:
            mods.append(name)
            remaining = remaining.replace(tag, "", 1)
    main = remaining.lower() if remaining else ""
    if mods:
        return "+".join(mods + [main])
    return main


# ---------------------------------------------------------------------------
# Portal shortcut handler
# ---------------------------------------------------------------------------


class PortalShortcutHandler:
    """Manages a global shortcut via XDG Desktop Portal on Wayland.

    Runs the DBus interaction in a daemon thread so it fits the existing
    threading model of HotkeyHandler.
    """

    def __init__(
        self,
        hotkey_str: str,
        start_callback: Callable[[], None] | None = None,
        stop_callback: Callable[[], None] | None = None,
        error_callback: Callable[[Exception], None] | None = None,
        mode: str = "toggle",
    ):
        self._hotkey_str = hotkey_str.lower()
        self._hotkey_parts = hotkey_str.lower().split("+")
        known_mods = {"ctrl", "shift", "alt", "meta"}
        self._hotkey_mods = frozenset(p for p in self._hotkey_parts if p in known_mods)
        self._hotkey_main = next((p for p in self._hotkey_parts if p not in known_mods), "")
        self.mode = mode
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.error_callback = error_callback

        self._connection = None
        self._session_handle = None
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        # Active signal filter (removed on stop)
        self._signal_filter = None

        # State tracking
        self._is_recording = False
        self._is_key_pressed = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def is_running(self) -> bool:
        return self._connection is not None and self._session_handle is not None

    def start(self) -> bool:
        """Connect to portal and register the shortcut.

        Returns True on success.
        """
        if jeepney is None:
            logger.error("portal_start_failed_jeepney_not_available")
            return False

        # Check Wayland
        session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
        wayland_display = os.environ.get("WAYLAND_DISPLAY", "")
        if session_type != "wayland" and not wayland_display:
            logger.warning(
                "portal_skipped_not_wayland",
                session_type=session_type,
                wayland_display=bool(wayland_display),
            )
            return False

        try:
            bus_addr = get_bus()
            self._connection = dbus_blocking.open_dbus_connection(bus_addr, enable_fds=False)
            logger.debug("portal_dbus_connected")
        except Exception as exc:
            logger.warning("portal_dbus_connect_failed", error=str(exc))
            self._connection = None
            return False

        # Run the registration in a thread
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._registration_thread,
            name="hotkey-portal-registration",
            daemon=True,
        )
        self._thread.start()

        # Wait up to 5 seconds for registration to complete
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline:
            if self._session_handle is not None:
                logger.info(
                    "portal_shortcut_registered",
                    hotkey=self._hotkey_str,
                    session=self._session_handle,
                )
                return True
            if not self._thread.is_alive():
                break
            time.sleep(0.05)

        # Registration timed out or failed
        logger.error("portal_shortcut_registration_timeout")
        self._cleanup_connection()
        return False

    def stop(self) -> None:
        """Close the portal session and DBus connection."""
        self._stop_event.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=3.0)
            self._thread = None
        self._cleanup_connection()

    def is_active(self) -> bool:
        return self.is_running

    def set_mode(self, mode: str) -> None:
        self.mode = mode

    # ------------------------------------------------------------------
    # Portal registration (runs in a thread)
    # ------------------------------------------------------------------

    def _registration_thread(self) -> None:
        """Register shortcut with the portal.

        Flow:
          1. CreateSession → get session_handle
          2. BindShortcuts  → register our shortcut
          3. Listen for Activated signals
        """
        if self._connection is None:
            return

        try:
            # Step 1: CreateSession
            session_token = uuid.uuid4().hex
            request_token = uuid.uuid4().hex
            sender_name = self._connection.unique_name.replace(".", "_").replace(":", "")

            request_path = f"/org/freedesktop/portal/desktop/request/{sender_name}/{request_token}"

            # Subscribe to the Response signal on the request path
            self._connection.add_filter(self._make_signal_matcher(request_path, _REQUEST_IFACE))

            # Build CreateSession call
            create_msg = new_method_call(
                DBusAddress(
                    object_path=_PORTAL_OBJECT_PATH,
                    bus_name=_PORTAL_BUS_NAME,
                    interface=_PORTAL_IFACE,
                ),
                "CreateSession",
                "a{sv}",
                (
                    {
                        "session_handle_token": ("s", session_token),
                        "handle_token": ("s", request_token),
                    },
                ),
            )

            reply = self._connection.send_and_get_reply(create_msg)

            if reply.header.message_type == MessageType.ERROR:
                err_name = reply.header.fields.get(HeaderFields.error_name, "unknown")
                logger.warning(
                    "portal_create_session_error",
                    error=err_name,
                    body=reply.body,
                )
                return

            # Wait for the Response signal to get session_handle
            session_handle = self._wait_for_response(request_path, timeout=30.0)
            if session_handle is None:
                logger.error("portal_no_session_handle")
                return

            self._session_handle = session_handle

            # Subscribe to Activated signals on the session
            self._connection.add_filter(
                self._make_signal_matcher(session_handle, _SESSION_IFACE, "Activated")
            )

            # Step 2: BindShortcuts
            bind_request_token = uuid.uuid4().hex
            bind_request_path = (
                f"/org/freedesktop/portal/desktop/request/{sender_name}/{bind_request_token}"
            )

            self._connection.add_filter(
                self._make_signal_matcher(bind_request_path, _REQUEST_IFACE)
            )

            portal_pref = _hotkey_to_portal_preference(self._hotkey_mods, self._hotkey_main)

            shortcuts = [
                (
                    "rota-ai-toggle",
                    {
                        "pref": ("s", portal_pref),
                        "description": ("s", "Toggle Rota AI voice recording"),
                    },
                ),
            ]

            bind_msg = new_method_call(
                DBusAddress(
                    object_path=_PORTAL_OBJECT_PATH,
                    bus_name=_PORTAL_BUS_NAME,
                    interface=_PORTAL_IFACE,
                ),
                "BindShortcuts",
                "oa{sv}a(ssa{sv})",
                (
                    session_handle,
                    {"handle_token": ("s", bind_request_token)},
                    shortcuts,
                ),
            )

            reply = self._connection.send_and_get_reply(bind_msg)

            if reply.header.message_type == MessageType.ERROR:
                err_name = reply.header.fields.get(HeaderFields.error_name, "unknown")
                logger.warning(
                    "portal_bind_shortcuts_error",
                    error=err_name,
                    body=reply.body,
                )
                return

            # Wait for bind confirmation
            bind_result = self._wait_for_response(bind_request_path, timeout=30.0)
            if bind_result is None:
                logger.error("portal_bind_no_response")
                return

            logger.info(
                "portal_shortcut_bound",
                shortcut=portal_pref,
                session=session_handle,
            )

            # Step 3: Listen for activated signals in a loop
            self._activation_listen_loop()

        except Exception:
            logger.exception("portal_registration_failed")
            if self.error_callback:
                try:
                    self.error_callback(RuntimeError("Portal shortcut registration failed"))
                except Exception:
                    pass

    def _activation_listen_loop(self) -> None:
        """Listen for Activated signals from the portal."""
        if self._connection is None or self._session_handle is None:
            return

        logger.info("portal_activation_listener_started")

        try:
            while not self._stop_event.is_set():
                # Poll for signals with timeout
                msg = self._connection.recv_until_filtered(
                    self._make_signal_matcher(self._session_handle, _SESSION_IFACE, "Activated"),
                    timeout=0.5,
                )

                if msg is None:
                    continue

                if msg.header.message_type == MessageType.SIGNAL:
                    try:
                        self._handle_activation(msg.body)
                    except Exception:
                        logger.exception("portal_activation_handler_failed")
        except Exception:
            logger.exception("portal_activation_listener_error")
        finally:
            logger.info("portal_activation_listener_exited")

    def _handle_activation(self, body) -> None:
        """Handle an Activated signal from the portal.

        The body format is typically:
          (session_handle: s, shortcut_id: s, timestamp: u, options: a{sv})
        """
        try:
            # body is a tuple: (session_handle, shortcut_id, timestamp, options)
            if isinstance(body, tuple) and len(body) >= 2:
                shortcut_id = body[1]
                if shortcut_id == "rota-ai-toggle":
                    self._toggle_recording()
        except Exception:
            logger.exception("portal_activation_parse_failed")

    def _toggle_recording(self) -> None:
        """Toggle recording state based on the mode."""
        action = None
        with self._lock:
            if self.mode == "toggle":
                if not self._is_recording:
                    self._is_recording = True
                    action = self.start_callback
                else:
                    self._is_recording = False
                    action = self.stop_callback
            elif self.mode == "hold":
                if not self._is_key_pressed:
                    self._is_key_pressed = True
                    self._is_recording = True
                    action = self.start_callback
                else:
                    self._is_key_pressed = False
                    self._is_recording = False
                    action = self.stop_callback

        if action:
            try:
                action()
            except Exception:
                logger.exception("portal_callback_failed")

    # ------------------------------------------------------------------
    # DBus helpers
    # ------------------------------------------------------------------

    def _make_signal_matcher(
        self, path: str, interface: str, signal_name: str | None = None
    ) -> dict:
        """Build a filter dict for matching DBus signals."""
        matcher = {
            "interface": interface,
            "path": path,
        }
        if signal_name:
            matcher["member"] = signal_name
        return matcher

    def _wait_for_response(self, request_path: str, timeout: float = 30.0) -> str | None:
        """Wait for a Response signal on the given request path.

        Returns the session_handle string on success, or None on failure.
        """
        if self._connection is None:
            return None

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and not self._stop_event.is_set():
            try:
                msg = self._connection.recv_until_filtered(
                    self._make_signal_matcher(request_path, _REQUEST_IFACE, "Response"),
                    timeout=0.5,
                )
            except Exception:
                continue

            if msg is None:
                continue

            if msg.header.message_type != MessageType.SIGNAL:
                continue

            try:
                # Response signal body:
                # (response_code: u, results: a{sv})
                if not isinstance(msg.body, tuple) or len(msg.body) < 2:
                    continue

                response_code = msg.body[0]
                if response_code != 0:  # Non-zero = failure/cancelled
                    logger.warning("portal_response_error", code=response_code)
                    return None

                results = msg.body[1]
                if not isinstance(results, dict):
                    continue

                # Extract session_handle from results dict.
                # In jeepney, variant dict values may be unwrapped (plain str)
                # or remain as variant tuples ('s', value). Handle both.
                raw = results.get("session_handle")
                if raw is None:
                    continue

                if isinstance(raw, tuple) and len(raw) >= 2:
                    session_handle = raw[1]
                else:
                    session_handle = str(raw)

                if session_handle:
                    return session_handle

            except Exception:
                logger.exception("portal_response_parse_failed")
                return None

        return None

    def _cleanup_connection(self) -> None:
        """Close the DBus connection."""
        if self._connection is not None:
            try:
                if self._session_handle:
                    # CloseSession
                    close_msg = new_method_call(
                        DBusAddress(
                            object_path=self._session_handle,
                            bus_name=_PORTAL_BUS_NAME,
                            interface=_SESSION_IFACE,
                        ),
                        "CloseSession",
                        "",
                        (),
                    )
                    try:
                        self._connection.send(close_msg)
                    except Exception:
                        pass
                self._connection.close()
            except Exception:
                logger.exception("portal_cleanup_error")
            self._connection = None
        self._session_handle = None


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    def on_start():
        print("▶ Recording...")

    def on_stop():
        print("■ Stopped.")

    handler = PortalShortcutHandler(
        hotkey_str="f9",
        start_callback=on_start,
        stop_callback=on_stop,
    )
    ok = handler.start()
    if ok:
        print("Portal shortcut registered. Press F9 to toggle. Ctrl+C to quit.")
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            handler.stop()
            print("Done.")
    else:
        print("ERROR: Could not register portal shortcut (not on Wayland or jeepney missing?).")
