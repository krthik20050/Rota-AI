"""
Base / layout / sidebar QSS — container, title bar, sidebar, stats panel,
page titles, empty states, scrollbar, tooltip, focus states.
"""
from __future__ import annotations

from ui.styles._main_window_qss_tokens import (
    CLR_ACCENT, CLR_BASE, CLR_BORDER, CLR_BORDER_HOVER,
    CLR_CARD, CLR_SIDEBAR,
    CLR_TEXT_DIM, CLR_TEXT_MUTED, CLR_TEXT_PRIMARY, CLR_TEXT_SECONDARY,
    FONT_BRAND_SIZE, FONT_FAMILY, FONT_MONO, FONT_PAGE_TITLE,
    FONT_SERIF, RADIUS_BTN, RADIUS_CARD, RADIUS_CONTAINER,
)

_QSS_BASE: str = f"""

* {{
    outline: none;
}}

/* ─── Container ─── */
QFrame#MainContainer {{
    background-color: {CLR_BASE};
    border-radius: {RADIUS_CONTAINER};
    border: 1px solid {CLR_BORDER};
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

/* ─── Sidebar ─── */
QFrame#Sidebar {{
    background-color: {CLR_SIDEBAR};
    border-right: 1px solid {CLR_BORDER};
    border-bottom-left-radius: {RADIUS_CONTAINER};
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

/* ─── Stats Panel (home right side) ─── */
QFrame#StatsPanel {{
    background-color: #101513;
    border-left: 1px solid {CLR_BORDER};
    border-bottom-right-radius: {RADIUS_CONTAINER};
}}
QLabel#PanelSection {{
    color: {CLR_TEXT_DIM};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.4px;
    font-family: {FONT_FAMILY};
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
    border: 1px solid {CLR_ACCENT};
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
