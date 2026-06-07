"""
Rota AI — Snippets Page (Wispr Flow-inspired)
==============================================
Voice-triggered text expansion manager.
Clean list + inline editor design.
"""

from __future__ import annotations

import datetime
import re

import structlog
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.components.flow_layout import FlowLayout

logger = structlog.get_logger(__name__)

CLR_ACCENT = "#86EFAC"
CLR_BORDER = "rgba(255, 255, 255, 0.05)"
CLR_CARD = "#191E1C"
CLR_TEXT_MUTED = "#5A5A60"
CLR_TEXT_SECONDARY = "#A0A0A5"
CLR_TEXT_PRIMARY = "#F0F0F2"
CLR_ERROR = "#F87171"
CLR_WARNING = "#FBBF24"

_ROW_QSS_SELECTED = (
    f"QFrame#SnippetRow {{ border: 1px solid {CLR_ACCENT}; background: rgba(134, 239, 172, 0.12); border-radius: 12px; }}"
    f"QFrame#SnippetRow:hover {{ border: 1px solid {CLR_ACCENT}; background: rgba(134, 239, 172, 0.18); }}"
)
_ROW_QSS_DISABLED = (
    f"QFrame#SnippetRow {{ border: 1px solid {CLR_BORDER}; background: rgba(255,255,255,0.02); border-radius: 12px; }}"
    f"QFrame#SnippetRow:hover {{ border: 1px solid rgba(255, 255, 255, 0.08); background: rgba(255, 255, 255, 0.04); }}"
)
_ROW_QSS_NORMAL = (
    f"QFrame#SnippetRow {{ border: 1px solid {CLR_BORDER}; background: {CLR_CARD}; border-radius: 12px; }}"
    f"QFrame#SnippetRow:hover {{ border: 1px solid rgba(134, 239, 172, 0.35); background: rgba(255, 255, 255, 0.06); }}"
)


