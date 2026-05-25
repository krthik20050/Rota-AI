"""
Linux startup registration -- replaces Windows winreg approach.

Uses XDG Autostandard to register/unregister the app for session startup.
Reference: https://specifications.freedesktop.org/autostart-spec/autostart-spec-latest.html
"""

from __future__ import annotations

import os

import structlog

logger = structlog.get_logger(__name__)

_AUTOSTART_DIR = os.path.expanduser("~/.config/autostart")
_DESKTOP_FILE = "rota-ai.desktop"


def register_startup(exe_path: str, app_name: str = "Rota AI") -> bool:
    """
    Register the application to start on login via XDG autostart.
    Creates ~/.config/autostart/rota-ai.desktop
    """
    try:
        os.makedirs(_AUTOSTART_DIR, exist_ok=True)
        dest = os.path.join(_AUTOSTART_DIR, _DESKTOP_FILE)

        desktop_entry = f"""[Desktop Entry]
Type=Application
Name={app_name}
Comment=Voice dictation for Linux
Exec={exe_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
X-KDE-autostart-after=panel
"""

        with open(dest, "w", encoding="utf-8") as f:
            f.write(desktop_entry)

        logger.info("startup_registered", path=dest)
        return True
    except Exception as e:
        logger.error("startup_registration_failed", error=str(e))
        return False


def unregister_startup() -> bool:
    """
    Unregister the application from session startup.
    Removes ~/.config/autostart/rota-ai.desktop
    """
    try:
        dest = os.path.join(_AUTOSTART_DIR, _DESKTOP_FILE)
        if os.path.exists(dest):
            os.remove(dest)
            logger.info("startup_unregistered", path=dest)
        return True
    except Exception as e:
        logger.error("startup_unregistration_failed", error=str(e))
        return False


def is_startup_enabled() -> bool:
    """Check if the application is registered for session startup."""
    dest = os.path.join(_AUTOSTART_DIR, _DESKTOP_FILE)
    return os.path.exists(dest)
