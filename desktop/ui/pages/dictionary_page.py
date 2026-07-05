from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

_DICT_PATH = Path(__file__).parent.parent.parent / "data" / "dictionary.json"


class DictionaryPage(QWidget):
    def __init__(self, personal_dict=None, parent=None):
        super().__init__(parent)
        self.personal_dict = personal_dict
        self._setup_ui()

    def _setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(16)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)
        title_row.setAlignment(Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignVCenter)
        title = QLabel("Dictionary")
        title.setObjectName("PageTitle")
        title_row.addWidget(title)
        self._dict_count_lbl = QLabel("0 words")
        self._dict_count_lbl.setObjectName("DictCountBadge")
        title_row.addWidget(self._dict_count_lbl)
        title_row.addStretch()
        lay.addLayout(title_row)

        subtitle = QLabel("Words Rota will always recognize correctly (names, tech terms, places).")
        subtitle.setObjectName("Subtitle")
        lay.addWidget(subtitle)

        # ── Controls row: search, sort toggle, add ──
        self._sort_newest = True  # default: newest first
        controls_row = QHBoxLayout()
        controls_row.setSpacing(8)

        self._dict_search_input = QLineEdit()
        self._dict_search_input.setObjectName("DictSearchInput")
        self._dict_search_input.setPlaceholderText("Search dictionary...")
        self._dict_search_input.textChanged.connect(self._dict_refresh)
        controls_row.addWidget(self._dict_search_input, 1)

        self._sort_btn = QPushButton("⬇ Newest")
        self._sort_btn.setObjectName("SortToggleBtn")
        self._sort_btn.setFixedHeight(34)
        self._sort_btn.setFixedWidth(90)
        self._sort_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._sort_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._sort_btn.clicked.connect(self._toggle_sort)
        controls_row.addWidget(self._sort_btn)

        lay.addLayout(controls_row)

        inputs_row = QHBoxLayout()
        inputs_row.setSpacing(12)
        self._dict_search_input = QLineEdit()
        self._dict_search_input.setObjectName("DictSearchInput")
        self._dict_search_input.setPlaceholderText("Search dictionary...")
        self._dict_search_input.textChanged.connect(self._dict_refresh)
        inputs_row.addWidget(self._dict_search_input, 1)
        self._dict_input = QLineEdit()
        self._dict_input.setObjectName("DictInput")
        self._dict_input.setPlaceholderText("Add a word or phrase...")
        self._dict_input.returnPressed.connect(self._dict_add_word)
        inputs_row.addWidget(self._dict_input, 1)
        add_btn = QPushButton("Add")
        add_btn.setObjectName("AddWordBtn")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._dict_add_word)
        inputs_row.addWidget(add_btn)
        lay.addLayout(inputs_row)

        # Phonetic correction suggestion panel
        self._suggestion_panel = QFrame()
        self._suggestion_panel.setObjectName("PhoneticSuggestionPanel")
        self._suggestion_panel.setVisible(False)
        self._suggestion_panel.setStyleSheet(
            "QFrame#PhoneticSuggestionPanel {"
            "  background: rgba(134, 239, 172, 0.08);"
            "  border: 1px solid rgba(134, 239, 172, 0.2);"
            "  border-radius: 8px; padding: 10px;"
            "}"
        )
        suggestion_lay = QHBoxLayout(self._suggestion_panel)
        suggestion_lay.setContentsMargins(12, 8, 12, 8)
        suggestion_lay.setSpacing(8)
        self._suggestion_icon = QLabel("💡")
        self._suggestion_icon.setFixedWidth(24)
        suggestion_lay.addWidget(self._suggestion_icon)
        self._suggestion_text = QLabel("")
        self._suggestion_text.setWordWrap(True)
        self._suggestion_text.setStyleSheet(
            "color: #86EFAC; font-size: 12px; background: transparent;"
        )
        suggestion_lay.addWidget(self._suggestion_text, 1)
        self._suggestion_add_btn = QPushButton("Add to Dictionary")
        self._suggestion_add_btn.setObjectName("SuggestionAddBtn")
        self._suggestion_add_btn.setStyleSheet(
            "QPushButton {"
            "  background: rgba(134, 239, 172, 0.15);"
            "  color: #86EFAC; border: 1px solid rgba(134, 239, 172, 0.3);"
            "  border-radius: 6px; padding: 6px 14px; font-size: 11px;"
            "}"
            "QPushButton:hover { background: rgba(134, 239, 172, 0.25); }"
        )
        self._suggestion_add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._suggestion_add_btn.setVisible(False)
        suggestion_lay.addWidget(self._suggestion_add_btn)
        self._suggestion_dismiss_btn = QPushButton("✕")
        self._suggestion_dismiss_btn.setFixedSize(20, 20)
        self._suggestion_dismiss_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #5A5A60; border: none; font-size: 12px; }"
            "QPushButton:hover { color: #F87171; }"
        )
        self._suggestion_dismiss_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._suggestion_dismiss_btn.clicked.connect(
            lambda: self._suggestion_panel.setVisible(False)
        )
        suggestion_lay.addWidget(self._suggestion_dismiss_btn)
        lay.addWidget(self._suggestion_panel)

        self._dict_scroll = QScrollArea()
        self._dict_scroll.setWidgetResizable(True)
        self._dict_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._dict_scroll.setObjectName("HistoryScroll")
        self._dict_container = QWidget()
        self._dict_container.setObjectName("DictContainer")
        self._dict_container.setStyleSheet("background: transparent;")
        self._dict_container.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._dict_layout = QVBoxLayout(self._dict_container)
        self._dict_layout.setContentsMargins(0, 0, 0, 0)
        self._dict_layout.setSpacing(8)
        self._dict_scroll.setWidget(self._dict_container)
        lay.addWidget(self._dict_scroll, 1)

        self._dict_refresh()

    def _dict_load(self) -> dict:
        if self.personal_dict is not None:
            return {"vocabulary": self.personal_dict.get_terms()}
        try:
            with open(_DICT_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"vocabulary": [], "initial_prompt": ""}

    def _dict_save(self, data: dict) -> None:
        if self.personal_dict is not None:
            return
        try:
            words = data.get("vocabulary", [])
            if words:
                data["initial_prompt"] = (
                    "This is a dictation app. Key terms: " + ", ".join(words) + "."
                )
            else:
                data["initial_prompt"] = ""
            with open(_DICT_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def _create_word_chip(self, word):
        chip = QFrame()
        chip.setObjectName("WordChip")
        chip.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        lay = QHBoxLayout(chip)
        lay.setContentsMargins(10, 5, 10, 5)
        lay.setSpacing(6)
        lbl = QLabel(word)
        lbl.setObjectName("WordChipLabel")
        lay.addWidget(lbl)
        del_btn = QPushButton("✕")
        del_btn.setObjectName("WordChipDeleteBtn")
        del_btn.setFixedSize(14, 14)
        del_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setToolTip(f"Remove '{word}'")
        del_btn.clicked.connect(lambda _, w=word: self._dict_remove_word(w))
        lay.addWidget(del_btn)
        return chip

    def _toggle_sort(self):
        """Toggle between newest-first and oldest-first ordering."""
        self._sort_newest = not self._sort_newest
        self._sort_btn.setText("⬇ Newest" if self._sort_newest else "⬆ Oldest")
        self._dict_refresh()

    def _dict_refresh(self):
        data = self._dict_load()
        words = data.get("vocabulary", [])
        search_term = ""
        if hasattr(self, "_dict_search_input"):
            search_term = self._dict_search_input.text().strip().lower()
        # Filter
        filtered_words = (
            [w for w in words if search_term in w.lower()] if search_term else list(words)
        )
        # Sort: newest first = reverse insertion order (last added = most recent)
        if self._sort_newest:
            filtered_words.reverse()
        if hasattr(self, "_dict_count_lbl"):
            self._dict_count_lbl.setText(
                f"{len(filtered_words)} word{'s' if len(filtered_words) != 1 else ''}"
            )
        while self._dict_layout.count():
            item = self._dict_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        if not filtered_words:
            empty = QLabel(
                "No matching custom words found."
                if search_term
                else "No custom words yet. Add some above."
            )
            empty.setObjectName("Subtitle")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._dict_layout.addWidget(empty)
            return
        # Group words into rows of up to 5 chips for a grid-like layout
        row_widget = None
        row_layout = None
        for i, word in enumerate(filtered_words):
            if i % 5 == 0:
                row_widget = QWidget()
                row_widget.setStyleSheet("background: transparent;")
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(8)
                self._dict_layout.addWidget(row_widget)
            row_layout.addWidget(self._create_word_chip(word))

    def _dict_add_word(self):
        word = self._dict_input.text().strip()
        if not word:
            return
        if self.personal_dict is not None:
            self.personal_dict.add_term(word)
        else:
            data = self._dict_load()
            vocab = data.get("vocabulary", [])
            if word not in vocab:
                vocab.append(word)
                data["vocabulary"] = vocab
                self._dict_save(data)
        self._dict_input.clear()
        self._dict_refresh()

    def _dict_remove_word(self, word: str):
        if self.personal_dict is not None:
            self.personal_dict.remove_term(word)
        else:
            data = self._dict_load()
            vocab = data.get("vocabulary", [])
            if word in vocab:
                vocab.remove(word)
                data["vocabulary"] = vocab
                self._dict_save(data)
        self._dict_refresh()

    def refresh(self):
        self._dict_refresh()

    def show_phonetic_suggestion(self, spoken: str, suggested: str):
        """Show a suggestion to add a word to the dictionary after Whisper mishears it."""
        self._suggestion_text.setText(
            f"Did you mean <b>{suggested}</b>? Rota heard "
            f"\"{spoken}\" — adding '{suggested}' to the dictionary improves accuracy."
        )
        self._suggestion_add_btn.setVisible(True)
        self._suggestion_add_btn.clicked.disconnect()
        self._suggestion_add_btn.clicked.connect(lambda: self._add_suggestion_word(suggested))
        self._suggestion_panel.setVisible(True)

    def _add_suggestion_word(self, word: str):
        """Add a suggested word to the dictionary."""
        if self.personal_dict is not None:
            self.personal_dict.add_term(word)
        else:
            data = self._dict_load()
            vocab = data.get("vocabulary", [])
            if word not in vocab:
                vocab.append(word)
                data["vocabulary"] = vocab
                self._dict_save(data)
        self._suggestion_text.setText(f'✅ Added <b>"{word}"</b> to dictionary!')
        self._suggestion_add_btn.setVisible(False)
        self._dict_refresh()
