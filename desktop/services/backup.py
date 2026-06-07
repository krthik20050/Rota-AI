"""
Auto-backup module for Rota AI.

Creates timestamped backups of all user data files (config, snippets,
personal dictionary) to a dedicated backup directory. Runs automatically
on app exit and every 24 hours during operation.

Backup directory: ~/.rota-backups/ (Linux/macOS) or %APPDATA%/RotaAI/backups/ (Windows)
Each backup is a subdirectory named YYYY-MM-DD_HHMMSS.
"""

import json
import os
import shutil
import sys
import threading
import time
from datetime import datetime

from utils.log import get_logger

logger = get_logger(__name__)

_MAX_BACKUPS = 30  # Keep at most 30 backups, oldest removed first
_BACKUP_INTERVAL = 86400  # 24 hours in seconds


def _get_backup_dir() -> str:
    """Return the OS-appropriate backup directory path."""
    if sys.platform.startswith("linux"):
        base = os.path.join(os.path.expanduser("~"), ".rota-backups")
    elif sys.platform == "darwin":
        base = os.path.join(
            os.path.expanduser("~/Library/Application Support"), "RotaAI", "backups"
        )
    else:
        base = os.path.join(os.environ.get("APPDATA", "."), "RotaAI", "backups")
    os.makedirs(base, exist_ok=True)
    return base


def _get_data_files() -> dict[str, str]:
    """
    Discover user data files by checking the standard paths.
    Returns {label: file_path} for each file that exists.
    """
    files: dict[str, str] = {}

    # Config
    if sys.platform.startswith("linux"):
        config_dir = os.path.join(
            os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "rota-ai"
        )
    elif sys.platform == "darwin":
        config_dir = os.path.join(
            os.path.expanduser("~/Library/Application Support"), "RotaAI"
        )
    else:
        config_dir = os.path.join(os.environ.get("APPDATA", "."), "RotaAI")

    config_path = os.path.join(config_dir, "config.json")
    if os.path.exists(config_path):
        files["config.json"] = config_path

    # Snippets
    if sys.platform.startswith("linux"):
        data_dir = os.path.join(
            os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")), "rota-ai"
        )
    elif sys.platform == "darwin":
        data_dir = config_dir  # Same dir on macOS
    else:
        data_dir = config_dir  # Same dir on Windows

    snippets_path = os.path.join(data_dir, "snippets.json")
    if os.path.exists(snippets_path):
        files["snippets.json"] = snippets_path

    # Personal dictionary
    dict_path = os.path.join(data_dir, "personal_dictionary.json")
    if os.path.exists(dict_path):
        files["personal_dictionary.json"] = dict_path

    # Auto-improvement log
    auto_path = os.path.join(data_dir, "auto_improvement.json")
    if os.path.exists(auto_path):
        files["auto_improvement.json"] = auto_path

    # Dictionary words
    words_path = os.path.join(data_dir, "dictionary.json")
    if os.path.exists(words_path):
        files["dictionary.json"] = words_path

    return files


def create_backup() -> str | None:
    """
    Create a timestamped backup of all user data files.

    Returns the backup directory path on success, or None on failure.
    """
    try:
        data_files = _get_data_files()
        if not data_files:
            logger.info("backup_skipped_no_data_files")
            return None

        backup_base = _get_backup_dir()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        backup_path = os.path.join(backup_base, timestamp)
        os.makedirs(backup_path, exist_ok=True)

        # Copy each file with metadata preserved
        for label, src_path in data_files.items():
            dst_path = os.path.join(backup_path, label)
            shutil.copy2(src_path, dst_path)

        # Write a manifest
        manifest = {
            "created_at": datetime.now().isoformat(),
            "files": list(data_files.keys()),
            "version": "1.0",
        }
        manifest_path = os.path.join(backup_path, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        logger.info("backup_created path=%s files=%d", backup_path, len(data_files))

        # Prune old backups
        _prune_old_backups(backup_base)

        return backup_path
    except Exception:
        logger.exception("backup_creation_failed")
        return None


def _prune_old_backups(backup_base: str) -> None:
    """Remove oldest backups exceeding _MAX_BACKUPS."""
    try:
        backup_dirs = sorted(
            [
                os.path.join(backup_base, d)
                for d in os.listdir(backup_base)
                if os.path.isdir(os.path.join(backup_base, d))
            ]
        )
        while len(backup_dirs) > _MAX_BACKUPS:
            oldest = backup_dirs.pop(0)
            shutil.rmtree(oldest, ignore_errors=True)
            logger.info("backup_pruned path=%s", oldest)
    except Exception:
        logger.debug("backup_prune_failed", exc_info=True)


def list_backups() -> list[dict]:
    """
    List all available backups with timestamps and file counts.

    Returns a list of dicts: [{path, timestamp, file_count}, ...]
    Sorted newest-first.
    """
    backup_base = _get_backup_dir()
    backups: list[dict] = []
    try:
        for d in sorted(os.listdir(backup_base), reverse=True):
            backup_path = os.path.join(backup_base, d)
            if not os.path.isdir(backup_path):
                continue
            manifest_path = os.path.join(backup_path, "manifest.json")
            file_count = 0
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, encoding="utf-8") as f:
                        manifest = json.load(f)
                    file_count = len(manifest.get("files", []))
                except Exception:
                    file_count = len(
                        [f for f in os.listdir(backup_path) if f != "manifest.json"]
                    )
            else:
                file_count = len(
                    [f for f in os.listdir(backup_path) if f != "manifest.json"]
                )
            backups.append(
                {
                    "path": backup_path,
                    "timestamp": d,
                    "file_count": file_count,
                }
            )
    except Exception:
        logger.debug("backup_list_failed", exc_info=True)
    return backups


class AutoBackupManager:
    """
    Manages automatic periodic backups of user data.

    Starts a background daemon thread that backs up on first call and
    every _BACKUP_INTERVAL seconds thereafter. Also provides a one-shot
    backup method for app-exit triggers.
    """

    def __init__(self, enabled: bool = True):
        self._enabled = enabled
        self._last_backup_time: float = 0.0
        self._timer: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        """Start the periodic backup daemon thread."""
        if not self._enabled:
            logger.info("auto_backup_disabled")
            return
        if self._timer is not None and self._timer.is_alive():
            return
        self._stop_event.clear()
        self._timer = threading.Thread(target=self._backup_loop, daemon=True)
        self._timer.start()
        logger.info("auto_backup_started interval_s=%d", _BACKUP_INTERVAL)

    def stop(self) -> None:
        """Stop the periodic backup thread."""
        self._stop_event.set()
        if self._timer is not None:
            self._timer.join(timeout=5)
            self._timer = None
        logger.info("auto_backup_stopped")

    def backup_now(self) -> str | None:
        """Perform an immediate backup. Returns backup path or None."""
        path = create_backup()
        if path:
            self._last_backup_time = time.time()
        return path

    def _backup_loop(self) -> None:
        """Background loop: backup immediately, then every interval."""
        while not self._stop_event.is_set():
            now = time.time()
            if now - self._last_backup_time >= _BACKUP_INTERVAL:
                self.backup_now()
            self._stop_event.wait(300)  # Check every 5 minutes
