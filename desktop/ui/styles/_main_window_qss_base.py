"""
Base / layout / sidebar QSS — container, title bar, sidebar, stats panel,
page titles, empty states, scrollbar, tooltip, focus states.

Design tokens (colors, typography, geometry) are defined here directly —
removed the separate _tokens.py module to reduce file count (ponytail:merge).
"""

from __future__ import annotations

# ── ponytail: inlined from _main_window_qss_tokens.py ─────────────────────
CLR_BASE = "#141918"
CLR_SIDEBAR = "#111614"
CLR_CARD = "#191E1C"
CLR_CARD_HOVER = "#1F2521"
CLR_BORDER = "rgba(255, 255, 255, 0.05)"
CLR_BORDER_HOVER = "rgba(255, 255, 255, 0.1)"

CLR_TEXT_PRIMARY = "#F0F0F2"
CLR_TEXT_SECONDARY = "#A0A0A5"
CLR_TEXT_MUTED = "#5A5A60"
CLR_TEXT_DIM = "#3A3A40"

CLR_ACCENT = "#86EFAC"
CLR_ACCENT_DIM = "rgba(134, 239, 172, 0.12)"
CLR_ACCENT_GLOW = "rgba(134, 239, 172, 0.2)"

CLR_SUCCESS = "#4ADE80"
CLR_ERROR = "#F87171"
CLR_WARNING = "#FBBF24"

FONT_FAMILY = "'Segoe UI', 'Inter', -apple-system, sans-serif"
FONT_SERIF = "'Georgia', 'Times New Roman', serif"
FONT_MONO = "'Courier New', 'Consolas', monospace"
FONT_BRAND_SIZE = "24px"
FONT_PAGE_TITLE = "28px"
FONT_BODY = "15px"
FONT_SMALL = "13px"
FONT_STAT = "36px"

RADIUS_CONTAINER = "18px"
RADIUS_CARD = "14px"
RADIUS_BTN = "10px"
SIDEBAR_W = 200
STATS_PANEL_W = 250

