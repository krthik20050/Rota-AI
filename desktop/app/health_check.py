from __future__ import annotations

import os
import tempfile
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class HealthCheckItem:
    name: str
    status: str
    message: str
    critical: bool = False
    duration_ms: float = 0.0
    details: Dict[str, str] = field(default_factory=dict)


@dataclass
class HealthCheckReport:
    checks: List[HealthCheckItem]
    completed_at: float = field(default_factory=time.time)

    def has_critical_failure(self) -> bool:
        return any(item.critical and item.status == "failed" for item in self.checks)

    def is_degraded(self) -> bool:
        return any(item.status in {"failed", "degraded"} for item in self.checks)

    def failed_messages(self) -> List[str]:
        return [f"{item.name}: {item.message}" for item in self.checks if item.status in {"failed", "degraded"}]


class StartupHealthChecker:
    """Runs startup checks off the UI thread and returns a structured report."""

    def __init__(
        self,
        appdata_dir: str,
        model_size: str,
        hotkey_validator: Optional[Callable[[], tuple[bool, str]]] = None,
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
            from PyQt6.QtCore import QTimer

            QTimer.singleShot(0, lambda: on_complete(report))
        except Exception:
            # Fallback: call directly
            on_complete(report)

    def run(self) -> HealthCheckReport:
        checks = [
            self._check_storage(),
            self._check_microphone_access(),
            self._check_model_availability(),
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
                "tiny", "tiny.en", "base", "base.en",
                "small", "small.en", "medium", "medium.en",
                "large-v1", "large-v2", "large-v3",
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
