"""Onboarding step builders for Rota AI wizard.

Steps:
  1 — Welcome + Hotkey (merged — the only setup you need)
  2 — Ready (you're all set)

API Keys and Model configuration are moved to Settings.
"""
from __future__ import annotations

import threading

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# ── Step 1: Welcome + Hotkey (merged) ──────────────────────────────


def build_step_welcome(dialog) -> QWidget:
    """Build the merged Welcome + Hotkey step.

    Combines the welcome screen (title, features, privacy notice) with
    the hotkey picker so the user completes both in a single step.
    """
    w = QWidget()
    w.setStyleSheet("background: transparent;")
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(8)

    num = QLabel("STEP 1 OF 2")
    num.setObjectName("StepNum")
    lay.addWidget(num)
    lay.addSpacing(2)

    title = QLabel("Meet Rota")
    title.setObjectName("StepTitle")
    lay.addWidget(title)
    lay.addSpacing(8)

    body = QLabel(
        "Rota turns your voice into clean, formatted text instantly. "
        "Press your hotkey, speak naturally, and your words appear "
        "where you need them."
    )
    body.setObjectName("StepBody")
    body.setWordWrap(True)
    lay.addWidget(body)
    lay.addSpacing(8)

    # Feature rows — compact
    features = [
        ("🎙️", "Voice Dictation", "Works in any app, any text field"),
        ("✨", "Smart Formatting", "Cloud or local models polish your words"),
        ("⚡", "Snippets", "Voice-trigger frequently used text"),
    ]
    for icon, title_txt, sub in features:
        row = QFrame()
        row.setObjectName("FeatureRow")
        rl = QHBoxLayout(row)
        rl.setContentsMargins(12, 7, 12, 7)
        rl.setSpacing(10)
        ic = QLabel(icon)
        ic.setObjectName("FeatureIcon")
        ic.setFixedWidth(28)
        rl.addWidget(ic)
        txt = QVBoxLayout()
        txt.setSpacing(1)
        t = QLabel(title_txt)
        t.setObjectName("FeatureTitle")
        s = QLabel(sub)
        s.setObjectName("FeatureSub")
        txt.addWidget(t)
        txt.addWidget(s)
        rl.addLayout(txt, 1)
        lay.addWidget(row)

    lay.addSpacing(8)

    # ── Hotkey section ──────────────────────────────────────────────
    hk_label = QLabel("Your Activation Key")
    hk_label.setObjectName("SectionTitle")
    hk_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #E8E8EA;")
    lay.addWidget(hk_label)

    current_hk = dialog._config.get("hotkey", "tab").lower() if dialog._config else "tab"
    dialog._hotkey_pill = QLabel(_hotkey_display_name(current_hk))
    dialog._hotkey_pill.setObjectName("HotkeyPill")
    dialog._hotkey_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
    dialog._hotkey_pill.setFixedHeight(44)
    lay.addWidget(dialog._hotkey_pill)

    btn_row = QHBoxLayout()
    btn_row.setSpacing(8)

    dialog._hotkey_record_btn = QPushButton("🎤 Record Hotkey")
    dialog._hotkey_record_btn.setObjectName("RecordHotkeyBtn")
    dialog._hotkey_record_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    dialog._hotkey_record_btn.setFixedHeight(38)
    dialog._hotkey_record_btn.clicked.connect(lambda: _start_hotkey_capture(dialog))
    btn_row.addWidget(dialog._hotkey_record_btn)

    dialog._hotkey_cancel_btn = QPushButton("Cancel")
    dialog._hotkey_cancel_btn.setObjectName("CancelBtn")
    dialog._hotkey_cancel_btn.setFixedHeight(38)
    dialog._hotkey_cancel_btn.setVisible(False)
    dialog._hotkey_cancel_btn.clicked.connect(lambda: _cancel_hotkey_capture(dialog))
    btn_row.addWidget(dialog._hotkey_cancel_btn)

    lay.addLayout(btn_row)

    dialog._hotkey_status = QLabel("")
    dialog._hotkey_status.setObjectName("FieldHint")
    dialog._hotkey_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lay.addWidget(dialog._hotkey_status)

    lay.addSpacing(4)

    hk_note = QLabel(
        "Works globally across all your apps. "
        "You can change this anytime in Settings."
    )
    hk_note.setObjectName("StepBody")
    hk_note.setWordWrap(True)
    hk_note.setStyleSheet("font-size: 11px; color: #5A5A60;")
    lay.addWidget(hk_note)

    lay.addSpacing(4)

    # ── Privacy notice ──────────────────────────────────────────────
    privacy_frame = QFrame()
    privacy_frame.setObjectName("FeatureRow")
    privacy_frame.setStyleSheet(
        "QFrame#FeatureRow { background: rgba(251,191,36,8); "
        "border: 1px solid rgba(251,191,36,25); border-radius: 8px; }"
    )
    pl = QHBoxLayout(privacy_frame)
    pl.setContentsMargins(10, 6, 10, 6)
    pl.setSpacing(8)
    icon_l = QLabel("🔒")
    icon_l.setObjectName("FeatureIcon")
    icon_l.setFixedWidth(24)
    pl.addWidget(icon_l)
    priv_txt = QVBoxLayout()
    priv_txt.setSpacing(1)
    priv_title = QLabel("Privacy Notice")
    priv_title.setObjectName("FeatureTitle")
    priv_title.setStyleSheet("color: rgba(251,191,36,200); font-size: 11px;")
    priv_body = QLabel(
        "With cloud keys: audio goes to Groq, text to Gemini. "
        "Without keys: everything runs locally. No data is sold."
    )
    priv_body.setObjectName("FeatureSub")
    priv_body.setWordWrap(True)
    priv_body.setStyleSheet("color: rgba(160,160,165,200); font-size: 10px;")
    priv_txt.addWidget(priv_title)
    priv_txt.addWidget(priv_body)
    pl.addLayout(priv_txt, 1)
    lay.addWidget(privacy_frame)

    lay.addStretch()
    return w


