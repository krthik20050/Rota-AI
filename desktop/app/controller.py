"""
controller.py — re-exports the public API that main.py and tests consume.

All logic lives in sub-modules; this file re-exports only what external
consumers actually import from `app.controller`.
"""

from __future__ import annotations

import sys

import structlog

from app.instance_guard import (
    try_acquire_instance_listener,
    wake_existing_instance,
)
from app.logging_config import configure_logging
from app.rota_app import RotaApp
from app.signal_bridges import RecordingState

logger = structlog.get_logger(__name__)

__all__ = [
    "RotaApp",
    "configure_logging",
    "logger",
    "try_acquire_instance_listener",
    "wake_existing_instance",
    "RecordingState",
]

if __name__ == "__main__":
    configure_logging()
    sock = try_acquire_instance_listener()
    if sock is None:
        ok = wake_existing_instance()
        logger.info("second_launch_wake", ok=ok)
        sys.exit(0 if ok else 1)
    app = RotaApp(instance_listen_sock=sock)
    app.run()
