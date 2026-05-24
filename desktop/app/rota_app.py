from __future__ import annotations

import logging
import os
import socket
import sys
import threading
from typing import Callable

import structlog

from PyQt6.QtCore import QObject, QSocketNotifier, QTimer, Qt, pyqtSlot
from PyQt6.QtWidgets import QApplication

from app.health_check import HealthCheckReport, StartupHealthChecker
from app.service_wiring import build_app_services
from plat import get_hotkey_handler as _get_hotkey_handler
from ui.history_window import HistoryWindow
from ui.main_window import MainWindow
from ui.overlay.pill_overlay import PillOverlay
from ui.settings_window import SettingsWindow
from ui.tray import RotaTrayIcon
from data.snippets import SnippetsManager
from ai.auto_improvement import AutoImprovementSystem
from app.instance_guard import release_instance_mutex
from app.logging_config import log_event
from app.signal_bridges import HotkeySignalBridge, RecordingState
from ui.toast import Toast

# Mixins — each handles a coherent subsystem
from app.thread_lifecycle_mixin import ThreadLifecycleMixin
from app.recording_state_mixin import RecordingStateMixin
from app.transcriber_mixin import TranscriberMixin
from app.processing_pipeline_mixin import ProcessingPipelineMixin
from app.hotkey_mixin import HotkeyMixin

logger = structlog.get_logger(__name__)


