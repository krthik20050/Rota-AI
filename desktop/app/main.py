import faulthandler
import os
import sys
import threading
import traceback
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── Native stability ──────────────────────────────────────────────────────────
# Dump Python stack trace to stderr on native crash (SIGSEGV, SIGABRT etc.)
# sys.stderr is None in windowed PyInstaller builds (console=False) — guard it.
if sys.stderr is not None:
    faulthandler.enable()

# Prevent ctranslate2/MKL/OpenMP thread storms that cause STATUS_STACK_BUFFER_OVERRUN (0xC0000409).
# These MUST be set before any native library imports.
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("CT2_VERBOSE", "0")   # suppress ctranslate2 noise

# Pre-import torch on the main thread.
# On Windows, torch.distributed.distributed_c10d crashes with an access violation
# when first imported from a background thread. Importing here ensures the native
# extension is fully initialized before any worker threads start.
try:
    import torch  # noqa: F401
    import torch.distributed  # noqa: F401 — pre-warm the crash-prone submodule
except Exception:
    pass

# ── Logging ───────────────────────────────────────────────────────────────────
from app.controller import (
    RotaApp,
    configure_logging,
    logger,
    try_acquire_instance_listener,
    wake_existing_instance,
)


def _show_crash_dialog(title: str, exc_type, exc_value, tb_str: str) -> None:
    """Show a visible error dialog so users can report the exact error."""
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance()
        if app is None:
            return
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(f"<b>{exc_type.__name__}:</b> {exc_value}")
        msg.setInformativeText(
            "Rota encountered an unexpected error.\n\n"
            "Please copy the details below and report this at:\n"
            "github.com/ruvnet/rota-ai/issues"
        )
        msg.setDetailedText(tb_str)
        msg.exec()
    except Exception:
        pass  # dialog failed — stderr print below is the fallback


def _excepthook(exc_type, exc_value, exc_tb):
    """Catch any unhandled exception on the main thread — log it, don't silently die."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        logger.error("unhandled_main_thread_exception type=%s\n%s", exc_type.__name__, tb_str)
    except Exception:
        print(f"UNHANDLED EXCEPTION: {exc_type.__name__}: {exc_value}\n{tb_str}", file=sys.stderr)
    _show_crash_dialog("Rota — Unexpected Error", exc_type, exc_value, tb_str)


def _thread_excepthook(args):
    """Catch any unhandled exception in a background thread — log it instead of silently dying."""
    if args.exc_type is SystemExit:
        return
    tb_str = "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
    try:
        thread_name = args.thread.name if args.thread else "unknown"
        logger.error("unhandled_thread_exception thread=%r type=%s\n%s",
                     thread_name, args.exc_type.__name__, tb_str)
    except Exception:
        print(f"THREAD CRASH: {args.exc_type.__name__}: {args.exc_value}\n{tb_str}", file=sys.stderr)
    _show_crash_dialog(
        f"Rota — Thread Crash ({args.thread.name if args.thread else 'unknown'})",
        args.exc_type,
        args.exc_value,
        tb_str,
    )


sys.excepthook = _excepthook
threading.excepthook = _thread_excepthook


def run() -> None:
    configure_logging()
    sock = try_acquire_instance_listener()
    if sock is None:
        # Grant the running instance permission to steal focus.
        # Windows blocks SetForegroundWindow unless the foreground process allows it.
        # On Linux this is handled by the compositor.
        if sys.platform == "win32":
            try:
                import ctypes
                ASFW_ANY = 0xFFFFFFFF
                ctypes.windll.user32.AllowSetForegroundWindow(ASFW_ANY)
            except Exception:
                pass
        ok = wake_existing_instance()
        logger.info("second_launch_wake", ok=ok)
        if ok:
            print("\n  Rota is already running - brought the window to the front.\n", flush=True)
        else:
            print(
                "\n  Rota may already be running - check the system tray.\n"
                "  (Could not signal the running window.)\n",
                flush=True,
            )
        return
    app = RotaApp(instance_listen_sock=sock)
    app.run()


if __name__ == "__main__":
    run()