class SnippetsPage(QWidget):
    def __init__(self, snippets_manager, parent=None):
        super().__init__(parent)
        self.snippets_manager = snippets_manager
        self._selected_snippet_key = None
        self._snippet_search_text = ""
        self._setup_ui()

    def _setup_ui(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(24)

        # ── Left panel: snippet list ──────────────────────────────
        left_col = QFrame()
        left_col.setObjectName("SnippetLeftCol")
        left_col.setFixedWidth(280)
        left_lay = QVBoxLayout(left_col)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(12)

        title_lay = QVBoxLayout()
        title_lay.setSpacing(4)
        left_title = QLabel("Snippets")
        left_title.setObjectName("PageTitle")
        left_subtitle = QLabel("Voice-triggered text expansion.")
        left_subtitle.setObjectName("Subtitle")
        title_lay.addWidget(left_title)
        title_lay.addWidget(left_subtitle)
        left_lay.addLayout(title_lay)

        # Search
        self._snippet_search_input = QLineEdit()
        self._snippet_search_input.setObjectName("SnippetSearch")
        self._snippet_search_input.setPlaceholderText("Search snippets...")
        self._snippet_search_input.setFixedHeight(34)
        self._snippet_search_input.textChanged.connect(self._snippet_search_changed)
        left_lay.addWidget(self._snippet_search_input)

        # Category filter
        self._category_combo = QComboBox()
        self._category_combo.setObjectName("SnippetCategoryFilter")
        self._category_combo.addItem("All Categories", "__all__")
        self._category_combo.currentIndexChanged.connect(self._category_filter_changed)
        self._category_combo.setFixedHeight(30)
        left_lay.addWidget(self._category_combo)

        # Snippet list scroll
        self._snippet_scroll = QScrollArea()
        self._snippet_scroll.setWidgetResizable(True)
        self._snippet_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._snippet_scroll.setObjectName("SnippetScroll")
        self._snippet_container = QWidget()
        self._snippet_layout = QVBoxLayout(self._snippet_container)
        self._snippet_layout.setContentsMargins(0, 0, 10, 0)
        self._snippet_layout.setSpacing(6)
        self._snippet_scroll.setWidget(self._snippet_container)
        left_lay.addWidget(self._snippet_scroll, 1)

        # Add button
        add_btn = QPushButton("+ Add New Snippet")
        add_btn.setObjectName("SnippetActionBtn")
        add_btn.setFixedHeight(36)
        add_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._add_snippet_clicked)
        left_lay.addWidget(add_btn)

        # Secondary actions row
        sec_btn_lay = QHBoxLayout()
        sec_btn_lay.setSpacing(6)
        for label, slot in [
            ("Import", self._import_snippets_clicked),
            ("Export", self._export_snippets_clicked),
            ("Reset", self._reset_snippets_defaults),
        ]:
            btn = QPushButton(label)
            btn.setObjectName("SnippetSecBtn")
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(slot)
            sec_btn_lay.addWidget(btn, 1)
        left_lay.addLayout(sec_btn_lay)

        lay.addWidget(left_col)

        # ── Right panel: stacked (empty state / editor) ───────────
        self._snippet_stack = QStackedWidget()
        self._snippet_stack.setObjectName("SnippetStack")
        self._snippet_stack.addWidget(self._build_empty_state())
        self._snippet_stack.addWidget(self._build_editor())
        lay.addWidget(self._snippet_stack, 1)

        self._snippets_refresh()

    def _build_empty_state(self):
        """Clean empty state with centered content."""
        page = QWidget()
        empty_lay = QVBoxLayout(page)
        empty_lay.setContentsMargins(0, 0, 0, 0)
        empty_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("SnippetEmptyCard")
        card.setFixedWidth(320)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(36, 48, 36, 48)
        card_lay.setSpacing(16)
        card_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("⚡")
        icon.setObjectName("SnippetEmptyIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t = QLabel("Select a Snippet")
        t.setObjectName("EmptyTitle")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s = QLabel("Choose a trigger from the list on the left or create a new one to get started.")
        s.setObjectName("EmptySubtitle")
        s.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s.setWordWrap(True)
        card_lay.addWidget(icon)
        card_lay.addWidget(t)
        card_lay.addWidget(s)
        empty_lay.addWidget(card)
        return page

    def _build_editor(self):
        """Right-side editor panel for creating/editing snippets."""
        self._snippet_editor_page = QWidget()
        editor_lay = QVBoxLayout(self._snippet_editor_page)
        editor_lay.setContentsMargins(0, 0, 0, 0)
        editor_lay.setSpacing(16)

        editor_form = QFrame()
        editor_form.setObjectName("SnippetEditorForm")
        form_lay = QVBoxLayout(editor_form)
        form_lay.setContentsMargins(24, 24, 24, 24)
        form_lay.setSpacing(16)

        # Trigger
        trigger_lbl = QLabel("Spoken Trigger Phrase")
        trigger_lbl.setStyleSheet(f"color: {CLR_TEXT_SECONDARY}; font-size: 12px; font-weight: 600;")
        form_lay.addWidget(trigger_lbl)
        self._snippet_trigger_input = QLineEdit()
        self._snippet_trigger_input.setObjectName("SnippetTriggerInput")
        self._snippet_trigger_input.setPlaceholderText("e.g. email signature, cal link")
        form_lay.addWidget(self._snippet_trigger_input)

        # Expansion header with char counter
        exp_header = QHBoxLayout()
        exp_label = QLabel("Expanded Text")
        exp_label.setStyleSheet(f"color: {CLR_TEXT_SECONDARY}; font-size: 12px; font-weight: 600;")
        exp_header.addWidget(exp_label)
        exp_header.addStretch()
        self._snippet_char_counter = QLabel("0 / 4000")
        self._snippet_char_counter.setStyleSheet(f"color: {CLR_TEXT_MUTED}; font-size: 11px;")
        exp_header.addWidget(self._snippet_char_counter)
        form_lay.addLayout(exp_header)

        self._snippet_expansion_input = QTextEdit()
        self._snippet_expansion_input.setObjectName("SnippetExpansionInput")
        self._snippet_expansion_input.setPlaceholderText("The full text that will expand when you speak the trigger...")
        self._snippet_expansion_input.setMinimumHeight(140)
        form_lay.addWidget(self._snippet_expansion_input, 2)

        # Variable insert buttons
        var_label = QLabel("Insert Variable:")
        var_label.setStyleSheet(f"color: {CLR_TEXT_SECONDARY}; font-size: 11px;")
        form_lay.addWidget(var_label)

        var_container = QWidget()
        var_container.setStyleSheet("background: transparent;")
        var_flow = FlowLayout(var_container, hspacing=6, vspacing=6)
        var_flow.setContentsMargins(0, 0, 0, 0)
        for var in [
            "date", "time", "clipboard", "today", "cursor",
            "day", "month", "year", "datetime", "timestamp",
        ]:
            v_btn = QPushButton(f"{{{{{var}}}}}")
            v_btn.setObjectName("SnippetVarBtn")
            v_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            v_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            v_btn.clicked.connect(lambda _, v=var: self._insert_var_placeholder(v))
            var_flow.addWidget(v_btn)
        form_lay.addWidget(var_container)

        # Live preview
        preview_label = QLabel("Live Preview")
        preview_label.setStyleSheet(f"color: {CLR_TEXT_SECONDARY}; font-size: 12px; font-weight: 600;")
        form_lay.addWidget(preview_label)
        self._snippet_preview_widget = QLabel()
        self._snippet_preview_widget.setObjectName("SnippetLivePreview")
        self._snippet_preview_widget.setWordWrap(True)
        self._snippet_preview_widget.setStyleSheet(
            f"background: rgba(255, 255, 255, 0.04); border: 1px solid {CLR_BORDER}; "
            f"border-radius: 8px; padding: 12px; color: {CLR_TEXT_SECONDARY}; min-height: 60px;"
        )
        form_lay.addWidget(self._snippet_preview_widget, 1)
        self._snippet_expansion_input.textChanged.connect(self._update_snippet_live_preview)

        # Action buttons
        edit_btn_lay = QHBoxLayout()
        edit_btn_lay.setSpacing(8)

        self._snippet_delete_btn = QPushButton("Delete")
        self._snippet_delete_btn.setObjectName("SnippetDeleteBtn")
        self._snippet_delete_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._snippet_delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._snippet_delete_btn.clicked.connect(self._delete_snippet_clicked)

        self._snippet_dup_btn = QPushButton("Duplicate")
        self._snippet_dup_btn.setObjectName("SnippetSecBtn")
        self._snippet_dup_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._snippet_dup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._snippet_dup_btn.clicked.connect(self._duplicate_snippet_clicked)

        edit_btn_lay.addWidget(self._snippet_delete_btn)
        edit_btn_lay.addWidget(self._snippet_dup_btn)
        edit_btn_lay.addStretch()

        self._snippet_save_btn = QPushButton("Save  Ctrl+S")
        self._snippet_save_btn.setObjectName("SnippetSaveBtn")
        self._snippet_save_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._snippet_save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._snippet_save_btn.clicked.connect(self._save_snippet_clicked)
        edit_btn_lay.addWidget(self._snippet_save_btn)

        form_lay.addLayout(edit_btn_lay)
        editor_lay.addWidget(editor_form)

        # Ctrl+S shortcut
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self._snippet_editor_page)
        save_shortcut.activated.connect(self._save_snippet_clicked)
        return self._snippet_editor_page

    # ── Editor helpers ────────────────────────────────────────────

    def _insert_var_placeholder(self, var: str):
        self._snippet_expansion_input.insertPlainText(f"{{{{{var}}}}}")
        self._snippet_expansion_input.setFocus()

    def _update_snippet_live_preview(self):
        if not hasattr(self, "_snippet_expansion_input") or not hasattr(self, "_snippet_preview_widget"):
            return
        raw_text = self._snippet_expansion_input.toPlainText()
        now = datetime.datetime.now()
        preview = raw_text
        preview = preview.replace("{{date}}", now.strftime("%Y-%m-%d"))
        preview = preview.replace("{{time}}", now.strftime("%H:%M:%S"))
        preview = preview.replace("{{today}}", now.strftime("%A, %B %d, %Y"))
        preview = preview.replace("{{clipboard}}", "[Clipboard Content]")
        preview = preview.replace("{{cursor}}", "|")
        if not preview.strip():
            self._snippet_preview_widget.setText("Type in the expansion field to see the live rendered output...")
        else:
            self._snippet_preview_widget.setText(preview)
        if hasattr(self, "_snippet_char_counter"):
            char_count = len(raw_text)
            color = CLR_ERROR if char_count > 3800 else (CLR_WARNING if char_count > 3200 else CLR_TEXT_MUTED)
            self._snippet_char_counter.setText(f"{char_count} / 4000")
            self._snippet_char_counter.setStyleSheet(f"color: {color}; font-size: 11px;")

    # ── Snippet list ──────────────────────────────────────────────

    def _snippets_refresh(self):
        """Rebuild the snippet list from the manager."""
        while self._snippet_layout.count():
            item = self._snippet_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if self.snippets_manager is None:
            empty = QLabel("Manager not initialized.")
            empty.setObjectName("Subtitle")
            self._snippet_layout.addWidget(empty)
            self._snippet_layout.addStretch()
            self._snippet_stack.setCurrentIndex(0)
            return

        # Refresh category filter
        self._category_combo.blockSignals(True)
        current_cat = self._category_combo.currentData()
        self._category_combo.clear()
        self._category_combo.addItem("All Categories", "__all__")
        for cat in self.snippets_manager.all_categories():
            self._category_combo.addItem(cat, cat)
        idx = self._category_combo.findData(current_cat)
        self._category_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self._category_combo.blockSignals(False)

        selected_category = self._category_combo.currentData()
        all_status = self.snippets_manager.all_with_status()

        # Filter by category
        if selected_category and selected_category != "__all__":
            filtered = {}
            for trigger, (expansion, enabled) in all_status.items():
                cat = self.snippets_manager.get_category(trigger)
                if cat == "" and selected_category == "Uncategorized":
                    filtered[trigger] = (expansion, enabled)
                elif cat == selected_category:
                    filtered[trigger] = (expansion, enabled)
            all_status = filtered

        # Search filter
        search = self._snippet_search_text.strip().lower()
        if search:
            all_status = {k: v for k, v in all_status.items() if search in k.lower() or search in v[0].lower()}

        if not all_status:
            msg = "No matches." if search else "No snippets yet.\nClick '+ Add New Snippet' below."
            empty = QLabel(msg)
            empty.setObjectName("Subtitle")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._snippet_layout.addWidget(empty)
            self._snippet_layout.addStretch()
            self._snippet_stack.setCurrentIndex(0)
            return

        # Build rows — newest first (reversed from dict insertion order)
        items = list(all_status.items())
        for trigger, (expansion, enabled) in reversed(items):
            row = self._build_snippet_row(trigger, expansion, enabled)
            self._snippet_layout.addWidget(row)

        self._snippet_layout.addStretch()

        # Sync editor with selected snippet
        snippets = {k: v[0] for k, v in all_status.items()}
        if self._selected_snippet_key in snippets:
            self._show_snippet_in_editor(self._selected_snippet_key, snippets[self._selected_snippet_key])
        else:
            self._selected_snippet_key = None
            self._snippet_stack.setCurrentIndex(0)

    def _build_snippet_row(self, trigger, expansion, enabled):
        """Build a single snippet list row with icon, trigger, preview, toggle."""
        row = QFrame()
        row.setObjectName("SnippetRow")
        row.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        is_selected = self._selected_snippet_key == trigger
        if is_selected:
            row.setStyleSheet(_ROW_QSS_SELECTED)
        elif not enabled:
            row.setStyleSheet(_ROW_QSS_DISABLED)
        else:
            row.setStyleSheet(_ROW_QSS_NORMAL)

        h = QHBoxLayout(row)
        h.setContentsMargins(14, 12, 10, 12)
        h.setSpacing(10)

        # Icon
        trig_lower = trigger.lower()
        if "mail" in trig_lower or "email" in trig_lower:
            icon_char = "✉"
        elif "link" in trig_lower or "url" in trig_lower or "web" in trig_lower:
            icon_char = "🔗"
        elif "time" in trig_lower or "date" in trig_lower or "day" in trig_lower:
            icon_char = "🕒"
        else:
            icon_char = "📝"
        icon_lbl = QLabel(icon_char)
        icon_lbl.setObjectName("SnippetRowIcon")
        icon_lbl.setFixedWidth(16)
        if not enabled:
            icon_lbl.setStyleSheet("opacity: 0.4;")
        h.addWidget(icon_lbl)

        # Trigger + preview
        txt = QVBoxLayout()
        txt.setSpacing(3)
        trig_lbl = QLabel(trigger if trigger else "New Snippet")
        trig_lbl.setObjectName("SnippetRowTrigger")
        if not enabled:
            trig_lbl.setStyleSheet(f"color: {CLR_TEXT_MUTED}; text-decoration: line-through;")
        preview_text = expansion.replace("\n", " ").strip()
        if len(preview_text) > 42:
            preview_text = preview_text[:40] + "..."
        elif not preview_text:
            preview_text = "empty expansion"
        exp_lbl = QLabel(preview_text)
        exp_lbl.setObjectName("SnippetRowPreview")
        txt.addWidget(trig_lbl)
        txt.addWidget(exp_lbl)
        h.addLayout(txt, 1)

        # Variable badge
        vars_found = re.findall(r"\{\{([^}]+)\}\}", expansion)
        if vars_found:
            var_badge = QLabel(f"{len(vars_found)} VAR" + ("S" if len(vars_found) > 1 else ""))
            var_badge.setObjectName("SnippetVarBadge")
            h.addWidget(var_badge)

        # Toggle button
        tog = QPushButton("ON" if enabled else "OFF")
        tog.setCheckable(True)
        tog.setChecked(enabled)
        tog.setFixedSize(36, 20)
        tog.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        tog.setCursor(Qt.CursorShape.PointingHandCursor)
        tog.setStyleSheet(
            f"QPushButton {{ background: {'rgba(134,239,172,0.25)' if enabled else 'rgba(255,255,255,0.06)'}; "
            f"color: {CLR_ACCENT if enabled else CLR_TEXT_MUTED}; "
            f"border: 1px solid {'rgba(134,239,172,0.5)' if enabled else 'rgba(255,255,255,0.08)'}; "
            f"border-radius: 10px; font-size: 9px; font-weight: bold; padding: 0; }}"
            f"QPushButton:hover {{ background: {'rgba(134,239,172,0.35)' if enabled else 'rgba(255,255,255,0.1)'}; }}"
        )

        def make_toggler(trig):
            def _toggle_it(checked):
                if self.snippets_manager:
                    self.snippets_manager.toggle(trig)
                    self._snippets_refresh()
            return _toggle_it

        tog.clicked.connect(make_toggler(trigger))
        h.addWidget(tog)

        # Click to select
        row.setCursor(Qt.CursorShape.PointingHandCursor)
        row.mouseReleaseEvent = (lambda trig: lambda event: self._select_snippet(trig))(trigger)
        return row

    def _show_snippet_in_editor(self, trigger: str, expansion: str):
        """Load a snippet into the right-side editor."""
        self._snippet_stack.setCurrentIndex(1)
        self._snippet_trigger_input.setText(trigger)
        self._snippet_expansion_input.setHtml("")
        self._snippet_expansion_input.setPlainText(expansion)
        self._snippet_delete_btn.setVisible(True)
        self._snippet_dup_btn.setVisible(True)

    # ── Actions ───────────────────────────────────────────────────

    def _select_snippet(self, key):
        self._selected_snippet_key = key
        self._snippets_refresh()

    def _snippet_search_changed(self, text: str):
        self._snippet_search_text = text
        self._snippets_refresh()

    def _category_filter_changed(self, idx: int):
        self._snippets_refresh()

    def _duplicate_snippet_clicked(self):
        if not self._selected_snippet_key or not self.snippets_manager:
            return
        original = self._selected_snippet_key
        expansion = self.snippets_manager.all().get(original, "")
        new_key = f"copy of {original}"
        counter = 2
        base = new_key
        while new_key in self.snippets_manager.all():
            new_key = f"{base} {counter}"
            counter += 1
        self.snippets_manager.set(new_key, expansion)
        self._selected_snippet_key = new_key
        self._snippets_refresh()

    def _add_snippet_clicked(self):
        self._selected_snippet_key = ""
        self._snippet_stack.setCurrentIndex(1)
        self._snippet_trigger_input.clear()
        self._snippet_expansion_input.clear()
        self._snippet_delete_btn.setVisible(False)
        self._snippet_dup_btn.setVisible(False)
        self._snippet_trigger_input.setFocus()

    def _save_snippet_clicked(self):
        trigger = self._snippet_trigger_input.text().strip()
        expansion = self._snippet_expansion_input.toPlainText().strip()
        if not trigger:
            return
        if self.snippets_manager:
            if self._selected_snippet_key and self._selected_snippet_key != trigger:
                self.snippets_manager.delete(self._selected_snippet_key)
            ok, msg = self.snippets_manager.set(trigger, expansion)
            if ok:
                self._selected_snippet_key = trigger
                self._snippets_refresh()

    def _delete_snippet_clicked(self):
        if self._selected_snippet_key and self.snippets_manager:
            self.snippets_manager.delete(self._selected_snippet_key)
            self._selected_snippet_key = None
            self._snippets_refresh()

    def _export_snippets_clicked(self):
        if not self.snippets_manager:
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Snippets", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                content = self.snippets_manager.export_json()
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                logger.error("snippets_export_failed", error=str(e))

    def _import_snippets_clicked(self):
        if not self.snippets_manager:
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Snippets", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                imported, skipped = self.snippets_manager.import_json(content)
                self._selected_snippet_key = None
                self._snippets_refresh()
            except Exception as e:
                logger.error("snippets_import_failed", error=str(e))

    def _reset_snippets_defaults(self):
        if not self.snippets_manager:
            return
        defaults = {
            "email signature": "Best regards,\n\nJohn Doe\nSenior Developer\n{{date}}",
            "meeting link": "Here is the link for our meeting: https://meet.google.com/abc-defg-hij",
            "thank you": "Thank you so much for your quick response! I will take a look and get back to you shortly.",
            "current date": "Today is {{today}}.",
            "clipboard paste": "Here is what I copied:\n\n{{clipboard}}",
        }
        for key, value in defaults.items():
            self.snippets_manager.set(key, value)
        self._selected_snippet_key = None
        self._snippets_refresh()

    def refresh(self):
        self._snippets_refresh()
