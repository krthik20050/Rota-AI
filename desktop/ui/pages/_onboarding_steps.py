from __future__ import annotations

import os
import threading

from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

_HOTKEYS = [
    ("Tab", "tab"),
    ("F9", "f9"),
    ("F1", "f1"),
    ("F2", "f2"),
    ("F3", "f3"),
    ("F4", "f4"),
    ("F5", "f5"),
    ("F6", "f6"),
    ("F7", "f7"),
    ("F8", "f8"),
    ("F10", "f10"),
    ("F11", "f11"),
    ("F12", "f12"),
    ("Ctrl+Shift", "ctrl+shift"),
    ("Ctrl+Shift+R", "ctrl+shift+r"),
    ("Ctrl+Shift+D", "ctrl+shift+d"),
    ("Ctrl+Shift+V", "ctrl+shift+v"),
    ("Ctrl+Alt+Space", "ctrl+alt+space"),
    ("Alt+Space", "alt+space"),
    ("Alt+F9", "alt+f9"),
    ("Pause/Break", "pause"),
]


def _detect_best_model() -> str:
    """Detect the best Whisper model for this device based on available RAM and GPU.

    Returns one of: 'tiny', 'base.en', 'small.en', 'medium', 'large-v3'
    Priority: GPU VRAM > system RAM > CPU fallback
    """
    try:
        # Check for NVIDIA GPU with CUDA
        try:
            import torch

            if torch.cuda.is_available():
                vram_gb = torch.cuda.get_device_properties(0).total_mem / (1024**3)
                if vram_gb >= 10:
                    return "large-v3"
                elif vram_gb >= 6:
                    return "medium"
                elif vram_gb >= 3:
                    return "small.en"
                elif vram_gb >= 1:
                    return "base.en"
                else:
                    return "tiny"
        except Exception:
            pass

        # Check system RAM via /proc/meminfo (Linux) or psutil
        try:
            import psutil

            ram_gb = psutil.virtual_memory().total / (1024**3)
        except Exception:
            try:
                # Fallback: read /proc/meminfo directly
                with open("/proc/meminfo") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            ram_gb = int(line.split()[1]) / (1024**2)  # kB to GB
                            break
                    else:
                        ram_gb = 4  # conservative default
            except Exception:
                ram_gb = 4  # conservative default

        if ram_gb >= 16:
            return "medium"
        elif ram_gb >= 8:
            return "small.en"
        elif ram_gb >= 4:
            return "base.en"
        elif ram_gb >= 2:
            return "tiny"
        else:
            return "tiny"
    except Exception:
        return "base.en"  # safe default


def _is_model_cached(model_size: str) -> bool:
    """Check if a faster-whisper model is already in the local cache.

    faster-whisper stores models in ~/.cache/huggingface/hub/ under directories
    named models--Systran--faster-whisper-{model-size}
    Also checks ~/.cache/huggingface/ as a flat fallback.
    """
    import glob
    import os

    model_slug = model_size.lower().replace(".", "-").replace("_", "-")
    home = os.path.expanduser("~")

    # Possible cache locations
    cache_dirs = [
        os.path.join(home, ".cache", "huggingface", "hub"),
        os.path.join(home, ".cache", "huggingface"),
        os.path.join(home, ".cache", "ctranslate2"),
    ]

    # HF_HOME override
    hf_home = os.environ.get("HF_HOME", "")
    if hf_home:
        cache_dirs.insert(0, os.path.join(hf_home, "hub"))
        cache_dirs.insert(1, hf_home)

    for cache_dir in cache_dirs:
        if not os.path.isdir(cache_dir):
            continue
        # Pattern: models--Systran--faster-whisper-{model}/*
        pattern = os.path.join(cache_dir, f"models--Systran--faster-whisper-{model_slug}")
        matches = glob.glob(pattern)
        if matches:
            # Verify it has actual model files (not just an empty dir)
            for m in matches:
                snapshots = os.path.join(m, "snapshots")
                if os.path.isdir(snapshots):
                    snap_contents = os.listdir(snapshots)
                    if snap_contents:
                        # Check for model.bin or model.bin.gz
                        for snap in snap_contents:
                            snap_dir = os.path.join(snapshots, snap)
                            if any(
                                os.path.isfile(os.path.join(snap_dir, f))
                                for f in ["model.bin", "model.bin.gz", "config.json"]
                            ):
                                return True
                # Also check if the model files are directly in the dir
                if any(
                    os.path.isfile(os.path.join(m, f))
                    for f in ["model.bin", "model.bin.gz", "config.json"]
                ):
                    return True
        # Also search recursively for config.json with matching model name
        for root, _dirs, files in os.walk(cache_dir):
            if "config.json" in files:
                # Check if this looks like a whisper model by checking path
                if f"faster-whisper-{model_slug}" in root:
                    return True
            # Don't recurse too deep
            if root.count(os.sep) > cache_dir.count(os.sep) + 5:
                break
    return False


