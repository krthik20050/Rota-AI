"""Offline release gate for the real desktop pages, without user data or models."""

from __future__ import annotations

import gc
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QEvent, QTimer
from PySide6.QtWidgets import QApplication
from shiboken6 import isValid

from data.config import ConfigManager
from data.history import HistoryManager
from ui.main_window import MainWindow


def run_desktop_smoke() -> int:
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    errors = []
    previous_hook = sys.excepthook

    def capture_error(exc_type, exc_value, exc_tb):
        errors.append(f"{exc_type.__name__}: {exc_value}")

    sys.excepthook = capture_error
    try:
        with tempfile.TemporaryDirectory(prefix="rota-smoke-") as folder:
            config = ConfigManager(config_path=str(Path(folder) / "config.json"))
            history = HistoryManager(db_path=str(Path(folder) / "history.db"))
            window = MainWindow(history, lambda: None, lambda: None, config=config)
            timer = QTimer()
            steps = 0

            def exercise():
                nonlocal steps
                try:
                    gc.collect()
                    window._select_page(("home", "insights", "settings")[steps % 3])
                    window.update_metrics(
                        {
                            "today": {"words": 100, "wpm": 120},
                            "lifetime": {"words": 100},
                            "enhanced": {
                                "trends": {
                                    "labels": ["Mon", "Tue"],
                                    "wpm": [100, 120],
                                    "clarity": [90, 95],
                                }
                            },
                        }
                    )
                    chart = window.insights_page.trend_chart
                    assert isValid(chart) and isValid(chart._anim_timer)
                    assert window.isAncestorOf(chart)
                    assert all(w is window for w in app.topLevelWidgets() if w.isVisible())
                    steps += 1
                    if steps == 12:
                        timer.stop()
                        app.quit()
                except Exception:
                    capture_error(*sys.exc_info())
                    timer.stop()
                    app.exit(1)

            try:
                window.show()
                timer.timeout.connect(exercise)
                timer.start(150)
                result = app.exec()
                if errors:
                    raise RuntimeError("Desktop smoke failed: " + "; ".join(errors))
                return result
            finally:
                timer.stop()
                window.hide()
                window.deleteLater()
                QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
                history._conn.close()
    finally:
        sys.excepthook = previous_hook
