from __future__ import annotations
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QProgressBar, QScrollArea,
    QStackedWidget, QVBoxLayout, QWidget, QPushButton,
)
from ui.components.circular_progress import CircularProgress

CLR_ACCENT = "#86EFAC"


def build_speech_tab(page) -> QScrollArea:
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    container = QWidget()
    container.setObjectName("TabContainer")
    lay = QVBoxLayout(container)
    lay.setContentsMargins(0, 0, 0, 10)
    lay.setSpacing(16)

    _build_archetype_card(page, lay)
    _build_rings_card(page, lay)
    _build_coaching_row(page, lay)
    _build_indicators_row(page, lay)
    _build_crutch_panel(page, lay)

    page.coach_container = QFrame()
    page.coach_container.setVisible(False)
    page.coach_focus_lbl = QLabel("")
    page.coach_drill_title_lbl = QLabel("")
    page.coach_tip_lbl = QLabel("")
    page.coach_drill_lbl = QLabel("")

    scroll.setWidget(container)
    return scroll


def _build_archetype_card(page, lay):
    page.archetype_card = QFrame()
    page.archetype_card.setObjectName("ArchetypeCard")
    arch_lay = QHBoxLayout(page.archetype_card)
    arch_lay.setContentsMargins(24, 20, 24, 20)
    arch_lay.setSpacing(20)

    badge_lay = QVBoxLayout()
    badge_lay.setSpacing(8)
    page.archetype_level_badge = QLabel("LVL --")
    page.archetype_level_badge.setObjectName("ArchetypeLevelBadge")
    page.archetype_level_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
    page.archetype_level_badge.setFixedSize(70, 70)
    page.xp_progress_lbl = QLabel("0 XP")
    page.xp_progress_lbl.setObjectName("Subtitle")
    page.xp_progress_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    page.xp_progress_bar = QProgressBar()
    page.xp_progress_bar.setFixedHeight(6)
    page.xp_progress_bar.setRange(0, 100)
    page.xp_progress_bar.setValue(0)
    page.xp_progress_bar.setTextVisible(False)
    page.xp_progress_bar.setStyleSheet(
        f"QProgressBar {{ background: rgba(255, 255, 255, 0.1); border: none; border-radius: 3px; }}"
        f"QProgressBar::chunk {{ background: {CLR_ACCENT}; border-radius: 3px; }}"
    )
    badge_lay.addWidget(page.archetype_level_badge, 0, Qt.AlignmentFlag.AlignCenter)
    badge_lay.addWidget(page.xp_progress_lbl)
    badge_lay.addWidget(page.xp_progress_bar)
    badge_lay.addStretch()

    details_lay = QVBoxLayout()
    details_lay.setSpacing(6)
    header_row = QHBoxLayout()
    page.archetype_icon_lbl = QLabel("🧭")
    page.archetype_icon_lbl.setStyleSheet("font-size: 24px; background: transparent;")
    title_block = QVBoxLayout()
    title_block.setSpacing(2)
    page.archetype_name_lbl = QLabel("Speech Archetype Loading...")
    page.archetype_name_lbl.setObjectName("SectionTitle")
    page.archetype_name_lbl.setStyleSheet("font-size: 16px; font-weight: 700;")
    page.archetype_title_lbl = QLabel("Analyze your speaking profile")
    page.archetype_title_lbl.setObjectName("Subtitle")
    title_block.addWidget(page.archetype_name_lbl)
    title_block.addWidget(page.archetype_title_lbl)
    header_row.addWidget(page.archetype_icon_lbl, 0, Qt.AlignmentFlag.AlignVCenter)
    header_row.addLayout(title_block, 1)
    page.archetype_desc_lbl = QLabel("Record dictation sessions to unlock your vocal archetype and style classification.")
    page.archetype_desc_lbl.setObjectName("InsightText")
    page.archetype_desc_lbl.setWordWrap(True)
    page.pacing_feedback_lbl = QLabel("")
    page.pacing_feedback_lbl.setObjectName("SuggestionText")
    page.pacing_feedback_lbl.setWordWrap(True)
    details_lay.addLayout(header_row)
    details_lay.addWidget(page.archetype_desc_lbl)
    details_lay.addWidget(page.pacing_feedback_lbl)
    details_lay.addStretch()

    arch_lay.addLayout(badge_lay, 0)
    arch_lay.addLayout(details_lay, 1)
    lay.addWidget(page.archetype_card)