def build_step_welcome(dialog) -> QWidget:
    w = QWidget()
    w.setStyleSheet("background: transparent;")
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(12)

    num = QLabel("WELCOME")
    num.setObjectName("StepNum")
    lay.addWidget(num)
    lay.addSpacing(4)

    title = QLabel("Meet Rota")
    title.setObjectName("StepTitle")
    lay.addWidget(title)
    lay.addSpacing(16)

    body = QLabel(
        "Rota turns your voice into clean, formatted text instantly.\n\n"
        "Press your hotkey, speak naturally, and your words appear exactly "
        "where you need them. No typing. No copy-paste. Just speak."
    )
    body.setObjectName("StepBody")
    body.setWordWrap(True)
    lay.addWidget(body)
    lay.addSpacing(20)

    features = [
        ("🎙️", "Voice Dictation", "Works in any app, any text field"),
        ("✨", "Smart Formatting", "Cloud or local models polish your words"),
        ("⚡", "Snippets", "Voice-trigger frequently used text"),
    ]
    for icon, title_txt, sub in features:
        row = QFrame()
        row.setObjectName("FeatureRow")
        rl = QHBoxLayout(row)
        rl.setContentsMargins(14, 9, 14, 9)
        rl.setSpacing(12)
        ic = QLabel(icon)
        ic.setObjectName("FeatureIcon")
        ic.setFixedWidth(32)
        rl.addWidget(ic)
        txt = QVBoxLayout()
        txt.setSpacing(2)
        t = QLabel(title_txt)
        t.setObjectName("FeatureTitle")
        s = QLabel(sub)
        s.setObjectName("FeatureSub")
        txt.addWidget(t)
        txt.addWidget(s)
        rl.addLayout(txt, 1)
        lay.addWidget(row)

    lay.addSpacing(12)

    privacy_frame = QFrame()
    privacy_frame.setObjectName("FeatureRow")
    privacy_frame.setStyleSheet(
        "QFrame#FeatureRow { background: rgba(251,191,36,8); "
        "border: 1px solid rgba(251,191,36,25); border-radius: 10px; }"
    )
    pl = QHBoxLayout(privacy_frame)
    pl.setContentsMargins(12, 8, 12, 8)
    pl.setSpacing(10)
    icon_l = QLabel("🔒")
    icon_l.setObjectName("FeatureIcon")
    icon_l.setFixedWidth(28)
    pl.addWidget(icon_l)
    priv_txt = QVBoxLayout()
    priv_txt.setSpacing(2)
    priv_title = QLabel("Privacy Notice")
    priv_title.setObjectName("FeatureTitle")
    priv_title.setStyleSheet("color: rgba(251,191,36,200); font-size: 12px;")
    priv_body = QLabel(
        "When cloud keys are set: audio goes to Groq (transcription) and text "
        "to Gemini (formatting). Keys stay on your device. No data is sold. "
        "Without keys, everything runs locally — nothing leaves your machine."
    )
    priv_body.setObjectName("FeatureSub")
    priv_body.setWordWrap(True)
    priv_body.setStyleSheet("color: rgba(160,160,165,200); font-size: 11px;")
    priv_txt.addWidget(priv_title)
    priv_txt.addWidget(priv_body)
    pl.addLayout(priv_txt, 1)
    lay.addWidget(privacy_frame)

    lay.addStretch()
    return w


