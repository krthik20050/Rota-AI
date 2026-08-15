"""
Wispr Flow "Voice in Motion" Design System — QSS Stylesheet
============================================================
Aggregator module. Imports design tokens from _base.py (tokens now inlined
there — ponytail:merge) and QSS sub-sections, then assembles WISPR_QSS.

Imported by ui.main_window.
"""

from __future__ import annotations

# ── Assemble full stylesheet ─────────────────────────────────────────
# Note: design tokens are now defined in _main_window_qss_base.py
# (CLR_BASE, CLR_ACCENT, CLR_ERROR, etc.) — the separate _tokens.py
# was removed (ponytail:merge: one less file to maintain).
# ponytail:merge — tokens now defined in _base.py (was _tokens.py)
# All imports below are re-exports for consumer modules (home_page, main_window).
# noqa comments keep ruff from stripping them as "unused".
from ui.styles._main_window_qss_base import (  # noqa: F401
    _QSS_BASE,
    CLR_ACCENT,
    CLR_ACCENT_DIM,
    CLR_ACCENT_GLOW,
    CLR_BASE,
    CLR_BORDER,
    CLR_BORDER_HOVER,
    CLR_CARD,
    CLR_CARD_HOVER,
    CLR_ERROR,
    CLR_SIDEBAR,
    CLR_SUCCESS,
    CLR_TEXT_DIM,
    CLR_TEXT_MUTED,
    CLR_TEXT_PRIMARY,
    CLR_TEXT_SECONDARY,
    CLR_WARNING,
    FONT_BODY,
    FONT_BRAND_SIZE,
    FONT_FAMILY,
    FONT_MONO,
    FONT_PAGE_TITLE,
    FONT_SERIF,
    FONT_SMALL,
    FONT_STAT,
    RADIUS_BTN,
    RADIUS_CARD,
    RADIUS_CONTAINER,
    SIDEBAR_W,
    STATS_PANEL_W,
)
from ui.styles._main_window_qss_components import _QSS_COMPONENTS  # noqa: F401

WISPR_QSS: str = _QSS_BASE + _QSS_COMPONENTS
