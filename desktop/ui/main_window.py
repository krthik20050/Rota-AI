"""
Rota AI — Main Dashboard Window
================================

Features:
  - Frameless window with custom title bar
  - Edge/corner resize handles (6px detection zone)
  - Window dragging via title bar
  - Double-click title bar to toggle maximize

To match Wispr Flow/Windows-native resize behavior:
  - All four edges + four corners are draggable resize zones
  - Cursor updates to Size*Cursor when hovering edges
  - Minimum window size enforced during resize
Wispr Flow "Voice in Motion" Design System.    Architecture:
  Frameless window → custom title bar → sidebar + content stack
  Sidebar: brand + status + nav + settings
  Content: Home | Insights | Dictionary | Snippets | Settings (in-app)

Kept under 500 lines — heavy widgets live in ui/pages/.
"""

from __future__ import annotations

import sys

import structlog
from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.pages.dictionary_page import DictionaryPage
from ui.pages.home_page import HomePage
from ui.pages.insights_page import InsightsPage
from ui.pages.settings_page import SettingsPage
from ui.pages.snippets_page import SnippetsPage
from ui.styles.main_window_qss import (
    CLR_ACCENT,
    CLR_BASE,
    CLR_ERROR,
    CLR_WARNING,
    RADIUS_CONTAINER,
    SIDEBAR_W,
    WISPR_QSS,
)
from ui.overlay.animation_utils import (
    apply_dwm_transparency,
    clear_window_region,
    set_pill_window_region,
)
from utils.window_effects import apply_blur, apply_win11_rounded_corners


# ── Rounded corner radius (matches RADIUS_CONTAINER from QSS tokens) ──
_VISUAL_MARGIN = 0  # px — zero gap between window edge and container
_ROUNDED_RADIUS = int(RADIUS_CONTAINER.rstrip("px")) + _VISUAL_MARGIN  # 18 + 0 = 18