def build_step_api_keys(dialog) -> QWidget:
    w = QWidget()
    w.setStyleSheet("background: transparent;")
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(10)

    num = QLabel("STEP 1 OF 4")
    num.setObjectName("StepNum")
    lay.addWidget(num)
    lay.addSpacing(4)

    title = QLabel("Choose Your Setup")
    title.setObjectName("StepTitle")
    lay.addWidget(title)
    lay.addSpacing(8)

    body = QLabel("Pick how you want to use Rota AI. You can change this anytime in Settings.")
    body.setObjectName("StepBody")
    body.setWordWrap(True)
    lay.addWidget(body)
    lay.addSpacing(16)

    # ── Path A: Quick Start ──
    quick_btn = QPushButton("⚡ Quick Start (Recommended)")
    quick_btn.setObjectName("PathQuickBtn")
    quick_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    quick_btn.setFixedHeight(48)
    quick_btn.clicked.connect(lambda: _select_path(dialog, "quick"))
    lay.addWidget(quick_btn)

    quick_desc = QLabel(
        "Use cloud transcription and formatting with free-tier API keys. "
        "No keys needed to start — Rota will guide you through getting them."
    )
    quick_desc.setObjectName("PathDesc")
    quick_desc.setWordWrap(True)
    lay.addWidget(quick_desc)

    lay.addSpacing(12)

    # ── Path B: Custom API Keys ──
    custom_frame = QFrame()
    custom_frame.setObjectName("PathCustomFrame")
    custom_lay = QVBoxLayout(custom_frame)
    custom_lay.setContentsMargins(16, 12, 16, 12)
    custom_lay.setSpacing(8)

    custom_header = QHBoxLayout()
    custom_title = QLabel("🔧 Custom API Keys")
    custom_title.setObjectName("PathTitle")
    custom_header.addWidget(custom_title)
    custom_header.addStretch()
    custom_switch = QPushButton("Use Custom Keys")
    custom_switch.setObjectName("PathSwitchBtn")
    custom_switch.setCursor(Qt.CursorShape.PointingHandCursor)
    custom_switch.clicked.connect(lambda: _select_path(dialog, "custom"))
    custom_header.addWidget(custom_switch)
    custom_lay.addLayout(custom_header)

    custom_desc = QLabel(
        "Bring your own Gemini and/or Groq API keys for cloud transcription "
        "and text formatting. Keys are stored locally on your device."
    )
    custom_desc.setObjectName("PathDesc")
    custom_desc.setWordWrap(True)
    custom_lay.addWidget(custom_desc)

    # Key inputs (hidden by default, shown when "custom" is selected)
    dialog._api_keys_container = QWidget()
    api_form = QVBoxLayout(dialog._api_keys_container)
    api_form.setContentsMargins(0, 8, 0, 0)
    api_form.setSpacing(6)

    def _resolve_key(config_key: str, env_var: str) -> str:
        if dialog._config:
            v = dialog._config.get(config_key, "")
            if v:
                return v
        return os.environ.get(env_var, "")

    gem_lbl = QLabel("Gemini API Key")
    gem_lbl.setObjectName("FieldLabel")
    api_form.addWidget(gem_lbl)
    gem_hint = QLabel("aistudio.google.com → Get API Key   (starts with AIza…)")
    gem_hint.setObjectName("FieldHint")
    api_form.addWidget(gem_hint)
    gem_row = QHBoxLayout()
    gem_row.setSpacing(8)
    dialog._gemini_input = QLineEdit()
    dialog._gemini_input.setObjectName("ApiInput")
    dialog._gemini_input.setPlaceholderText("AIzaSy…")
    dialog._gemini_input.setEchoMode(QLineEdit.EchoMode.Password)
    dialog._gemini_input.setText(_resolve_key("gemini_api_key", "GEMINI_API_KEY"))
    gem_row.addWidget(dialog._gemini_input, 1)
    gem_open = QPushButton("Get Key →")
    gem_open.setObjectName("GetKeyBtn")
    gem_open.setCursor(Qt.CursorShape.PointingHandCursor)
    gem_open.clicked.connect(
        lambda: QDesktopServices.openUrl(QUrl("https://aistudio.google.com/app/apikey"))
    )
    gem_row.addWidget(gem_open)
    api_form.addLayout(gem_row)

    groq_lbl = QLabel("Groq API Key  (for cloud transcription)")
    groq_lbl.setObjectName("FieldLabel")
    api_form.addWidget(groq_lbl)
    groq_hint = QLabel("console.groq.com → API Keys   (starts with gsk_…)")
    groq_hint.setObjectName("FieldHint")
    api_form.addWidget(groq_hint)
    groq_row = QHBoxLayout()
    groq_row.setSpacing(8)
    dialog._groq_input = QLineEdit()
    dialog._groq_input.setObjectName("ApiInput")
    dialog._groq_input.setPlaceholderText("gsk_…")
    dialog._groq_input.setEchoMode(QLineEdit.EchoMode.Password)
    dialog._groq_input.setText(_resolve_key("groq_api_key", "GROQ_API_KEY"))
    groq_row.addWidget(dialog._groq_input, 1)
    groq_open = QPushButton("Get Key →")
    groq_open.setObjectName("GetKeyBtn")
    groq_open.setCursor(Qt.CursorShape.PointingHandCursor)
    groq_open.clicked.connect(
        lambda: QDesktopServices.openUrl(QUrl("https://console.groq.com/keys"))
    )
    groq_row.addWidget(groq_open)
    api_form.addLayout(groq_row)

    dialog._gemini_input.textChanged.connect(lambda: _select_path(dialog, "custom"))
    dialog._groq_input.textChanged.connect(lambda: _select_path(dialog, "custom"))

    dialog._api_keys_container.setVisible(False)
    custom_lay.addWidget(dialog._api_keys_container)

    dialog._api_status = QLabel("")
    dialog._api_status.setObjectName("StatusLabel")
    custom_lay.addWidget(dialog._api_status)

    lay.addWidget(custom_frame)

    # ── Path C: Local Only ──
    local_frame = QFrame()
    local_frame.setObjectName("PathLocalFrame")
    local_lay = QVBoxLayout(local_frame)
    local_lay.setContentsMargins(16, 10, 16, 10)
    local_row = QHBoxLayout()
    local_icon = QLabel("💻")
    local_icon.setObjectName("PathIcon")
    local_row.addWidget(local_icon)
    local_title = QLabel("Local Only (No Cloud)")
    local_title.setObjectName("PathTitle")
    local_row.addWidget(local_title)
    local_row.addStretch()
    local_switch = QPushButton("Go Local")
    local_switch.setObjectName("PathSwitchLocalBtn")
    local_switch.setCursor(Qt.CursorShape.PointingHandCursor)
    local_switch.clicked.connect(lambda: _select_path(dialog, "local"))
    local_row.addWidget(local_switch)
    local_lay.addLayout(local_row)
    local_desc = QLabel(
        "Everything runs on your device. No API keys, no internet required after "
        "model download. Privacy-first approach."
    )
    local_desc.setObjectName("PathDesc")
    local_desc.setWordWrap(True)
    local_lay.addWidget(local_desc)
    lay.addWidget(local_frame)

    lay.addStretch()
    return w


