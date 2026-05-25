from __future__ import annotations

import ctypes
import os
import socket

_INSTANCE_WAKE_PORT = 47201
_WAKE_MAGIC = b"ROTA_WAKE_MAIN\n"
_INSTANCE_MUTEX_NAME = "Global\\RotaAI.SingleInstance"
_instance_mutex_handle = None


def try_acquire_instance_mutex() -> bool:
    """Acquire a process singleton mutex on Windows; best-effort pass-through elsewhere."""
    global _instance_mutex_handle
    if os.name != "nt":
        return True

    kernel32 = ctypes.windll.kernel32
    handle = kernel32.CreateMutexW(None, False, _INSTANCE_MUTEX_NAME)
    if not handle:
        # Fail-open: keep app usable if mutex API unexpectedly fails.
        return True
    ERROR_ALREADY_EXISTS = 183
    if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(handle)
        return False
    _instance_mutex_handle = handle
    return True


def release_instance_mutex() -> None:
    global _instance_mutex_handle
    if os.name != "nt" or _instance_mutex_handle is None:
        return
    try:
        ctypes.windll.kernel32.CloseHandle(_instance_mutex_handle)
    except Exception:
        pass
    _instance_mutex_handle = None


def try_acquire_instance_listener() -> socket.socket | None:
    """Bind loopback port if we are the primary instance; otherwise None."""
    if not try_acquire_instance_mutex():
        return None

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Enforce single-owner bind on Windows so parallel launches cannot both listen.
    if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    try:
        sock.bind(("127.0.0.1", _INSTANCE_WAKE_PORT))
        sock.listen(8)
        sock.setblocking(False)
        return sock
    except OSError:
        sock.close()
        release_instance_mutex()
        return None


def wake_existing_instance() -> bool:
    """Ask the primary instance to show its main window."""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(3.0)
        client.connect(("127.0.0.1", _INSTANCE_WAKE_PORT))
        client.sendall(_WAKE_MAGIC)
        try:
            client.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        client.close()
        return True
    except OSError:
        return False
