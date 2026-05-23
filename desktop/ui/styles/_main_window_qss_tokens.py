"""
Wispr Flow design tokens — colors, typography, geometry.
Imported by all QSS sub-modules and re-exported via main_window_qss.py.
"""
from __future__ import annotations

# ── Base colors ──────────────────────────────────────────────────────
CLR_BASE          = "#141918"
CLR_SIDEBAR       = "#111614"
CLR_CARD          = "#191E1C"
CLR_CARD_HOVER    = "#1F2521"
CLR_BORDER        = "rgba(255, 255, 255, 0.05)"
CLR_BORDER_HOVER  = "rgba(255, 255, 255, 0.1)"

# ── Text hierarchy ───────────────────────────────────────────────────
CLR_TEXT_PRIMARY   = "#F0F0F2"
CLR_TEXT_SECONDARY = "#A0A0A5"
CLR_TEXT_MUTED     = "#5A5A60"
CLR_TEXT_DIM       = "#3A3A40"

# ── Accent ───────────────────────────────────────────────────────────
CLR_ACCENT         = "#86EFAC"
CLR_ACCENT_DIM     = "rgba(134, 239, 172, 0.12)"
CLR_ACCENT_GLOW    = "rgba(134, 239, 172, 0.2)"

# ── State colors ─────────────────────────────────────────────────────
CLR_SUCCESS        = "#4ADE80"
CLR_ERROR          = "#F87171"
CLR_WARNING        = "#FBBF24"

# ── Typography ───────────────────────────────────────────────────────
FONT_FAMILY       = "'Segoe UI', 'Inter', -apple-system, sans-serif"
FONT_SERIF        = "'Georgia', 'Times New Roman', serif"
FONT_MONO         = "'Courier New', 'Consolas', monospace"
FONT_BRAND_SIZE   = "24px"
FONT_PAGE_TITLE   = "28px"
FONT_BODY         = "15px"
FONT_SMALL        = "13px"
FONT_STAT         = "36px"

# ── Geometry ─────────────────────────────────────────────────────────
RADIUS_CONTAINER  = "18px"
RADIUS_CARD       = "14px"
RADIUS_BTN        = "10px"
SIDEBAR_W         = 200
STATS_PANEL_W     = 250
