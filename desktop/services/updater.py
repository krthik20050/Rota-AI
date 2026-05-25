"""
updater.py — background update checker.

Hits the GitHub Releases API once on startup.
Calls on_update_found(latest_version, release_url) on the calling thread
if a newer version is available. The caller is responsible for scheduling
any UI work onto the Qt main thread (e.g. via QTimer.singleShot).
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request

import structlog

logger = structlog.get_logger(__name__)

_GITHUB_API = "https://api.github.com/repos/krthik20050/Rota-AI/releases/latest"
_RELEASES_URL = "https://github.com/krthik20050/Rota-AI/releases/latest"
_TIMEOUT = 10  # seconds


def _version_tuple(version: str) -> tuple[int, ...]:
    """Convert '1.2.3' or 'v1.2.3' to (1, 2, 3)."""
    clean = version.strip().lstrip("v")
    try:
        return tuple(int(x) for x in clean.split("."))
    except ValueError:
        return (0,)


def check_for_update(current_version: str, on_update_found) -> None:
    """
    Start a background thread that checks GitHub for a newer release.

    Args:
        current_version: The running app version, e.g. "1.0.0".
        on_update_found: Callable(latest_version: str, url: str) —
                         called from the background thread when an update exists.
                         Callers must marshal to the Qt thread themselves.
    """

    def _check() -> None:
        try:
            req = urllib.request.Request(
                _GITHUB_API,
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "RotaAI-updater/1.0",
                },
            )
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
                data = json.loads(resp.read().decode())

            tag: str = data.get("tag_name", "").strip().lstrip("v")
            url: str = data.get("html_url", _RELEASES_URL)

            if not tag:
                logger.debug("update_check_no_tag")
                return

            if _version_tuple(tag) > _version_tuple(current_version):
                logger.info("update_available", current=current_version, latest=tag)
                on_update_found(tag, url)
            else:
                logger.debug("update_check_up_to_date", current=current_version, latest=tag)

        except urllib.error.URLError as e:
            logger.debug("update_check_network_error", error=str(e))
        except Exception as e:
            logger.debug("update_check_failed", error=str(e))

    thread = threading.Thread(target=_check, daemon=True, name="update-checker")
    thread.start()
