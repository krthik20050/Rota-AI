"""
Rota AI — Main Dashboard Window
================================
Wispr Flow "Voice in Motion" Design System.

Architecture:
  Frameless window → custom title bar → sidebar + content stack
  Sidebar: brand + status + nav + settings
  Content: Home | Insights | Dictionary | Snippets

Kept under 500 lines — heavy widgets live in ui/pages/.
"""
from __future__ import annotations

import structlog
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QVBoxLayout, QWidget,
)
from PyQt6.QtGui import QFont

from ui.pages.home_page import HomePage
from ui.pages.dictionary_page import DictionaryPage
from ui.pages.snippets_page import SnippetsPage
from ui.pages.insights_page import InsightsPage
from ui.styles.main_window_qss import (
    WISPR_QSS,
    CLR_BASE, CLR_ACCENT, CLR_ERROR, CLR_WARNING,
    FONT_FAMILY, SIDEBAR_W,
)
from utils.window_effects import apply_blur

logger = structlog.get_logger(__name__)


class MainWindow(QWidget):
    """
    Premium control surface for Rota AI.
    Thin orchestrator — page widgets own their own state.
    """

    def __init__(
        self,
        history_manager,
        on_start_clicked,
        on_stop_clicked,
        on_settings_clicked=None,
        snippets_manager=None,
        personal_dict=None,
        ai_processor=None,
        config=None,
        parent=None,
    ):
        super().__init__(parent)
        self.history_manager = history_manager
        self.on_start_clicked = on_start_clicked
        self.on_stop_clicked = on_stop_clicked
        self.on_settings_clicked = on_settings_clicked
        self.snippets_manager = snippets_manager
        self.personal_dict = personal_dict
        self.ai_processor = ai_processor
        self._config = config

        self._is_maximized = False
        self.state_value = "IDLE"
        self.latest_raw_text = ""
        self.latest_cleaned_text = ""
        self._last_error_message = ""
        self.nav_buttons: dict[str, QPushButton] = {}

        self.setWindowTitle("Rota")
        self.resize(1060, 720)
        self.setMinimumSize(860, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._init_ui()
        self._apply_configured_font()
        self.home_page.refresh_history()
        self._select_page("home")

    # ══════════════════════════════════════════════════════════════
    # UI construction
    # ══════════════════════════════════════════════════════════════
    def _init_ui(self):
        self.setStyleSheet(WISPR_QSS)

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(8, 8, 8, 8)

        self.container = QFrame()
        self.container.setObjectName("MainContainer")

        container_v = QVBoxLayout(self.container)
        container_v.setContentsMargins(0, 0, 0, 0)
        container_v.setSpacing(0)
        container_v.addWidget(self._build_titlebar())

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)
        content.addWidget(self._build_sidebar())

        self.content_stack = QStackedWidget()
        self.home_page = HomePage(
            self.history_manager, self.ai_processor, self._config, parent=self
        )
        self.insights_page = InsightsPage(self._config, self.history_manager, parent=self)
        self.dictionary_page = DictionaryPage(self.personal_dict, parent=self)
        self.snippets_page = SnippetsPage(self.snippets_manager, parent=self)

        self.page_indexes = {
            "home":       self.content_stack.addWidget(self.home_page),
            "insights":   self.content_stack.addWidget(self.insights_page),
            "dictionary": self.content_stack.addWidget(self.dictionary_page),
            "snippets":   self.content_stack.addWidget(self.snippets_page),
        }
        content.addWidget(self.content_stack, 1)
        container_v.addLayout(content, 1)

        self.root_layout.addWidget(self.container)

    # ══════════════════════════════════════════════════════════════
    # Title Bar
    # ══════════════════════════════════════════════════════════════
    def _build_titlebar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("TitleBar")
        bar.setFixedHeight(42)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(18, 0, 10, 0)
        lay.setSpacing(0)
        lay.addStretch()

        for char, obj_name, callback in [
            ("─", "WinBtn",   self.showMinimized),
            ("□", "MaxBtn",   self._toggle_maximize),
            ("✕", "CloseBtn", self.hide),
        ]:
            btn = QPushButton(char)
            btn.setObjectName(obj_name)
            btn.setFixedSize(30, 30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(callback)
            lay.addWidget(btn)
            if obj_name == "MaxBtn":
                self._max_btn = btn

        return bar

    def _toggle_maximize(self):
        if self._is_maximized:
            self._is_maximized = False
            self.root_layout.setContentsMargins(8, 8, 8, 8)
            self.container.setStyleSheet("")
            self.showNormal()
            self._max_btn.setText("□")
        else:
            self._is_maximized = True
            self.root_layout.setContentsMargins(0, 0, 0, 0)
            self.container.setStyleSheet(
                f"QFrame#MainContainer {{ background-color: {CLR_BASE};"
                f" border-radius: 0px; border: none; }}"
            )
            self.showMaximized()
            self._max_btn.setText("❐")

    # ══════════════════════════════════════════════════════════════
    # Sidebar
    # ══════════════════════════════════════════════════════════════
    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(SIDEBAR_W)
        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(18, 20, 18, 22)
        lay.setSpacing(4)

        brand = QLabel("Rota")
        brand.setObjectName("Brand")
        lay.addWidget(brand)

        self._status_pill = QLabel("● Ready")
        self._status_pill.setObjectName("StatusPill")
        lay.addWidget(self._status_pill)
        lay.addSpacing(28)

        for key, label in [
            ("home",       "Home"),
            ("insights",   "Insights"),
            ("dictionary", "Dictionary"),
            ("snippets",   "Snippets"),
        ]:
            btn = QPushButton(label)
            btn.setObjectName("NavBtn")
            btn.setCheckable(True)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self._select_page(k))
            self.nav_buttons[key] = btn
            lay.addWidget(btn)

        lay.addStretch()

        settings_btn = QPushButton("⚙️  Settings")
        settings_btn.setObjectName("SettingsNavBtn")
        settings_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if self.on_settings_clicked:
            settings_btn.clicked.connect(self.on_settings_clicked)
        lay.addWidget(settings_btn)

        return sidebar

    # ══════════════════════════════════════════════════════════════
    # Navigation
    # ══════════════════════════════════════════════════════════════
    def _select_page(self, key: str):
        self.content_stack.setCurrentIndex(self.page_indexes[key])
        for k, btn in self.nav_buttons.items():
            btn.setChecked(k == key)
        if key == "dictionary":
            self.dictionary_page.refresh()
        elif key == "snippets":
            self.snippets_page.refresh()
        elif key == "insights":
            QTimer.singleShot(60, self._animate_insights_entry)

    def _animate_insights_entry(self):
        self.insights_page.animate_entry()

    # ══════════════════════════════════════════════════════════════
    # Public API — called by controller.py
    # ══════════════════════════════════════════════════════════════
    def refresh_history(self, highlight_latest: bool = False):
        self.home_page.refresh_history(highlight_latest)

    def update_state(self, state: str, session_id=None):
        self.state_value = state
        states = {
            "IDLE":       ("● Ready",      CLR_ACCENT),
            "LISTENING":  ("◉ Recording",  CLR_ERROR),
            "PROCESSING": ("◌ Processing", CLR_WARNING),
            "ERROR":      ("✕ Error",      CLR_ERROR),
        }
        text, color = states.get(state, ("● Ready", CLR_ACCENT))
        self._status_pill.setText(text)
        self._status_pill.setStyleSheet(
            f"color: {color}; font-size: 14px; font-weight: 600; background: transparent;"
        )
        compact = (
            f"color: {color}; font-size: 11px; font-weight: 600;"
            f"background: rgba(134, 239, 172, 0.08);"
            f"border: 1px solid rgba(134, 239, 172, 0.18);"
            f"border-radius: 6px; padding: 4px 10px;"
        )
        self.home_page.update_status(text, color, compact)

    def update_metrics(self, words_or_dashboard, wpm=None, recording_seconds=None):
        if not hasattr(self, "insights_page"):
            return

        if isinstance(words_or_dashboard, dict):
            today = words_or_dashboard.get("today", {})
            lifetime = words_or_dashboard.get("lifetime", {})
            today_words = int(today.get("words", 0))
            today_wpm = int(today.get("wpm", 0))
            lifetime_words = int(lifetime.get("words", 0))
        else:
            today_words = int(words_or_dashboard or 0)
            today_wpm = int(wpm or 0)
            lifetime_words = int(words_or_dashboard or 0)

        self.insights_page.update_from_dashboard(words_or_dashboard, wpm)
        self.home_page.update_stats(today_wpm, today_words, lifetime_words)

    def update_insight(self, summary, suggestion, clarity, conciseness):
        self.insights_page.update_insight(summary, suggestion, clarity, conciseness)

    def update_text_results(self, raw, cleaned):
        self.latest_raw_text = raw or ""
        self.latest_cleaned_text = cleaned or ""

    def apply_font_settings(self):
        if not self._config:
            return
        fam = self._config.get("ui_font_family", "Segoe UI")
        sz = int(self._config.get("ui_font_size", 13))
        scope = self._config.get("ui_font_scope", "app")
        font = QFont(fam, sz)
        _DEFAULT = "'Segoe UI', 'Inter', -apple-system, sans-serif"
        patched_qss = WISPR_QSS.replace(_DEFAULT, f"'{fam}'")

        if scope == "app":
            QApplication.instance().setFont(font)
            self.setStyleSheet(patched_qss)
        elif scope == "main_window":
            self.setFont(font)
            self.setStyleSheet(patched_qss)
        elif scope == "history":
            self.home_page.set_history_font(font)
        # overlay manages its own font — no action needed

    # Stub methods — satisfy controller interface without logic
    def update_timings(self, timings): pass
    def update_hotkey_status(self, msg): pass
    def update_health_status(self, status, issues): pass
    def set_error_details(self, msg): self._last_error_message = msg
    def set_recording_enabled(self, enabled, reason=""): pass

    # ══════════════════════════════════════════════════════════════
    # Window events
    # ══════════════════════════════════════════════════════════════
    def showEvent(self, event):
        super().showEvent(event)
        apply_blur(int(self.winId()))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self._is_maximized:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._drag_pos = event.globalPosition().toPoint()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 42:
            self._toggle_maximize()

    def _apply_configured_font(self):
        self.apply_font_settings()
