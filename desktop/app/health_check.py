from __future__ import annotations

import os
import shutil
import sys
import tempfile
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class HealthCheckItem:
    name: str
    status: str
    message: str
    critical: bool = False
    duration_ms: float = 0.0
    details: dict[str, str] = field(default_factory=dict)


@dataclass
class HealthCheckReport:
    checks: list[HealthCheckItem]
    completed_at: float = field(default_factory=time.time)

    def has_critical_failure(self) -> bool:
        return any(item.critical and item.status == "failed" for item in self.checks)

    def is_degraded(self) -> bool:
        return any(item.status in {"failed", "degraded"} for item in self.checks)

    def failed_messages(self) -> list[str]:
        return [
            f"{item.name}: {item.message}"
            for item in self.checks
            if item.status in {"failed", "degraded"}
        ]


class StartupHealthChecker:
    """Runs startup checks off the UI thread and returns a structured report."""

    def __init__(
        self,
        appdata_dir: str,
        model_size: str,
        hotkey_validator: Callable[[], tuple[bool, str]] | None = None,
    ):
        self.appdata_dir = appdata_dir
        self.model_size = model_size
        self.hotkey_validator = hotkey_validator

    def run_async(self, on_complete: Callable[[HealthCheckReport], None]) -> None:
        thread = threading.Thread(
            target=self._run_and_callback,
            args=(on_complete,),
            daemon=True,
            name="startup-health-check",
        )
        thread.start()

    def _run_and_callback(self, on_complete: Callable[[HealthCheckReport], None]) -> None:
        report = self.run()
        try:
            # If running within a Qt app, ensure callback is posted to the
            # Qt main thread to avoid race conditions with UI state.
            from PySide6.QtCore import QTimer

            QTimer.singleShot(0, lambda: on_complete(report))
        except Exception:
            # Fallback: call directly
            on_complete(report)

    def run(self) -> HealthCheckReport:
        checks = [
            self._check_storage(),
            self._check_microphone_access(),
            self._check_model_availability(),
            self._check_platform_integration(),
            self._check_hotkey_registration(),
        ]
        return HealthCheckReport(checks=checks)

    def _check_storage(self) -> HealthCheckItem:
        started = time.perf_counter()
        try:
            os.makedirs(self.appdata_dir, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w",
                dir=self.appdata_dir,
                prefix="health-",
                suffix=".tmp",
                delete=True,
                encoding="utf-8",
            ) as handle:
                handle.write("ok")
                handle.flush()
            return HealthCheckItem(
                name="writable_storage",
                status="ok",
                message="Storage is writable",
                duration_ms=(time.perf_counter() - started) * 1000.0,
            )
        except Exception as exc:
            return HealthCheckItem(
                name="writable_storage",
                status="failed",
                message="Cannot write app data",
                critical=True,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                details={"error": str(exc)},
            )

    def _check_microphone_access(self) -> HealthCheckItem:
        started = time.perf_counter()
        try:
            import sounddevice as sd

            default_input, _default_output = sd.default.device
            if default_input is None or default_input < 0:
                return HealthCheckItem(
                    name="microphone_access",
                    status="failed",
                    message="No default microphone found",
                    critical=True,
                    duration_ms=(time.perf_counter() - started) * 1000.0,
                )
            device_info = sd.query_devices(default_input)
            if int(device_info.get("max_input_channels", 0)) <= 0:
                return HealthCheckItem(
                    name="microphone_access",
                    status="failed",
                    message="Default input device has no input channels",
                    critical=True,
                    duration_ms=(time.perf_counter() - started) * 1000.0,
                )
            return HealthCheckItem(
                name="microphone_access",
                status="ok",
                message=f"Mic available: {device_info.get('name', 'unknown')}",
                duration_ms=(time.perf_counter() - started) * 1000.0,
            )
        except Exception as exc:
            return HealthCheckItem(
                name="microphone_access",
                status="failed",
                message="Microphone check failed",
                critical=True,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                details={"error": str(exc)},
            )

    def _check_model_availability(self) -> HealthCheckItem:
        # IMPORTANT: Do NOT load ctranslate2/WhisperModel here.
        # Concurrent model instantiation from multiple threads corrupts the MKL
        # heap and causes STATUS_FATAL_USER_CALLBACK_EXCEPTION (-1073740771).
        # The real model load happens in TranscriberLoadThread — errors from that
        # are surfaced via _on_transcriber_load_error.
        started = time.perf_counter()
        try:
            import faster_whisper  # noqa: F401 — just verify the package is installed

            _VALID_SIZES = {
                "tiny",
                "tiny.en",
                "base",
                "base.en",
                "small",
                "small.en",
                "medium",
                "medium.en",
                "large-v1",
                "large-v2",
                "large-v3",
            }
            if self.model_size not in _VALID_SIZES:
                return HealthCheckItem(
                    name="model_availability",
                    status="degraded",
                    message=f"Unknown model size '{self.model_size}' — check Settings > Model",
                    duration_ms=(time.perf_counter() - started) * 1000.0,
                )
            return HealthCheckItem(
                name="model_availability",
                status="ok",
                message=f"Whisper model '{self.model_size}' configured — loading in background",
                duration_ms=(time.perf_counter() - started) * 1000.0,
            )
        except ImportError:
            return HealthCheckItem(
                name="model_availability",
                status="failed",
                message="faster-whisper package missing — reinstall dependencies",
                critical=True,
                duration_ms=(time.perf_counter() - started) * 1000.0,
            )
        except Exception as exc:
            return HealthCheckItem(
                name="model_availability",
                status="failed",
                message="Speech model check failed",
                critical=True,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                details={"error": str(exc), "model_size": self.model_size},
            )

    def _check_hotkey_registration(self) -> HealthCheckItem:
        started = time.perf_counter()
        if self.hotkey_validator is None:
            return HealthCheckItem(
                name="hotkey_registration",
                status="degraded",
                message="Hotkey check unavailable",
                critical=False,
                duration_ms=(time.perf_counter() - started) * 1000.0,
            )

        try:
            success, message = self.hotkey_validator()
            return HealthCheckItem(
                name="hotkey_registration",
                status="ok" if success else "failed",
                message=message,
                critical=True,
                duration_ms=(time.perf_counter() - started) * 1000.0,
            )
        except Exception as exc:
            return HealthCheckItem(
                name="hotkey_registration",
                status="failed",
                message="Hotkey validator raised an exception",
                critical=True,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                details={"error": str(exc)},
            )

    def _check_platform_integration(self) -> HealthCheckItem:
        started = time.perf_counter()
        try:
            if sys.platform == "darwin":
                return self._check_macos_integration(started)
            if sys.platform.startswith("linux"):
                return self._check_linux_integration(started)
            return self._check_windows_integration(started)
        except Exception as exc:
            return HealthCheckItem(
                name="platform_integration",
                status="degraded",
                message="Platform integration check failed",
                critical=False,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                details={"error": str(exc)},
            )

    def _check_macos_integration(self, started: float) -> HealthCheckItem:
        missing: list[str] = []
        degraded: list[str] = []

        try:
            import AppKit  # noqa: F401
            import ApplicationServices  # noqa: F401
            import Quartz  # noqa: F401
        except ImportError as exc:
            missing.append(f"PyObjC framework missing: {exc.name}")

        try:
            from plat.macos_setup import check_accessibility, check_input_monitoring

            if not check_accessibility().ok:
                missing.append("Accessibility permission")
            if not check_input_monitoring().ok:
                degraded.append("Input Monitoring permission")
        except Exception as exc:
            degraded.append(f"Permission check failed: {exc}")

        if missing:
            return HealthCheckItem(
                name="platform_integration",
                status="failed",
                message="macOS integration incomplete: " + ", ".join(missing),
                critical=True,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                details={"degraded": ", ".join(degraded)},
            )
        if degraded:
            return HealthCheckItem(
                name="platform_integration",
                status="degraded",
                message="macOS integration partially available: " + ", ".join(degraded),
                critical=False,
                duration_ms=(time.perf_counter() - started) * 1000.0,
            )
        return HealthCheckItem(
            name="platform_integration",
            status="ok",
            message="macOS Accessibility and Input Monitoring are ready",
            duration_ms=(time.perf_counter() - started) * 1000.0,
        )

    def _check_linux_integration(self, started: float) -> HealthCheckItem:
        missing: list[str] = []
        degraded: list[str] = []

        # Determine session type
        on_x11 = bool(os.environ.get("DISPLAY"))
        on_wayland = (
            os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"
            or bool(os.environ.get("WAYLAND_DISPLAY"))
        )
        session_type = "wayland" if on_wayland else "x11" if on_x11 else "unknown"

        # --- Hotkey backends (non-invasive preferred) ---
        # On X11, pynput is the primary backend (no grab, no freeze).
        # On Wayland, jeepney (XDG Desktop Portal) is the primary backend.
        # evdev is only needed as a last-resort fallback on either.
        if on_x11:
            try:
                import pynput  # noqa: F401
            except ImportError:
                degraded.append("pynput (recommended for X11 hotkeys; evdev fallback available)")

        if on_wayland:
            try:
                import jeepney  # noqa: F401
            except ImportError:
                degraded.append("jeepney (recommended for Wayland hotkeys)")

        # evdev is optional — only flagged if neither primary backend is available
        try:
            import evdev  # noqa: F401
        except ImportError:
            if not on_x11 and not on_wayland:
                missing.append("evdev")
            else:
                degraded.append("evdev (fallback only; install for headless/EDE use)")

        # --- Keyring ---
        try:
            import keyring  # noqa: F401
        except ImportError:
            degraded.append("keyring")

        # --- Text injection tools ---
        if on_wayland:
            if not any(shutil.which(tool) for tool in ("wtype", "dotool", "ydotool")):
                missing.append("one of wtype, dotool, or ydotool")
            if shutil.which("wl-copy") is None:
                degraded.append("wl-copy")
        else:
            if shutil.which("xdotool") is None:
                missing.append("xdotool")
            if shutil.which("xclip") is None and shutil.which("wl-copy") is None:
                degraded.append("xclip or wl-copy")

        if missing:
            return HealthCheckItem(
                name="platform_integration",
                status="failed",
                message="Linux integration missing: " + ", ".join(missing),
                critical=True,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                details={"degraded": ", ".join(degraded), "session": session_type or "unknown"},
            )
        if degraded:
            return HealthCheckItem(
                name="platform_integration",
                status="degraded",
                message="Linux integration partially available: " + ", ".join(degraded),
                critical=False,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                details={"session": session_type or "unknown"},
            )
        return HealthCheckItem(
            name="platform_integration",
            status="ok",
            message="Linux platform tools are ready",
            duration_ms=(time.perf_counter() - started) * 1000.0,
            details={"session": session_type or "unknown"},
        )

    def _check_windows_integration(self, started: float) -> HealthCheckItem:
        missing: list[str] = []
        degraded: list[str] = []

        # --- COM/ctypes availability ---
        try:
            import ctypes  # noqa: F401

            # Verify windll user32 is accessible (core Windows API)
            ctypes.windll.user32.GetSystemMetrics(0)
        except Exception:
            missing.append("Windows ctypes API (user32)")

        # --- Audio control (pycaw) ---
        try:
            from pycaw.pycaw import AudioUtilities  # noqa: F401
        except ImportError:
            degraded.append("pycaw (audio ducking/mute)")

        # --- Text injection (win32clipboard, win32con) ---
        try:
            import win32clipboard  # noqa: F401
            import win32con  # noqa: F401
        except ImportError:
            degraded.append("pywin32 (clipboard injection)")

        # --- System tray / startup (winreg) ---
        try:
            import winreg  # noqa: F401
        except ImportError:
            degraded.append("winreg (startup registration)")

        # --- Keyring (optional) ---
        try:
            import keyring  # noqa: F401
        except ImportError:
            degraded.append("keyring (credential storage)")

        # --- Windows version info ---
        try:
            import platform as _platform

            win_ver_str = _platform.win32_ver() or ""
            win_release = _platform.release()
            details: dict[str, str] = {"os": f"Windows {win_release} ({win_ver_str})"}
            major = int(win_release) if win_release.isdigit() else 0
            if major < 10:
                degraded.append("Windows 10+ recommended")
        except Exception:
            details = {"os": "Windows (version unknown)"}

        if missing:
            return HealthCheckItem(
                name="platform_integration",
                status="failed",
                message="Windows integration missing: " + ", ".join(missing),
                critical=True,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                details=details,
            )
        if degraded:
            return HealthCheckItem(
                name="platform_integration",
                status="degraded",
                message="Windows integration degraded: " + ", ".join(degraded),
                critical=False,
                duration_ms=(time.perf_counter() - started) * 1000.0,
                details=details,
            )
        return HealthCheckItem(
            name="platform_integration",
            status="ok",
            message="Windows platform tools are ready",
            duration_ms=(time.perf_counter() - started) * 1000.0,
            details=details,
        )
