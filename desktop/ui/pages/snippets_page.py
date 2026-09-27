"""
Rota AI — Snippets Page (rebuilt)
=================================
Wispr-Flow-style two-panel manager: a filterable card list on the left and a
single focused editor on the right.

Design rules kept from the codebase:
- PySide6 widgets, page-local QSS keyed on objectName
- Accent #86EFAC on dark surfaces, matching Insights/Home
- No full-list rebuilds on small state changes: toggles and renames update
  the affected row in place; the list rebuilds only when the *set* of visible
  rows changes (filter change, add, delete)
- Every selectable surface is a real button with hover/pressed states
"""

from __future__ import annotations

import datetime
import re

import structlog
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

logger = structlog.get_logger(__name__)

# ── Design tokens (match the rest of the app) ────────────────────────────────
ACCENT = "#86EFAC"
ACCENT_DIM = "rgba(134, 239, 172, 0.12)"
ACCENT_LINE = "rgba(134, 239, 172, 0.4)"
SURFACE = "#151A18"
SURFACE_ALT = "#191E1C"
BORDER = "rgba(255, 255, 255, 0.06)"
TEXT_PRIMARY = "#F0F0F2"
TEXT_SECONDARY = "#A0A0A5"
TEXT_MUTED = "#5A5A60"
DANGER = "#F87171"
WARNING = "#FBBF24"

MAX_TRIGGER = 60
MAX_EXPANSION = 4000

VARIABLES = (
    "date",
    "time",
    "today",
    "day",
    "month",
    "year",
    "datetime",
    "timestamp",
    "clipboard",
    "cursor",
)

