"""
Settings window for Rota AI.
Wispr "Voice in Motion" design: warm dark bg, calm green save button,
soft corners, generous spacing, clear typography hierarchy.
"""

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
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
from ui.styles.settings_qss import FOOTER_QSS, SETTINGS_QSS
from ui.widgets.combo_boxes import NonScrollComboBox, SmartComboBox
from utils.window_effects import apply_blur

# Re-export so existing `from ui.settings_window import SmartComboBox` callers keep working
__all__ = ["SmartComboBox", "NonScrollComboBox", "SettingsWindow"]


class SettingsWindow(QDialog):
    """Settings dialog with Wispr Flow design language."""

    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        # Alias expected by _settings_sections.py helpers (they use dlg.config)
        self.config = config_manager
        self.setWindowTitle("Settings (Rota)")
        self.resize(560, 760)
        self.setMinimumSize(480, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self._init_ui()
        self._load_config()

    def _init_ui(self):
        self.setStyleSheet(SETTINGS_QSS)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area = scroll

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(36, 28, 36, 28)
        content_layout.setSpacing(0)

        # Header
        header_lay = QVBoxLayout()
        header_lay.setSpacing(4)
        title = QLabel("Settings")
        title.setObjectName("Title")
        subtitle = QLabel("Configure your voice dictation experience")
        subtitle.setObjectName("Subtitle")
        header_lay.addWidget(title)
        header_lay.addWidget(subtitle)
        content_layout.addLayout(header_lay)
        content_layout.addSpacing(24)

        # Sections (delegated to helpers)
        build_recording_section(self, content_layout)
        build_api_keys_section(self, content_layout)
        build_formatting_section(self, content_layout)
        build_shortcuts_section(self, content_layout)
        build_text_formatting_section(self, content_layout)
        build_audio_section(self, content_layout)
        build_per_app_section(self, content_layout)
        build_appearance_section(self, content_layout)

        content_layout.addStretch()

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Footer buttons — outside scroll area, always visible
        footer = QFrame()
        footer.setObjectName("SettingsFooter")
        footer.setStyleSheet(FOOTER_QSS)
        footer_lay = QHBoxLayout(footer)
        footer_lay.setContentsMargins(36, 14, 36, 18)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("CancelBtn")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setObjectName("SaveBtn")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self._save_and_close)

        footer_lay.addStretch()
        footer_lay.addWidget(self.cancel_btn)
        footer_lay.addWidget(self.save_btn)

        main_layout.addWidget(footer)

    def showEvent(self, event):
        super().showEvent(event)
        apply_blur(int(self.winId()))
        if hasattr(self, "_scroll_area"):
            self._scroll_area.verticalScrollBar().setValue(0)

    def _field_label(self, title: str, description: str = "") -> QWidget:
        """Two-line label: bold title + small grey description."""
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
        if hasattr(self, "font_preview_lbl") and hasattr(self, "font_family_combo"):
            fam = self.font_family_combo.currentData() or "Segoe UI"
            sz = self.font_size_spin.value()
            self.font_preview_lbl.setFont(QFont(fam, sz))

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
        section.setObjectName("Section")
        section_lay = QVBoxLayout(section)
        section_lay.setContentsMargins(20, 16, 20, 16)
        section_lay.addLayout(form)
        parent.addWidget(section)

    def _load_config(self):
        conf = self.config_manager.config
        self.gemini_key_input.setText(
            conf.get("gemini_api_key", "") or os.environ.get("GEMINI_API_KEY", "")
        )
        self.groq_key_input.setText(
            conf.get("groq_api_key", "") or os.environ.get("GROQ_API_KEY", "")
        )

        # Hotkey display is set by build_recording_section; refresh it here in case
        # config changed since the widget was built
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

    def _rebuild_per_app_list(self):
        """Rebuild the per-app override rows in the settings UI."""
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
            del_btn.clicked.connect(lambda checked, a=app_name: self._remove_per_app(a))
            row_lay.addWidget(del_btn)

            self.per_app_layout.addWidget(row)

    def _remove_per_app(self, app_name: str):
        """Remove a per-app override entry."""
        per_app = self.config.get("per_app_config", {}).copy()
        if app_name in per_app:
            del per_app[app_name]
            self.config.set("per_app_config", per_app)
            self._rebuild_per_app_list()

    def _save_and_close(self):
        gemini_key = self.gemini_key_input.text().strip()
        groq_key = self.groq_key_input.text().strip()
        self.config_manager.set("gemini_api_key", gemini_key)
        self.config_manager.set("groq_api_key", groq_key)
        if gemini_key:
            os.environ["GEMINI_API_KEY"] = gemini_key
        if groq_key:
            os.environ["GROQ_API_KEY"] = groq_key

        # Hotkey is saved immediately when captured via the record button; no combo to read here.
        self.config_manager.set("hotkey_mode", self.hotkey_mode_combo.currentData())
        self.config_manager.set("model_size", self.model_size_combo.currentData())
        self.config_manager.set("ai_enabled", self.ai_enabled_check.isChecked())
        self.config_manager.set("ai_provider", self.ai_provider_combo.currentData())
        self.config_manager.set("bg_audio_control", self.bg_audio_combo.currentData())
        self.config_manager.set("startup_enabled", self.startup_check.isChecked())
        self.config_manager.set("writing_mode", self.writing_mode_combo.currentData())
        self.config_manager.set("ollama_url", self.ollama_url_input.text().strip())
        self.config_manager.set("ollama_model", self.ollama_model_input.text().strip())
        try:
            self.config_manager.set(
                "auto_stop_silence_s", float(self.auto_stop_input.text().strip())
            )
        except ValueError:
            self.config_manager.set("auto_stop_silence_s", 2.5)

        self.config_manager.set("transcription_quality", self.quality_combo.currentData())
        self.config_manager.set("cpu_threads", self.cpu_threads_combo.currentData())
        self.config_manager.set("live_transcription_enabled", self.live_feedback_check.isChecked())

        self.config_manager.set(
            "ui_font_family", self.font_family_combo.currentData() or "Segoe UI"
        )
        self.config_manager.set("ui_font_size", self.font_size_spin.value())
        self.config_manager.set("ui_font_scope", self.font_scope_combo.currentData() or "app")
        self.config_manager.set("date_display", self.date_display_combo.currentData() or "relative")
        hd = self.history_days_combo.currentData()
        self.config_manager.set("history_days", hd if hd is not None else 2)

        self.config_manager.set("denoise_enabled", self.denoise_check.isChecked())
        self.config_manager.set("auto_backup_enabled", True)

        self.config_manager.save()
        self.accept()