# ── Step 2: Ready ──────────────────────────────────────────────────


def build_step_ready(dialog) -> QWidget:
    """Build the final 'You're all set!' step."""
    w = QWidget()
    w.setStyleSheet("background: transparent;")
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(12)

    num = QLabel("STEP 2 OF 2")
    num.setObjectName("StepNum")
    lay.addWidget(num)
    lay.addSpacing(4)

    title = QLabel("You're all set!")
    title.setObjectName("StepTitle")
    lay.addWidget(title)
    lay.addSpacing(12)

    body = QLabel(
        "Click any text field, press your hotkey, and start speaking.\n\n"
        "Your voice will be transcribed and typed instantly, "
        "with Smart Formatting for perfectly polished output.\n\n"
        "Cloud transcription, API keys, and model settings "
        "can be configured in the Settings panel anytime."
    )
    body.setObjectName("StepBody")
    body.setWordWrap(True)
    lay.addWidget(body)

    lay.addStretch()
    return w
# ── Hotkey capture helpers ────────────────────────────────────────


def _hotkey_display_name(hotkey_str: str) -> str:
    """Convert internal hotkey string to user-friendly display name.

    Examples:
        'tab' → 'Tab'
        'ctrl+shift+k' → 'Ctrl+Shift+K'
        'f9' → 'F9'
        'alt+space' → 'Alt+Space'
    """
    if not hotkey_str:
        return "Tab"
    parts = hotkey_str.lower().split("+")
    display_parts = []
    for p in parts:
        if p in ("ctrl", "shift", "alt", "meta"):
            display_parts.append(p.capitalize())
        elif p.startswith("f") and p[1:].isdigit():
            display_parts.append(p.upper())
        elif len(p) == 1:
            display_parts.append(p.upper())
        else:
            display_parts.append(p.capitalize())
    return "+".join(display_parts) if display_parts else hotkey_str


def _start_hotkey_capture(dialog):
    """Start hotkey capture mode in a background thread."""
    dialog._hotkey_record_btn.setEnabled(False)
    dialog._hotkey_record_btn.setText("Listening…")
    dialog._hotkey_cancel_btn.setVisible(True)
    dialog._hotkey_status.setText("Press your desired key combination now")
    dialog._hotkey_status.setObjectName("StatusOk")

    def _capture():
        result = None
        error_msg = ""
        try:
            from plat import get_hotkey_handler

            HotkeyHandlerClass = get_hotkey_handler()
            result = HotkeyHandlerClass.capture_hotkey(timeout=8.0)
        except Exception as exc:
            error_msg = str(exc)

        def _apply_result():
            if getattr(dialog, "_closing", False):
                return
            try:
                if error_msg:
                    dialog._hotkey_status.setText(f"Error: {error_msg}")
                    dialog._hotkey_status.setObjectName("StatusError")
                elif result:
                    dialog._config.set("hotkey", result)
                    dialog._hotkey_pill.setText(_hotkey_display_name(result))
                    dialog._hotkey_status.setText(f"Set to: {_hotkey_display_name(result)}")
                    dialog._hotkey_status.setObjectName("StatusOk")
                else:
                    dialog._hotkey_status.setText("Cancelled. Try again or use Settings to change.")
                    dialog._hotkey_status.setObjectName("FieldHint")
                dialog._hotkey_record_btn.setEnabled(True)
                dialog._hotkey_record_btn.setText("🎤 Record Hotkey")
                dialog._hotkey_cancel_btn.setVisible(False)
            except RuntimeError:
                pass  # widget already destroyed

        QTimer.singleShot(0, _apply_result)

    t = threading.Thread(target=_capture, daemon=True)
    t.start()


def _cancel_hotkey_capture(dialog):
    """Cancel ongoing hotkey capture."""
    dialog._hotkey_record_btn.setEnabled(True)
    dialog._hotkey_record_btn.setText("🎤 Record Hotkey")
    dialog._hotkey_cancel_btn.setVisible(False)
    dialog._hotkey_status.setText("Cancelled. Try again or use Settings to change.")
    dialog._hotkey_status.setObjectName("FieldHint")