_PAGE_QSS = f"""
QFrame#SnpCard {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}
QFrame#SnpCard:hover {{
    border: 1px solid rgba(134, 239, 172, 0.35);
    background: {SURFACE_ALT};
}}
QFrame#SnpCardSelected {{
    background: {ACCENT_DIM};
    border: 1px solid {ACCENT_LINE};
    border-radius: 10px;
}}
QFrame#SnpEditorCard {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}
QLabel#PageTitle {{
    color: {TEXT_PRIMARY};
    font-size: 22px;
    font-weight: 700;
    background: transparent;
}}
QLabel#Subtitle {{
    color: {TEXT_MUTED};
    font-size: 12px;
    background: transparent;
}}
QLabel#SectionTitle {{
    color: {TEXT_SECONDARY};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    background: transparent;
}}
QLabel#CardTrigger {{
    color: {TEXT_PRIMARY};
    font-size: 13px;
    font-weight: 600;
    background: transparent;
}}
QLabel#CardPreview {{
    color: {TEXT_MUTED};
    font-size: 11px;
    background: transparent;
}}
QLabel#CardDisabled {{ color: {TEXT_MUTED}; }}
QPushButton#Chip {{
    background: rgba(255, 255, 255, 0.04);
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 11px;
}}
QPushButton#Chip:hover {{ background: rgba(255, 255, 255, 0.08); }}
QPushButton#ChipOn {{
    background: {ACCENT_DIM};
    color: {ACCENT};
    border: 1px solid {ACCENT_LINE};
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 600;
}}
QPushButton#ChipOn:hover {{ background: rgba(134, 239, 172, 0.2); }}
QLineEdit#SnpSearch {{
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid {BORDER};
    border-radius: 8px;
    color: {TEXT_PRIMARY};
    padding: 6px 10px;
    font-size: 12px;
}}
QLineEdit#SnpSearch:focus {{ border: 1px solid rgba(134, 239, 172, 0.45); }}
QLineEdit#SnpField {{
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid {BORDER};
    border-radius: 8px;
    color: {TEXT_PRIMARY};
    padding: 8px 10px;
    font-size: 13px;
}}
QLineEdit#SnpField:focus {{ border: 1px solid rgba(134, 239, 172, 0.45); }}
QTextEdit#SnpExpansion {{
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid {BORDER};
    border-radius: 8px;
    color: {TEXT_PRIMARY};
    padding: 8px 10px;
    font-size: 12px;
    selection-background-color: rgba(134, 239, 172, 0.3);
}}
QTextEdit#SnpExpansion:focus {{ border: 1px solid rgba(134, 239, 172, 0.45); }}
QLabel#PreviewBox {{
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid {BORDER};
    border-radius: 8px;
    color: {TEXT_SECONDARY};
    font-size: 12px;
}}
QPushButton#Primary {{
    background: {ACCENT};
    color: #0B0F0D;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: 700;
}}
QPushButton#Primary:hover {{ background: #A5F5BE; }}
QPushButton#Primary:disabled {{
    background: rgba(134, 239, 172, 0.25);
    color: rgba(11, 15, 13, 0.55);
}}
QPushButton#Ghost {{
    background: rgba(255, 255, 255, 0.04);
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 12px;
}}
QPushButton#Ghost:hover {{ background: rgba(255, 255, 255, 0.08); color: {TEXT_PRIMARY}; }}
QPushButton#DangerGhost {{
    background: transparent;
    color: {DANGER};
    border: 1px solid rgba(248, 113, 113, 0.35);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#DangerGhost:hover {{ background: rgba(248, 113, 113, 0.12); }}
QPushButton#VarBtn {{
    background: rgba(255, 255, 255, 0.05);
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 10px;
    font-family: Consolas, monospace;
}}
QPushButton#VarBtn:hover {{
    background: {ACCENT_DIM};
    color: {ACCENT};
    border: 1px solid {ACCENT_LINE};
}}
QPushButton#Toggle {{
    border: none;
    border-radius: 9px;
    color: #0B0F0D;
    font-size: 9px;
    font-weight: 800;
    background: rgba(255, 255, 255, 0.10);
    color: {TEXT_MUTED};
}}
QPushButton#ToggleOn {{ background: {ACCENT}; color: #0B0F0D; }}
QLabel#Badge {{
    background: rgba(255, 255, 255, 0.05);
    color: {TEXT_MUTED};
    border-radius: 6px;
    padding: 1px 6px;
    font-size: 9px;
    font-weight: 700;
}}
QLabel#EmptyIcon {{ font-size: 34px; background: transparent; }}
QLabel#EmptyTitle {{ color: {TEXT_SECONDARY}; font-size: 14px; font-weight: 600; background: transparent; }}
QLabel#EmptySub {{ color: {TEXT_MUTED}; font-size: 11px; background: transparent; }}
"""


def _resolve_preview(text: str) -> str:
    """Resolve the variables a preview can show without side effects."""
    now = datetime.datetime.now()
    out = text
    out = out.replace("{{date}}", now.strftime("%Y-%m-%d"))
    out = out.replace("{{time}}", now.strftime("%H:%M:%S"))
    out = out.replace("{{today}}", now.strftime("%A, %B %d, %Y"))
    out = out.replace("{{day}}", now.strftime("%d"))
    out = out.replace("{{month}}", now.strftime("%m"))
    out = out.replace("{{year}}", now.strftime("%Y"))
    out = out.replace("{{datetime}}", now.strftime("%Y-%m-%d %H:%M"))
    out = out.replace("{{timestamp}}", str(int(now.timestamp())))
    out = out.replace("{{clipboard}}", "[clipboard content]")
    out = out.replace("{{cursor}}", "|")
    return out


