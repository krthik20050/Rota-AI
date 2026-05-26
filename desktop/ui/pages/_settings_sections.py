"""
Section-building helpers for SettingsWindow._init_ui.
Each function receives the dialog instance as `dlg` and a parent layout,
builds the widgets, attaches them to `dlg`, and adds them to `parent`.
"""

import threading

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ui.widgets.combo_boxes import NonScrollComboBox, SmartComboBox


def build_recording_section(dlg, parent):
    """Recording section: hotkey, mode, model, quality, threads, live feedback."""

    dlg._add_section(parent, "Recording", "Configure how Rota captures your voice")

    form = QFormLayout()
    form.setSpacing(16)
    form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    form.setFormAlignment(Qt.AlignmentFlag.AlignTop)

    # Hotkey display + record button
    hk_row_w = QWidget()
    hk_row = QHBoxLayout(hk_row_w)
    hk_row.setContentsMargins(0, 0, 0, 0)
    hk_row.setSpacing(8)

    current_hk = dlg.config.get("hotkey", "tab") if hasattr(dlg, "config") else "tab"
    from ui.pages._settings_sections import _hotkey_display_name

    dlg.hotkey_display = QLabel(_hotkey_display_name(current_hk))
    dlg.hotkey_display.setObjectName("HotkeyPill")
    dlg.hotkey_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
    dlg.hotkey_display.setFixedHeight(40)
    hk_row.addWidget(dlg.hotkey_display, 1)

    dlg.hotkey_record_btn = QPushButton(" Record New Hotkey")
    dlg.hotkey_record_btn.setObjectName("RecordHotkeyBtn")
    dlg.hotkey_record_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    dlg.hotkey_record_btn.setFixedHeight(40)
    dlg.hotkey_record_btn.clicked.connect(lambda: _start_settings_hotkey_capture(dlg))
    hk_row.addWidget(dlg.hotkey_record_btn)

    form.addRow(
        dlg._field_label("Global Hotkey", "Press the button to record a new key combination."),
        hk_row_w,
    )

    dlg.hotkey_status = QLabel("")
    dlg.hotkey_status.setObjectName("FieldHint")
    dlg.hotkey_status.setVisible(False)
    form.addRow("", dlg.hotkey_status)

    dlg.hotkey_mode_combo = NonScrollComboBox()
    dlg.hotkey_mode_combo.add_option("Hold to Record", "hold", recommended=True)
    dlg.hotkey_mode_combo.add_option("Toggle Mode", "toggle")
    form.addRow(
        dlg._field_label(
            "Recording Mode", "Hold: record while held. Toggle: press once to start, again to stop."
        ),
        dlg.hotkey_mode_combo,
    )

    dlg.model_size_combo = NonScrollComboBox()
    dlg.model_size_combo.add_option("tiny (fastest, least accurate)", "tiny")
    dlg.model_size_combo.add_option("base (fast, decent accuracy)", "base")
    dlg.model_size_combo.add_option("base.en (English only, faster)", "base.en", recommended=True)
    dlg.model_size_combo.add_option("small (better accuracy, slower)", "small")
    dlg.model_size_combo.add_option("small.en (English, balanced)", "small.en")
    dlg.model_size_combo.add_option("medium (high accuracy, slow)", "medium")
    dlg.model_size_combo.add_option("large-v3 (best accuracy, very slow)", "large-v3")
    form.addRow(
        dlg._field_label(
            "Whisper Model", "Larger models are more accurate but use more CPU and RAM."
        ),
        dlg.model_size_combo,
    )

    dlg.quality_combo = NonScrollComboBox()
    dlg.quality_combo.add_option("High Accuracy (uses beam search)", "high")
    dlg.quality_combo.add_option("Balanced", "balanced", recommended=True)
    dlg.quality_combo.add_option("Fast (Greedy) (quickest, least precise)", "fast")
    form.addRow(
        dlg._field_label(
            "Transcription Quality",
            "Controls the decoding strategy. Balanced is best for most use cases.",
        ),
        dlg.quality_combo,
    )

    dlg.cpu_threads_combo = NonScrollComboBox()
    dlg.cpu_threads_combo.add_option("Auto-detect", 0, recommended=True)
    dlg.cpu_threads_combo.add_option("1 Thread", 1)
    dlg.cpu_threads_combo.add_option("2 Threads", 2)
    dlg.cpu_threads_combo.add_option("4 Threads", 4)
    dlg.cpu_threads_combo.add_option("8 Threads", 8)
    form.addRow(
        dlg._field_label(
            "CPU Threads",
            "Number of CPU threads for transcription. Auto-detect is best unless you want to limit CPU usage.",
        ),
        dlg.cpu_threads_combo,
    )

    dlg.live_feedback_check = QCheckBox("Show partial text while recording")
    form.addRow(
        dlg._field_label(
            "Live Feedback", "Displays a real-time preview of transcribed text as you speak."
        ),
        dlg.live_feedback_check,
    )

    dlg._add_form_section(parent, form)


