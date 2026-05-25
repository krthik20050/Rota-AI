"""
macOS single-instance guard — uses POSIX file locking.

Replaces the Windows kernel32 mutex approach with a lock file at:
  /tmp/rota-ai.lock

The lock is automatically released when the process exits (even on crash).
"""

from __future__ import annotations

import fcntl
import os

import structlog

logger = structlog.get_logger(__name__)

_LOCK_PATH = "/tmp/rota-ai.lock"  # noqa: S108
_lock_fd = None


def try_acquire_instance_lock() -> bool:
    """
    Acquire a process singleton lock via POSIX file locking.
    Returns True if we got the lock, False if another instance is running.
    """
    global _lock_fd
    try:
        _lock_fd = os.open(_LOCK_PATH, os.O_CREAT | os.O_WRONLY)
        fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Write our PID to the lock file
        os.ftruncate(_lock_fd, 0)
        os.write(_lock_fd, str(os.getpid()).encode())
        logger.info("instance_lock_acquired", pid=os.getpid())
        return True
    except OSError:
        logger.warning("instance_lock_failed", lock_path=_LOCK_PATH)
        if _lock_fd is not None:
            try:
                os.close(_lock_fd)
            except Exception:
                pass
            _lock_fd = None
        return False


def release_instance_lock() -> None:
    """Release the singleton lock."""
    global _lock_fd
    if _lock_fd is not None:
        try:
            fcntl.flock(_lock_fd, fcntl.LOCK_UN)
            os.close(_lock_fd)
        except Exception:
            pass
        _lock_fd = None
    try:
        if os.path.exists(_LOCK_PATH):
            os.remove(_LOCK_PATH)
    except Exception:
        pass
    logger.info("instance_lock_released")