class _SnippetCard(QFrame):
    """One snippet row in the list. Click = select; pill = toggle in place."""

    clicked = Signal(str)
    toggled = Signal(str)

    def __init__(self, trigger: str, expansion: str, enabled: bool, parent=None):
        super().__init__(parent)
        self.trigger = trigger
        self.expansion = expansion
        self.enabled = enabled
        self.setObjectName("SnpCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        h = QHBoxLayout(self)
        h.setContentsMargins(12, 9, 10, 9)
        h.setSpacing(10)

        txt = QVBoxLayout()
        txt.setSpacing(2)
        self._trig_lbl = QLabel(trigger or "Untitled snippet")
        self._trig_lbl.setObjectName("CardTrigger")
        preview = expansion.replace("\n", " ").strip()
        if len(preview) > 60:
            preview = preview[:58] + "…"
        self._prev_lbl = QLabel(preview or "empty expansion")
        self._prev_lbl.setObjectName("CardPreview")
        txt.addWidget(self._trig_lbl)
        txt.addWidget(self._prev_lbl)
        h.addLayout(txt, 1)

        n_vars = len(re.findall(r"\{\{([^}]+)\}\}", expansion))
        if n_vars:
            badge = QLabel(f"{n_vars} var" + ("s" if n_vars > 1 else ""))
            badge.setObjectName("Badge")
            h.addWidget(badge)

        self._pill = QPushButton("ON" if enabled else "OFF")
        self._pill.setObjectName("ToggleOn" if enabled else "Toggle")
        self._pill.setFixedSize(34, 18)
        self._pill.setCursor(Qt.CursorShape.PointingHandCursor)
        self._pill.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._pill.clicked.connect(lambda: self.toggled.emit(self.trigger))
        h.addWidget(self._pill)

    def set_selected(self, selected: bool) -> None:
        self.setObjectName("SnpCardSelected" if selected else "SnpCard")
        self.setStyleSheet(_PAGE_QSS)

    def set_enabled_state(self, enabled: bool) -> None:
        self.enabled = enabled
        self._pill.setText("ON" if enabled else "OFF")
        self._pill.setObjectName("ToggleOn" if enabled else "Toggle")
        self.setStyleSheet(_PAGE_QSS)
        self._trig_lbl.setStyleSheet(
            "" if enabled else f"color: {TEXT_MUTED}; text-decoration: line-through;"
        )

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.trigger)
        super().mouseReleaseEvent(event)