def build_api_keys_section(dlg, parent):
    """API Keys section: Gemini + Groq."""
    dlg._add_section(parent, "API Keys", "Your cloud credentials: stored locally, never shared")

    key_form = QFormLayout()
    key_form.setSpacing(16)
    key_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    key_form.setFormAlignment(Qt.AlignmentFlag.AlignTop)

    dlg.gemini_key_input = QLineEdit()
    dlg.gemini_key_input.setPlaceholderText("AIzaSy… (from aistudio.google.com)")
    dlg.gemini_key_input.setEchoMode(QLineEdit.EchoMode.Password)
    key_form.addRow(
        dlg._field_label(
            "Gemini API Key",
            "Used for Smart Formatting. Get a free key at aistudio.google.com/app/apikey",
        ),
        dlg.gemini_key_input,
    )

    dlg.groq_key_input = QLineEdit()
    dlg.groq_key_input.setPlaceholderText("gsk_… (from console.groq.com/keys)")
    dlg.groq_key_input.setEchoMode(QLineEdit.EchoMode.Password)
    key_form.addRow(
        dlg._field_label(
            "Groq API Key",
            "Used for cloud transcription (optional). Get a free key at console.groq.com",
        ),
        dlg.groq_key_input,
    )

    dlg._add_form_section(parent, key_form)


def build_formatting_section(dlg, parent):
    """Formatting Settings section: smart formatting, provider, bg audio, startup."""
    dlg._add_section(
        parent, "Formatting Settings", "Configure smart text formatting and background audio"
    )

    ai_form = QFormLayout()
    ai_form.setSpacing(16)
    ai_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    ai_form.setFormAlignment(Qt.AlignmentFlag.AlignTop)

    dlg.ai_enabled_check = QCheckBox("Enable Smart Formatting")
    ai_form.addRow(
        dlg._field_label(
            "Smart Formatting",
            "Runs a language model to remove fillers, fix grammar, and polish your dictation.",
        ),
        dlg.ai_enabled_check,
    )

    dlg.ai_provider_combo = NonScrollComboBox()
    dlg.ai_provider_combo.add_option("Auto (Gemini → Groq fallback)", "auto", recommended=True)
    dlg.ai_provider_combo.add_option("Gemini Cloud LLM (best quality)", "gemini")
    dlg.ai_provider_combo.add_option("Groq Cloud LLM (ultra-fast)", "groq")
    dlg.ai_provider_combo.add_option("Ollama (local, offline)", "ollama")
    dlg.ai_provider_combo.add_option("None (regex only)", "none")
    ai_form.addRow(
        dlg._field_label(
            "Formatting Engine",
            "Auto tries Gemini first then falls back to Groq. Use Ollama for fully offline processing.",
        ),
        dlg.ai_provider_combo,
    )

    dlg.bg_audio_combo = NonScrollComboBox()
    dlg.bg_audio_combo.add_option("Ignore (do nothing)", "none")
    dlg.bg_audio_combo.add_option("Mute System Volume", "mute")
    dlg.bg_audio_combo.add_option("Pause Media", "pause", recommended=True)
    ai_form.addRow(
        dlg._field_label(
            "Background Audio", "Controls what happens to media playback when you start recording."
        ),
        dlg.bg_audio_combo,
    )

    dlg.startup_check = QCheckBox("Launch Rota when you sign in")
    ai_form.addRow(
        dlg._field_label(
            "Startup",
            "Adds Rota to your OS login items so it launches automatically on sign-in.",
        ),
        dlg.startup_check,
    )

    dlg._add_form_section(parent, ai_form)


