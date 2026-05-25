"""
macOS startup registration — uses launchd plist.

Registers/unregisters the app for login via a launchd agent plist at:
  ~/Library/LaunchAgents/com.rota-ai.plist

Reference: https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html
"""

from __future__ import annotations

import os
import subprocess
import structlog

logger = structlog.get_logger(__name__)

_AUTOSTART_DIR = os.path.expanduser("~/Library/LaunchAgents")
_PLIST_FILE = "com.rota-ai.plist"
_LABEL = "com.rota-ai"


def register_startup(exe_path: str, app_name: str = "Rota AI") -> bool:
    """
    Register the application to start on login via launchd.
    Creates ~/Library/LaunchAgents/com.rota-ai.plist
    """
    try:
        os.makedirs(_AUTOSTART_DIR, exist_ok=True)
        dest = os.path.join(_AUTOSTART_DIR, _PLIST_FILE)

        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exe_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/rota-ai.stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/rota-ai.stderr.log</string>
</dict>
</plist>
"""
        with open(dest, "w", encoding="utf-8") as f:
            f.write(plist_content)

        # Unload first (in case of re-registration)
        subprocess.run(["launchctl", "unload", dest], capture_output=True, timeout=5)
        # Load the agent using modern bootstrap (launchctl load is deprecated)
        subprocess.run(
            ["launchctl", "bootstrap", "gui/{}".format(os.getuid()), dest],
            capture_output=True, timeout=5,
        )

        logger.info("startup_registered", path=dest)
        return True
    except Exception as e:
        logger.error("startup_registration_failed", error=str(e))
        return False


def unregister_startup() -> bool:
    """
    Unregister the application from login.
    Removes ~/Library/LaunchAgents/com.rota-ai.plist
    """
    try:
        dest = os.path.join(_AUTOSTART_DIR, _PLIST_FILE)
        if os.path.exists(dest):
            # Unload using modern bootout (launchctl unload is deprecated)
            subprocess.run(
                ["launchctl", "bootout", "gui/{}".format(os.getuid()), dest],
                capture_output=True, timeout=5,
            )
            os.remove(dest)
            logger.info("startup_unregistered", path=dest)
        return True
    except Exception as e:
        logger.error("startup_unregistration_failed", error=str(e))
        return False


def is_startup_enabled() -> bool:
    """Check if the application is registered for login."""
    dest = os.path.join(_AUTOSTART_DIR, _PLIST_FILE)
    return os.path.exists(dest)