class SnippetsPage(QWidget):
    """Wispr-Flow-style snippet manager: list + focused editor."""

    def __init__(self, snippets_manager, parent=None):
        super().__init__(parent)
        self.snippets_manager = snippets_manager
        self._selected: str | None = None
        self._creating_new = False
        self._search = ""
        self._category = "__all__"
        self._dirty = False
        self._cards: dict[str, _SnippetCard] = {}
        self.setStyleSheet(_PAGE_QSS)
        self._build_ui()
        self._reload_list()
        self._load_editor(None)

    # ── UI construction ───────────────────────────────────────────────────

    def _build_ui(self) -> None:
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(20)

        # ── Left: header, search, chips, card list ───────────────────────
        left = QVBoxLayout()
        left.setSpacing(10)

        title = QLabel("Snippets")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Say a trigger phrase while dictating and Rota expands it instantly.")
        subtitle.setObjectName("Subtitle")
        subtitle.setWordWrap(True)
        left.addWidget(title)
        left.addWidget(subtitle)

        self._search_box = QLineEdit()
        self._search_box.setObjectName("SnpSearch")
        self._search_box.setPlaceholderText("Search triggers and content…")
        self._search_box.setFixedHeight(34)
        self._search_box.setClearButtonEnabled(True)
        self._search_box.textChanged.connect(self._on_search)
        left.addWidget(self._search_box)

        self._chip_row = QHBoxLayout()
        self._chip_row.setSpacing(6)
        left.addLayout(self._chip_row)

        self._list_scroll = QScrollArea()
        self._list_scroll.setWidgetResizable(True)
        self._list_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._list_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 2, 4, 2)
        self._list_layout.setSpacing(6)
        self._list_scroll.setWidget(self._list_container)
        left.addWidget(self._list_scroll, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        add_btn = QPushButton("+ New")
        add_btn.setObjectName("Primary")
        add_btn.setFixedHeight(34)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._on_new)
        btn_row.addWidget(add_btn, 2)
        for label, slot in (
            ("Import", self._on_import),
            ("Export", self._on_export),
        ):
            b = QPushButton(label)
            b.setObjectName("Ghost")
            b.setFixedHeight(34)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(slot)
            btn_row.addWidget(b, 1)
        left.addLayout(btn_row)

        lay.addLayout(left, 5)

        # ── Right: editor / empty state ──────────────────────────────────
        self._editor_stack = QVBoxLayout()
        self._editor_stack.setSpacing(0)
        lay.addLayout(self._editor_stack, 7)

        self._editor = self._build_editor()
        self._empty = self._build_empty_state()
        self._editor_stack.addWidget(self._empty)
        self._editor_stack.addWidget(self._editor)

    def _build_empty_state(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon = QLabel("⚡")
        icon.setObjectName("EmptyIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t = QLabel("No snippet selected")
        t.setObjectName("EmptyTitle")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s = QLabel(
            "Pick a snippet from the list, or create one and say its trigger\n"
            "while dictating — Rota expands it on the spot."
        )
        s.setObjectName("EmptySub")
        s.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(icon)
        v.addWidget(t)
        v.addWidget(s)
        return w

    def _build_editor(self) -> QWidget:
        w = QWidget()
        outer = QVBoxLayout(w)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("SnpEditorCard")
        v = QVBoxLayout(card)
        v.setContentsMargins(22, 20, 22, 20)
        v.setSpacing(12)

        # Header row: title + delete
        head = QHBoxLayout()
        self._editor_title = QLabel("Edit snippet")
        self._editor_title.setObjectName("SectionTitle")
        head.addWidget(self._editor_title, 1)
        self._delete_btn = QPushButton("Delete")
        self._delete_btn.setObjectName("DangerGhost")
        self._delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._delete_btn.clicked.connect(self._on_delete)
        self._delete_btn.setVisible(False)
        head.addWidget(self._delete_btn)
        v.addLayout(head)

        # Trigger
        lbl = QLabel("SPOKEN TRIGGER")
        lbl.setObjectName("SectionTitle")
        v.addWidget(lbl)
        self._trigger_input = QLineEdit()
        self._trigger_input.setObjectName("SnpField")
        self._trigger_input.setPlaceholderText("e.g. email signature")
        self._trigger_input.textChanged.connect(self._on_dirty)
        v.addWidget(self._trigger_input)

        # Category
        cat_lbl = QLabel("CATEGORY")
        cat_lbl.setObjectName("SectionTitle")
        v.addWidget(cat_lbl)
        self._category_input = QLineEdit()
        self._category_input.setObjectName("SnpField")
        self._category_input.setPlaceholderText("e.g. Email (optional)")
        self._category_input.textChanged.connect(self._on_dirty)
        v.addWidget(self._category_input)

        # Expansion + counter
        exp_head = QHBoxLayout()
        exp_lbl = QLabel("EXPANSION TEXT")
        exp_lbl.setObjectName("SectionTitle")
        exp_head.addWidget(exp_lbl, 1)
        self._counter = QLabel("0 / 4000")
        self._counter.setObjectName("Subtitle")
        exp_head.addWidget(self._counter)
        v.addLayout(exp_head)

        self._expansion_input = QTextEdit()
        self._expansion_input.setObjectName("SnpExpansion")
        self._expansion_input.setPlaceholderText(
            "The full text Rota types when it hears the trigger…"
        )
        self._expansion_input.setMinimumHeight(150)
        self._expansion_input.textChanged.connect(self._on_expansion_changed)
        v.addWidget(self._expansion_input, 2)

        # Variable chips
        vars_lbl = QLabel("INSERT VARIABLE")
        vars_lbl.setObjectName("SectionTitle")
        v.addWidget(vars_lbl)
        var_row = QHBoxLayout()
        var_row.setSpacing(6)
        for var in VARIABLES:
            b = QPushButton(f"{{{{{var}}}}}")
            b.setObjectName("VarBtn")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            b.clicked.connect(lambda _, v_=var: self._insert_var(v_))
            var_row.addWidget(b)
        var_row.addStretch()
        v.addLayout(var_row)

        # Live preview
        pv_lbl = QLabel("LIVE PREVIEW")
        pv_lbl.setObjectName("SectionTitle")
        v.addWidget(pv_lbl)
        self._preview = QLabel("Type an expansion to see how it will be typed…")
        self._preview.setObjectName("PreviewBox")
        self._preview.setWordWrap(True)
        self._preview.setMinimumHeight(52)
        self._preview.setAlignment(Qt.AlignmentFlag.AlignTop)
        v.addWidget(self._preview, 1)

        # Footer: hint + save
        foot = QHBoxLayout()
        self._dirty_lbl = QLabel("")
        self._dirty_lbl.setObjectName("Subtitle")
        foot.addWidget(self._dirty_lbl, 1)
        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setObjectName("Ghost")
        self._cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cancel_btn.clicked.connect(self._on_cancel)
        self._cancel_btn.setVisible(False)
        foot.addWidget(self._cancel_btn)
        self._save_btn = QPushButton("Save  ·  Ctrl+S")
        self._save_btn.setObjectName("Primary")
        self._save_btn.setFixedHeight(34)
        self._save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._save_btn.setEnabled(False)
        self._save_btn.clicked.connect(self._on_save)
        foot.addWidget(self._save_btn)
        v.addLayout(foot)

        outer.addWidget(card)
        save_sc = QShortcut(QKeySequence("Ctrl+S"), self)
        save_sc.activated.connect(self._on_save)
        esc_sc = QShortcut(QKeySequence("Escape"), self)
        esc_sc.activated.connect(self._on_cancel)
        return w

    # ── List rendering ────────────────────────────────────────────────────

    def _all_entries(self) -> dict[str, tuple[str, bool]]:
        if self.snippets_manager is None:
            return {}
        return self.snippets_manager.all_with_status()

    def _visible_entries(self) -> dict[str, tuple[str, bool, str]]:
        """Returns {trigger: (expansion, enabled, category)} after filtering."""
        data = self._all_entries()
        out: dict[str, tuple[str, bool, str]] = {}
        for trig, (exp, enabled) in data.items():
            cat = (
                self.snippets_manager.get_category(trig) if self.snippets_manager else ""
            ) or "Uncategorized"
            if self._category == "__starred__" and trig not in self._favorites():
                continue
            if self._category not in ("__all__", "__starred__") and cat != self._category:
                continue
            if self._search:
                q = self._search.lower()
                if q not in trig.lower() and q not in exp.lower() and q not in cat.lower():
                    continue
            out[trig] = (exp, enabled, cat)
        return out

    def _favorites(self) -> set[str]:
        cfg = getattr(self.snippets_manager, "_favorites", None)
        return set(cfg) if isinstance(cfg, set | list) else set()

    def _reload_chips(self) -> None:
        while self._chip_row.count():
            item = self._chip_row.takeAt(0)
            wdg = item.widget()
            if wdg:
                wdg.deleteLater()
        # Buckets from the manager itself, so an empty "Uncategorized" group
        # never renders a dead chip.
        cats = ["__all__"]
        if self.snippets_manager:
            grouped = self.snippets_manager.all_categorized()
            cats += sorted(c for c in grouped if grouped[c])
        for cat in cats:
            label = "All" if cat == "__all__" else cat
            chip = QPushButton(label)
            chip.setObjectName("ChipOn" if cat == self._category else "Chip")
            chip.setCursor(Qt.CursorShape.PointingHandCursor)
            chip.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            chip.clicked.connect(lambda _, c=cat: self._on_category(c))
            self._chip_row.addWidget(chip)
        self._chip_row.addStretch()

    def _reload_list(self) -> None:
        """Full rebuild — only called when the visible row set changes."""
        self._reload_chips()
        for card in self._cards.values():
            card.deleteLater()
        self._cards.clear()
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            wdg = item.widget()
            if wdg:
                wdg.deleteLater()

        entries = self._visible_entries()
        if not entries:
            empty = QLabel(
                "No snippets match."
                if (self._search or self._category != "__all__")
                else "No snippets yet.\nClick + New and say the trigger while dictating."
            )
            empty.setObjectName("EmptySub")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_layout.addWidget(empty)
            self._list_layout.addStretch()
            return

        for trig, (exp, enabled, _cat) in reversed(list(entries.items())):
            card = _SnippetCard(trig, exp, enabled)
            card.clicked.connect(self._on_select)
            card.toggled.connect(self._on_toggle)
            card.set_selected(trig == self._selected)
            self._cards[trig] = card
            self._list_layout.addWidget(card)
        self._list_layout.addStretch()

    # ── In-place updates (no rebuild) ─────────────────────────────────────

    def _on_toggle(self, trig: str) -> None:
        if not self.snippets_manager:
            return
        self.snippets_manager.toggle(trig)
        enabled = self.snippets_manager.is_enabled(trig)
        card = self._cards.get(trig)
        if card:
            card.set_enabled_state(enabled)

    def _on_select(self, trig: str) -> None:
        if self._dirty and not self._confirm_discard():
            return
        self._selected = trig
        self._creating_new = False
        for t, card in self._cards.items():
            card.set_selected(t == trig)
        self._load_editor(trig)

    # ── Editor logic ──────────────────────────────────────────────────────

    def _load_editor(self, trig: str | None) -> None:
        # Programmatic population fires textChanged/textEdited signals; the
        # loading guard stops that from marking a freshly-loaded snippet as
        # dirty (Save would otherwise enable itself with no user edit).
        self._loading = True
        try:
            self._load_editor_inner(trig)
        finally:
            self._loading = False

    def _load_editor_inner(self, trig: str | None) -> None:
        self._dirty = False
        self._dirty_lbl.setText("")
        self._save_btn.setEnabled(False)
        self._cancel_btn.setVisible(False)
        entry = self._all_entries().get(trig) if trig else None
        self._creating_new = entry is None and trig is not None

        if entry is None:
            if trig is None:
                self._editor.setVisible(False)
                self._empty.setVisible(True)
                return
            # New snippet
            self._editor_title.setText("New snippet")
            self._trigger_input.clear()
            self._category_input.clear()
            self._expansion_input.clear()
            self._delete_btn.setVisible(False)
        else:
            self._editor_title.setText("Edit snippet")
            self._trigger_input.setText(trig)
            cat = (self.snippets_manager.get_category(trig) if self.snippets_manager else "") or ""
            self._category_input.setText(cat)
            self._expansion_input.setPlainText(entry[0])
            self._delete_btn.setVisible(True)

        self._empty.setVisible(False)
        self._editor.setVisible(True)
        self._trigger_input.setFocus()

    def _on_expansion_changed(self) -> None:
        text = self._expansion_input.toPlainText()
        n = len(text)
        self._counter.setText(f"{n} / {MAX_EXPANSION}")
        color = TEXT_MUTED
        if n > MAX_EXPANSION * 0.95:
            color = DANGER
        elif n > MAX_EXPANSION * 0.8:
            color = WARNING
        self._counter.setStyleSheet(f"color: {color}; font-size: 11px; background: transparent;")
        preview_src = text.strip()
        self._preview.setText(
            _resolve_preview(preview_src)
            if preview_src
            else "Type an expansion to see how it will be typed…"
        )
        self._on_dirty()

    def _on_dirty(self) -> None:
        if getattr(self, "_loading", False) or not self._editor.isVisible():
            return
        self._dirty = True
        self._dirty_lbl.setText("Unsaved changes")
        self._save_btn.setEnabled(bool(self._trigger_input.text().strip()))
        self._cancel_btn.setVisible(True)

    def _insert_var(self, var: str) -> None:
        self._expansion_input.insertPlainText(f"{{{{{var}}}}}")
        self._expansion_input.setFocus()

    def _on_save(self) -> None:
        if not self.snippets_manager or not self._editor.isVisible():
            return
        trigger = self._trigger_input.text().strip()
        expansion = self._expansion_input.toPlainText().strip()
        category = self._category_input.text().strip()
        if not trigger:
            self._dirty_lbl.setText("Trigger phrase is required")
            return
        if len(trigger) > MAX_TRIGGER:
            self._dirty_lbl.setText(f"Trigger too long (max {MAX_TRIGGER} chars)")
            return
        if len(expansion) > MAX_EXPANSION:
            self._dirty_lbl.setText(f"Expansion too long (max {MAX_EXPANSION} chars)")
            return

        original = None if self._creating_new else self._selected
        if original and original != trigger:
            self.snippets_manager.delete(original)
        ok, msg = self.snippets_manager.set(trigger, expansion, category=category)
        if not ok:
            self._dirty_lbl.setText(msg)
            return

        self._selected = trigger
        self._creating_new = False
        self._dirty = False
        self._dirty_lbl.setText("")
        self._save_btn.setEnabled(False)
        self._cancel_btn.setVisible(False)
        self._delete_btn.setVisible(True)
        self._editor_title.setText("Edit snippet")
        self._reload_list()

    def _on_cancel(self) -> None:
        if not self._dirty:
            return
        if not self._confirm_discard():
            return
        self._load_editor(self._selected)

    def _confirm_discard(self) -> bool:
        from PySide6.QtWidgets import QMessageBox

        ret = QMessageBox.question(
            self,
            "Discard changes?",
            "You have unsaved changes to this snippet. Discard them?",
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        return ret == QMessageBox.StandardButton.Discard

    def _on_new(self) -> None:
        if self._dirty and not self._confirm_discard():
            return
        self._selected = "__new__"
        for card in self._cards.values():
            card.set_selected(False)
        self._load_editor("__new__")

    def _on_delete(self) -> None:
        if not self.snippets_manager or self._creating_new or not self._selected:
            return
        trig = self._selected
        if getattr(self, "_pending_delete", None) != trig:
            self._pending_delete = trig
            self._delete_btn.setText("Really delete?")
            QTimer.singleShot(3000, self._reset_delete)
            return
        self.snippets_manager.delete(trig)
        self._reset_delete()
        self._selected = None
        self._reload_list()
        self._load_editor(None)

    def _reset_delete(self) -> None:
        self._pending_delete = None
        self._delete_btn.setText("Delete")

    def _on_category(self, cat: str) -> None:
        if self._dirty and not self._confirm_discard():
            return
        self._category = cat
        self._reload_list()

    def _on_search(self, text: str) -> None:
        if self._dirty and not self._confirm_discard():
            return
        self._search = text.strip()
        self._reload_list()

    # ── Import / export ───────────────────────────────────────────────────

    def _on_export(self) -> None:
        if not self.snippets_manager:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export snippets", "rota-snippets.json", "JSON (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.snippets_manager.export_json())
        except Exception as exc:
            logger.error("snippets_export_failed", error=str(exc))

    def _on_import(self) -> None:
        if not self.snippets_manager:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Import snippets", "", "JSON (*.json)")
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as f:
                self.snippets_manager.import_json(f.read())
        except Exception as exc:
            logger.error("snippets_import_failed", error=str(exc))
        self._reload_list()

    # ── Public API (main_window calls refresh()) ──────────────────────────

    def refresh(self) -> None:
        """External refresh: rebuild list, keep selection when possible."""
        if self._selected not in self._all_entries():
            self._selected = None
            self._creating_new = False
            self._load_editor(None)
        self._reload_list()