def _build_rings_card(page, lay):
    rings_card = QFrame()
    rings_card.setObjectName("InsightCard")
    rings_lay = QVBoxLayout(rings_card)
    rings_lay.setContentsMargins(20, 18, 20, 18)
    rings_lay.setSpacing(12)
    rings_lay.addLayout(page._section_title_row(
        "Delivery & Purity Metrics",
        "Clarity Score: ratio of clean words to total words spoken.\n"
        "Conciseness: how efficiently you express ideas (low repetition = high).\n"
        "Speech Purity: percentage of speech free from filler words (um, uh, like)."
    ))
    rings_sub = QLabel("Real-time analysis of clarity, structure, and speaking rhythm")
    rings_sub.setObjectName("Subtitle")
    rings_lay.addWidget(rings_sub)
    rings_row = QHBoxLayout()
    rings_row.setSpacing(24)
    page.clarity_ring = CircularProgress("Clarity Score", 0.0, "#86EFAC")
    page.conciseness_ring = CircularProgress("Conciseness", 0.0, "#93C5FD")
    page.filler_ring = CircularProgress("Speech Purity", 0.0, "#FCA5A5")
    rings_row.addWidget(page.clarity_ring)
    rings_row.addWidget(page.conciseness_ring)
    rings_row.addWidget(page.filler_ring)
    rings_lay.addLayout(rings_row)
    lay.addWidget(rings_card)


def _build_coaching_row(page, lay):
    coaching_row = QHBoxLayout()
    coaching_row.setSpacing(16)
    _build_col1(page, coaching_row)
    _build_col2(page, coaching_row)
    _build_col3_carousel(page, coaching_row)
    lay.addLayout(coaching_row)


