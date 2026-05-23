from __future__ import annotations

from enum import Enum

from PyQt6.QtCore import QObject, pyqtSignal


class HotkeySignalBridge(QObject):
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()


class DebugLogBridge(QObject):
    line_received = pyqtSignal(str)


class RecordingState(Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    INJECTING = "INJECTING"
    DONE = "DONE"
    ERROR = "ERROR"
