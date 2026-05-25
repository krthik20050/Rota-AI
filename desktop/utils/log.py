"""
Structured logging wrapper — stdlib Logger with structlog-style keyword arguments.

Usage (same API as structlog):
    logger = get_logger(__name__)
    logger.info("event_name", key="value", count=42)
    logger.error("fail", exc_info=True)
"""

import logging


class StructLogger:
    """stdlib Logger that accepts keyword arguments by appending them to the message."""

    __slots__ = ("_log",)

    def __init__(self, name: str):
        self._log = logging.getLogger(name)

    def _fmt(self, msg: str, kwargs: dict) -> str:
        if not kwargs:
            return msg
        return msg + " " + " ".join(f"{k}={v!r}" for k, v in kwargs.items())

    def debug(self, msg: str, *args, **kwargs):
        if self._log.isEnabledFor(logging.DEBUG):
            exc_info = kwargs.pop("exc_info", False)
            self._log.debug(self._fmt(msg, kwargs), *args, exc_info=exc_info)

    def info(self, msg: str, *args, **kwargs):
        if self._log.isEnabledFor(logging.INFO):
            exc_info = kwargs.pop("exc_info", False)
            self._log.info(self._fmt(msg, kwargs), *args, exc_info=exc_info)

    def warning(self, msg: str, *args, **kwargs):
        exc_info = kwargs.pop("exc_info", False)
        self._log.warning(self._fmt(msg, kwargs), *args, exc_info=exc_info)

    def error(self, msg: str, *args, **kwargs):
        exc_info = kwargs.pop("exc_info", False)
        self._log.error(self._fmt(msg, kwargs), *args, exc_info=exc_info)

    def critical(self, msg: str, *args, **kwargs):
        exc_info = kwargs.pop("exc_info", False)
        self._log.critical(self._fmt(msg, kwargs), *args, exc_info=exc_info)

    def exception(self, msg: str, *args, **kwargs):
        kwargs.pop("exc_info", None)  # always True for exception()
        self._log.exception(self._fmt(msg, kwargs), *args)

    def bind(self, **_) -> "StructLogger":
        return self  # structlog compatibility no-op


def get_logger(name: str) -> StructLogger:
    return StructLogger(name)
