"""
Component QSS — cards, history items, dictionary, snippets,
segmented control, archetype card, buttons, stat cards.
"""
from __future__ import annotations

from ui.styles._main_window_qss_tokens import (
    CLR_ACCENT, CLR_BORDER, CLR_BORDER_HOVER,
    CLR_CARD, CLR_ERROR,
    CLR_TEXT_MUTED, CLR_TEXT_PRIMARY, CLR_TEXT_SECONDARY,
    FONT_FAMILY, FONT_MONO, FONT_STAT,
    RADIUS_CARD,
)

_QSS_COMPONENTS: str = f"""

/* ─── Mini Stat Cards ─── */
QFrame#MiniStat {{
    background-color: rgba(255, 255, 255, 0.04);
    border-radius: 8px;
    border: 1px solid {CLR_BORDER};
}}
QLabel#MiniStatTitle {{
    color: {CLR_TEXT_MUTED};
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-family: {FONT_FAMILY};
}}
QLabel#MiniStatValue {{
    color: {CLR_TEXT_PRIMARY};
    font-size: 16px;
    font-weight: 700;
    font-family: {FONT_FAMILY};
}}

/* ─── Latest Transcript Card ─── */
QFrame#LatestTranscriptCard {{
    background-color: {CLR_CARD};
    border-radius: {RADIUS_CARD};
    border: 1px solid {CLR_BORDER};
}}
QLabel#SectionTitle {{
    color: {CLR_TEXT_PRIMARY};
    font-size: 15px;
    font-weight: 700;
    font-family: {FONT_FAMILY};
}}
QLabel#LatestCleanedText {{
    color: {CLR_TEXT_PRIMARY};
    font-size: 14px;
    line-height: 1.35;
    font-family: {FONT_FAMILY};
}}
QLabel#LatestRawText {{
    color: {CLR_TEXT_SECONDARY};
    font-size: 13px;
    line-height: 1.35;
    font-family: {FONT_FAMILY};
}}
QLabel#TranscriptSectionLabel {{
    color: {CLR_TEXT_MUTED};
    font-size: 10px;
    font-weight: 700;
    font-family: {FONT_FAMILY};
    letter-spacing: 0.8px;
    text-transform: uppercase;
}}
QFrame#TranscriptDivider {{
    border: none;
    border-top: 1px solid {CLR_BORDER};
    margin: 0px;
}}
QPushButton#SmallButton {{
    background-color: rgba(255, 255, 255, 0.08);
    color: {CLR_TEXT_SECONDARY};
    border: 1px solid {CLR_BORDER};
    border-radius: 7px;
    padding: 5px 10px;
    font-size: 11px;
    font-weight: 600;
    font-family: {FONT_FAMILY};
}}
QPushButton#SmallButton:hover {{
    background-color: rgba(255, 255, 255, 0.12);
    color: {CLR_TEXT_PRIMARY};
    border-color: {CLR_BORDER_HOVER};
}}
QPushButton#SectionToggleBtn {{
    background: transparent;
    color: {CLR_TEXT_MUTED};
    border: none;
    border-radius: 4px;
    font-size: 10px;
    padding: 0px 3px;
}}
QPushButton#SectionToggleBtn:hover {{
    background: rgba(255, 255, 255, 0.06);
    color: {CLR_TEXT_SECONDARY};
}}

/* ─── Stat Cards (Insights) ─── */
QFrame#StatCard {{
    background-color: {CLR_CARD};
    border-radius: {RADIUS_CARD};
    border: 1px solid {CLR_BORDER};
}}
QFrame#StatCard:hover {{
    border: 1px solid {CLR_BORDER_HOVER};
}}
QLabel#StatTitle {{
    color: {CLR_TEXT_MUTED};
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 0.3px;
    font-family: {FONT_FAMILY};
}}
QLabel#StatValue {{
    color: {CLR_TEXT_PRIMARY};
    font-size: {FONT_STAT};
    font-weight: 700;
    font-family: {FONT_MONO};
}}

/* ─── Insight Card ─── */
QFrame#InsightCard {{
    background-color: {CLR_CARD};
    border-radius: {RADIUS_CARD};
    border: 1px solid {CLR_BORDER};
}}
QLabel#InsightText {{
    color: {CLR_TEXT_SECONDARY};
    font-size: 13px;
    font-family: {FONT_FAMILY};
}}
QLabel#SuggestionText {{
    color: {CLR_ACCENT};
    font-size: 12px;
    font-weight: 500;
    font-family: {FONT_FAMILY};
}}

/* ─── Buttons ─── */
QPushButton#IconBtn {{
    background: rgba(255, 255, 255, 0.04);
    color: {CLR_TEXT_MUTED};
    border: 1px solid {CLR_BORDER};
    border-radius: 8px;
    font-size: 15px;
}}
QPushButton#IconBtn:hover {{
    background: rgba(255, 255, 255, 0.08);
    color: {CLR_TEXT_PRIMARY};
}}
QPushButton#IconBtn:pressed {{
    background: rgba(255, 255, 255, 0.12);
}}

/* ─── Dictionary ─── */
QLineEdit#DictInput {{
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid {CLR_BORDER};
    border-radius: 8px;
    color: {CLR_TEXT_PRIMARY};
    font-size: 13px;
    font-family: {FONT_FAMILY};
    padding: 8px 14px;
    selection-background-color: {CLR_ACCENT};
}}
QLineEdit#DictInput:focus {{
    border: 1px solid {CLR_ACCENT};
    background: rgba(255, 255, 255, 0.07);
}}
QLineEdit#DictSearchInput {{
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid {CLR_BORDER};
    border-radius: 8px;
    color: {CLR_TEXT_PRIMARY};
    font-size: 13px;
    font-family: {FONT_FAMILY};
    padding: 8px 14px;
    selection-background-color: {CLR_ACCENT};
}}
QLineEdit#DictSearchInput:focus {{
    border: 1px solid {CLR_ACCENT};
    background: rgba(255, 255, 255, 0.07);
}}
QLabel#DictCountBadge {{
    background: rgba(134, 239, 172, 0.12);
    color: #86EFAC;
    border: 1.5px solid rgba(134, 239, 172, 0.35);
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 700;
    font-family: {FONT_FAMILY};
}}
QPushButton#AddWordBtn {{
    background: {CLR_ACCENT};
    color: #0A0A0A;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    font-family: {FONT_FAMILY};
    padding: 8px 20px;
}}
QPushButton#AddWordBtn:hover {{
    background: #A3F4BF;
}}
QFrame#WordChip {{
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
}}
QFrame#WordChip:hover {{
    background-color: rgba(134, 239, 172, 0.1);
    border: 1px solid rgba(134, 239, 172, 0.35);
}}
QPushButton#WordChipDeleteBtn:focus {{
    outline: none;
    border: none;
}}
QLabel#WordChipIcon {{
    font-size: 11px;
    background: transparent;
}}
QLabel#WordChipLabel {{
    color: {CLR_TEXT_PRIMARY};
    font-size: 13px;
    font-weight: 500;
    background: transparent;
    font-family: {FONT_FAMILY};
}}
QPushButton#WordChipDeleteBtn {{
    background: transparent;
    color: {CLR_TEXT_MUTED};
    border: none;
    border-radius: 8px;
    font-size: 10px;
    font-weight: bold;
}}
QPushButton#WordChipDeleteBtn:hover {{
    background: rgba(248, 113, 113, 0.4);
    color: #F87171;
}}

/* ─── Snippets Page ─── */
QFrame#SnippetLeftCol {{
    background-color: transparent;
    border-right: 1px solid {CLR_BORDER};
    padding-right: 12px;
}}
QScrollArea#SnippetScroll {{
    background: transparent;
    border: none;
}}
QPushButton#SnippetActionBtn {{
    background: {CLR_ACCENT};
    color: #0A0A0A;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    font-family: {FONT_FAMILY};
    padding: 8px 16px;
}}
QPushButton#SnippetActionBtn:hover {{
    background: #A3F4BF;
}}
QPushButton#SnippetSecBtn {{
    background: rgba(255, 255, 255, 0.04);
    color: {CLR_TEXT_SECONDARY};
    border: 1px solid {CLR_BORDER};
    border-radius: 8px;
    font-size: 11px;
    font-family: {FONT_FAMILY};
    padding: 8px 12px;
}}
QPushButton#SnippetSecBtn:hover {{
    background: rgba(255, 255, 255, 0.08);
    color: {CLR_TEXT_PRIMARY};
}}
QFrame#SnippetEmptyCard {{
    background-color: {CLR_CARD};
    border-radius: {RADIUS_CARD};
    border: 1px dashed {CLR_BORDER};
    padding: 36px;
}}
QLabel#SnippetEmptyIcon {{
    font-size: 48px;
    background: transparent;
    margin-bottom: 12px;
}}
QFrame#SnippetEditorForm {{
    background-color: rgba(20, 25, 24, 0.75);
    border-radius: {RADIUS_CARD};
    border: 1px solid rgba(255, 255, 255, 0.1);
}}
QLineEdit#SnippetTriggerInput {{
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid {CLR_BORDER};
    border-radius: 8px;
    color: {CLR_TEXT_PRIMARY};
    font-size: 13px;
    font-family: {FONT_FAMILY};
    padding: 10px 14px;
    selection-background-color: {CLR_ACCENT};
}}
QLineEdit#SnippetTriggerInput:focus {{
    border: 1px solid {CLR_ACCENT};
    background: rgba(255, 255, 255, 0.06);
}}
QTextEdit#SnippetExpansionInput {{
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid {CLR_BORDER};
    border-radius: 8px;
    color: {CLR_TEXT_PRIMARY};
    font-size: 13px;
    font-family: {FONT_FAMILY};
    padding: 12px;
    selection-background-color: {CLR_ACCENT};
}}
QTextEdit#SnippetExpansionInput:focus {{
    border: 1px solid {CLR_ACCENT};
    background: rgba(255, 255, 255, 0.06);
}}
QPushButton#SnippetVarBtn {{
    background: rgba(255, 255, 255, 0.06);
    color: {CLR_TEXT_SECONDARY};
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    font-size: 11px;
    font-family: {FONT_FAMILY};
    padding: 4px 12px;
}}
QPushButton#SnippetVarBtn:hover {{
    background: rgba(134, 239, 172, 0.1);
    color: #86EFAC;
    border: 1px solid #86EFAC;
}}
QPushButton#SnippetSaveBtn {{
    background: {CLR_ACCENT};
    color: #0A0A0A;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    font-family: {FONT_FAMILY};
    padding: 8px 24px;
}}
QPushButton#SnippetSaveBtn:hover {{
    background: #A3F4BF;
}}
QPushButton#SnippetDeleteBtn {{
    background: transparent;
    color: {CLR_ERROR};
    border: 1px solid rgba(248, 113, 113, 0.8);
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    font-family: {FONT_FAMILY};
    padding: 8px 16px;
}}
QPushButton#SnippetDeleteBtn:hover {{
    background: rgba(248, 113, 113, 0.3);
    border-color: {CLR_ERROR};
}}
QFrame#SnippetRow {{
    border-radius: 12px;
    margin: 0px 0px 1px 0px;
}}
QFrame#SnippetRow:hover {{
    border: 1px solid rgba(134, 239, 172, 0.35);
    background: rgba(255, 255, 255, 0.06);
}}
QLabel#SnippetRowIcon {{
    color: {CLR_ACCENT};
    font-size: 14px;
    background: transparent;
}}
QLabel#SnippetRowTrigger {{
    color: {CLR_TEXT_PRIMARY};
    font-weight: 700;
    font-size: 13px;
    font-family: {FONT_FAMILY};
    background: transparent;
}}
QLabel#SnippetRowPreview {{
    color: {CLR_TEXT_MUTED};
    font-size: 11px;
    font-family: {FONT_FAMILY};
    background: transparent;
}}
QLabel#SnippetVarBadge {{
    background: rgba(134, 239, 172, 0.16);
    color: #86EFAC;
    border: 1px solid rgba(134, 239, 172, 0.35);
    border-radius: 8px;
    padding: 2px 6px;
    font-size: 9px;
    font-weight: 700;
    font-family: {FONT_FAMILY};
}}
QLineEdit#SnippetSearch {{
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid {CLR_BORDER};
    border-radius: 8px;
    color: {CLR_TEXT_PRIMARY};
    font-size: 13px;
    font-family: {FONT_FAMILY};
    padding: 0 10px;
}}
QLineEdit#SnippetSearch:focus {{
    border: 1px solid rgba(134, 239, 172, 0.4);
    background: rgba(255, 255, 255, 0.06);
}}

/* ─── Segmented Control ─── */
QFrame#SegmentedControl {{
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 2px;
}}
QPushButton#TabToggleBtn {{
    background-color: transparent;
    color: #8E8E93;
    border: none;
    border-radius: 12px;
    padding: 5px 14px;
    font-size: 11px;
    font-weight: 600;
    font-family: {FONT_FAMILY};
}}
QPushButton#TabToggleBtn:hover {{
    color: #E8E8EA;
    background-color: rgba(255, 255, 255, 0.04);
}}
QPushButton#TabToggleBtn:checked {{
    background-color: rgba(255, 255, 255, 0.12);
    color: #86EFAC;
    border: 1.5px solid rgba(134, 239, 172, 0.35);
}}

/* ─── Archetype Card ─── */
QFrame#ArchetypeCard {{
    background-color: {CLR_CARD};
    border-radius: {RADIUS_CARD};
    border: 1px solid {CLR_BORDER};
}}
QFrame#ArchetypeCard:hover {{
    border: 1px solid {CLR_BORDER_HOVER};
}}
QLabel#ArchetypeLevelBadge {{
    background: rgba(134, 239, 172, 0.12);
    border: 1.5px solid #86EFAC;
    border-radius: 35px;
    color: #86EFAC;
    font-size: 13px;
    font-weight: 800;
    font-family: {FONT_FAMILY};
}}

"""
