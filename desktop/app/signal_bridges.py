from __future__ import annotations

from enum import Enum

from PySide6.QtCore import QObject, Signal


class HotkeySignalBridge(QObject):
    start_requested = Signal()
    stop_requested = Signal()


class DebugLogBridge(QObject):
    line_received = Signal(str)


class RecordingState(Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    INJECTING = "INJECTING"
    DONE = "DONE"
    ERROR = "ERROR"