def _select_path(dialog, path: str):
    """Handle path selection in API keys step."""
    dialog._api_path = path
    if path == "quick":
        dialog._api_keys_container.setVisible(False)
        dialog._api_status.setText(
            "Quick Start selected. You'll be guided to get free API keys after setup."
        )
        dialog._api_status.setObjectName("StatusOk")
    elif path == "custom":
        dialog._api_keys_container.setVisible(True)
        dialog._api_status.setText("")
    elif path == "local":
        dialog._api_keys_container.setVisible(False)
        dialog._config.set("groq_api_key", "")
        dialog._config.set("gemini_api_key", "")
        dialog._api_status.setText("Local-only mode. No cloud transcription or formatting.")
        dialog._api_status.setObjectName("StatusOk")


def build_step_model(dialog) -> QWidget:
    w = QWidget()
    w.setStyleSheet("background: transparent;")
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(12)

    num = QLabel("STEP 2 OF 4")
    num.setObjectName("StepNum")
    lay.addWidget(num)
    lay.addSpacing(4)

    title = QLabel("Offline Fallback Model")
    title.setObjectName("StepTitle")
    lay.addWidget(title)
    lay.addSpacing(8)

    body = QLabel(
        "Rota uses Groq's cloud for transcription when online. "
        "A local Whisper model is downloaded as a fallback in case Groq goes down, "
        "your internet stops working, or you're offline. The best model for your "
        "device has been selected automatically. It downloads in the background "
        "while you continue setup — no waiting. You can always change it in Settings."
    )
    body.setObjectName("StepBody")
    body.setWordWrap(True)
    lay.addWidget(body)
    lay.addSpacing(14)

    model_lbl = QLabel("Model Size")
    model_lbl.setObjectName("FieldLabel")
    lay.addWidget(model_lbl)

    dialog._model_combo = QComboBox()
    dialog._model_combo.setObjectName("HotkeyCombo")
    models = [
        ("tiny (fastest, least accurate)", "tiny"),
        ("base.en (English, fast, recommended)", "base.en"),
        ("small.en (English, balanced)", "small.en"),
        ("medium (high accuracy, slower)", "medium"),
        ("large-v3 (best accuracy, ~3 GB)", "large-v3"),
    ]
    for label, data in models:
        dialog._model_combo.addItem(label, data)

    recommended = _detect_best_model()
    current = dialog._config.get("model_size", recommended) if dialog._config else recommended
    # Check if this model is already cached
    dialog._model_already_cached = _is_model_cached(current)
    idx = dialog._model_combo.findData(current)
    dialog._model_combo.setCurrentIndex(max(0, idx))
    lay.addWidget(dialog._model_combo)

    lay.addSpacing(8)

    dl_row = QHBoxLayout()
    dl_row.setSpacing(12)
    dialog._download_btn = QPushButton("Download Model")
    dialog._download_btn.setObjectName("DownloadBtn")
    dialog._download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    dialog._download_btn.clicked.connect(dialog._start_download)
    dl_row.addWidget(dialog._download_btn)
    dl_row.addStretch()

    dialog._download_status = QLabel("")
    dialog._download_status.setObjectName("StatusLabel")

    # Set initial status based on cache check
    if dialog._model_already_cached:
        dialog._download_status.setText("Model already downloaded on this device.")
        dialog._download_status.setObjectName("StatusOk")
        dialog._download_btn.setText("Already Downloaded")
        dialog._download_btn.setEnabled(False)
    else:
        dialog._download_status.setText("Will download in the background — you can continue setup")

    dl_row.addWidget(dialog._download_status)
    lay.addLayout(dl_row)

    lay.addSpacing(4)
    note = QLabel(
        "This is a fallback model — it downloads in the background so you don't have to wait. Groq cloud is used for transcription when online."
    )
    note.setObjectName("FieldHint")
    note.setWordWrap(True)
    lay.addWidget(note)

    lay.addStretch()
    return w


