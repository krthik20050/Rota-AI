from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
)
from PyQt6.QtCore import Qt

class DebugWindow(QWidget):
    """Minimal dark-themed debug UI."""

    def __init__(self, on_start_clicked, on_stop_clicked, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rota Debug")
        self.resize(600, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #111111;
                color: #CCCCCC;
                font-family: 'Consolas', 'Courier New';
            }
            QLabel {
                font-weight: bold;
                color: #888888;
                margin-top: 10px;
            }
            QPlainTextEdit {
                background-color: #1A1A1A;
                border: 1px solid #333333;
                border-radius: 4px;
                color: #00FF00;
            }
            QPushButton {
                background-color: #333333;
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)

        self.state_label = QLabel("State: IDLE")
        self.session_label = QLabel("Session ID: -")
        root.addWidget(self.state_label)
        root.addWidget(self.session_label)

        button_row = QHBoxLayout()
        self.start_button = QPushButton("Start Recording")
        self.stop_button = QPushButton("Stop Recording")
        self.start_button.clicked.connect(on_start_clicked)
        self.stop_button.clicked.connect(on_stop_clicked)
        button_row.addWidget(self.start_button)
        button_row.addWidget(self.stop_button)
        root.addLayout(button_row)

        root.addWidget(QLabel("RAW TRANSCRIPTION"))
        self.raw_text = QPlainTextEdit()
        self.raw_text.setReadOnly(True)
        root.addWidget(self.raw_text)

        root.addWidget(QLabel("CLEANED TRANSCRIPTION"))
        self.cleaned_text = QPlainTextEdit()
        self.cleaned_text.setReadOnly(True)
        root.addWidget(self.cleaned_text)

        root.addWidget(QLabel("TIMINGS"))
        self.timings_text = QPlainTextEdit()
        self.timings_text.setReadOnly(True)
        self.timings_text.setMaximumHeight(100)
        root.addWidget(self.timings_text)

        root.addWidget(QLabel("LATEST LOGS"))
        self.logs_text = QPlainTextEdit()
        self.logs_text.setReadOnly(True)
        root.addWidget(self.logs_text)

    def update_state(self, state_value, session_id):
        self.state_label.setText(f"State: {state_value}")
        self.session_label.setText(f"Session ID: {session_id or '-'}")

    def update_text_results(self, raw_text, cleaned_text):
        self.raw_text.setPlainText(raw_text or "")
        self.cleaned_text.setPlainText(cleaned_text or "")

    def update_timings(self, timings):
        if not timings:
            self.timings_text.setPlainText("No timings yet.")
            return
        lines = [f"{key}: {value}" for key, value in timings.items()]
        self.timings_text.setPlainText("\n".join(lines))

    def update_logs(self, lines):
        self.logs_text.setPlainText("\n".join(lines))
