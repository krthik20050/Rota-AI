"""
QSS stylesheets for the Settings window.
"""

SETTINGS_QSS = """
    QDialog {
        background-color: #161618;
        color: #F0F0F2;
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }
    QLabel#Title {
        font-size: 22px;
        font-weight: 700;
        color: #F0F0F2;
        margin-bottom: 6px;
    }
    QLabel#Subtitle {
        font-size: 13px;
        color: #6B6B70;
        margin-bottom: 16px;
    }
    QLabel#SectionTitle {
        font-size: 12px;
        font-weight: 700;
        color: #86EFAC;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
    }
    QLabel#SectionDesc {
        font-size: 12px;
        color: #6B6B70;
        margin-bottom: 16px;
        margin-top: 2px;
    }
    QFrame#Section {
        background-color: #1C1C1F;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 8);
        margin-bottom: 16px;
    }
    QLabel {
        font-size: 13px;
        color: #A0A0A5;
    }
    QLabel#FieldLabel {
        font-size: 13px;
        color: #A0A0A5;
        font-weight: 500;
    }
    QLabel#FieldDesc {
        font-size: 11px;
        color: #4A4A52;
    }
    QLabel#FontPreview {
        font-size: 13px;
        color: #A0A0A5;
        background: #222226;
        border: 1px solid rgba(255,255,255,8);
        border-radius: 8px;
        padding: 10px 14px;
    }
    QFontComboBox {
        background-color: #222226;
        color: #F0F0F2;
        border: 1px solid rgba(255, 255, 255, 8);
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
    }
    QSpinBox {
        background-color: #222226;
        color: #F0F0F2;
        border: 1px solid rgba(255, 255, 255, 8);
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
    }
    QLineEdit, QComboBox {
        background-color: #222226;
        color: #F0F0F2;
        border: 1px solid rgba(255, 255, 255, 8);
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
        font-family: 'Segoe UI', 'Inter';
    }
    QLineEdit:focus, QComboBox:focus {
        border: 1px solid rgba(134, 239, 172, 30);
        background-color: #262629;
    }
    QComboBox::drop-down {
        border: 0px;
    }
    QComboBox QAbstractItemView {
        background-color: #1C1C1F;
        color: #F0F0F2;
        border: 1px solid rgba(255, 255, 255, 10);
        border-radius: 8px;
        selection-background-color: rgba(134, 239, 172, 15);
        selection-color: #FFFFFF;
        padding: 4px;
    }
    QCheckBox {
        color: #A0A0A5;
        font-size: 13px;
        spacing: 10px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 5px;
        border: 1.5px solid rgba(255, 255, 255, 15);
        background: #1C1C1F;
    }
    QCheckBox::indicator:checked {
        background: #86EFAC;
        border: 1.5px solid #86EFAC;
    }
    QCheckBox:hover::indicator {
        border: 1.5px solid rgba(255, 255, 255, 25);
    }
    QPushButton#SaveBtn {
        background-color: #86EFAC;
        color: #0A0A0B;
        border: none;
        border-radius: 10px;
        padding: 11px 24px;
        font-weight: 600;
        font-size: 13px;
    }
    QPushButton#SaveBtn:hover {
        background-color: #A7F3D0;
    }
    QPushButton#CancelBtn {
        background-color: rgba(255, 255, 255, 6);
        color: #A0A0A5;
        border: 1px solid rgba(255, 255, 255, 15);
        border-radius: 10px;
        padding: 11px 24px;
        font-weight: 600;
        font-size: 13px;
    }
    QPushButton#CancelBtn:hover {
        background-color: rgba(255, 255, 255, 12);
        color: #F0F0F2;
        border-color: rgba(255, 255, 255, 25);
    }
    QLabel#HotkeyPill {
        background-color: #222226;
        color: #F0F0F2;
        border: 1px solid rgba(255, 255, 255, 8);
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
        font-weight: 500;
    }
    QPushButton#RecordHotkeyBtn {
        background-color: rgba(255, 255, 255, 6);
        color: #A0A0A5;
        border: 1px solid rgba(255, 255, 255, 15);
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 13px;
        font-weight: 500;
    }
    QPushButton#RecordHotkeyBtn:hover {
        background-color: rgba(255, 255, 255, 12);
        color: #F0F0F2;
        border-color: rgba(255, 255, 255, 25);
    }
    QPushButton#RecordHotkeyBtn:disabled {
        color: #4A4A52;
        border-color: rgba(255, 255, 255, 6);
    }
    QScrollArea {
        background: transparent;
        border: none;
    }
    QScrollBar:vertical {
        background: transparent;
        width: 14px;
        margin: 6px 4px;
        border-radius: 7px;
    }
    QScrollBar::handle:vertical {
        background: rgba(255, 255, 255, 35);
        border-radius: 7px;
        min-height: 40px;
    }
    QScrollBar::handle:vertical:hover {
        background: rgba(255, 255, 255, 65);
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: transparent;
    }
"""

FOOTER_QSS = """
    QFrame#SettingsFooter {
        background-color: #161618;
        border-top: 1px solid rgba(255,255,255,8);
    }
"""
