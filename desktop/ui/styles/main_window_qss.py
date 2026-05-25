"""
Wispr Flow "Voice in Motion" Design System — QSS Stylesheet
============================================================
Aggregator module. Imports design tokens and QSS sub-sections,
assembles WISPR_QSS, and re-exports all public names.

Imported by ui.main_window.
"""

from __future__ import annotations

# ── Assemble full stylesheet ─────────────────────────────────────────
from ui.styles._main_window_qss_base import _QSS_BASE
from ui.styles._main_window_qss_components import _QSS_COMPONENTS

# ── Re-export all design tokens ──────────────────────────────────────
from ui.styles._main_window_qss_tokens import (  # noqa: F401
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

WISPR_QSS: str = _QSS_BASE + _QSS_COMPONENTS
