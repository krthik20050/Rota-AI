"""Tests for app.instance_guard — single-instance helpers."""

import socket
import threading
from unittest.mock import patch

import pytest

import app.instance_guard as guard


@pytest.fixture(autouse=True)
def reset_mutex():
    original = guard._instance_mutex_handle
    yield
    guard._instance_mutex_handle = original


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class TestWakeExistingInstance:
    def test_returns_false_when_nothing_listening(self):
        # Use a port that has nothing listening
        with patch.object(guard, "_INSTANCE_WAKE_PORT", _find_free_port()):
            result = guard.wake_existing_instance()
        assert result is False

    def test_sends_magic_bytes_to_listener(self):
        port = _find_free_port()
        received = []
        ready = threading.Event()
        done = threading.Event()

        def _server():
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("127.0.0.1", port))
            srv.listen(1)
            srv.settimeout(3.0)
            ready.set()
            try:
                conn, _ = srv.accept()
                data = conn.recv(64)
                received.append(data)
                conn.close()
            except Exception:
                pass
            finally:
                srv.close()
                done.set()

        t = threading.Thread(target=_server, daemon=True)
        t.start()
        ready.wait(timeout=2)

        with patch.object(guard, "_INSTANCE_WAKE_PORT", port):
            result = guard.wake_existing_instance()

        done.wait(timeout=2)
        assert result is True
        assert received and guard._WAKE_MAGIC in received[0]


class TestTryAcquireInstanceListener:
    def test_returns_none_when_mutex_fails(self):
        with patch.object(guard, "try_acquire_instance_mutex", return_value=False):
            result = guard.try_acquire_instance_listener()
        assert result is None

    def test_returns_none_when_port_in_use(self):
        port = _find_free_port()
        blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        blocker.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            blocker.bind(("127.0.0.1", port))
            blocker.listen(1)
            with (
                patch.object(guard, "try_acquire_instance_mutex", return_value=True),
                patch.object(guard, "_INSTANCE_WAKE_PORT", port),
            ):
                result = guard.try_acquire_instance_listener()
            assert result is None
        finally:
            blocker.close()
