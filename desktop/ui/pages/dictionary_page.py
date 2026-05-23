from __future__ import annotations
import json
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QVBoxLayout, QWidget, QFrame,
)

from ui.components.flow_layout import FlowLayout

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

        self._dict_scroll = QScrollArea()
        self._dict_scroll.setWidgetResizable(True)
        self._dict_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._dict_scroll.setObjectName("HistoryScroll")
        self._dict_container = QWidget()
        self._dict_container.setObjectName("DictContainer")
        self._dict_container.setStyleSheet("background: transparent;")
        self._dict_flow_layout = FlowLayout(self._dict_container, hspacing=8, vspacing=8)
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
                data["initial_prompt"] = "This is a dictation app. Key terms: " + ", ".join(words) + "."
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

    def _dict_refresh(self):
        data = self._dict_load()
        words = data.get("vocabulary", [])
        search_term = ""
        if hasattr(self, "_dict_search_input"):
            search_term = self._dict_search_input.text().strip().lower()
        filtered_words = [w for w in words if search_term in w.lower()] if search_term else words
        if hasattr(self, "_dict_count_lbl"):
            self._dict_count_lbl.setText(f"{len(filtered_words)} word{'s' if len(filtered_words) != 1 else ''}")
        while self._dict_flow_layout.count():
            item = self._dict_flow_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        if not filtered_words:
            empty = QLabel("No matching custom words found." if search_term else "No custom words yet. Add some above.")
            empty.setObjectName("Subtitle")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._dict_flow_layout.addWidget(empty)
            return
        for word in filtered_words:
            self._dict_flow_layout.addWidget(self._create_word_chip(word))

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