def _build_col1(page, coaching_row):
    col1_card = QFrame()
    col1_card.setObjectName("InsightCard")
    col1_lay = QVBoxLayout(col1_card)
    col1_lay.setContentsMargins(20, 18, 20, 18)
    col1_lay.setSpacing(12)
    col1_lay.addWidget(_lbl("Linguistic & Cadence", "SectionTitle"))
    col1_lay.addWidget(_lbl("Pause efficiency and structural pacing", "Subtitle"))

    pe_widget = QWidget()
    pe_widget.setStyleSheet("background: transparent;")
    pe_lay = QVBoxLayout(pe_widget)
    pe_lay.setContentsMargins(0, 4, 0, 4)
    pe_lay.setSpacing(4)
    pe_lbl_row = QHBoxLayout()
    pe_title_lbl = QLabel("Pause Efficiency")
    pe_title_lbl.setObjectName("InsightText")
    pe_title_lbl.setStyleSheet("font-weight: 600; color: #E8E8EA; background: transparent;")
    page.pause_efficiency_val = QLabel("100.0%")
    page.pause_efficiency_val.setObjectName("SuggestionText")
    page.pause_efficiency_val.setStyleSheet("background: transparent; font-weight: bold; color: #86EFAC;")
    pe_lbl_row.addWidget(pe_title_lbl)
    pe_lbl_row.addStretch()
    pe_lbl_row.addWidget(page.pause_efficiency_val)
    page.pause_efficiency_progress = QProgressBar()
    page.pause_efficiency_progress.setFixedHeight(6)
    page.pause_efficiency_progress.setRange(0, 100)
    page.pause_efficiency_progress.setValue(100)
    page.pause_efficiency_progress.setTextVisible(False)
    page.pause_efficiency_progress.setStyleSheet(
        "QProgressBar { background: rgba(255, 255, 255, 0.1); border: none; border-radius: 3px; }"
        "QProgressBar::chunk { background: #86EFAC; border-radius: 3px; }"
    )
    pe_lay.addLayout(pe_lbl_row)
    pe_lay.addWidget(page.pause_efficiency_progress)
    col1_lay.addWidget(pe_widget)

    page.cadence_card = QFrame()
    page.cadence_card.setStyleSheet("background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 6px;")
    cadence_lay = QVBoxLayout(page.cadence_card)
    cadence_lay.setSpacing(4)
    cadence_lbl = QLabel("Speaking Cadence")
    cadence_lbl.setStyleSheet("font-size: 10px; color: #8E8E93; background: transparent;")
    cadence_val_lay = QHBoxLayout()
    page.cadence_rating_val = QLabel("Balanced Flow")
    page.cadence_rating_val.setStyleSheet("font-size: 14px; font-weight: bold; color: #93C5FD; background: transparent;")
    page.cadence_variety_val = QLabel("Variety: 0.0")
    page.cadence_variety_val.setStyleSheet("font-size: 11px; color: #8E8E93; background: transparent;")
    cadence_val_lay.addWidget(page.cadence_rating_val)
    cadence_val_lay.addStretch()
    cadence_val_lay.addWidget(page.cadence_variety_val)
    cadence_lay.addWidget(cadence_lbl)
    cadence_lay.addLayout(cadence_val_lay)
    col1_lay.addWidget(page.cadence_card)

    readability_widget = QWidget()
    readability_widget.setStyleSheet("background: transparent;")
    readability_lay = QVBoxLayout(readability_widget)
    readability_lay.setContentsMargins(0, 4, 0, 4)
    readability_lay.setSpacing(4)
    readability_lbl_row = QHBoxLayout()
    readability_title_lbl = QLabel("Readability Level")
    readability_title_lbl.setObjectName("InsightText")
    readability_title_lbl.setStyleSheet("font-weight: 600; color: #E8E8EA; background: transparent;")
    page.readability_grade_val = QLabel("Standard Conversational")
    page.readability_grade_val.setObjectName("SuggestionText")
    page.readability_grade_val.setStyleSheet("background: transparent; font-weight: bold; color: #C084FC;")
    readability_lbl_row.addWidget(readability_title_lbl)
    readability_lbl_row.addStretch()
    readability_lbl_row.addWidget(page.readability_grade_val)
    page.readability_desc_lbl = QLabel("Highly accessible standard speech structure.")
    page.readability_desc_lbl.setObjectName("Subtitle")
    page.readability_desc_lbl.setStyleSheet("background: transparent; font-size: 11px;")
    page.readability_desc_lbl.setWordWrap(True)
    readability_lay.addLayout(readability_lbl_row)
    readability_lay.addWidget(page.readability_desc_lbl)
    col1_lay.addWidget(readability_widget)
    col1_lay.addStretch()
    coaching_row.addWidget(col1_card, 1)


def _build_col2(page, coaching_row):
    col2_card = QFrame()
    col2_card.setObjectName("InsightCard")
    col2_lay = QVBoxLayout(col2_card)
    col2_lay.setContentsMargins(20, 18, 20, 18)
    col2_lay.setSpacing(12)
    col2_lay.addLayout(page._section_title_row(
        "Speaking Tone",
        "Tone dimensions are calculated from keyword patterns in your dictations:\n"
        "\u2022 Confident: assertive verbs, definitive statements\n"
        "\u2022 Thoughtful: hedging words, reflective phrases\n"
        "\u2022 Warm: inclusive language, collaborative phrases\n"
        "\u2022 Technical: jargon density, domain-specific terminology"
    ))
    col2_lay.addWidget(_lbl("Linguistic dimension percentages", "Subtitle"))

    def make_tone_row(name, color_hex):
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        row_l = QVBoxLayout(w)
        row_l.setContentsMargins(0, 2, 0, 2)
        row_l.setSpacing(4)
        lbl_row = QHBoxLayout()
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("font-size: 11px; font-weight: bold; color: #E8E8EA; background: transparent;")
        lbl_val = QLabel("0.0%")
        lbl_val.setStyleSheet("font-size: 11px; font-weight: bold; color: #8E8E93; background: transparent;")
        lbl_row.addWidget(lbl_name)
        lbl_row.addStretch()
        lbl_row.addWidget(lbl_val)
        p_bar = QProgressBar()
        p_bar.setFixedHeight(6)
        p_bar.setRange(0, 100)
        p_bar.setValue(0)
        p_bar.setTextVisible(False)
        p_bar.setStyleSheet(
            "QProgressBar { background: rgba(255, 255, 255, 0.1); border: none; border-radius: 3px; }"
            f"QProgressBar::chunk {{ background: {color_hex}; border-radius: 3px; }}"
        )
        row_l.addLayout(lbl_row)
        row_l.addWidget(p_bar)
        return w, p_bar, lbl_val

    w_conf, page.tone_confident_progress, page.tone_confident_val = make_tone_row("Confident & Decisive", "#86EFAC")
    w_thou, page.tone_thoughtful_progress, page.tone_thoughtful_val = make_tone_row("Thoughtful & Deliberative", "#93C5FD")
    w_warm, page.tone_warm_progress, page.tone_warm_val = make_tone_row("Warm & Collaborative", "#FCA5A5")
    w_tech, page.tone_technical_progress, page.tone_technical_val = make_tone_row("Technical & Analytical", "#C084FC")
    col2_lay.addWidget(w_conf)
    col2_lay.addWidget(w_thou)
    col2_lay.addWidget(w_warm)
    col2_lay.addWidget(w_tech)
    col2_lay.addStretch()
    coaching_row.addWidget(col2_card, 1)