def build_shortcuts_section(dlg, parent):
    """Keyboard Shortcuts section: static reference table."""
    dlg._add_section(parent, "Keyboard Shortcuts", "Quick reference for keyboard commands")

    shortcuts_form = QFormLayout()
    shortcuts_form.setSpacing(12)

    shortcuts = [
        ("F9", "Start/Stop recording"),
        ("Ctrl+Shift+R", "Force restart recording"),
        ("Escape", "Cancel current recording"),
        ("Ctrl+C", "Copy selected text"),
    ]
    for key, desc in shortcuts:
        key_label = QLabel(
            f"<span style='background:#222226; padding:4px 10px; border-radius:4px; color:#F0F0F2;'>{key}</span>"
        )
        desc_label = QLabel(desc)
        shortcuts_form.addRow(key_label, desc_label)

    dlg._add_form_section(parent, shortcuts_form)


def build_text_formatting_section(dlg, parent):
    """Text & Formatting section: writing mode, ollama settings, auto-stop."""
    dlg._add_section(
        parent, "Text & Formatting", "Configure text formatting modes and auto-stop behaviour"
    )

    ai_writing_form = QFormLayout()
    ai_writing_form.setSpacing(16)
    ai_writing_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    ai_writing_form.setFormAlignment(Qt.AlignmentFlag.AlignTop)

    dlg.writing_mode_combo = NonScrollComboBox()
    dlg.writing_mode_combo.add_option("Raw (no text cleanup)", "raw")
    dlg.writing_mode_combo.add_option("Clean (filler removal)", "clean", recommended=True)
    dlg.writing_mode_combo.add_option("Professional (formal tone)", "professional")
    dlg.writing_mode_combo.add_option("Casual (conversational)", "casual")
    dlg.writing_mode_combo.add_option("Bullet Points (structured list)", "bullets")
    ai_writing_form.addRow(
        dlg._field_label(
            "Writing Mode",
            "Determines how the engine reformats your dictation after transcription.",
        ),
        dlg.writing_mode_combo,
    )

    dlg.ollama_url_input = QLineEdit()
    dlg.ollama_url_input.setPlaceholderText("http://localhost:11434")
    ai_writing_form.addRow(
        dlg._field_label(
            "Ollama URL",
            "Address of your local Ollama instance. Only used when Formatting Engine is set to Ollama.",
        ),
        dlg.ollama_url_input,
    )

    dlg.ollama_model_input = QLineEdit()
    dlg.ollama_model_input.setPlaceholderText("qwen3.5:latest")
    ai_writing_form.addRow(
        dlg._field_label(
            "Ollama Model",
            "The model name pulled in Ollama to use for text formatting (e.g. llama3.2:1b).",
        ),
        dlg.ollama_model_input,
    )

    dlg.auto_stop_input = QLineEdit()
    dlg.auto_stop_input.setPlaceholderText("2.5")
    ai_writing_form.addRow(
        dlg._field_label(
            "Auto-stop Silence (s)",
            "Stops recording automatically after this many seconds of silence. Set 0 to disable.",
        ),
        dlg.auto_stop_input,
    )

    dlg._add_form_section(parent, ai_writing_form)


