"""Compositor detection for Linux desktop environments.

Provides compositor-aware utilities so the app can:
- Detect GNOME, KDE, Sway, Hyprland, etc.
- Suggest compositor-specific setup instructions
- Fall back gracefully on unsupported compositors

Usage:
    from plat.compositor import detect_compositor

    info = detect_compositor()
    info.name         # "gnome", "kde", "sway", "hyprland", "other-wayland", "x11", "unknown"
    info.display_server  # "wayland", "x11", "tty", "unknown"
    info.is_wayland      # True/False
    info.session_type    # raw XDG_SESSION_TYPE value
    print(info.setup_guide())  # compositor-specific setup instructions
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field


@dataclass
class CompositorInfo:
    """Detected compositor and desktop environment metadata."""

    name: str = "unknown"
    display_server: str = "unknown"
    desktop_env: str = ""
    session_type: str = ""

    # Flavour-specific indicators (used for debugging)
    _indicators: dict[str, str] = field(default_factory=dict)

    @property
    def is_wayland(self) -> bool:
        return self.display_server == "wayland"

    @property
    def is_x11(self) -> bool:
        return self.display_server == "x11"

    @property
    def supports_portal(self) -> bool:
        """Return True if known to support XDG Desktop Portal GlobalShortcuts.

        Supported compositors:
          - GNOME 42+
          - KDE Plasma 5.25+
          - Sway 1.8+
          - Hyprland (recent versions)
        """
        portal_ready = {"gnome", "kde", "sway", "hyprland"}
        return self.name in portal_ready

    @property
    def needs_pynput(self) -> bool:
        """Return True if the user should install pynput for non-invasive hotkeys."""
        return self.is_x11

    def setup_guide(self) -> str:
        """Return compositor-specific setup instructions."""
        guides = {
            "gnome": (
                "GNOME detected. Global shortcuts are supported via XDG Desktop Portal.\n"
                "  • GNOME 42+ includes the GlobalShortcuts portal.\n"
                "  • Make sure 'jeepney' is installed: pip install jeepney\n"
                "  • If shortcuts don't work, check Settings → Keyboard → Keyboard Shortcuts\n"
                "    and ensure no conflict with the F9 key.\n"
            ),
            "kde": (
                "KDE Plasma detected. Global shortcuts are supported via XDG Desktop Portal.\n"
                "  • KDE Plasma 5.25+ includes the GlobalShortcuts portal.\n"
                "  • Make sure 'jeepney' is installed: pip install jeepney\n"
                "  • If shortcuts don't work, check System Settings → Shortcuts\n"
                "    and ensure Rota's hotkey is not conflicting.\n"
            ),
            "sway": (
                "Sway detected. Global shortcuts are supported via XDG Desktop Portal.\n"
                "  • Sway 1.8+ includes the GlobalShortcuts portal.\n"
                "  • Make sure 'jeepney' is installed: pip install jeepney\n"
                "  • You may need 'xdg-desktop-portal-wlr' installed:\n"
                "      sudo apt install xdg-desktop-portal-wlr\n"
                "  • If using the evdev fallback, add your user to the 'input' group:\n"
                "      sudo usermod -aG input $USER  then log out and back in.\n"
            ),
            "hyprland": (
                "Hyprland detected. Global shortcuts are supported via XDG Desktop Portal.\n"
                "  • Make sure 'jeepney' and 'xdg-desktop-portal-hyprland' are installed:\n"
                "      pip install jeepney\n"
                "      sudo apt install xdg-desktop-portal-hyprland\n"
                "  • Restart the portal service if shortcuts don't work:\n"
                "      systemctl --user restart xdg-desktop-portal\n"
            ),
            "other-wayland": (
                "Wayland compositor detected (not GNOME/KDE/Sway/Hyprland).\n"
                "  • Rota will attempt the XDG Desktop Portal GlobalShortcuts backend,\n"
                "    but your compositor may not support it.\n"
                "  • If the portal backend fails, evdev will be used as fallback\n"
                "    (may freeze keyboard).\n"
                "  • To use evdev: sudo usermod -aG input $USER  then log out and back in.\n"
            ),
            "x11": (
                "X11 detected. Rota will use pynput for non-invasive hotkeys.\n"
                "  • Install pynput if not already installed: pip install pynput\n"
                "  • pynput uses XGrabKey — only captures the hotkey, not all keys.\n"
                "  • No keyboard freeze on X11.\n"
            ),
        }
        return guides.get(self.name, self._unknown_guide())

    def _unknown_guide(self) -> str:
        base = (
            "Desktop environment not fully detected.\n"
            "  • Rota will try the best available hotkey backend.\n"
            "  • If you experience keyboard freeze, install pynput:\n"
            "      pip install pynput\n"
            "  • Or run with a specific backend: --hotkey-backend=pynput\n"
            "  • evdev fallback requires 'input' group membership:\n"
            "      sudo usermod -aG input $USER  then log out and back in.\n"
        )
        return base

    def short_summary(self) -> str:
        """One-line summary for health checks / logging."""
        if self.is_x11:
            return f"X11 / {self.desktop_env or 'generic'}"
        if self.is_wayland:
            return f"Wayland / {self.name.replace('-', ' ').title()}"
        return f"{self.display_server} / {self.name}"


def detect_compositor() -> CompositorInfo:
    """Detect the current Linux compositor / desktop environment.

    Returns a CompositorInfo dataclass with the detected environment.
    """
    info = CompositorInfo()
    info.session_type = os.environ.get("XDG_SESSION_TYPE", "").lower().strip()

    # ── Display server detection ──────────────────────────────────────────
    if os.environ.get("WAYLAND_DISPLAY"):
        info.display_server = "wayland"
    elif os.environ.get("DISPLAY"):
        info.display_server = "x11"
    elif info.session_type == "wayland":
        info.display_server = "wayland"
    elif info.session_type == "x11":
        info.display_server = "x11"
    elif info.session_type == "tty":
        info.display_server = "tty"
    else:
        info.display_server = "unknown"

    info._indicators["XDG_SESSION_TYPE"] = info.session_type
    info._indicators["WAYLAND_DISPLAY"] = os.environ.get("WAYLAND_DISPLAY", "")
    info._indicators["DISPLAY"] = os.environ.get("DISPLAY", "")

    # ── Compositor / DE detection ─────────────────────────────────────────
    xdg_current = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    desktop_session = os.environ.get("DESKTOP_SESSION", "").lower()
    info._indicators["XDG_CURRENT_DESKTOP"] = xdg_current
    info._indicators["DESKTOP_SESSION"] = desktop_session

    # GNOME
    if (
        "gnome" in xdg_current
        or "gnome" in desktop_session
        or os.environ.get("GNOME_DESKTOP_SESSION_ID")
    ):
        info.name = "gnome"
        info.desktop_env = xdg_current or desktop_session
        return info

    # KDE Plasma
    if "kde" in xdg_current or "kde" in desktop_session or "plasma" in xdg_current:
        info.name = "kde"
        info.desktop_env = xdg_current or desktop_session
        return info

    # Sway (wlroots)
    if (
        "sway" in xdg_current
        or "sway" in desktop_session
        or os.environ.get("SWAYSOCK")
        or shutil.which("swaymsg")
    ):
        info.name = "sway"
        info.desktop_env = xdg_current or desktop_session
        info._indicators["SWAYSOCK"] = os.environ.get("SWAYSOCK", "")
        return info

    # Hyprland
    if (
        "hyprland" in xdg_current
        or "hyprland" in desktop_session
        or os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    ):
        info.name = "hyprland"
        info.desktop_env = xdg_current or desktop_session
        info._indicators["HYPRLAND_INSTANCE_SIGNATURE"] = os.environ.get(
            "HYPRLAND_INSTANCE_SIGNATURE", ""
        )
        return info

    # Other known Wayland compositors
    wayland_compositors = {"wlroots", "river", "wayfire", "cosmic"}
    if info.is_wayland:
        for comp in wayland_compositors:
            if comp in xdg_current or comp in desktop_session:
                info.name = comp
                info.desktop_env = xdg_current or desktop_session
                return info
        # Wayland but unknown compositor
        info.name = "other-wayland"
        info.desktop_env = xdg_current or desktop_session
        return info

    # X11 (not Wayland)
    if info.is_x11:
        info.name = "x11"
        info.desktop_env = xdg_current or desktop_session
        return info

    # Unknown
    info.desktop_env = xdg_current or desktop_session
    return info