def build_step_hotkey(dialog) -> QWidget:
    w = QWidget()
    w.setStyleSheet("background: transparent;")
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(12)

    num = QLabel("STEP 3 OF 4")
    num.setObjectName("StepNum")
    lay.addWidget(num)
    lay.addSpacing(4)

    title = QLabel("Your Activation Key")
    title.setObjectName("StepTitle")
    lay.addWidget(title)
    lay.addSpacing(8)

    body = QLabel(
        "Press the button below, then press any key combination you want to use. "
        "It works globally across all your apps."
    )
    body.setObjectName("StepBody")
    body.setWordWrap(True)
    lay.addWidget(body)
    lay.addSpacing(20)

    # Hotkey pill display
    current_hk = dialog._config.get("hotkey", "tab").lower() if dialog._config else "tab"
    dialog._hotkey_pill = QLabel(_hotkey_display_name(current_hk))
    dialog._hotkey_pill.setObjectName("HotkeyPill")
    dialog._hotkey_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
    dialog._hotkey_pill.setFixedHeight(52)
    lay.addWidget(dialog._hotkey_pill)

    lay.addSpacing(12)

    # Record button row
    btn_row = QHBoxLayout()
    btn_row.setSpacing(8)

    dialog._hotkey_record_btn = QPushButton("🎤 Record Hotkey")
    dialog._hotkey_record_btn.setObjectName("RecordHotkeyBtn")
    dialog._hotkey_record_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    dialog._hotkey_record_btn.setFixedHeight(44)
    dialog._hotkey_record_btn.clicked.connect(lambda: _start_hotkey_capture(dialog))
    btn_row.addWidget(dialog._hotkey_record_btn)

    dialog._hotkey_cancel_btn = QPushButton("Cancel")
    dialog._hotkey_cancel_btn.setObjectName("CancelBtn")
    dialog._hotkey_cancel_btn.setFixedHeight(44)
    dialog._hotkey_cancel_btn.setVisible(False)
    dialog._hotkey_cancel_btn.clicked.connect(lambda: _cancel_hotkey_capture(dialog))
    btn_row.addWidget(dialog._hotkey_cancel_btn)

    lay.addLayout(btn_row)

    # Status label
    dialog._hotkey_status = QLabel("")
    dialog._hotkey_status.setObjectName("FieldHint")
    dialog._hotkey_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lay.addWidget(dialog._hotkey_status)

    lay.addSpacing(8)
    note = QLabel("You can change this anytime in Settings. Press Escape to cancel recording.")
    note.setObjectName("StepBody")
    note.setWordWrap(True)
    lay.addWidget(note)

    lay.addStretch()
    return w


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
    """Start hotkey capture mode."""
    dialog._hotkey_record_btn.setEnabled(False)
    dialog._hotkey_record_btn.setText("Listening…")
    dialog._hotkey_cancel_btn.setVisible(True)
    dialog._hotkey_status.setText("Press your desired key combination now")
    dialog._hotkey_status.setObjectName("StatusOk")

    # Capture in a background thread so UI stays responsive.
    # CRITICAL: Qt widgets are NOT thread-safe. Never touch them from here.
    # All widget mutations are posted back to the main thread via QTimer.singleShot.
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
            # Guard: dialog may have been closed while we were waiting.
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
                pass  # widget already destroyed (dialog closed mid-capture)

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


def build_step_ready(dialog) -> QWidget:
    w = QWidget()
    w.setStyleSheet("background: transparent;")
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(12)

    num = QLabel("STEP 4 OF 4")
    num.setObjectName("StepNum")
    lay.addWidget(num)
    lay.addSpacing(4)

    title = QLabel("You're all set!")
    title.setObjectName("StepTitle")
    lay.addWidget(title)
    lay.addSpacing(16)

    body = QLabel(
        "Click any text field, press your hotkey, and start speaking.\n\n"
        "Your voice will be transcribed and typed instantly, with Smart Formatting "
        "for perfectly polished output.\n\n"
        "Add custom words in Dictionary to improve accuracy and expand shortcuts with Snippets."
    )
    body.setObjectName("StepBody")
    body.setWordWrap(True)
    lay.addWidget(body)
    lay.addSpacing(20)

    dialog._ready_summary = QLabel("")
    dialog._ready_summary.setObjectName("StatusOk")
    dialog._ready_summary.setWordWrap(True)
    lay.addWidget(dialog._ready_summary)

    lay.addStretch()
    return w
