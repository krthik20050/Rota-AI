from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout


class Toast(QDialog):
    """Simple toast notification for status messages."""

    def __init__(
        self,
        message: str,
        parent=None,
        warning: bool = False,
        on_click: Callable | None = None,
        duration_ms: int = 3500,
    ):
        super().__init__(parent)
        self._on_click = on_click
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        if on_click is not None:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(message)
        if warning:
            bg = "#D97706"
            text_color = "#000000"
        else:
            bg = "#2A2A2E"
            text_color = "#F0F0F2"
        self.label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {bg};
                color: {text_color};
                padding: 12px 22px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
                border: 1px solid rgba(255, 255, 255, 0.15);
            }}
            """
        )
        layout.addWidget(self.label)
        self.setLayout(layout)

        screen = QApplication.primaryScreen()
        if screen is not None:
            screen_geo = screen.availableGeometry()
            self.adjustSize()
            self.move(
                (screen_geo.width() - self.width()) // 2,
                screen_geo.bottom() - 110,
            )

        QTimer.singleShot(duration_ms, self.close)

    def mousePressEvent(self, event):
        if self._on_click is not None:
            self._on_click()
            self.close()
        else:
            super().mousePressEvent(event)
