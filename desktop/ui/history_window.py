"""
Standalone history window for Rota AI.
Shows ALL history grouped by date, with working Transcript / Undo / Retry / Extract Audio.
"""
from datetime import datetime, date as Date, timezone
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QLineEdit, QLabel, QScrollArea, QMessageBox,
    QVBoxLayout, QHBoxLayout, QWidget
)
import pyperclip

from ui.components.history_item import HistoryItemWidget
from utils.window_effects import apply_blur


def _relative_date_label(d: Date) -> str:
    today = Date.today()
    delta = (today - d).days
    if delta == 0:
        return "Today"
    if delta == 1:
        return "Yesterday"
    return d.strftime("%B %d, %Y")


class HistoryWindow(QDialog):
    """Full history browser with search, date grouping, and all actions."""

    def __init__(self, history_manager, ai_processor=None, date_display="relative"):
        super().__init__()
        self.history_manager = history_manager
        self.ai_processor = ai_processor
        self.date_display = date_display
        self.setWindowTitle("History (Rota)")
        self.resize(780, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._init_ui()
        self._refresh_list()

    def _init_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #161618; color: #F0F0F2;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
            QLabel#Title { font-size: 22px; font-weight: 700; color: #F0F0F2; }
            QLineEdit#SearchInput {
                background-color: #1C1C1F; color: #F0F0F2;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px; padding: 11px 18px;
                font-size: 13px; font-family: 'Segoe UI', 'Inter';
            }
            QLineEdit#SearchInput:focus {
                border: 1px solid rgba(134, 239, 172, 0.25);
                background-color: #202023;
            }
            QScrollArea { background: transparent; border: none; }
            QWidget#ListContainer { background: transparent; }
            QLabel#EmptyState { color: #3A3A40; font-size: 14px; padding: 40px; }
            QLabel#DateHeader {
                color: #5A5A62; font-size: 11px; font-weight: 700;
                letter-spacing: 1.2px; padding: 4px 0;
                font-family: 'Segoe UI', sans-serif;
            }
            QScrollBar:vertical {
                background: transparent; width: 14px; margin: 6px 4px; border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.35); border-radius: 7px; min-height: 40px;
            }
            QScrollBar::handle:vertical:hover { background: rgba(255, 255, 255, 0.65); }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 36)
        layout.setSpacing(20)

        title = QLabel("History")
        title.setObjectName("Title")
        layout.addWidget(title)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchInput")
        self.search_input.setPlaceholderText("Search your dictations...")
        self.search_input.textChanged.connect(self._refresh_list)
        layout.addWidget(self.search_input)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        self.list_container = QWidget()
        self.list_container.setObjectName("ListContainer")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 12, 0)
        self.list_layout.setSpacing(8)

        self.scroll_area.setWidget(self.list_container)
        layout.addWidget(self.scroll_area, 1)

    def showEvent(self, event):
        super().showEvent(event)
        apply_blur(int(self.winId()))

    def _refresh_list(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        query = self.search_input.text().strip()
        entries = self.history_manager.get_entries(query if query else None)

        if not entries:
            empty = QLabel("No dictations found" if query else "Your history will appear here")
            empty.setObjectName("EmptyState")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_layout.addWidget(empty)
            self.list_layout.addStretch()
            return

        # Group by date
        current_date = None
        for entry_id, timestamp, raw, cleaned, is_prompt in entries:
            entry_date = self._parse_date(str(timestamp))
            date_key = entry_date or Date.min

            if date_key != current_date:
                current_date = date_key
                label_text = self._format_date_label(entry_date)
                date_hdr = QLabel(label_text.upper())
                date_hdr.setObjectName("DateHeader")
                if self.list_layout.count() > 0:
                    self.list_layout.addSpacing(8)
                self.list_layout.addWidget(date_hdr)

            item = HistoryItemWidget(entry_id, timestamp, raw, cleaned, is_prompt)
            item.copy_requested.connect(pyperclip.copy)
            item.copy_raw_requested.connect(pyperclip.copy)
            item.delete_requested.connect(self._handle_delete)
            item.retry_requested.connect(self._handle_retry)
            item.undo_requested.connect(self._handle_undo)
            item.extract_audio_requested.connect(self._handle_extract_audio)
            self.list_layout.addWidget(item)

        self.list_layout.addStretch()

    def _parse_date(self, timestamp: str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                dt_utc = datetime.strptime(timestamp.split(".")[0], fmt).replace(tzinfo=timezone.utc)
                return dt_utc.astimezone().date()
            except ValueError:
                continue
        return None

    def _format_date_label(self, d) -> str:
        if d is None:
            return "Unknown date"
        if self.date_display == "relative":
            return _relative_date_label(d)
        return d.strftime("%Y-%m-%d")

    def _handle_delete(self, entry_id: int):
        self.history_manager.delete_entry(entry_id)
        self._refresh_list()

    def _handle_undo(self, entry_id: int):
        row = self.history_manager.get_entry(entry_id)
        if row is None:
            return
        _, _, raw_text, _, _ = row
        self.history_manager.update_entry(entry_id, raw_text)
        self._refresh_list()

    def _handle_retry(self, entry_id: int):
        row = self.history_manager.get_entry(entry_id)
        if row is None:
            return
        _, _, raw_text, _, _ = row

        if self.ai_processor is None:
            QMessageBox.information(
                self, "Retry",
                "Smart formatting engine is not available. Enable Smart Formatting in Settings and restart."
            )
            return

        try:
            cleaned = self.ai_processor.process_text(raw_text)
            self.history_manager.update_entry(entry_id, cleaned)
            self._refresh_list()
        except Exception as exc:
            QMessageBox.warning(self, "Retry failed", f"Formatting failed:\n{exc}")

    def _handle_extract_audio(self, entry_id: int):
        QMessageBox.information(
            self, "Extract Audio",
            "Audio is not stored for past recordings.\n\n"
            "Rota stores text transcriptions only. Audio extraction is not available."
        )

    def _copy_text(self, text):
        if text:
            pyperclip.copy(text)
