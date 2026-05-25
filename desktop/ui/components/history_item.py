"""
History item card — timeline aesthetic.
Time on LEFT, content on RIGHT, vertical three-dot menu for actions.
"""

from datetime import UTC, datetime

import pyperclip
from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class _TranscriptDialog(QDialog):
    """Modal dialog showing the raw transcript text."""

    def __init__(self, raw_text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Raw Transcript")
        self.resize(540, 320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet("""
            QDialog { background: #1A1A1D; color: #E8E8EA; }
            QTextEdit {
                background: #222226; color: #E8E8EA; border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px; padding: 14px; font-size: 14px;
                font-family: 'Courier New', monospace; line-height: 1.5;
            }
            QPushButton {
                background: rgba(255, 255, 255, 0.06); color: #A0A0A5;
                border: 1px solid rgba(255, 255, 255, 0.14); border-radius: 8px;
                padding: 8px 20px; font-size: 13px;
            }
            QPushButton:hover { background: rgba(255, 255, 255, 0.12); color: #F0F0F2; }
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)

        lbl = QLabel("Raw Transcript")
        lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #F0F0F2;")
        lay.addWidget(lbl)

        body = QTextEdit()
        body.setPlainText(raw_text or "(No raw transcript available)")
        body.setReadOnly(True)
        lay.addWidget(body, 1)

        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.clicked.connect(lambda: pyperclip.copy(raw_text or ""))
        lay.addWidget(copy_btn, 0, Qt.AlignmentFlag.AlignRight)


class HistoryItemWidget(QFrame):
    """Timeline-style card — HH:MM on left, transcription on right."""

    copy_requested = pyqtSignal(str)
    copy_raw_requested = pyqtSignal(str)
    delete_requested = pyqtSignal(int)
    retry_requested = pyqtSignal(int)
    transcript_requested = pyqtSignal(int)
    undo_requested = pyqtSignal(int)
    extract_audio_requested = pyqtSignal(int)

    def __init__(
        self,
        entry_id,
        timestamp,
        raw_text,
        cleaned_text,
        is_prompt,
        parent=None,
        *,
        is_latest=False,
    ):
        super().__init__(parent)
        self.entry_id = entry_id
        self.raw_text_value = raw_text or ""
        self.cleaned_text_value = cleaned_text or ""
        self._raw_visible = False
        self.setObjectName("HistoryItem")

        accent_border = "rgba(134, 239, 172, 0.22)" if is_latest else "rgba(255, 255, 255, 0.04)"
        hover_border = "rgba(134, 239, 172, 0.4)" if is_latest else "rgba(255, 255, 255, 0.08)"
        hover_bg = "#1E2420" if is_latest else "#1C1C1E"

        self.setStyleSheet(f"""
            QFrame#HistoryItem {{
                background-color: #191E1C;
                border-radius: 10px;
                border: 1px solid {accent_border};
            }}
            QFrame#HistoryItem:hover {{
                background-color: {hover_bg};
                border: 1px solid {hover_border};
            }}
            QFrame#TimeCol {{ background: transparent; border: none; }}
            QLabel#TimeHHMM {{
                color: #86EFAC; font-size: 16px; font-weight: 700;
                font-family: 'Courier New', 'Consolas', monospace;
                background: transparent;
            }}
            QLabel#TimeAMPM {{
                color: #3A3A42; font-size: 11px; font-weight: 700;
                font-family: 'Courier New', 'Consolas', monospace;
                letter-spacing: 0.8px; background: transparent;
            }}
            QFrame#ContentCol {{ background: transparent; border: none; }}
            QLabel#CleanedText {{
                color: #E8E8EA; font-size: 15px; font-weight: 400;
                background: transparent;
            }}
            QLabel#RawText {{
                color: #4A4A52; font-size: 13px; font-style: italic;
                background: transparent;
            }}
            QPushButton#CopyBtn {{
                background-color: transparent; color: #5A5A62;
                border: 1px solid rgba(255, 255, 255, 0.07);
                border-radius: 5px; padding: 3px 10px;
                font-size: 12px; font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
            }}
            QPushButton#CopyBtn:hover {{
                background-color: rgba(255, 255, 255, 0.07); color: #CCCCCC;
                border: 1px solid rgba(255, 255, 255, 0.14);
            }}
            QPushButton#MenuBtn {{
                background-color: transparent; color: #3A3A42;
                border: none; border-radius: 5px;
                padding: 3px 8px; font-size: 15px; font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
                letter-spacing: 1px;
            }}
            QPushButton#MenuBtn:hover {{
                background-color: rgba(255, 255, 255, 0.08); color: #CCCCCC;
            }}
            QPushButton#ShowRawBtn {{
                background-color: transparent; color: #3A3A42;
                border: none; padding: 0; font-size: 10px;
                font-family: 'Segoe UI', sans-serif; text-align: left;
            }}
            QPushButton#ShowRawBtn:hover {{ color: #6A6A72; }}
            QLabel#PromptBadge {{
                color: #86EFAC; background-color: rgba(134, 239, 172, 0.1);
                border-radius: 4px; padding: 2px 8px;
                font-size: 10px; font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
            }}
        """)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # LEFT: time column
        time_col = QFrame()
        time_col.setObjectName("TimeCol")
        time_col.setFixedWidth(76)
        tc = QVBoxLayout(time_col)
        tc.setContentsMargins(14, 14, 6, 14)
        tc.setSpacing(1)
        tc.setAlignment(Qt.AlignmentFlag.AlignTop)

        hhmm, ampm = self._split_time(timestamp)
        hhmm_lbl = QLabel(hhmm)
        hhmm_lbl.setObjectName("TimeHHMM")
        tc.addWidget(hhmm_lbl)

        ampm_lbl = QLabel(ampm)
        ampm_lbl.setObjectName("TimeAMPM")
        tc.addWidget(ampm_lbl)
        tc.addStretch()
        outer.addWidget(time_col)

        # Separator
        sep = QFrame()
        sep.setFixedWidth(1)
        sep.setStyleSheet("background: rgba(255, 255, 255, 0.04); border: none; margin: 8px 0;")
        outer.addWidget(sep)

        # RIGHT: content
        content = QFrame()
        content.setObjectName("ContentCol")
        c = QVBoxLayout(content)
        c.setContentsMargins(14, 10, 14, 8)
        c.setSpacing(4)

        # Main text at TOP
        self.cleaned_label = QLabel(self.cleaned_text_value or "...")
        self.cleaned_label.setObjectName("CleanedText")
        self.cleaned_label.setWordWrap(True)
        c.addWidget(self.cleaned_label)

        # Raw toggle
        if self.raw_text_value:
            self._show_raw_btn = QPushButton("▸ Show raw")
            self._show_raw_btn.setObjectName("ShowRawBtn")
            self._show_raw_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._show_raw_btn.clicked.connect(self._toggle_raw)
            c.addWidget(self._show_raw_btn)

            self.raw_label = QLabel(self.raw_text_value)
            self.raw_label.setObjectName("RawText")
            self.raw_label.setWordWrap(True)
            self.raw_label.setVisible(False)
            c.addWidget(self.raw_label)
        else:
            self._show_raw_btn = None

        # Action row at BOTTOM
        meta = QHBoxLayout()
        meta.setSpacing(6)
        meta.setContentsMargins(0, 2, 0, 0)

        if is_prompt:
            badge = QLabel("COMMAND")
            badge.setObjectName("PromptBadge")
            meta.addWidget(badge)

        meta.addStretch()

        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setObjectName("CopyBtn")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self._emit_copy)
        meta.addWidget(self.copy_btn)

        # Vertical three-dot menu button (⋮ = top to bottom)
        self.menu_btn = QPushButton("⋮")
        self.menu_btn.setObjectName("MenuBtn")
        self.menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_btn.clicked.connect(self._show_menu)
        meta.addWidget(self.menu_btn)

        c.addLayout(meta)

        outer.addWidget(content, 1)

    def _split_time(self, timestamp) -> tuple[str, str]:
        text = str(timestamp)
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                dt_utc = datetime.strptime(text.split(".")[0], fmt).replace(tzinfo=UTC)
                dt_local = dt_utc.astimezone()
                return dt_local.strftime("%I:%M"), dt_local.strftime("%p")
            except ValueError:
                continue
        return text[:5], ""

    def _toggle_raw(self):
        self._raw_visible = not self._raw_visible
        self.raw_label.setVisible(self._raw_visible)
        self._show_raw_btn.setText("▾ Hide raw" if self._raw_visible else "▸ Show raw")

    def _show_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1C2320;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 4px;
                color: #E8E8EA;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
            }
            QMenu::item { padding: 7px 16px; border-radius: 5px; }
            QMenu::item:selected {
                background: rgba(134, 239, 172, 0.12); color: #F0F0F2;
            }
            QMenu::separator {
                height: 1px; background: rgba(255, 255, 255, 0.08); margin: 4px 8px;
            }
        """)

        act_copy = menu.addAction("Copy")
        act_copy_raw = menu.addAction("Copy Raw")
        menu.addSeparator()
        act_transcript = menu.addAction("Transcript")
        act_retry = menu.addAction("Retry")
        act_undo = menu.addAction("Undo Edit")
        act_extract = menu.addAction("Extract Audio")
        menu.addSeparator()
        act_delete = menu.addAction("Delete")

        chosen = menu.exec(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))

        if chosen == act_copy:
            self._emit_copy()
        elif chosen == act_copy_raw:
            pyperclip.copy(self.raw_text_value)
            self.copy_raw_requested.emit(self.raw_text_value)
            self._show_copy_toast("Copied raw ✓")
        elif chosen == act_delete:
            self.delete_requested.emit(self.entry_id)
        elif chosen == act_retry:
            self.retry_requested.emit(self.entry_id)
        elif chosen == act_transcript:
            self._show_transcript()
        elif chosen == act_undo:
            self.undo_requested.emit(self.entry_id)
        elif chosen == act_extract:
            self.extract_audio_requested.emit(self.entry_id)

    def _show_transcript(self):
        dlg = _TranscriptDialog(self.raw_text_value, self)
        dlg.exec()

    def _emit_copy(self):
        text = self.cleaned_text_value or self.raw_text_value
        pyperclip.copy(text)
        self.copy_requested.emit(text)
        self._show_copy_toast("Copied ✓")

    def _show_copy_toast(self, message: str = "Copied ✓"):
        """Flash the copy button with a brief 'Copied ✓' confirmation."""
        self.copy_btn.setText("Copied ✓")
        self.copy_btn.setStyleSheet(
            "QPushButton#CopyBtn {"
            "background-color: rgba(134, 239, 172, 0.15);"
            "color: #86EFAC;"
            "border: 1px solid rgba(134, 239, 172, 0.4);"
            "border-radius: 5px; padding: 3px 10px;"
            "font-size: 12px; font-weight: 700;"
            "font-family: 'Segoe UI', sans-serif;"
            "}"
        )
        effect = QGraphicsOpacityEffect(self.copy_btn)
        self.copy_btn.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", self.copy_btn)
        anim.setDuration(1200)
        anim.setKeyValueAt(0.0, 0.0)
        anim.setKeyValueAt(0.1, 1.0)
        anim.setKeyValueAt(0.7, 1.0)
        anim.setKeyValueAt(1.0, 0.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.finished.connect(self._reset_copy_btn)
        anim.start()
        self._copy_anim = anim

    def _reset_copy_btn(self):
        self.copy_btn.setText("Copy")
        self.copy_btn.setStyleSheet("")
        self.copy_btn.setGraphicsEffect(None)

    def update_cleaned_text(self, new_text: str):
        """Update the displayed cleaned text (after undo/retry)."""
        self.cleaned_text_value = new_text
        self.cleaned_label.setText(new_text or "...")
