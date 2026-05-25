import queue
import threading
import time
from collections.abc import Generator
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RecordingSession:
    """Isolated state container for a single recording lifecycle."""

    id: str
    audio_queue: "queue.Queue" = field(default_factory=queue.Queue)
    start_time: float = field(default_factory=time.time)
    stop_time: float | None = None
    state: str = "RECORDING"
    field_info: dict[str, Any] | None = None
    raw_text: str = ""
    cleaned_text: str = ""
    app_context: Any | None = None  # AppContext captured at recording start
    stop_event: threading.Event = field(default_factory=threading.Event)

    def mark_stopped(self) -> None:
        self.stop_time = time.time()
        self.state = "STOPPED"
        self.stop_event.set()

    def mark_processing(self) -> None:
        self.state = "PROCESSING"

    def mark_completed(self, raw_text: str, cleaned_text: str) -> None:
        self.raw_text = raw_text
        self.cleaned_text = cleaned_text
        self.state = "COMPLETED"

    def mark_failed(self) -> None:
        self.state = "ERROR"

    def iter_chunks(self, timeout_s: float = 0.25, idle_timeouts: int = 20) -> Generator:
        idle_count = 0
        while True:
            try:
                chunk = self.audio_queue.get(timeout=timeout_s)
            except queue.Empty:
                if self.stop_event.is_set():
                    idle_count += 1
                    if idle_count >= idle_timeouts:
                        break
                continue
            if chunk is None:
                break
            idle_count = 0
            yield chunk