class RotaApp(
    ThreadLifecycleMixin,
    RecordingStateMixin,
    TranscriberMixin,
    ProcessingPipelineMixin,
    HotkeyMixin,
    QObject,
):
    """Main application controller. Coordinates all subsystems via mixins."""

    def __init__(self, instance_listen_sock: socket.socket | None = None):
        self.app = QApplication(sys.argv)
        super().__init__()
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setApplicationName("Rota")
        logger.info("app_start")

        self._instance_listen_sock = instance_listen_sock
        self._instance_wake_notifier = None
        if instance_listen_sock is not None:
            self._instance_wake_notifier = QSocketNotifier(
                instance_listen_sock.fileno(),
                QSocketNotifier.Type.Read,
                self,
            )
            self._instance_wake_notifier.activated.connect(self._on_instance_wake_ready)

        services = build_app_services()
        self.config = services.config
        self.history = services.history
        self.session_store = services.session_store
        self.insights_service = services.insights_service
        self.enhanced_insights = services.enhanced_insights
        self.recorder = services.recorder
        self.transcriber = None
        self.ai_processor = services.ai_processor
        self.injector = services.injector
        self.snippets = SnippetsManager()
        self.auto_improvement = AutoImprovementSystem(
            personal_dict=self.ai_processor.personal_dict if self.ai_processor else None
        )
        from audio.audio_control import SystemAudioController
        self.audio_controller = SystemAudioController(self.config)

        self.state = RecordingState.IDLE
        self._start_time = 0
        self._current_model_size = str(self.config.get("model_size") or "base")
        self._current_cpu_threads = int(self.config.get("cpu_threads", 0))
        self._state_lock = threading.RLock()
        self._hotkey_last_trigger_at = 0.0
        self._hotkey_debounce_seconds = 0.2
        self._hotkey_restart_attempted = False
        self._processing_session_id = None
        self._processor_thread = None
        self._retired_processor_threads = []
        self._processor_thread_lock = threading.Lock()
        self._duration_timer = QTimer()
        self._duration_timer.timeout.connect(self._check_max_duration)
        self._processing_timeout_timer = QTimer(self)
        self._processing_timeout_timer.setSingleShot(True)
        self._processing_timeout_timer.timeout.connect(self._on_processing_timeout)
        self._active_toast = None
        self._active_session = None
        self._sessions = {}
        self._transcriber_thread = None
        self._retired_transcriber_threads = []
        self._transcriber_loading = False
        self._transcriber_error = None
        self._transcriber_state_lock = threading.Lock()
        self._health_report = None
        self._recording_enabled = True
        self._metrics_timer = QTimer()
        self._metrics_timer.timeout.connect(self._update_metrics)
        self._metrics_timer.start(1000)

        self._last_session_id = None
        self._latest_raw_text = ""
        self._latest_cleaned_text = ""
        self._latest_timings = {}
        self._last_recording_seconds = 0.0

        self.overlay = PillOverlay()
        self.recorder.audio_level_signal.connect(self.overlay.on_audio_level)
        self.overlay.stop_requested.connect(self._handle_hotkey_stop)
        self.overlay.cancel_requested.connect(self._cancel_recording)

        self.hotkey_bridge = HotkeySignalBridge()
        self.hotkey_bridge.start_requested.connect(self._handle_hotkey_start)
        self.hotkey_bridge.stop_requested.connect(self._handle_hotkey_stop)

        self.main_window = MainWindow(
            self.history,
            self._handle_manual_start,
            self._handle_manual_stop,
            self.show_settings,
            snippets_manager=self.snippets,
            personal_dict=self.ai_processor.personal_dict if self.ai_processor else None,
            ai_processor=self.ai_processor if self.config.get("ai_enabled") else None,
            config=self.config,
        )
        self.main_window.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)

        self._onboarding_pending = not self.config.get("onboarding_complete", False)
        if self._onboarding_pending:
            self._show_onboarding()
        else:
            self.main_window.show()

        log_event("main_window_created", visible=self.main_window.isVisible())
        QTimer.singleShot(0, self._log_window_visible)
        if not self._onboarding_pending:
            QTimer.singleShot(0, self._deferred_startup)

        self.tray = self._create_tray()
        self.hotkey_handler = None
        self._pipeline_runner: Callable[[str], None] | None = None
        self._refresh_debug_window()

    def _show_onboarding(self):
        from ui.onboarding import OnboardingDialog
        self._onboarding_dlg = OnboardingDialog(config=self.config, parent=None)
        self._onboarding_dlg.finished_signal.connect(self._on_onboarding_done)
        screen = self.app.primaryScreen().availableGeometry()
        self._onboarding_dlg.move(
            screen.center().x() - self._onboarding_dlg.width() // 2,
            screen.center().y() - self._onboarding_dlg.height() // 2,
        )
        self._onboarding_dlg.show()

    def _on_onboarding_done(self):
        from app.service_wiring import _inject_api_keys
        _inject_api_keys(self.config)
        if self.ai_processor is not None:
            self.ai_processor.update_api_keys(
                groq_key=os.environ.get("GROQ_API_KEY", ""),
                gemini_key=os.environ.get("GEMINI_API_KEY", ""),
            )
        self._onboarding_dlg = None
        self._onboarding_pending = False
        QTimer.singleShot(50, self._show_main_after_onboarding)

    def _show_main_after_onboarding(self):
        self.main_window.show()
        QTimer.singleShot(100, self._deferred_startup)

    def _create_tray(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(project_root, "assets", "icon.ico")
        tray = RotaTrayIcon(icon_path=icon_path if os.path.exists(icon_path) else None)
        tray.open_action.triggered.connect(self.show_history)
        tray.settings_action.triggered.connect(self.show_settings)
        tray.exit_action.triggered.connect(self.exit_app)
        tray.open_action.setVisible(True)
        tray.settings_action.setVisible(True)
        tray.mode_action.setVisible(True)
        tray.ai_action.setVisible(True)
        tray.show()
        return tray

    def _deferred_startup(self):
        logger.info("deferred_startup_begin")
        self._setup_tray_connections()
        hotkey = str(self.config.get("hotkey") or "f9")
        mode = str(self.config.get("hotkey_mode") or "toggle")
        HotkeyHandler = _get_hotkey_handler()
        self.hotkey_handler = HotkeyHandler(
            hotkey=hotkey,
            mode=mode,
            start_callback=self.hotkey_bridge.start_requested.emit,
            stop_callback=self.hotkey_bridge.stop_requested.emit,
        )
        hotkey_ok = self._start_hotkey_listener()
        self._load_transcriber_async(self._current_model_size)
        self._run_startup_health_checks(hotkey_ok)

        history_days = int(self.config.get("history_days", 30) or 30)
        try:
            pruned_h = self.history.prune_old_entries(history_days)
            pruned_s = self.session_store.prune_old_sessions(history_days)
            if pruned_h or pruned_s:
                logger.info("startup_db_pruned", history_rows=pruned_h, session_rows=pruned_s, days=history_days)
        except Exception as e:
            logger.error("startup_db_prune_failed", error=str(e))

        try:
            from utils.seeder import seed_mock_data
            seeded = seed_mock_data(self.session_store)
            if seeded > 0:
                logger.info("seeded_mock_history_sessions", count=seeded)
        except Exception as e:
            logger.error("seeding_history_failed", error=str(e))

        # Register undo hotkey via the existing pynput listener — do NOT use the
        # `keyboard` library here. That library starts its own WH_KEYBOARD_LL hook
        # thread which conflicts with pynput's thread and causes 0x8001010d /
        # access-violation crashes on Windows.
        try:
            if self.hotkey_handler is not None and self.hotkey_handler.backend == "pynput":
                self.hotkey_handler.add_hotkey(
                    "ctrl+shift+z",
                    lambda: QTimer.singleShot(0, self._do_undo_injection),
                )
                logger.info("undo_hotkey_registered")
            else:
                logger.warning("undo_hotkey_skipped backend=%s", getattr(self.hotkey_handler, "backend", None))
        except Exception as e:
            logger.warning("undo_hotkey_register_failed", error=str(e))
        logger.info("deferred_startup_done")
        self._schedule_update_check()

    def _run_startup_health_checks(self, hotkey_ok):
        if sys.platform == "win32":
            appdata_dir = os.path.join(os.environ.get("APPDATA", "."), "RotaAI")
        else:
            xdg_data = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
            appdata_dir = os.path.join(xdg_data, "rota-ai")
        checker = StartupHealthChecker(
            appdata_dir=appdata_dir,
            model_size=str(self._current_model_size),
            hotkey_validator=lambda: (
                hotkey_ok,
                "Hotkey listener registered" if hotkey_ok else "F9 hotkey failed to register",
            ),
        )
        checker.run_async(lambda report: QTimer.singleShot(0, lambda: self._on_health_report(report)))

    def _on_health_report(self, report: HealthCheckReport):
        self._health_report = report
        critical = report.has_critical_failure()
        degraded = report.is_degraded()
        issues = report.failed_messages()
        log_event(
            "startup_health_check",
            status="failed" if critical else ("degraded" if degraded else "ok"),
            checks=[item.__dict__ for item in report.checks],
        )
        self.main_window.update_health_status("critical" if critical else ("degraded" if degraded else "ok"), issues)
        if critical:
            self._recording_enabled = False
            self.main_window.set_recording_enabled(False, "F9 disabled: startup checks failed")
            self.main_window.update_hotkey_status("F9 disabled — startup checks failed")
            if issues:
                self.show_toast(
                    f"Startup issue: {issues[0]} — see the status panel for details",
                    warning=True,
                )

    def _log_window_visible(self):
        logger.info(
            "main_window_shown",
            visible=self.main_window.isVisible(),
            active=self.main_window.isActiveWindow(),
            win_id=int(self.main_window.winId()),
        )

    @pyqtSlot()
    def _handle_manual_start(self):
        self._dispatch_pipeline_action("start")

    @pyqtSlot()
    def _handle_manual_stop(self):
        self._dispatch_pipeline_action("stop")

    def set_pipeline_runner(self, runner: Callable[[str], None]) -> None:
        self._pipeline_runner = runner

    def _dispatch_pipeline_action(self, action: str) -> None:
        if self._pipeline_runner is not None:
            self._pipeline_runner(action)
            return
        if action == "start":
            self.on_start_recording()
        elif action == "stop":
            self.on_stop_recording()

    def _refresh_debug_window(self):
        if not hasattr(self, "main_window"):
            return
        state_value = getattr(self, "state", RecordingState.IDLE).value
        self.main_window.update_state(state_value, self._last_session_id)
        self.main_window.update_text_results(self._latest_raw_text, self._latest_cleaned_text)
        self.main_window.update_timings(self._latest_timings)
        self._update_metrics()
        if hasattr(self, "tray"):
            self.tray.update_runtime_state(state_value)

    def _update_metrics(self):
        if not hasattr(self, "main_window"):
            return
        dashboard = self.session_store.get_dashboard_metrics()
        try:
            enhanced = self.enhanced_insights.get_dashboard_insights()
            dashboard["enhanced"] = enhanced
            daily_counts = self.session_store.get_daily_word_counts(days=91)
            dashboard["daily_counts"] = daily_counts
            achievements = self.enhanced_insights.get_achievements()
            dashboard["achievements"] = achievements
            dashboard["top_phrases"] = self.enhanced_insights.get_phrase_rankings(limit=5)
            dashboard["app_usage"] = self.enhanced_insights.get_app_usage()
        except Exception as e:
            logger.error("failed_to_get_enhanced_insights", error=str(e))
        self.main_window.update_metrics(dashboard)
        latest = dashboard.get("latest")
        if latest:
            self.main_window.update_insight(
                latest["insight_summary"],
                latest["insight_suggestion"],
                latest["clarity_score"],
                latest["conciseness_score"],
            )

    def _start_hotkey_listener(self):
        try:
            if self.hotkey_handler is None:
                return False
            self.hotkey_handler.start_listening()
            self._update_readiness_status()
            return True
        except Exception:
            logger.error("hotkey_listener_start_failed", exc_info=True)
            self.main_window.update_hotkey_status("F9 unavailable")
            self.show_toast(
                "F9 hotkey unavailable — another app may be blocking it. Try changing it in Settings",
                warning=True,
            )
            return False

    def show_toast(self, message, warning=False):
        self._active_toast = Toast(message, warning=warning)
        self._active_toast.show()

    def _do_undo_injection(self):
        if self.injector is None:
            return
        success, msg = self.injector.undo_last_inject()
        if success:
            self.show_toast("Undo: previous clipboard restored — paste (Ctrl+V) to recover")
        else:
            logger.debug("undo_unavailable", reason=msg)

    def show_settings(self):
        win = SettingsWindow(self.config)
        if win.exec():
            if self.hotkey_handler is not None:
                self.hotkey_handler.stop_listening()
            hotkey = str(self.config.get("hotkey") or "f9")
            mode = str(self.config.get("hotkey_mode") or "toggle")
            HotkeyHandler = _get_hotkey_handler()
            self.hotkey_handler = HotkeyHandler(
                hotkey=hotkey,
                mode=mode,
                start_callback=self.hotkey_bridge.start_requested.emit,
                stop_callback=self.hotkey_bridge.stop_requested.emit,
            )
            self._start_hotkey_listener()

            if self.transcriber is not None:
                self.transcriber.transcription_quality = str(self.config.get("transcription_quality", "balanced"))

            if self.ai_processor is not None:
                self.ai_processor.writing_mode = self.config.get("writing_mode", "clean")
                self.ai_processor.ai_provider = self.config.get("ai_provider", "gemini")
                self.ai_processor.ollama_model = self.config.get("ollama_model", "llama3.2:1b")
                self.ai_processor.ollama_url = self.config.get("ollama_url", "http://localhost:11434").rstrip("/")
                self.ai_processor.update_api_keys(
                    groq_key=os.environ.get("GROQ_API_KEY", ""),
                    gemini_key=os.environ.get("GEMINI_API_KEY", ""),
                )

            new_model_size = str(self.config.get("model_size") or "base")
            new_cpu_threads = int(self.config.get("cpu_threads", 0))
            if self._current_model_size != new_model_size or self._current_cpu_threads != new_cpu_threads:
                self._current_model_size = new_model_size
                self._current_cpu_threads = new_cpu_threads
                self._load_transcriber_async(new_model_size)

            self.tray.update_status(self.config.get("hotkey_mode"), self.config.get("ai_enabled"))

            if hasattr(self.main_window, "apply_font_settings"):
                self.main_window.apply_font_settings()
            self.main_window._history_signature = None
            self.main_window.refresh_history()

    def show_history(self):
        ai_proc = self.ai_processor if self.config.get("ai_enabled") else None
        date_display = self.config.get("date_display", "relative")
        win = HistoryWindow(self.history, ai_processor=ai_proc, date_display=date_display)
        win.exec()
        self.main_window.refresh_history()

    def toggle_mode(self):
        current = self.config.get("hotkey_mode")
        new_mode = "toggle" if current == "hold" else "hold"
        self.config.set("hotkey_mode", new_mode)
        self.config.save()
        if self.hotkey_handler is not None:
            self.hotkey_handler.set_mode(new_mode)
        self.tray.update_status(new_mode, self.config.get("ai_enabled"))

    def toggle_ai(self):
        enabled = not self.config.get("ai_enabled")
        self.config.set("ai_enabled", enabled)
        self.config.save()
        self.tray.update_status(self.config.get("hotkey_mode"), enabled)

    def exit_app(self):
        if self._instance_wake_notifier is not None:
            self._instance_wake_notifier.setEnabled(False)
            self._instance_wake_notifier.deleteLater()
            self._instance_wake_notifier = None
        if self._instance_listen_sock is not None:
            try:
                self._instance_listen_sock.close()
            except OSError:
                pass
            self._instance_listen_sock = None
        release_instance_mutex()
        log_handler = getattr(self, "_log_handler", None)
        if log_handler is not None:
            logging.getLogger().removeHandler(log_handler)
            self._log_handler = None
        if self.hotkey_handler is not None:
            self.hotkey_handler.stop_listening()
        self.recorder.stop()
        if self._processor_thread is not None and self._processor_thread.isRunning():
            self._processor_thread.requestInterruption()
            self._processor_thread.quit()
            if not self._processor_thread.wait(1000):
                self._processor_thread.terminate()
                self._processor_thread.wait(1000)
        if self._transcriber_thread is not None and self._transcriber_thread.isRunning():
            self._transcriber_thread.quit()
            self._transcriber_thread.wait(1000)
        self.app.quit()

    def _schedule_update_check(self):
        """Check for updates 8 seconds after startup so it doesn't slow launch."""
        QTimer.singleShot(8000, self._start_update_check)

    def _start_update_check(self):
        import webbrowser
        from app.version import __version__
        from services.updater import check_for_update

        def on_update_found(latest: str, url: str) -> None:
            # Marshal to Qt main thread
            QTimer.singleShot(0, lambda: self._show_update_toast(latest, url))

        check_for_update(__version__, on_update_found)

    def _show_update_toast(self, latest: str, url: str) -> None:
        import webbrowser
        self._active_toast = Toast(
            f"Update available: v{latest} — click to download",
            on_click=lambda: webbrowser.open(url),
            duration_ms=10000,
        )
        self._active_toast.show()
        logger.info("update_toast_shown", latest=latest)

    def run(self):
        sys.exit(self.app.exec())