def _build_col3_carousel(page, coaching_row):
    col3_card = QFrame()
    col3_card.setObjectName("InsightCard")
    col3_lay = QVBoxLayout(col3_card)
    col3_lay.setContentsMargins(20, 18, 20, 18)
    col3_lay.setSpacing(10)

    col3_header = QHBoxLayout()
    col3_header.setSpacing(8)
    col3_title_block = QVBoxLayout()
    col3_title_block.setSpacing(2)
    col3_title_block.addWidget(_lbl("Vocal Drills", "SectionTitle"))
    page.carousel_subtitle = QLabel("Personalized bottleneck drill")
    page.carousel_subtitle.setObjectName("Subtitle")
    col3_title_block.addWidget(page.carousel_subtitle)
    col3_header.addLayout(col3_title_block, 1)

    nav_frame = QFrame()
    nav_frame.setStyleSheet("background: transparent;")
    nav_btn_lay = QHBoxLayout(nav_frame)
    nav_btn_lay.setContentsMargins(0, 0, 0, 0)
    nav_btn_lay.setSpacing(6)
    _nav_btn_style = (
        "QPushButton { background: rgba(255, 255, 255, 0.08); color: #A0A0A5; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 14px; font-size: 16px; font-weight: bold; }"
        "QPushButton:hover { background: rgba(255, 255, 255, 0.14); color: #F0F0F2; border-color: rgba(255, 255, 255, 0.2); }"
    )
    page.carousel_prev_btn = QPushButton("‹")
    page.carousel_prev_btn.setFixedSize(28, 28)
    page.carousel_prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    page.carousel_prev_btn.setStyleSheet(_nav_btn_style)
    page.carousel_page_lbl = QLabel("1 / 3")
    page.carousel_page_lbl.setStyleSheet("font-size: 10px; font-weight: 600; color: #8E8E93; background: transparent;")
    page.carousel_page_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    page.carousel_page_lbl.setFixedWidth(32)
    page.carousel_next_btn = QPushButton("›")
    page.carousel_next_btn.setFixedSize(28, 28)
    page.carousel_next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    page.carousel_next_btn.setStyleSheet(_nav_btn_style)
    nav_btn_lay.addWidget(page.carousel_prev_btn)
    nav_btn_lay.addWidget(page.carousel_page_lbl)
    nav_btn_lay.addWidget(page.carousel_next_btn)
    col3_header.addWidget(nav_frame, 0, Qt.AlignmentFlag.AlignVCenter)
    col3_lay.addLayout(col3_header)

    page.drill_carousel = QStackedWidget()
    page.drill_carousel.setStyleSheet("background: transparent;")
    page._drill_slides = []
    for i in range(3):
        slide = page._build_drill_slide(
            icon="🎯" if i == 0 else ("🫁" if i == 1 else "🎤"),
            title="Loading..." if i == 0 else ("Vocal Warmup" if i == 1 else "Rhetorical Delivery"),
            subtitle="Analyzing your speech..." if i == 0 else ("Resonance exercises" if i == 1 else "Advanced techniques"),
            drill="Record dictation sessions to unlock personalized drills.",
            metric_name="-", metric_value="-", target="-",
        )
        page._drill_slides.append(slide)
        page.drill_carousel.addWidget(slide["frame"])
    col3_lay.addWidget(page.drill_carousel, 1)
    page.carousel_prev_btn.clicked.connect(page._carousel_prev)
    page.carousel_next_btn.clicked.connect(page._carousel_next)
    coaching_row.addWidget(col3_card, 1)