def build_audio_section(dlg, parent):
    """Audio section: noise suppression toggle, audio quality settings."""
    dlg._add_section(parent, "Audio", "Configure audio processing and noise handling")

    audio_form = QFormLayout()
    audio_form.setSpacing(16)
    audio_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    audio_form.setFormAlignment(Qt.AlignmentFlag.AlignTop)

    dlg.denoise_check = QCheckBox("Enable noise suppression")
    audio_form.addRow(
        dlg._field_label(
            "Noise Reduction",
            "Filters background noise before transcription. Helps in noisy environments but may slightly reduce accuracy.",
        ),
        dlg.denoise_check,
    )

    dlg._add_form_section(parent, audio_form)


def build_per_app_section(dlg, parent):
    """Per-App settings section: override writing mode by application."""
    dlg._add_section(parent, "Per-App Overrides", "Customize settings for specific applications")

    per_app_form = QFormLayout()
    per_app_form.setSpacing(16)
    per_app_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    per_app_form.setFormAlignment(Qt.AlignmentFlag.AlignTop)

    dlg.per_app_list = QFrame()
    dlg.per_app_list.setObjectName("PerAppList")
    dlg.per_app_list.setStyleSheet(
        "QFrame#PerAppList { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; }"
    )
    dlg.per_app_layout = QVBoxLayout(dlg.per_app_list)
    dlg.per_app_layout.setContentsMargins(12, 12, 12, 12)
    dlg.per_app_layout.setSpacing(8)
    per_app_form.addRow(
        dlg._field_label(
            "App Overrides",
            "Override writing mode and AI provider for specific apps. "
            "Say 'scratch that' in a terminal and it will use raw mode automatically.",
        ),
        dlg.per_app_list,
    )

    add_app_btn = QPushButton("+ Add Current Application")
    add_app_btn.setObjectName("PerAppAddBtn")
    add_app_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    add_app_btn.clicked.connect(lambda: _add_current_app_per_app(dlg))
    per_app_form.addRow("", add_app_btn)

    dlg._add_form_section(parent, per_app_form)


def _add_current_app_per_app(dlg):
    """Detect the currently focused app and add it to per-app config."""
    try:
        app_name = _detect_active_app()
        if not app_name:
            return
        _add_per_app_row(dlg, app_name, "clean", "auto")
        dlg._rebuild_per_app_list()
    except Exception:
        pass


def _detect_active_app() -> str:
    """Detect the currently active/focused application name using existing injection/app_detector."""
    try:
        from injection.app_detector import get_active_app

        ctx = get_active_app()
        if ctx and ctx.process_name:
            return ctx.process_name.lower().replace(".exe", "")
    except Exception:
        pass
    return ""


def _add_per_app_row(dlg, app_name: str, writing_mode: str, ai_provider: str):
    """Add a per-app override entry to the config."""
    per_app = dlg.config.get("per_app_config", {}).copy()
    per_app[app_name] = {
        "writing_mode": writing_mode,
        "ai_provider": ai_provider,
    }
    dlg.config.set("per_app_config", per_app)
    dlg._rebuild_per_app_list()


