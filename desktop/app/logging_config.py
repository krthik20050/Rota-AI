from __future__ import annotations

import logging
import os

import structlog

logger = structlog.get_logger(__name__)


def log_event(event, status="ok", duration_ms=None, error=None, **kwargs):
    event_name = str(event)
    payload = {"status": status}
    if duration_ms is not None:
        payload["duration_ms"] = round(duration_ms, 2)
    if error:
        payload["error"] = str(error)
    payload.update(kwargs)
    payload.pop("event", None)
    if status == "failed":
        logger.error(event_name, **payload)
    else:
        logger.info(event_name, **payload)


def configure_logging():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    def _add_file_handler(path: str) -> None:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            fh = logging.FileHandler(path, encoding="utf-8")
            fh.setFormatter(logging.Formatter("%(message)s"))
            logging.getLogger().addHandler(fh)
        except Exception:
            pass

    # Primary: platform-specific app data directory
    import sys

    if sys.platform == "darwin":
        _appdata_dir = os.path.join(os.path.expanduser("~/Library/Application Support"), "RotaAI")
    elif sys.platform.startswith("linux"):
        _xdg_state = os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state"))
        _appdata_dir = os.path.join(_xdg_state, "rota-ai")
    else:
        _appdata_dir = os.path.join(os.environ.get("APPDATA", "."), "RotaAI")
    _add_file_handler(os.path.join(_appdata_dir, "rota.log"))

    # Secondary: project logs/ dir for easy dev access
    _project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _add_file_handler(os.path.join(_project_root, "logs", "rota.log"))
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", utc=False),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


class TailBufferLogHandler(logging.Handler):
    """Collect logs and forward one-line entries to the UI bridge."""

    def __init__(self, emit_line_callback):
        super().__init__()
        self._emit_line_callback = emit_line_callback
        self.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

    def emit(self, record):
        try:
            line = self.format(record)
            self._emit_line_callback(line)
        except Exception:
            pass