def _build_indicators_row(page, lay):
    indicators_row = QHBoxLayout()
    indicators_row.setSpacing(16)

    hes_card = QFrame()
    hes_card.setObjectName("InsightCard")
    hes_lay = QVBoxLayout(hes_card)
    hes_lay.setContentsMargins(20, 16, 20, 16)
    hes_lay.setSpacing(8)
    hes_lay.addWidget(_lbl("Hesitation Rate", "SectionTitle"))
    hes_lay.addWidget(_lbl("Filler words vs natural pauses", "Subtitle"))
    hes_metric = QHBoxLayout()
    page.hesitation_val = QLabel("0.0%")
    page.hesitation_val.setStyleSheet("font-size: 28px; font-weight: 800; color: #86EFAC; background: transparent;")
    hes_desc_block = QVBoxLayout()
    hes_desc_block.setSpacing(2)
    page.hesitation_desc = QLabel("Low hesitation (confident flow)")
    page.hesitation_desc.setStyleSheet("font-size: 11px; color: #A0A0A5; background: transparent;")
    page.hesitation_desc.setWordWrap(True)
    hes_desc_block.addWidget(page.hesitation_desc)
    hes_desc_block.addStretch()
    hes_metric.addWidget(page.hesitation_val, 0, Qt.AlignmentFlag.AlignTop)
    hes_metric.addLayout(hes_desc_block, 1)
    hes_lay.addLayout(hes_metric)
    page.hesitation_progress = QProgressBar()
    page.hesitation_progress.setFixedHeight(6)
    page.hesitation_progress.setRange(0, 100)
    page.hesitation_progress.setValue(0)
    page.hesitation_progress.setTextVisible(False)
    page.hesitation_progress.setStyleSheet(
        "QProgressBar { background: rgba(255, 255, 255, 0.1); border: none; border-radius: 3px; }"
        "QProgressBar::chunk { background: #86EFAC; border-radius: 3px; }"
    )
    hes_lay.addWidget(page.hesitation_progress)
    hes_lay.addStretch()
    indicators_row.addWidget(hes_card, 1)

    pace_card = QFrame()
    pace_card.setObjectName("InsightCard")
    pace_lay = QVBoxLayout(pace_card)
    pace_lay.setContentsMargins(20, 16, 20, 16)
    pace_lay.setSpacing(8)
    pace_lay.addWidget(_lbl("Speaking Pace", "SectionTitle"))
    pace_lay.addWidget(_lbl("Sentence structure analysis", "Subtitle"))
    pace_indicator = QHBoxLayout()
    pace_indicator.setSpacing(6)
    page._pacing_zones = {}
    for zone_name, zone_color in [("Slow", "#93C5FD"), ("Optimal", "#86EFAC"), ("Fast", "#FCA5A5")]:
        zone_frame = QFrame()
        zone_frame.setStyleSheet("background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px;")
        zone_ly = QVBoxLayout(zone_frame)
        zone_ly.setContentsMargins(10, 10, 10, 10)
        zone_ly.setSpacing(4)
        zone_lbl = QLabel(zone_name)
        zone_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        zone_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #5A5A60; background: transparent;")
        zone_dot = QLabel("●")
        zone_dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        zone_dot.setStyleSheet("font-size: 18px; color: #3A3A40; background: transparent;")
        zone_ly.addWidget(zone_dot)
        zone_ly.addWidget(zone_lbl)
        page._pacing_zones[zone_name] = {"frame": zone_frame, "label": zone_lbl, "dot": zone_dot, "color": zone_color}
        pace_indicator.addWidget(zone_frame, 1)
    pace_lay.addLayout(pace_indicator)
    page.pacing_desc = QLabel("Record more sessions to classify your pace.")
    page.pacing_desc.setStyleSheet("font-size: 11px; color: #8E8E93; background: transparent;")
    page.pacing_desc.setWordWrap(True)
    pace_lay.addWidget(page.pacing_desc)
    pace_lay.addStretch()
    indicators_row.addWidget(pace_card, 1)

    hedge_card = QFrame()
    hedge_card.setObjectName("InsightCard")
    hedge_lay = QVBoxLayout(hedge_card)
    hedge_lay.setContentsMargins(20, 16, 20, 16)
    hedge_lay.setSpacing(8)
    hedge_lay.addWidget(_lbl("Hedging Index", "SectionTitle"))
    hedge_lay.addWidget(_lbl("Weak language detection", "Subtitle"))
    hedge_metric = QHBoxLayout()
    page.hedging_val = QLabel("0.0%")
    page.hedging_val.setStyleSheet("font-size: 28px; font-weight: 800; color: #C084FC; background: transparent;")
    hedge_detail = QVBoxLayout()
    hedge_detail.setSpacing(2)
    page.hedging_desc = QLabel("No weak language detected yet.")
    page.hedging_desc.setStyleSheet("font-size: 11px; color: #A0A0A5; background: transparent;")
    page.hedging_desc.setWordWrap(True)
    page.hedging_count_lbl = QLabel("0 hedge words found")
    page.hedging_count_lbl.setStyleSheet("font-size: 10px; color: #8E8E93; background: transparent;")
    hedge_detail.addWidget(page.hedging_desc)
    hedge_detail.addWidget(page.hedging_count_lbl)
    hedge_detail.addStretch()
    hedge_metric.addWidget(page.hedging_val, 0, Qt.AlignmentFlag.AlignTop)
    hedge_metric.addLayout(hedge_detail, 1)
    hedge_lay.addLayout(hedge_metric)
    hedge_lay.addStretch()
    indicators_row.addWidget(hedge_card, 1)

    lay.addLayout(indicators_row)


