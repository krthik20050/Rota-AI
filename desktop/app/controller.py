"""
controller.py — backward-compat re-export shim.

All logic lives in sub-modules; this file re-exports the public API that
main.py and tests import from `app.controller`.
"""

from __future__ import annotations

import sys

import structlog
from PyQt6.QtCore import QTimer

from app.instance_guard import (
    release_instance_mutex,
    try_acquire_instance_listener,
    try_acquire_instance_mutex,
    wake_existing_instance,
)
from app.logging_config import (
    TailBufferLogHandler,
    configure_logging,
    log_event,
)
from app.processor_thread import ProcessorThread, TranscriberLoadThread
from app.rota_app import RotaApp
from app.signal_bridges import HotkeySignalBridge, RecordingState
from ui.toast import Toast

logger = structlog.get_logger(__name__)

__all__ = [
    "RotaApp",
    "configure_logging",
    "logger",
    "try_acquire_instance_listener",
    "wake_existing_instance",
    "RecordingState",
    "HotkeySignalBridge",
    "ProcessorThread",
    "TranscriberLoadThread",
    "TailBufferLogHandler",
    "log_event",
    "release_instance_mutex",
    "try_acquire_instance_mutex",
    "Toast",
    "QTimer",
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