def build_appearance_section(dlg, parent):
    """Appearance section: font family, size, scope, preview, date display, history days."""
    dlg._add_section(parent, "Appearance", "Choose font and where it applies")

    font_form = QFormLayout()
    font_form.setSpacing(16)
    font_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    font_form.setFormAlignment(Qt.AlignmentFlag.AlignTop)

    dlg.font_family_combo = SmartComboBox()
    _all_fonts = sorted(QFontDatabase.families())
    for fam in _all_fonts:
        dlg.font_family_combo.add_option(fam, fam, recommended=(fam == "Segoe UI"))
    dlg.font_family_combo.currentIndexChanged.connect(dlg._update_font_preview)
    font_form.addRow(
        dlg._field_label("UI Font", "Choose from all fonts installed on this system."),
        dlg.font_family_combo,
    )

    dlg.font_size_spin = QSpinBox()
    dlg.font_size_spin.setRange(8, 36)
    dlg.font_size_spin.setValue(13)
    dlg.font_size_spin.setSuffix(" px")
    dlg.font_size_spin.valueChanged.connect(dlg._update_font_preview)
    font_form.addRow(
        dlg._field_label("Font Size", "Base font size. Affects body text throughout the UI."),
        dlg.font_size_spin,
    )

    dlg.font_scope_combo = NonScrollComboBox()
    dlg.font_scope_combo.add_option("Entire Application", "app", recommended=True)
    dlg.font_scope_combo.add_option("Main Window only", "main_window")
    dlg.font_scope_combo.add_option("History Text only", "history")
    dlg.font_scope_combo.add_option("Overlay Pill only", "overlay")
    font_form.addRow(
        dlg._field_label(
            "Apply Font To", "Choose which part of the interface uses the selected font."
        ),
        dlg.font_scope_combo,
    )

    dlg.font_preview_lbl = QLabel("The quick brown fox jumps over the lazy dog")
    dlg.font_preview_lbl.setObjectName("FontPreview")
    dlg.font_preview_lbl.setWordWrap(True)
    font_form.addRow(QLabel("Preview"), dlg.font_preview_lbl)

    dlg.date_display_combo = NonScrollComboBox()
    dlg.date_display_combo.add_option(
        "Relative (Today, Yesterday, etc.)", "relative", recommended=True
    )
    dlg.date_display_combo.add_option("Absolute (2025-01-15 style)", "absolute")
    font_form.addRow(
        dlg._field_label("Date Display", "How dates appear in the History panel."),
        dlg.date_display_combo,
    )

    dlg.history_days_combo = NonScrollComboBox()
    dlg.history_days_combo.add_option("Today only", 1)
    dlg.history_days_combo.add_option("Today + Yesterday (2 days)", 2, recommended=True)
    dlg.history_days_combo.add_option("Last 7 days", 7)
    dlg.history_days_combo.add_option("Last 30 days", 30)
    dlg.history_days_combo.add_option("All time", 0)
    font_form.addRow(
        dlg._field_label("History Shown", "How many days of history to display on the Home page."),
        dlg.history_days_combo,
    )

    dlg._add_form_section(parent, font_form)


def _hotkey_display_name(hotkey_str: str) -> str:
    """Convert internal hotkey string to user-friendly display name."""
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


def _start_settings_hotkey_capture(dlg):
    """Start hotkey capture from settings window."""
    dlg.hotkey_record_btn.setEnabled(False)
    dlg.hotkey_record_btn.setText("Listening...")
    dlg.hotkey_status.setText("Press your desired key combination now")
    dlg.hotkey_status.setObjectName("StatusOk")
    dlg.hotkey_status.setVisible(True)

    def _capture():
        try:
            from plat import get_hotkey_handler

            HotkeyHandlerClass = get_hotkey_handler()
            result = HotkeyHandlerClass.capture_hotkey(timeout=8.0)
            if result:
                dlg.config.set("hotkey", result)
                from ui.pages._settings_sections import _hotkey_display_name

                dlg.hotkey_display.setText(_hotkey_display_name(result))
                dlg.hotkey_status.setText(f"Hotkey set to: {_hotkey_display_name(result)}")
                dlg.hotkey_status.setObjectName("StatusOk")
            else:
                dlg.hotkey_status.setText("Cancelled.")
                dlg.hotkey_status.setObjectName("FieldHint")
        except Exception as e:
            dlg.hotkey_status.setText(f"Error: {e}")
            dlg.hotkey_status.setObjectName("StatusError")
        finally:
            dlg.hotkey_record_btn.setEnabled(True)
            dlg.hotkey_record_btn.setText(" Record New Hotkey")

    t = threading.Thread(target=_capture, daemon=True)
    t.start()
