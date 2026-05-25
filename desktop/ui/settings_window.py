"""
Settings window for Rota AI.
Wispr "Voice in Motion" design: warm dark bg, calm green save button,
soft corners, generous spacing, clear typography hierarchy.
"""

import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
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
    build_formatting_section,
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
        self.gemini_key_input.setText(conf.get("gemini_api_key", ""))
        self.groq_key_input.setText(conf.get("groq_api_key", ""))

        hotkey_val = conf.get("hotkey", "f9").lower()
        hk_idx = self.hotkey_combo.findData(hotkey_val)
        self.hotkey_combo.setCurrentIndex(hk_idx if hk_idx >= 0 else 8)
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

    def _save_and_close(self):
        gemini_key = self.gemini_key_input.text().strip()
        groq_key = self.groq_key_input.text().strip()
        self.config_manager.set("gemini_api_key", gemini_key)
        self.config_manager.set("groq_api_key", groq_key)
        if gemini_key:
            os.environ["GEMINI_API_KEY"] = gemini_key
        if groq_key:
            os.environ["GROQ_API_KEY"] = groq_key

        self.config_manager.set("hotkey", self.hotkey_combo.currentData() or "f9")
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

        self.config_manager.save()
        self.accept()
