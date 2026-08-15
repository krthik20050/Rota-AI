"""
Rota AI — In-App Settings Page
===============================
Embedded in MainWindow's QStackedWidget so settings open inside the app
instead of a separate modal dialog. Reuses the same section builders
from _settings_sections.py.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.pages._settings_sections import (
    build_api_keys_section,
    build_appearance_section,
    build_audio_section,
    build_formatting_section,
    build_per_app_section,
    build_recording_section,
    build_shortcuts_section,
    build_text_formatting_section,
)


class SettingsPage(QWidget):
    """Settings page embedded in the main window — no separate dialog needed.

    Implements the same ``dlg`` interface that ``_settings_sections.py`` helpers
    expect (``_add_section``, ``_add_form_section``, ``_field_label``, etc.)
    so the existing section builders work without modification.
    """

    def __init__(self, config, on_save=None, on_back=None, parent=None):
        super().__init__(parent)
        self.config = config
        self._save_callback = on_save
        self._back_callback = on_back

        self._init_ui()

    def _init_ui(self):
        # Root layout — fills the page
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        # ── Page-level stylesheet ─────────────────────────────────────
        self.setStyleSheet("""
            QLabel#SectionTitle {
                font-size: 12px; font-weight: 700; color: #86EFAC;
                text-transform: uppercase; letter-spacing: 1px;
                margin-bottom: 12px; background: transparent;
            }
            QLabel#SectionDesc {
                font-size: 12px; color: #6B6B70;
                margin-bottom: 16px; margin-top: 2px; background: transparent;
            }
            QFrame#SettingsPageSection {
                background-color: #1C1C1F;
                border-radius: 14px;
                border: 1px solid rgba(255, 255, 255, 8);
                margin-bottom: 16px;
            }
            QLabel { font-size: 13px; color: #A0A0A5; background: transparent; }
            QLabel#FieldLabel { font-size: 13px; color: #A0A0A5; font-weight: 500; }
            QLabel#FieldDesc { font-size: 11px; color: #4A4A52; }
            QLineEdit, QComboBox {
                background-color: #222226; color: #F0F0F2;
                border: 1px solid rgba(255, 255, 255, 8);
                border-radius: 8px; padding: 10px 14px; font-size: 13px;
                font-family: 'Segoe UI', 'Inter';
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid rgba(134, 239, 172, 30);
                background-color: #262629;
            }
            QComboBox::drop-down { border: 0px; }
            QComboBox QAbstractItemView {
                background-color: #1C1C1F; color: #F0F0F2;
                border: 1px solid rgba(255, 255, 255, 10);
                border-radius: 8px;
                selection-background-color: rgba(134, 239, 172, 15);
                selection-color: #FFFFFF; padding: 4px;
            }
            QCheckBox {
                color: #A0A0A5; font-size: 13px; spacing: 10px;
            }
            QCheckBox::indicator {
                width: 18px; height: 18px; border-radius: 5px;
                border: 1.5px solid rgba(255, 255, 255, 15);
                background: #1C1C1F;
            }
            QCheckBox::indicator:checked {
                background: #86EFAC; border: 1.5px solid #86EFAC;
            }
            QCheckBox:hover::indicator {
                border: 1.5px solid rgba(255, 255, 255, 25);
            }
            QSpinBox {
                background-color: #222226; color: #F0F0F2;
                border: 1px solid rgba(255, 255, 255, 8);
                border-radius: 8px; padding: 10px 14px; font-size: 13px;
            }
            QLabel#HotkeyPill {
                background-color: #222226; color: #F0F0F2;
                border: 1px solid rgba(255, 255, 255, 8);
                border-radius: 8px; padding: 10px 14px;
                font-size: 13px; font-weight: 500;
            }
            QPushButton#RecordHotkeyBtn {
                background-color: rgba(255, 255, 255, 6);
                color: #A0A0A5;
                border: 1px solid rgba(255, 255, 255, 15);
                border-radius: 8px; padding: 8px 16px;
                font-size: 13px; font-weight: 500;
            }
            QPushButton#RecordHotkeyBtn:hover {
                background-color: rgba(255, 255, 255, 12);
                color: #F0F0F2;
                border-color: rgba(255, 255, 255, 25);
            }
            QPushButton#RecordHotkeyBtn:disabled {
                color: #4A4A52; border-color: rgba(255, 255, 255, 6);
            }
            QLabel#FontPreview {
                font-size: 13px; color: #A0A0A5;
                background: #222226;
                border: 1px solid rgba(255,255,255,8);
                border-radius: 8px; padding: 10px 14px;
            }
            QFontComboBox {
                background-color: #222226; color: #F0F0F2;
                border: 1px solid rgba(255, 255, 255, 8);
                border-radius: 8px; padding: 10px 14px; font-size: 13px;
            }
            QScrollBar:vertical {
                background: transparent; width: 14px;
                margin: 6px 4px; border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 35);
                border-radius: 7px; min-height: 40px;
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
            QFrame#SettingsPageHeader {
                background: transparent;
                border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            }
            QPushButton#SettingsBackBtn {
                background: rgba(255, 255, 255, 0.04); color: #A0A0A5;
                border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px;
                padding: 7px 14px; font-size: 13px;
            }
            QPushButton#SettingsBackBtn:hover {
                background: rgba(255, 255, 255, 0.08); color: #F0F0F2;
            }
            QPushButton#SettingsSaveBtn {
                background-color: #86EFAC; color: #0A0A0B;
                border: none; border-radius: 10px;
                padding: 8px 20px; font-weight: 600; font-size: 13px;
            }
            QPushButton#SettingsSaveBtn:hover {
                background-color: #A7F3D0;
            }
            QLabel#SettingsPageTitle {
                font-size: 18px; font-weight: 700; color: #F0F0F2;
            }
            QLabel#FieldHint {
                font-size: 11px; color: #5A5A60;
            }
            QPushButton#TestKeyBtn {
                background: rgba(255, 255, 255, 0.06); color: #A0A0A5;
                border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 8px;
                font-size: 11px; font-weight: 500;
            }
            QPushButton#TestKeyBtn:hover {
                background: rgba(255, 255, 255, 0.1); color: #F0F0F2;
            }
            QPushButton#PerAppAddBtn {
                background: rgba(134, 239, 172, 0.08); color: #86EFAC;
                border: 1px solid rgba(134, 239, 172, 0.2); border-radius: 8px;
                padding: 8px 14px; font-size: 12px; font-weight: 500;
            }
            QPushButton#PerAppAddBtn:hover {
                background: rgba(134, 239, 172, 0.14);
            }
        """)

        # ── Header bar ────────────────────────────────────────────────
        header = QFrame()
        header.setObjectName("SettingsPageHeader")
        header.setFixedHeight(52)
        header_lay = QHBoxLayout(header)
        header_lay.setContentsMargins(16, 0, 16, 0)
        header_lay.setSpacing(0)

        self._back_btn = QPushButton("←  Back")
        self._back_btn.setObjectName("SettingsBackBtn")
        self._back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._back_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        if self._back_callback:
            self._back_btn.clicked.connect(self._back_callback)
        header_lay.addWidget(self._back_btn)
        header_lay.addStretch()

        title = QLabel("Settings")
        title.setObjectName("SettingsPageTitle")
        header_lay.addWidget(title)
        header_lay.addStretch()

        self._save_btn = QPushButton("Save Settings")
        self._save_btn.setObjectName("SettingsSaveBtn")
        self._save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._save_btn.clicked.connect(self._on_save_clicked)
        header_lay.addWidget(self._save_btn)

        main_lay.addWidget(header)

        # ── Scrollable settings content ───────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self._scroll_area = scroll

        content = QWidget()
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(36, 16, 36, 28)
        self._content_layout.setSpacing(0)

        # Build all sections (delegated to helpers — same as SettingsWindow)
        build_recording_section(self, self._content_layout)
        build_api_keys_section(self, self._content_layout)
        build_formatting_section(self, self._content_layout)
        build_shortcuts_section(self, self._content_layout)
        build_text_formatting_section(self, self._content_layout)
        build_audio_section(self, self._content_layout)
        build_per_app_section(self, self._content_layout)
        build_appearance_section(self, self._content_layout)

        self._content_layout.addStretch()

        scroll.setWidget(content)
        main_lay.addWidget(scroll, 1)

    # ──────────────────────────────────────────────────────────────────
    # Section builder helpers (same interface as SettingsWindow)
    # ──────────────────────────────────────────────────────────────────

    def _add_section(self, parent, title, description):
        section_lay = QVBoxLayout()
        section_lay.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("SectionTitle")
        section_lay.addWidget(title_label)

        if description:
            desc_label = QLabel(description)
            desc_label.setObjectName("SectionDesc")
            section_lay.addWidget(desc_label)

        parent.addLayout(section_lay)

    def _add_form_section(self, parent, form):
        section = QFrame()
        section.setObjectName("SettingsPageSection")
        section_lay = QVBoxLayout(section)
        section_lay.setContentsMargins(20, 16, 20, 16)
        section_lay.addLayout(form)
        parent.addWidget(section)

    def _field_label(self, title: str, description: str = "") -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        t = QLabel(title)
        t.setObjectName("FieldLabel")
        lay.addWidget(t)
        if description:
            d = QLabel(description)
            d.setObjectName("FieldDesc")
            d.setWordWrap(True)
            lay.addWidget(d)
        return w

    def _update_font_preview(self):
        """Update the font preview — matches SettingsWindow interface."""
        if hasattr(self, "font_preview_lbl") and hasattr(self, "font_family_combo"):
            from PySide6.QtGui import QFont

            fam = self.font_family_combo.currentData() or "Segoe UI"
            sz = self.font_size_spin.value()
            self.font_preview_lbl.setFont(QFont(fam, sz))

    def _rebuild_per_app_list(self):
        """Rebuild per-app override rows — matches SettingsWindow interface."""
        if not hasattr(self, "per_app_layout"):
            return
        # Clear existing rows
        while self.per_app_layout.count():
            item = self.per_app_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        per_app = self.config.get("per_app_config", {})
        if not per_app:
            empty_lbl = QLabel("No app overrides configured yet. Click below to add one.")
            empty_lbl.setStyleSheet("color: #5A5A60; font-size: 11px; padding: 8px;")
            self.per_app_layout.addWidget(empty_lbl)
            return

        for app_name, settings in per_app.items():
            row = QFrame()
            row.setObjectName("PerAppRow")
            row.setStyleSheet(
                "QFrame#PerAppRow { background: rgba(255,255,255,0.04); border-radius: 6px; }"
            )
            row_lay = QHBoxLayout(row)
            row_lay.setContentsMargins(12, 8, 12, 8)
            row_lay.setSpacing(8)

            app_label = QLabel(f"<b>{app_name}</b>")
            app_label.setStyleSheet("color: #F0F0F2; font-size: 12px;")
            row_lay.addWidget(app_label, 1)

            mode = settings.get("writing_mode", "clean")
            mode_lbl = QLabel(f"mode: {mode}")
            mode_lbl.setStyleSheet("color: #86EFAC; font-size: 11px;")
            row_lay.addWidget(mode_lbl)

            provider = settings.get("ai_provider", "auto")
            prov_lbl = QLabel(f"AI: {provider}")
            prov_lbl.setStyleSheet("color: #A0A0A5; font-size: 11px;")
            row_lay.addWidget(prov_lbl)

            del_btn = QPushButton("✕")
            del_btn.setFixedSize(22, 22)
            del_btn.setStyleSheet(
                "QPushButton { background: transparent; color: #5A5A60; border: none; }"
                "QPushButton:hover { color: #F87171; }"
            )
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.clicked.connect(lambda _checked, a=app_name: self._remove_per_app(a))
            row_lay.addWidget(del_btn)

            self.per_app_layout.addWidget(row)

    def _remove_per_app(self, app_name: str):
        """Remove a per-app override entry."""
        per_app = self.config.get("per_app_config", {}).copy()
        if app_name in per_app:
            del per_app[app_name]
            self.config.set("per_app_config", per_app)
            self._rebuild_per_app_list()

    def _load_config(self):
        """Load current config values into all widgets — same as SettingsWindow._load_config."""
        import os

        conf = self.config.config

        self.gemini_key_input.setText(
            conf.get("gemini_api_key", "") or os.environ.get("GEMINI_API_KEY", "")
        )
        self.groq_key_input.setText(
            conf.get("groq_api_key", "") or os.environ.get("GROQ_API_KEY", "")
        )

        if hasattr(self, "hotkey_display"):
            from ui.pages._settings_sections import _hotkey_display_name
            self.hotkey_display.setText(_hotkey_display_name(conf.get("hotkey", "f9")))

        mode = conf.get("hotkey_mode", "hold")
        idx = self.hotkey_mode_combo.findData(mode)
        self.hotkey_mode_combo.setCurrentIndex(idx if idx >= 0 else 0)

        model = conf.get("model_size", "base.en")
        idx = self.model_size_combo.findData(model)
        self.model_size_combo.setCurrentIndex(idx if idx >= 0 else 2)

        self.ai_enabled_check.setChecked(conf.get("ai_enabled", True))
        self.startup_check.setChecked(conf.get("startup_enabled", False))

        writing_mode = conf.get("writing_mode", "clean")
        idx = self.writing_mode_combo.findData(writing_mode)
        self.writing_mode_combo.setCurrentIndex(idx if idx >= 0 else 1)

        self.ollama_url_input.setText(conf.get("ollama_url", "http://localhost:11434"))
        self.ollama_model_input.setText(conf.get("ollama_model", "llama3.2:1b"))
        self.auto_stop_input.setText(str(conf.get("auto_stop_silence_s", 2.5)))

        quality = conf.get("transcription_quality", "balanced")
        q_idx = self.quality_combo.findData(quality)
        self.quality_combo.setCurrentIndex(q_idx if q_idx >= 0 else 1)

        threads = int(conf.get("cpu_threads", 0))
        t_idx = self.cpu_threads_combo.findData(threads)
        self.cpu_threads_combo.setCurrentIndex(t_idx if t_idx >= 0 else 0)

        self.live_feedback_check.setChecked(conf.get("live_transcription_enabled", True))
        self.denoise_check.setChecked(conf.get("denoise_enabled", False))

        ai_prov = conf.get("ai_provider", "auto")
        ai_idx = self.ai_provider_combo.findData(ai_prov)
        self.ai_provider_combo.setCurrentIndex(ai_idx if ai_idx >= 0 else 0)

        bg_aud = conf.get("bg_audio_control", "pause")
        bg_idx = self.bg_audio_combo.findData(bg_aud)
        self.bg_audio_combo.setCurrentIndex(bg_idx if bg_idx >= 0 else 2)

        font_fam = conf.get("ui_font_family", "Segoe UI")
        font_sz = int(conf.get("ui_font_size", 13))
        f_idx = self.font_family_combo.findData(font_fam)
        self.font_family_combo.setCurrentIndex(f_idx if f_idx >= 0 else 0)
        self.font_size_spin.setValue(font_sz)
        self._update_font_preview()

        font_scope = conf.get("ui_font_scope", "app")
        fs_idx = self.font_scope_combo.findData(font_scope)
        self.font_scope_combo.setCurrentIndex(fs_idx if fs_idx >= 0 else 0)

        date_disp = conf.get("date_display", "relative")
        dd_idx = self.date_display_combo.findData(date_disp)
        self.date_display_combo.setCurrentIndex(dd_idx if dd_idx >= 0 else 0)

        history_days = int(conf.get("history_days", 2))
        hd_idx = self.history_days_combo.findData(history_days)
        self.history_days_combo.setCurrentIndex(hd_idx if hd_idx >= 0 else 1)

        self._rebuild_per_app_list()

    # ──────────────────────────────────────────────────────────────────
    # Save logic
    # ──────────────────────────────────────────────────────────────────

    def _save_config(self):
        """Save current widget values to the config (same as SettingsWindow._save_and_close)."""
        import os

        gemini_key = self.gemini_key_input.text().strip()
        groq_key = self.groq_key_input.text().strip()
        self.config.set("gemini_api_key", gemini_key)
        self.config.set("groq_api_key", groq_key)
        if gemini_key:
            os.environ["GEMINI_API_KEY"] = gemini_key
        if groq_key:
            os.environ["GROQ_API_KEY"] = groq_key

        self.config.set("hotkey_mode", self.hotkey_mode_combo.currentData())
        self.config.set("model_size", self.model_size_combo.currentData())
        self.config.set("ai_enabled", self.ai_enabled_check.isChecked())
        self.config.set("ai_provider", self.ai_provider_combo.currentData())
        self.config.set("bg_audio_control", self.bg_audio_combo.currentData())
        self.config.set("startup_enabled", self.startup_check.isChecked())
        self.config.set("writing_mode", self.writing_mode_combo.currentData())
        self.config.set("ollama_url", self.ollama_url_input.text().strip())
        self.config.set("ollama_model", self.ollama_model_input.text().strip())
        try:
            self.config.set(
                "auto_stop_silence_s", float(self.auto_stop_input.text().strip())
            )
        except ValueError:
            self.config.set("auto_stop_silence_s", 2.5)

        self.config.set("transcription_quality", self.quality_combo.currentData())
        self.config.set("cpu_threads", self.cpu_threads_combo.currentData())
        self.config.set("live_transcription_enabled", self.live_feedback_check.isChecked())

        self.config.set(
            "ui_font_family", self.font_family_combo.currentData() or "Segoe UI"
        )
        self.config.set("ui_font_size", self.font_size_spin.value())
        self.config.set("ui_font_scope", self.font_scope_combo.currentData() or "app")
        self.config.set("date_display", self.date_display_combo.currentData() or "relative")
        hd = self.history_days_combo.currentData()
        self.config.set("history_days", hd if hd is not None else 2)

        self.config.set("denoise_enabled", self.denoise_check.isChecked())
        self.config.set("auto_backup_enabled", True)

        self.config.save()

    def _on_save_clicked(self):
        """Save settings, then invoke the save callback and navigate back."""
        self._save_config()
        if self._save_callback:
            self._save_callback()
