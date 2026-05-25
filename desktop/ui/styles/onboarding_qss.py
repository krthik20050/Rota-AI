from __future__ import annotations

_BASE = "#141918"
_CARD = "#191E1C"
_BORDER = "rgba(255,255,255,6)"
_ACCENT = "#86EFAC"
_TEXT_P = "#F0F0F2"
_TEXT_S = "#A0A0A5"
_TEXT_MUT = "#5A5A60"
_TEXT_DIM = "#3A3A40"
_ERROR = "#F87171"
_SERIF = "'Georgia','Times New Roman',serif"
_BODY = "'Segoe UI','Inter',sans-serif"
_MONO = "'Courier New','Consolas',monospace"

ONBOARDING_QSS = f"""
QDialog {{ background: transparent; }}
QFrame#OBContainer {{
    background: {_BASE}; border-radius: 20px; border: 1px solid {_BORDER};
}}
QLabel#StepNum {{
    color: {_ACCENT}; font-size: 11px; font-weight: 600;
    letter-spacing: 1.8px; font-family: {_BODY}; background: transparent;
}}
QLabel#StepTitle {{
    color: {_TEXT_P}; font-size: 26px; font-weight: 700;
    font-family: {_SERIF}; background: transparent;
}}
QLabel#StepBody {{
    color: {_TEXT_S}; font-size: 13px; font-family: {_BODY}; background: transparent;
}}
QLabel#FieldLabel {{
    color: {_TEXT_S}; font-size: 12px; font-weight: 600;
    font-family: {_BODY}; background: transparent;
}}
QLabel#FieldHint {{
    color: {_TEXT_MUT}; font-size: 11px; font-family: {_BODY}; background: transparent;
}}
QLabel#StatusLabel {{
    color: {_TEXT_MUT}; font-size: 12px; font-family: {_BODY}; background: transparent;
}}
QLabel#StatusOk  {{ color: {_ACCENT}; font-size: 12px; font-family: {_BODY}; background: transparent; }}
QLabel#StatusErr {{ color: {_ERROR};  font-size: 12px; font-family: {_BODY}; background: transparent; }}
QLabel#HotkeyPill {{
    color: {_ACCENT}; background: rgba(134,239,172,12);
    border: 1px solid rgba(134,239,172,30); border-radius: 8px;
    font-size: 20px; font-weight: 700; font-family: {_MONO}; padding: 8px 24px;
}}
QFrame#FeatureRow {{
    background: {_CARD}; border-radius: 12px; border: 1px solid {_BORDER};
}}
QLabel#FeatureIcon {{ font-size: 26px; background: transparent; }}
QLabel#FeatureTitle {{
    color: {_TEXT_P}; font-size: 13px; font-weight: 600;
    font-family: {_BODY}; background: transparent;
}}
QLabel#FeatureSub {{
    color: {_TEXT_MUT}; font-size: 11px; font-family: {_BODY}; background: transparent;
}}
QLineEdit#ApiInput {{
    background: rgba(255,255,255,5); border: 1px solid {_BORDER};
    border-radius: 8px; color: {_TEXT_P}; font-size: 13px;
    font-family: {_MONO}; padding: 9px 12px;
}}
QLineEdit#ApiInput:focus {{ border: 1px solid rgba(134,239,172,40); }}
QPushButton#GetKeyBtn {{
    background: rgba(255,255,255,5); color: {_TEXT_S};
    border: 1px solid {_BORDER}; border-radius: 8px;
    font-size: 12px; font-family: {_BODY}; padding: 9px 14px;
}}
QPushButton#GetKeyBtn:hover {{ background: rgba(255,255,255,9); color: {_TEXT_P}; }}
QComboBox#HotkeyCombo {{
    background: rgba(255,255,255,5); border: 1px solid {_BORDER};
    border-radius: 8px; color: {_TEXT_P}; font-size: 14px;
    font-weight: 600; font-family: {_MONO}; padding: 10px 14px;
}}
QComboBox#HotkeyCombo:focus {{ border: 1px solid rgba(134,239,172,40); }}
QComboBox#HotkeyCombo QAbstractItemView {{
    background: #1C1C1F; color: {_TEXT_P}; border: 1px solid rgba(255,255,255,10);
    border-radius: 8px; selection-background-color: rgba(134,239,172,15);
    selection-color: #fff; padding: 4px;
}}
QPushButton#DownloadBtn {{
    background: rgba(134,239,172,15); color: {_ACCENT};
    border: 1px solid rgba(134,239,172,30); border-radius: 8px;
    font-size: 13px; font-weight: 600; font-family: {_BODY}; padding: 10px 20px;
}}
QPushButton#DownloadBtn:hover {{ background: rgba(134,239,172,25); }}
QPushButton#DownloadBtn:disabled {{ color: {_TEXT_MUT}; border-color: {_BORDER}; background: rgba(255,255,255,3); }}
QPushButton#NextBtn {{
    background: {_ACCENT}; color: #0A1A0A; border: none; border-radius: 10px;
    font-size: 14px; font-weight: 700; font-family: {_BODY}; padding: 12px 32px;
}}
QPushButton#NextBtn:hover {{ background: #A3F4BF; }}
QPushButton#BackBtn {{
    background: rgba(255,255,255,5); color: {_TEXT_S};
    border: 1px solid {_BORDER}; border-radius: 10px;
    font-size: 13px; font-family: {_BODY}; padding: 12px 24px;
}}
QPushButton#BackBtn:hover {{ background: rgba(255,255,255,9); color: {_TEXT_P}; }}
QPushButton#SkipBtn {{
    background: transparent; color: {_TEXT_MUT}; border: none;
    font-size: 12px; font-family: {_BODY}; padding: 4px 8px;
}}
QPushButton#SkipBtn:hover {{ color: {_TEXT_S}; }}
QFrame#DotActive   {{ background: {_ACCENT}; border-radius: 4px; }}
QFrame#DotInactive {{ background: rgba(255,255,255,18); border-radius: 3px; }}
QPushButton#WindowCtrlBtn {{
    background: transparent; color: {_TEXT_MUT}; border: none;
    font-size: 14px; font-family: {_BODY}; padding: 0px;
    border-radius: 6px;
}}
QPushButton#WindowCtrlBtn:hover {{ background: rgba(255,255,255,8); color: {_TEXT_P}; }}
QPushButton#WindowCloseBtn {{
    background: transparent; color: {_TEXT_MUT}; border: none;
    font-size: 13px; font-family: {_BODY}; padding: 0px;
    border-radius: 6px;
}}
QPushButton#WindowCloseBtn:hover {{ background: rgba(239,68,68,200); color: #fff; }}
"""