def _build_crutch_panel(page, lay):
    crutch_panel = QFrame()
    crutch_panel.setObjectName("InsightCard")
    cp_lay = QVBoxLayout(crutch_panel)
    cp_lay.setContentsMargins(20, 18, 20, 18)
    cp_lay.setSpacing(12)

    cp_header = QHBoxLayout()
    cp_title_block = QVBoxLayout()
    cp_title_block.setSpacing(2)
    cp_title_block.addWidget(_lbl("Verbal Crutch & Synonym Coach", "SectionTitle"))
    cp_title_block.addWidget(_lbl("Replace filler habits with powerful alternatives", "Subtitle"))
    cp_header.addLayout(cp_title_block, 1)

    page.crutch_warning_card = QFrame()
    page.crutch_warning_card.setStyleSheet(
        "background: rgba(134, 239, 172, 0.1); border: 1px solid rgba(134, 239, 172, 0.3); border-radius: 6px;"
    )
    cw_badge_lay = QHBoxLayout(page.crutch_warning_card)
    cw_badge_lay.setContentsMargins(8, 4, 8, 4)
    cw_badge_lay.setSpacing(6)
    cw_icon = QLabel("✨")
    cw_icon.setObjectName("cw_icon")
    cw_icon.setStyleSheet("font-size: 12px; background: transparent;")
    cw_title_lbl = QLabel("Verbal Purity High")
    cw_title_lbl.setObjectName("cw_title")
    cw_title_lbl.setStyleSheet("font-size: 10px; font-weight: bold; color: #86EFAC; background: transparent;")
    cw_badge_lay.addWidget(cw_icon)
    cw_badge_lay.addWidget(cw_title_lbl)
    cp_header.addWidget(page.crutch_warning_card, 0, Qt.AlignmentFlag.AlignVCenter)
    cp_lay.addLayout(cp_header)

    page.cw_desc_lbl = QLabel("Excellent! No major filler or crutch words detected.")
    page.cw_desc_lbl.setObjectName("InsightText")
    page.cw_desc_lbl.setStyleSheet("font-size: 12px; color: #A0A0A5; background: transparent;")
    page.cw_desc_lbl.setWordWrap(True)
    cp_lay.addWidget(page.cw_desc_lbl)

    page.synonym_grid_container = QVBoxLayout()
    page.synonym_grid_container.setSpacing(6)
    cp_lay.addLayout(page.synonym_grid_container)

    lay.addWidget(crutch_panel)


def _lbl(text, obj_name):
    l = QLabel(text)
    l.setObjectName(obj_name)
    return l