_QSS_BASE: str = f"""

* {{
    outline: none;
}}

/* ─── Container ─── */
QFrame#MainContainer {{
    background-color: {CLR_BASE};
    border-radius: {RADIUS_CONTAINER};
    border: 1px solid rgba(255, 255, 255, 0.12);
}}

/* ─── Title Bar ─── */
QFrame#TitleBar {{
    background: transparent;
    border-top-left-radius: {RADIUS_CONTAINER};
    border-top-right-radius: {RADIUS_CONTAINER};
}}
QPushButton#WinBtn, QPushButton#MaxBtn {{
    background: transparent;
    color: {CLR_TEXT_DIM};
    border: none;
    border-radius: 6px;
    font-size: 13px;
}}
QPushButton#WinBtn:hover, QPushButton#MaxBtn:hover {{
    background: rgba(255, 255, 255, 0.08);
    color: {CLR_TEXT_SECONDARY};
}}
QPushButton#CloseBtn {{
    background: transparent;
    color: {CLR_TEXT_DIM};
    border: none;
    border-radius: 6px;
    font-size: 13px;
}}
QPushButton#CloseBtn:hover {{
    background: rgba(248, 113, 113, 0.63);
    color: #FFFFFF;
}}
QPushButton#CloseBtn:pressed {{
    background: rgba(248, 113, 113, 0.80);
}}
QPushButton#WinBtn:pressed, QPushButton#MaxBtn:pressed {{
    background: rgba(255, 255, 255, 0.12);
}}

/* ─── Sidebar ─── */
QFrame#Sidebar {{
    background-color: {CLR_SIDEBAR};
    border-right: 1px solid {CLR_BORDER};
    border-radius: {RADIUS_CONTAINER};
}}
QLabel#Brand {{
    font-size: {FONT_BRAND_SIZE};
    font-weight: 700;
    color: {CLR_TEXT_PRIMARY};
    font-family: {FONT_SERIF};
    letter-spacing: -0.3px;
}}
QLabel#StatusPill {{
    color: {CLR_ACCENT};
    font-size: 14px;
    font-weight: 600;
    background: transparent;
    margin-top: 2px;
    font-family: {FONT_FAMILY};
}}
QLabel#HotkeyHint {{
    color: {CLR_TEXT_DIM};
    font-size: 12px;
    font-weight: 500;
    background: transparent;
    font-family: {FONT_FAMILY};
}}
QLabel#SectionLabel {{
    color: {CLR_TEXT_MUTED};
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.2px;
    font-family: {FONT_FAMILY};
}}
QPushButton#NavBtn {{
    background-color: transparent;
    color: {CLR_TEXT_MUTED};
    border: none;
    border-radius: {RADIUS_BTN};
    padding: 9px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
    font-family: {FONT_FAMILY};
}}
QPushButton#NavBtn:hover {{
    background-color: rgba(255, 255, 255, 0.05);
    color: {CLR_TEXT_SECONDARY};
}}
QPushButton#NavBtn:pressed {{
    background-color: rgba(255, 255, 255, 0.08);
}}
QPushButton#NavBtn:checked {{
    background-color: rgba(255, 255, 255, 0.08);
    color: {CLR_TEXT_PRIMARY};
    font-weight: 600;
}}
QPushButton#SettingsNavBtn {{
    background-color: rgba(134, 239, 172, 0.08);
    color: {CLR_TEXT_SECONDARY};
    border: 1px solid rgba(134, 239, 172, 0.18);
    border-radius: {RADIUS_BTN};
    padding: 10px 14px;
    text-align: left;
    font-size: 15px;
    font-weight: 500;
    font-family: {FONT_FAMILY};
}}
QPushButton#SettingsNavBtn:hover {{
    background-color: rgba(134, 239, 172, 0.16);
    color: {CLR_TEXT_PRIMARY};
    border-color: rgba(134, 239, 172, 0.35);
}}
QPushButton#SettingsNavBtn:pressed {{
    background-color: rgba(134, 239, 172, 0.22);
}}

/* ─── Stats Panel (home right side) ─── */
QFrame#StatsPanel {{
    background-color: #101513;
    border-left: 1px solid {CLR_BORDER};
    border-radius: {RADIUS_CONTAINER};
}}
QLabel#PanelSection {{
    color: {CLR_TEXT_DIM};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.4px;
    font-family: {FONT_FAMILY};
}}
/* ─── Home Page Stat Cards ─── */
QFrame#HomeStatCard {{
    background-color: rgba(255, 255, 255, 0.03);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    padding: 0px;
}}
QFrame#HomeStatCard:hover {{
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
}}
QLabel#HomeStatBig {{
    color: {CLR_TEXT_PRIMARY};
    font-size: 36px;
    font-weight: 700;
    font-family: {FONT_MONO};
}}
QLabel#HomeStatusPill {{
    color: {CLR_ACCENT};
    font-size: 15px;
    font-weight: 500;
    font-family: {FONT_FAMILY};
    background: transparent;
}}
QLabel#VoiceProfilePill {{
    color: {CLR_ACCENT};
    font-size: 11px;
    font-weight: 600;
    font-family: {FONT_FAMILY};
    background: rgba(134, 239, 172, 0.08);
    border: 1px solid rgba(134, 239, 172, 0.18);
    border-radius: 6px;
    padding: 4px 10px;
}}
QFrame#InfoPopup {{
    background-color: #1C2320;
    border: 1px solid rgba(134, 239, 172, 0.2);
    border-radius: 8px;
}}
QLabel#InfoBtn {{
    background: transparent;
    color: {CLR_TEXT_MUTED};
    font-size: 11px;
    padding: 0px;
}}
QLabel#InfoBtn:hover {{
    color: {CLR_ACCENT};
}}

/* ─── Page Titles ─── */
QLabel#PageTitle {{
    font-size: {FONT_PAGE_TITLE};
    font-weight: 700;
    color: {CLR_TEXT_PRIMARY};
    font-family: {FONT_SERIF};
    letter-spacing: -0.2px;
}}
QLabel#Subtitle {{
    color: {CLR_TEXT_MUTED};
    font-size: 14px;
    font-family: {FONT_FAMILY};
}}
QLabel#EmptyState {{
    color: {CLR_TEXT_DIM};
    font-size: 14px;
    font-family: {FONT_FAMILY};
    padding: 40px;
}}
QFrame#EmptyContainer {{
    background-color: {CLR_CARD};
    border-radius: {RADIUS_CARD};
    border: 1px dashed {CLR_BORDER};
    margin: 8px 0;
}}
QLabel#EmptyIcon {{
    font-size: 36px;
    background: transparent;
}}
QLabel#EmptyTitle {{
    color: {CLR_TEXT_SECONDARY};
    font-size: 15px;
    font-weight: 600;
    font-family: {FONT_FAMILY};
    background: transparent;
}}
QLabel#EmptySubtitle {{
    color: {CLR_TEXT_MUTED};
    font-size: 13px;
    font-family: {FONT_FAMILY};
    background: transparent;
}}

/* ─── Page Transitions ─── */
QStackedWidget {{
    background: transparent;
}}

/* ─── Focus States ─── */
QPushButton:focus {{
    outline: none;
}}
QPushButton#WordChipDeleteBtn:focus {{
    outline: none;
    border: none;
    background: transparent;
}}

/* ─── Tooltip ─── */
QToolTip {{
    background: #1C2420;
    color: {CLR_TEXT_PRIMARY};
    border: 1px solid {CLR_BORDER_HOVER};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
    font-family: {FONT_FAMILY};
}}

/* ─── Scrollbar ─── */
QScrollBar:vertical {{
    background: transparent;
    width: 14px;
    margin: 6px 4px;
    border-radius: 7px;
}}
QScrollBar::handle:vertical {{
    background: rgba(255, 255, 255, 0.35);
    border-radius: 7px;
    min-height: 40px;
}}
QScrollBar::handle:vertical:hover {{
    background: rgba(255, 255, 255, 0.65);
}}
QScrollBar::handle:vertical:pressed {{
    background: rgba(134, 239, 172, 0.8);
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

"""
