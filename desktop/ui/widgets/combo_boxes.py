"""Reusable combo box widgets shared between settings_window and _settings_sections."""
from PyQt6.QtWidgets import QComboBox


class SmartComboBox(QComboBox):
    """Combo box that shows '(recommended)' hint only while dropdown is open."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._recommended_idx = -1
        self._base_texts: list[str] = []

    def add_option(self, text: str, data, *, recommended: bool = False):
        idx = self.count()
        self.addItem(text, data)
        self._base_texts.append(text)
        if recommended:
            self._recommended_idx = idx

    def showPopup(self):
        if self._recommended_idx >= 0:
            self.setItemText(
                self._recommended_idx,
                self._base_texts[self._recommended_idx] + "  (recommended)"
            )
        super().showPopup()

    def hidePopup(self):
        if self._recommended_idx >= 0:
            self.setItemText(
                self._recommended_idx,
                self._base_texts[self._recommended_idx]
            )
        super().hidePopup()


class NonScrollComboBox(SmartComboBox):
    """SmartComboBox that ignores mouse wheel — prevents accidental changes while scrolling."""

    def wheelEvent(self, event):
        event.ignore()