# ── Resize constants ─────────────────────────────────────────────────
_RESIZE_MARGIN = 8  # px from each edge; OS-level resize detection zone
_MIN_W = 860
_MIN_H = 600

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
        self.on_settings_clicked = on_settings_clicked  # kept for tray/fallback
        self._settings_save_callback = None
        self._previous_page = "home"
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

        # ── Resize state ─────────────────────────────────────────────
        self.setMouseTracking(True)
        self._resize_direction: set[str] = set()  # e.g. {'left', 'top'}
        self._drag_pos: QPoint | None = None
        self._show_grip = False  # show resize grip on hover near bottom-right corner
        self._last_cursor_shape: Qt.CursorShape | None = None  # cache to avoid redundant setCursor

        self.setWindowTitle("Rota")
        self.resize(1060, 720)
        self.setMinimumSize(_MIN_W, _MIN_H)
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
        self.root_layout.setContentsMargins(_VISUAL_MARGIN, _VISUAL_MARGIN,
                                                 _VISUAL_MARGIN, _VISUAL_MARGIN)

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
        self.settings_page = SettingsPage(
            self._config,
            on_save=self._on_settings_saved,
            on_back=self._on_settings_back,
            parent=self,
        )

        self.page_indexes = {
            "home": self.content_stack.addWidget(self.home_page),
            "insights": self.content_stack.addWidget(self.insights_page),
            "dictionary": self.content_stack.addWidget(self.dictionary_page),
            "snippets": self.content_stack.addWidget(self.snippets_page),
            "settings": self.content_stack.addWidget(self.settings_page),
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
            ("─", "WinBtn", self.showMinimized),
            ("□", "MaxBtn", self._toggle_maximize),
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
            self.root_layout.setContentsMargins(_VISUAL_MARGIN, _VISUAL_MARGIN,
                                                 _VISUAL_MARGIN, _VISUAL_MARGIN)
            self.container.setStyleSheet("")
            self.showNormal()
            # showNormal triggers resizeEvent → timer → _update_window_region re-applies clip
            self._max_btn.setText("□")
        else:
            self._is_maximized = True
            # Remove the SetWindowRgn clip so window fills the screen edge-to-edge
            if sys.platform == "win32":
                try:
                    clear_window_region(int(self.winId()))
                except Exception:
                    pass
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
            ("home", "Home"),
            ("insights", "Insights"),
            ("dictionary", "Dictionary"),
            ("snippets", "Snippets"),
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
        settings_btn.clicked.connect(lambda: self._select_page("settings"))
        lay.addWidget(settings_btn)

        return sidebar

    # ══════════════════════════════════════════════════════════════
    # Navigation
    # ══════════════════════════════════════════════════════════════
    def _select_page(self, key: str):
        if key == "settings":
            # Remember where we came from so Back goes to the right page
            self._previous_page = self._previous_page or "home"
            self.settings_page._load_config()
        else:
            self._previous_page = key
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
    # Settings page hooks
    # ══════════════════════════════════════════════════════════════

    def _on_settings_saved(self):
        """Called after settings are saved. Invokes the external save callback."""
        if self._settings_save_callback:
            self._settings_save_callback()
        self._select_page(self._previous_page)

    def _on_settings_back(self):
        """Called when the user clicks Back on the settings page — no save."""
        self._select_page(self._previous_page)

    def navigate_to_settings(self, save_callback=None):
        """Navigate to the settings page with an optional post-save callback.

        Called by rota_app (from tray or other triggers) to open settings
        inside the main window instead of a separate dialog.
        """
        self._settings_save_callback = save_callback
        self._select_page("settings")

    # ══════════════════════════════════════════════════════════════
    # Public API — called by controller.py
    # ══════════════════════════════════════════════════════════════
    def refresh_history(self, highlight_latest: bool = False):
        self.home_page.refresh_history(highlight_latest)

    def update_state(self, state: str, session_id=None):
        self.state_value = state
        states = {
            "IDLE": ("● Ready", CLR_ACCENT),
            "LISTENING": ("◉ Recording", CLR_ERROR),
            "PROCESSING": ("◌ Processing", CLR_WARNING),
            "ERROR": ("✕ Error", CLR_ERROR),
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
            # Clear + re-set stylesheet to force Qt to re-evaluate font inheritance
            self.setStyleSheet("")
            self.setStyleSheet(patched_qss)
        elif scope == "main_window":
            self.setFont(font)
            self.setStyleSheet("")
            self.setStyleSheet(patched_qss)
        elif scope == "history":
            self.home_page.set_history_font(font)
        # overlay manages its own font — no action needed

        # Force re-apply font on the settings page itself
        if hasattr(self, "settings_page") and self.settings_page.isVisible():
            self.settings_page._update_font_preview()

    # Stub methods — satisfy controller interface without logic
    def update_timings(self, timings):
        pass

    def update_hotkey_status(self, msg):
        pass

    def update_health_status(self, status, issues):
        pass

    def set_error_details(self, msg):
        self._last_error_message = msg

    def set_recording_enabled(self, enabled, reason=""):
        pass

    # ══════════════════════════════════════════════════════════════
    # Window events
    # ══════════════════════════════════════════════════════════════

    @staticmethod
    def _edge_cursor(dirs: frozenset[str]) -> Qt.CursorShape:
        """Return the cursor shape for a given set of edge directions."""
        if not dirs:
            return Qt.CursorShape.ArrowCursor
        if dirs == frozenset({"left"}) or dirs == frozenset({"right"}):
            return Qt.CursorShape.SizeHorCursor
        if dirs == frozenset({"top"}) or dirs == frozenset({"bottom"}):
            return Qt.CursorShape.SizeVerCursor
        if dirs in (frozenset({"top", "left"}), frozenset({"bottom", "right"})):
            return Qt.CursorShape.SizeFDiagCursor
        if dirs in (frozenset({"top", "right"}), frozenset({"bottom", "left"})):
            return Qt.CursorShape.SizeBDiagCursor
        return Qt.CursorShape.ArrowCursor

    def _detect_edges(self, local_pos) -> set[str]:
        """Detect which edges of the window the cursor is hovering near."""
        x, y = local_pos.x(), local_pos.y()
        w, h = self.width(), self.height()
        m = _RESIZE_MARGIN
        dirs: set[str] = set()
        if x <= m:
            dirs.add("left")
        if x >= w - m:
            dirs.add("right")
        if y <= m:
            dirs.add("top")
        if y >= h - m:
            dirs.add("bottom")
        return dirs

    def showEvent(self, event):
        super().showEvent(event)
        # Defer window effects so the native HWND is fully mapped
        QTimer.singleShot(0, self._apply_window_effects)

    def resizeEvent(self, event):
        """Recalculate the window's rounded-corner clip region on resize."""
        super().resizeEvent(event)
        if not self._is_maximized:
            QTimer.singleShot(0, self._update_window_region)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            self._resize_direction = self._detect_edges(event.position())

    def mouseMoveEvent(self, event):
        if self._is_maximized:
            return

        pos = event.position()
        buttons = event.buttons()

        # ── Hover (no button) → update cursor shape + grip visibility ──
        if buttons == Qt.MouseButton.NoButton:
            dirs = self._detect_edges(pos)
            new_cursor = self._edge_cursor(frozenset(dirs))
            # Only update cursor when the shape changes — prevents overriding
            # child widget cursors (buttons, text fields, etc.)
            if new_cursor != self._last_cursor_shape:
                self._last_cursor_shape = new_cursor
                if new_cursor == Qt.CursorShape.ArrowCursor:
                    self.unsetCursor()  # Let Qt manage child widget cursors naturally
                else:
                    self.setCursor(new_cursor)
            # Show resize grip when hovering near bottom-right corner
            show_grip = ("bottom" in dirs and "right" in dirs)
            if show_grip != self._show_grip:
                self._show_grip = show_grip
                self.update()
            return

        # ── Drag (left button) → resize or move ──
        if buttons & Qt.MouseButton.LeftButton and self._drag_pos is not None:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self._drag_pos = event.globalPosition().toPoint()

            if self._resize_direction:
                self._do_resize(delta)
            elif pos.y() < 50:
                # Only drag when cursor is in title-bar vicinity
                self.move(self.x() + delta.x(), self.y() + delta.y())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._resize_direction = set()
            self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 42:
            self._toggle_maximize()

    def _do_resize(self, delta):
        """Apply a pixel delta to the window geometry based on active edges."""
        x, y, w, h = self.x(), self.y(), self.width(), self.height()
        dx, dy = delta.x(), delta.y()

        # Clamp each edge independently, recording how much was actually used
        if "left" in self._resize_direction:
            new_w = w - dx
            if new_w >= _MIN_W:
                x += dx
                w = new_w
        elif "right" in self._resize_direction:
            new_w = w + dx
            if new_w >= _MIN_W:
                w = new_w

        if "top" in self._resize_direction:
            new_h = h - dy
            if new_h >= _MIN_H:
                y += dy
                h = new_h
        elif "bottom" in self._resize_direction:
            new_h = h + dy
            if new_h >= _MIN_H:
                h = new_h

        self.setGeometry(x, y, w, h)

    # ══════════════════════════════════════════════════════════════
    # Window effects (blur + rounded corners via OS clip region)
    # ══════════════════════════════════════════════════════════════

    def _apply_window_effects(self) -> None:
        """Apply OS-level rounded corners, DWM transparency, and acrylic blur.

        Uses THREE approaches for maximum reliability:
        1. DwmSetWindowAttribute (Win11 native) — tells DWM to round corners
           at the compositor level, hardware-accelerated.
        2. SetWindowRgn (Win10/11) — physically clips the OS window HWND so
           corners are genuinely transparent wherever the cursor goes.
        3. DWM glass + acrylic blur for the visual depth effect.
        """
        if sys.platform != "win32":
            return
        try:
            win_id = int(self.winId())
            # 1. Windows 11 native corner rounding (no-op on Win10)
            apply_win11_rounded_corners(win_id)
            # 2. DWM glass extends into client area — prevents white rect artifact
            apply_dwm_transparency(win_id)
            # 3. Acrylic blur effect
            apply_blur(win_id)
            # 4. Physical OS-level clip to rounded rect (works on Win10 + Win11)
            self._update_window_region()
        except Exception:
            logger.warning("window_effects_failed", exc_info=True)

    def _update_window_region(self) -> None:
        """Re-apply the rounded-rect clip region at the OS level.

        Uses ``SetWindowRgn`` (via ``set_pill_window_region``) which operates
        in **physical (device) pixels**. We multiply by DPR for correct clipping
        on high-DPI displays.

        Called on show, resize, and restore-from-maximized.
        """
        if sys.platform != "win32":
            return
        try:
            dpr = self.devicePixelRatio() or 1.0
            w = int(self.width() * dpr)
            h = int(self.height() * dpr)
            if w > 0 and h > 0:
                set_pill_window_region(
                    int(self.winId()),
                    w,
                    h,
                    _ROUNDED_RADIUS,
                )
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════════
    # Paint — resize grip + container border
    # ══════════════════════════════════════════════════════════════

    def paintEvent(self, event):
        """Draw a subtle resize grip at the container's bottom-right corner."""
        super().paintEvent(event)
        if self._is_maximized or not self._show_grip:
            return
        # Grip sits at the container's bottom-right corner
        cx = self.container.width() - 2   # 2px inset from container right edge
        cy = self.container.height() - 2  # 2px inset from container bottom edge
        ox = self.container.x()           # translate from MainWindow coords
        oy = self.container.y()
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen = QPen(QColor(255, 255, 255, 80), 1.5)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            # Three short diagonal lines — classic Windows resize grip
            for i in range(3):
                off = i * 5
                painter.drawLine(
                    ox + cx - off, oy + cy - 8,
                    ox + cx - 8, oy + cy - off,
                )
        finally:
            painter.end()

    def _apply_configured_font(self):
        self.apply_font_settings()
