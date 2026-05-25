"""
System tray icon for Rota AI.
Wispr Flow design: warm dark context menu, no emojis (per UI/UX Pro Max rules),
clean text labels, state-aware tooltip.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon


class RotaTrayIcon(QSystemTrayIcon):
    """System tray icon with Wispr-styled dark context menu."""

    def __init__(self, icon_path=None, parent=None):
        icon = QIcon(icon_path) if icon_path else QIcon.fromTheme("audio-input-microphone")
        super().__init__(icon, parent)
        self.setToolTip("Rota: Ready")
        self._init_menu()

    def _init_menu(self):
        self.menu = QMenu()
        self.menu.setWindowFlags(
            self.menu.windowFlags()
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Wispr warm dark menu — #161618 base, soft corners, generous padding
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #161618;
                color: #E8E8EA;
                border: 1px solid rgba(255, 255, 255, 10);
                border-radius: 12px;
                padding: 8px 4px;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 13px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 6px;
                margin: 2px 6px;
            }
            QMenu::item:selected {
                background-color: rgba(255, 255, 255, 8);
                color: #FFFFFF;
            }
            QMenu::separator {
                height: 1px;
                background: rgba(255, 255, 255, 6);
                margin: 6px 14px;
            }
        """)

        # Clean text labels — no emojis per UI/UX Pro Max rule
        self.open_action = QAction("Open Dashboard")
        self.menu.addAction(self.open_action)

        self.settings_action = QAction("Settings")
        self.menu.addAction(self.settings_action)

        self.menu.addSeparator()

        self.mode_action = QAction("Mode: Hold to Record")
        self.menu.addAction(self.mode_action)

        self.ai_action = QAction("Smart Formatting: ON")
        self.ai_action.setCheckable(True)
        self.ai_action.setChecked(True)
        self.menu.addAction(self.ai_action)

        self.menu.addSeparator()

        self.exit_action = QAction("Quit Rota")
        self.menu.addAction(self.exit_action)

        self.setContextMenu(self.menu)

    def update_status(self, mode, ai_enabled):
        mode_text = "Hold to Record" if mode == "hold" else "Toggle Mode"
        self.mode_action.setText(f"Mode: {mode_text}")
        self.ai_action.setChecked(ai_enabled)
        self.ai_action.setText(f"Smart Formatting: {'ON' if ai_enabled else 'OFF'}")

    def update_runtime_state(self, state):
        states = {
            "IDLE": "Ready",
            "LISTENING": "Recording...",
            "PROCESSING": "Processing...",
            "ERROR": "Error",
        }
        self.setToolTip(f"Rota: {states.get(state, state)}")
