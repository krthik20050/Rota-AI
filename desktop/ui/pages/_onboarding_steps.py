from __future__ import annotations

import os

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QVBoxLayout, QWidget,
)

_HOTKEYS = [
    ("Tab",             "tab"),
    ("F9",              "f9"),
    ("F1",  "f1"), ("F2", "f2"), ("F3", "f3"), ("F4", "f4"),
    ("F5",  "f5"), ("F6", "f6"), ("F7", "f7"), ("F8", "f8"),
    ("F10", "f10"), ("F11", "f11"), ("F12", "f12"),
    ("Ctrl+Shift",   "ctrl+shift"),
    ("Ctrl+Shift+R", "ctrl+shift+r"), ("Ctrl+Shift+D", "ctrl+shift+d"),
    ("Ctrl+Shift+V", "ctrl+shift+v"), ("Ctrl+Alt+Space", "ctrl+alt+space"),
    ("Alt+Space",   "alt+space"),   ("Alt+F9", "alt+f9"),
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
                vram_gb = torch.cuda.get_device_properties(0).total_mem / (1024 ** 3)
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
            ram_gb = psutil.virtual_memory().total / (1024 ** 3)
        except Exception:
            try:
                # Fallback: read /proc/meminfo directly
                with open("/proc/meminfo") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            ram_gb = int(line.split()[1]) / (1024 ** 2)  # kB to GB
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
        for root, dirs, files in os.walk(cache_dir):
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
        ("🎙️", "Voice Dictation",  "Works in any app, any text field"),
        ("✨", "Smart Formatting",   "Cloud or local models polish your words"),
        ("⚡", "Snippets",         "Voice-trigger frequently used text"),
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

    title = QLabel("Connect Cloud Services")
    title.setObjectName("StepTitle")
    lay.addWidget(title)
    lay.addSpacing(8)

    body = QLabel(
        "Both fields are optional: skip if you already have keys set up. "
        "Gemini handles smart text formatting; Groq powers cloud transcription. "
        "Keys are stored locally and can be changed in Settings anytime."
    )
    body.setObjectName("StepBody")
    body.setWordWrap(True)
    lay.addWidget(body)
    lay.addSpacing(14)

    def _resolve_key(config_key: str, env_var: str) -> str:
        if dialog._config:
            v = dialog._config.get(config_key, "")
            if v:
                return v
        return os.environ.get(env_var, "")

    gem_lbl = QLabel("Gemini API Key  (optional)")
    gem_lbl.setObjectName("FieldLabel")
    lay.addWidget(gem_lbl)
    gem_hint = QLabel("aistudio.google.com → Get API Key   (starts with AIza…)")
    gem_hint.setObjectName("FieldHint")
    lay.addWidget(gem_hint)
    gem_row = QHBoxLayout()
    gem_row.setSpacing(8)
    dialog._gemini_input = QLineEdit()
    dialog._gemini_input.setObjectName("ApiInput")
    dialog._gemini_input.setPlaceholderText("AIzaSy… (or leave blank if already set in .env)")
    dialog._gemini_input.setEchoMode(QLineEdit.EchoMode.Password)
    dialog._gemini_input.setText(_resolve_key("gemini_api_key", "GEMINI_API_KEY"))
    gem_row.addWidget(dialog._gemini_input, 1)
    gem_open = QPushButton("Get Key →")
    gem_open.setObjectName("GetKeyBtn")
    gem_open.setCursor(Qt.CursorShape.PointingHandCursor)
    gem_open.clicked.connect(lambda: QDesktopServices.openUrl(
        QUrl("https://aistudio.google.com/app/apikey")))
    gem_row.addWidget(gem_open)
    lay.addLayout(gem_row)

    lay.addSpacing(10)

    groq_lbl = QLabel("Groq API Key  (optional, for cloud transcription)")
    groq_lbl.setObjectName("FieldLabel")
    lay.addWidget(groq_lbl)
    groq_hint = QLabel("console.groq.com → API Keys   (starts with gsk_…)")
    groq_hint.setObjectName("FieldHint")
    lay.addWidget(groq_hint)
    groq_row = QHBoxLayout()
    groq_row.setSpacing(8)
    dialog._groq_input = QLineEdit()
    dialog._groq_input.setObjectName("ApiInput")
    dialog._groq_input.setPlaceholderText("gsk_… (or leave blank if already set in .env)")
    dialog._groq_input.setEchoMode(QLineEdit.EchoMode.Password)
    dialog._groq_input.setText(_resolve_key("groq_api_key", "GROQ_API_KEY"))
    groq_row.addWidget(dialog._groq_input, 1)
    groq_open = QPushButton("Get Key →")
    groq_open.setObjectName("GetKeyBtn")
    groq_open.setCursor(Qt.CursorShape.PointingHandCursor)
    groq_open.clicked.connect(lambda: QDesktopServices.openUrl(
        QUrl("https://console.groq.com/keys")))
    groq_row.addWidget(groq_open)
    lay.addLayout(groq_row)

    dialog._api_status = QLabel("")
    dialog._api_status.setObjectName("StatusLabel")
    lay.addWidget(dialog._api_status)

    lay.addStretch()
    return w


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
        ("tiny (fastest, least accurate)",       "tiny"),
        ("base.en (English, fast, recommended)", "base.en"),
        ("small.en (English, balanced)",           "small.en"),
        ("medium (high accuracy, slower)",         "medium"),
        ("large-v3 (best accuracy, ~3 GB)",        "large-v3"),
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
    note = QLabel("This is a fallback model — it downloads in the background so you don't have to wait. Groq cloud is used for transcription when online.")
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
        "Choose the keyboard shortcut that starts and stops recording. "
        "It works globally across all your apps."
    )
    body.setObjectName("StepBody")
    body.setWordWrap(True)
    lay.addWidget(body)
    lay.addSpacing(20)

    hk_lbl = QLabel("Global Hotkey")
    hk_lbl.setObjectName("FieldLabel")
    lay.addWidget(hk_lbl)

    dialog._hotkey_combo = QComboBox()
    dialog._hotkey_combo.setObjectName("HotkeyCombo")
    dialog._hotkey_combo.wheelEvent = lambda e: e.ignore()
    for label, data in _HOTKEYS:
        dialog._hotkey_combo.addItem(label, data)
    current_hk = dialog._config.get("hotkey", "f9").lower() if dialog._config else "f9"
    idx = dialog._hotkey_combo.findData(current_hk)
    dialog._hotkey_combo.setCurrentIndex(max(0, idx))
    dialog._hotkey_combo.currentIndexChanged.connect(dialog._update_hotkey_pill)
    lay.addWidget(dialog._hotkey_combo)

    lay.addSpacing(16)

    dialog._hotkey_pill = QLabel("Tab")
    dialog._hotkey_pill.setObjectName("HotkeyPill")
    dialog._hotkey_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
    dialog._hotkey_pill.setFixedHeight(52)
    dialog._update_hotkey_pill()
    lay.addWidget(dialog._hotkey_pill)

    lay.addSpacing(12)
    note = QLabel("You can change this anytime in Settings.")
    note.setObjectName("StepBody")
    lay.addWidget(note)

    lay.addStretch()
    return w


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
