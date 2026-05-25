from __future__ import annotations

"""
Updater functions for InsightsPage.
Separated to keep insights_page.py under 500 lines.
"""

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _clear_layout(layout):
    if layout is None:
        return
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
        elif child.layout():
            _clear_layout(child.layout())


def _clear_grid(grid):
    if grid is None:
        return
    while grid.count():
        item = grid.takeAt(0)
        if item.widget():
            item.widget().deleteLater()


# ---------------------------------------------------------------------------
# Main dashboard update
# ---------------------------------------------------------------------------


def update_from_dashboard(page, words_or_dashboard, wpm=None):
    """Update all InsightsPage widgets from a dashboard dict or raw values."""
    if isinstance(words_or_dashboard, dict):
        today = words_or_dashboard.get("today", {})
        lifetime = words_or_dashboard.get("lifetime", {})
        today_words = int(today.get("words", 0))
        today_wpm = int(today.get("wpm", 0))
        lifetime_words = int(lifetime.get("words", 0))
        daily_counts = words_or_dashboard.get("daily_counts", {})
        enhanced = words_or_dashboard.get("enhanced", {})
        achievements = words_or_dashboard.get("achievements", [])
        top_phrases = words_or_dashboard.get("top_phrases", [])
        app_usage = words_or_dashboard.get("app_usage", {})
    else:
        today_words = int(words_or_dashboard or 0)
        today_wpm = int(wpm or 0)
        lifetime_words = int(words_or_dashboard or 0)
        daily_counts = {}
        enhanced = {}
        achievements = []
        top_phrases = []
        app_usage = {}

    streak_val = 0
    if isinstance(enhanced, dict):
        streak_val = enhanced.get("streak", {}).get("daily_streak", 0)

    page._last_today_words = today_words
    page._insights_targets = [today_words, today_wpm, lifetime_words, streak_val]

    if not page._insights_anim_timer.isActive():
        if hasattr(page, "total_words_card"):
            page.total_words_card.value_label.setText(f"{today_words:,}")
        if hasattr(page, "wpm_card"):
            page.wpm_card.value_label.setText(f"{today_wpm}")
        if hasattr(page, "session_card"):
            page.session_card.value_label.setText(f"{lifetime_words:,}")
        if hasattr(page, "streak_card"):
            page.streak_card.value_label.setText(
                f"{streak_val} {'day' if streak_val == 1 else 'days'}"
            )

    if hasattr(page, "_insights_speedometer") and not page._insights_anim_timer.isActive():
        page._insights_speedometer.set_value(today_words)

    if (
        hasattr(page, "daily_challenge_desc")
        and hasattr(page, "daily_challenge_progress")
        and hasattr(page, "daily_challenge_ring")
    ):
        if isinstance(enhanced, dict) and enhanced.get("daily_challenge"):
            dc = enhanced["daily_challenge"]
            desc = getattr(dc, "description", None) or (
                dc.get("description") if isinstance(dc, dict) else "Transcribe 500 words today"
            )
            target = getattr(dc, "target", None) or (
                dc.get("target") if isinstance(dc, dict) else 500
            )
            progress = getattr(dc, "progress", None) or (
                dc.get("progress") if isinstance(dc, dict) else 0
            )
            page.daily_challenge_desc.setText(desc)
            page.daily_challenge_progress.setText(f"{progress:,} / {target:,} words")
            pct = min(100.0, (progress / max(1, target)) * 100.0)
            page.daily_challenge_ring.setPercentage(pct)

    if hasattr(page, "heatmap_grid") and daily_counts:
        page.heatmap_grid.setDailyCounts(daily_counts)

    _update_app_breakdown(page, app_usage)
    _update_archetype(page, enhanced)
    _update_rings(page, enhanced)
    _update_vocab(page, enhanced)
    _update_conciseness(page, enhanced)
    _update_productivity(page, enhanced)
    _update_crutch_warning(page, enhanced)
    _update_diurnal(page, enhanced)
    _update_trends(page, enhanced)

    if isinstance(enhanced, dict) and "advanced_coaching" in enhanced:
        update_advanced_coaching(page, enhanced["advanced_coaching"])

    _update_fillers_flow(page, top_phrases)
    _update_achievements(page, achievements)
    _update_drill_slides(page, enhanced)


# ---------------------------------------------------------------------------
# Section updaters
# ---------------------------------------------------------------------------


def _update_app_breakdown(page, app_usage):
    if not hasattr(page, "app_breakdown_layout"):
        return
    # Only rebuild and animate when the data actually changes.
    prev = getattr(page, "_last_app_usage", None)
    if prev == app_usage:
        return
    page._last_app_usage = dict(app_usage) if app_usage else {}

    _clear_layout(page.app_breakdown_layout)
    if app_usage:
        max_usage = max(app_usage.values()) if app_usage else 1
        for app_name, count in sorted(app_usage.items(), key=lambda x: x[1], reverse=True):
            row_widget = QWidget()
            row_lay = QHBoxLayout(row_widget)
            row_lay.setContentsMargins(0, 0, 0, 0)
            row_lay.setSpacing(10)
            lbl_name = QLabel(app_name)
            lbl_name.setObjectName("InsightText")
            lbl_name.setStyleSheet("font-weight: 500; min-width: 80px; background: transparent;")
            prog = QProgressBar()
            prog.setFixedHeight(6)
            prog.setRange(0, max_usage)
            prog.setValue(0)
            prog.setTextVisible(False)
            prog.setStyleSheet(
                "QProgressBar { background: rgba(255, 255, 255, 0.1); border: none; border-radius: 3px; }"
                "QProgressBar::chunk { background: #86EFAC; border-radius: 3px; }"
            )
            _anim = QPropertyAnimation(prog, b"value")
            _anim.setDuration(900)
            _anim.setStartValue(0)
            _anim.setEndValue(count)
            _anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            _anim.start()
            prog._bar_anim = _anim  # keep reference alive
            lbl_val = QLabel(f"{count} {'session' if count == 1 else 'sessions'}")
            lbl_val.setObjectName("SuggestionText")
            lbl_val.setStyleSheet("min-width: 70px; text-align: right; background: transparent;")
            row_lay.addWidget(lbl_name)
            row_lay.addWidget(prog, 1)
            row_lay.addWidget(lbl_val)
            page.app_breakdown_layout.addWidget(row_widget)
    else:
        empty = QLabel("No application usage tracked yet.")
        empty.setObjectName("InsightText")
        empty.setStyleSheet("background: transparent;")
        page.app_breakdown_layout.addWidget(empty)


def _update_archetype(page, enhanced):
    if not (hasattr(page, "archetype_level_badge") and isinstance(enhanced, dict)):
        return
    persona = enhanced.get("persona", {})
    profile = enhanced.get("speech_profile", {})
    level = persona.get("level", 1) if isinstance(persona, dict) else 1
    xp = persona.get("xp", 0) if isinstance(persona, dict) else 0
    xp_in_level = xp % 100
    name = (
        profile.get("archetype_name", "The Observer")
        if isinstance(profile, dict)
        else "The Observer"
    )
    title = (
        profile.get("archetype_title", "Silent Voice")
        if isinstance(profile, dict)
        else "Silent Voice"
    )
    desc = profile.get("archetype_description", "") if isinstance(profile, dict) else ""
    pacing = profile.get("pacing_feedback", "") if isinstance(profile, dict) else ""
    icon = profile.get("archetype_icon", "🧭") if isinstance(profile, dict) else "🧭"
    page.archetype_level_badge.setText(f"LVL {level}")
    page.xp_progress_lbl.setText(f"{xp_in_level} / 100 XP")
    page.xp_progress_bar.setValue(xp_in_level)
    page.archetype_name_lbl.setText(name)
    page.archetype_title_lbl.setText(title)
    page.archetype_icon_lbl.setText(icon)
    page.archetype_desc_lbl.setText(desc)
    page.pacing_feedback_lbl.setText(pacing)


def _update_rings(page, enhanced):
    if not (
        hasattr(page, "clarity_ring")
        and hasattr(page, "conciseness_ring")
        and hasattr(page, "filler_ring")
    ):
        return
    latest = enhanced.get("latest_session", {}) if isinstance(enhanced, dict) else {}
    clarity = latest.get("clarity_score", 0.0)
    conciseness = latest.get("conciseness_score", 0.0)
    filler_ratio = latest.get("filler_ratio", 0.0)
    purity = max(0.0, 100.0 - filler_ratio * 100.0)
    page.clarity_ring.setPercentage(float(clarity))
    page.conciseness_ring.setPercentage(float(conciseness))
    page.filler_ring.setPercentage(float(purity))


def _update_vocab(page, enhanced):
    if not (
        hasattr(page, "vocab_val_lbl")
        and hasattr(page, "vocab_progress")
        and hasattr(page, "vocab_desc")
    ):
        return
    lex = enhanced.get("lexical_diversity", 1.0) if isinstance(enhanced, dict) else 1.0
    pct = lex * 100.0
    page.vocab_val_lbl.setText(f"{pct:.1f}%")
    page.vocab_progress.setValue(int(pct))
    if lex >= 0.7:
        desc = "Rich and diverse vocabulary usage."
    elif lex >= 0.5:
        desc = "Standard conversational vocabulary variety."
    else:
        desc = "Repetitive phrasing. Try introducing more varied expressions."
    page.vocab_desc.setText(desc)


def _update_conciseness(page, enhanced):
    if not (
        hasattr(page, "concise_val_lbl")
        and hasattr(page, "concise_progress")
        and hasattr(page, "concise_desc")
    ):
        return
    latest = enhanced.get("latest_session", {}) if isinstance(enhanced, dict) else {}
    concise = latest.get("conciseness_score", 0.0)
    page.concise_val_lbl.setText(f"{concise:.1f}%")
    page.concise_progress.setValue(int(concise))
    if concise >= 90:
        desc = "Ultra-efficient speaking style with low redundancy."
    elif concise >= 70:
        desc = "Clear and structured dictation flow."
    else:
        desc = "Wordy dictation. Try speaking more concisely."
    page.concise_desc.setText(desc)


def _update_productivity(page, enhanced):
    if not (hasattr(page, "saved_multiplier_lbl") and hasattr(page, "saved_duration_lbl")):
        return
    prod = enhanced.get("productivity", {}) if isinstance(enhanced, dict) else {}
    mult = prod.get("typing_multiplier", 3.5)
    saved_mins = prod.get("time_saved_minutes", 0.0)
    page.saved_multiplier_lbl.setText(f"{mult}x Faster")
    page.saved_duration_lbl.setText(f"Saved {saved_mins:.1f} mins compared to typing")


def _update_crutch_warning(page, enhanced):
    if not (hasattr(page, "crutch_warning_card") and hasattr(page, "cw_desc_lbl")):
        return
    crutch_words = enhanced.get("crutch_words", []) if isinstance(enhanced, dict) else []
    active_crutches = [c for c in crutch_words if c.get("count", 0) > 0]
    if active_crutches:
        top_crutch = active_crutches[0]
        phrase = top_crutch.get("phrase", "")
        count = top_crutch.get("count", 0)
        page.cw_desc_lbl.setText(
            f"Your top crutch word is '{phrase}' used {count} times. Try pausing instead."
        )
        page.crutch_warning_card.setStyleSheet(
            "background: rgba(248, 113, 113, 0.1); border: 1px solid rgba(248, 113, 113, 0.3); border-radius: 6px;"
        )
        title_lbl = page.crutch_warning_card.findChild(QLabel, "cw_title")
        if title_lbl:
            title_lbl.setStyleSheet(
                "font-size: 10px; font-weight: bold; color: #F87171; background: transparent; border: none;"
            )
            title_lbl.setText("Crutch Word Warning")
        icon_lbl = page.crutch_warning_card.findChild(QLabel, "cw_icon")
        if icon_lbl:
            icon_lbl.setText("⚠️")
    else:
        page.cw_desc_lbl.setText(
            "Excellent! No major filler or crutch words detected in your recent speaking."
        )
        page.crutch_warning_card.setStyleSheet(
            "background: rgba(134, 239, 172, 0.1); border: 1px solid rgba(134, 239, 172, 0.3); border-radius: 6px;"
        )
        title_lbl = page.crutch_warning_card.findChild(QLabel, "cw_title")
        if title_lbl:
            title_lbl.setStyleSheet(
                "font-size: 10px; font-weight: bold; color: #86EFAC; background: transparent; border: none;"
            )
            title_lbl.setText("Verbal Purity High")
        icon_lbl = page.crutch_warning_card.findChild(QLabel, "cw_icon")
        if icon_lbl:
            icon_lbl.setText("✨")


def _update_diurnal(page, enhanced):
    if not (hasattr(page, "diurnal_bars") and hasattr(page, "diurnal_desc")):
        return
    active_hours = enhanced.get("active_hours", {}) if isinstance(enhanced, dict) else {}
    percentages = active_hours.get("percentages", {})
    desc = active_hours.get("description", "Active times help optimize schedule.")
    page.diurnal_desc.setText(desc)
    for period, (p_bar, lbl_val) in page.diurnal_bars.items():
        val = percentages.get(period, 0.0)
        p_bar.setValue(int(val))
        lbl_val.setText(f"{val:.1f}%")


def _update_trends(page, enhanced):
    if not hasattr(page, "trend_chart"):
        return
    trends = enhanced.get("trends", {}) if isinstance(enhanced, dict) else {}
    page._trend_labels = trends.get("labels", [])
    page._trend_wpm = trends.get("wpm", [])
    page._trend_clarity = trends.get("clarity", [])
    page.trend_chart.setTrendData(page._trend_labels, page._trend_wpm, page._trend_clarity)


def _update_fillers_flow(page, top_phrases):
    if not hasattr(page, "fillers_flow"):
        return
    _clear_layout(page.fillers_flow)
    if top_phrases:
        for phrase_insight in top_phrases:
            phrase = getattr(phrase_insight, "phrase", None) or (
                phrase_insight.get("phrase") if isinstance(phrase_insight, dict) else ""
            )
            count = getattr(phrase_insight, "count", None) or (
                phrase_insight.get("count") if isinstance(phrase_insight, dict) else 0
            )
            rank = getattr(phrase_insight, "rank", None) or (
                phrase_insight.get("rank") if isinstance(phrase_insight, dict) else 1
            )
            row_widget = QWidget()
            row_lay = QHBoxLayout(row_widget)
            row_lay.setContentsMargins(4, 4, 4, 4)
            row_lay.setSpacing(12)
            lbl_rank = QLabel(str(rank))
            lbl_rank.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_rank.setFixedSize(20, 20)
            lbl_rank.setStyleSheet(
                "background: rgba(255, 255, 255, 0.15); border-radius: 10px; color: #8E8E93; font-weight: bold; font-size: 10px;"
            )
            lbl_phrase = QLabel(phrase)
            lbl_phrase.setObjectName("InsightText")
            lbl_phrase.setStyleSheet("font-weight: 600; color: #E8E8EA; background: transparent;")
            lbl_count = QLabel(f"{count} times")
            lbl_count.setObjectName("SuggestionText")
            lbl_count.setStyleSheet("color: #8E8E93; background: transparent;")
            row_lay.addWidget(lbl_rank)
            row_lay.addWidget(lbl_phrase, 1)
            row_lay.addWidget(lbl_count)
            page.fillers_flow.addWidget(row_widget)
    else:
        empty = QLabel("No verbal habits detected yet.")
        empty.setObjectName("InsightText")
        empty.setStyleSheet("background: transparent;")
        page.fillers_flow.addWidget(empty)


def _update_achievements(page, achievements):
    if not (hasattr(page, "achievements_layout") and achievements):
        return
    _clear_grid(page.achievements_layout)
    row = col = 0
    for ach in achievements:
        name = getattr(ach, "name", None) or (ach.get("name") if isinstance(ach, dict) else "")
        desc = getattr(ach, "description", None) or (
            ach.get("description") if isinstance(ach, dict) else ""
        )
        icon = getattr(ach, "icon", None) or (ach.get("icon") if isinstance(ach, dict) else "🏆")
        unlocked = getattr(ach, "unlocked", None) or (
            ach.get("unlocked") if isinstance(ach, dict) else False
        )
        ach_item = QFrame()
        ach_item.setObjectName("AchievementCard")
        ach_item.setProperty("unlocked", "true" if unlocked else "false")
        item_lay = QHBoxLayout(ach_item)
        item_lay.setContentsMargins(8, 8, 8, 8)
        item_lay.setSpacing(10)
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet(
            f"font-size: 20px; background: transparent;{'opacity: 0.3;' if not unlocked else ''}"
        )
        det = QVBoxLayout()
        det.setSpacing(2)
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {'#86EFAC' if unlocked else '#8E8E93'}; background: transparent;"
        )
        lbl_desc = QLabel(desc)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet(
            f"font-size: 9px; color: {'#C5C5C7' if unlocked else '#5A5A60'}; background: transparent;"
        )
        det.addWidget(lbl_name)
        det.addWidget(lbl_desc)
        det.addStretch()
        item_lay.addWidget(lbl_icon, 0, Qt.AlignmentFlag.AlignTop)
        item_lay.addLayout(det, 1)
        border_color = "rgba(134, 239, 172, 0.8)" if unlocked else "rgba(255, 255, 255, 0.08)"
        bg_color = "rgba(134, 239, 172, 0.15)" if unlocked else "rgba(255, 255, 255, 0.05)"
        ach_item.setStyleSheet(
            f"QFrame {{ background: {bg_color}; border: 1px solid {border_color}; border-radius: 6px; }}"
        )
        page.achievements_layout.addWidget(ach_item, row, col)
        col += 1
        if col > 1:
            col = 0
            row += 1


def _update_drill_slides(page, enhanced):
    if not (hasattr(page, "_drill_slides") and isinstance(enhanced, dict)):
        return
    vocal_drills = enhanced.get("vocal_drills", [])
    for i, slide in enumerate(page._drill_slides):
        if i < len(vocal_drills):
            d = vocal_drills[i]
            slide["icon_lbl"].setText(d.get("icon", "🎯"))
            slide["title_lbl"].setText(d.get("title", "-"))
            slide["subtitle_lbl"].setText(d.get("subtitle", ""))
            slide["drill_lbl"].setText(d.get("drill", ""))
            slide["metric_lbl"].setText(
                f"{d.get('metric_name', '-')}: {d.get('metric_value', '-')}"
            )
            slide["target_lbl"].setText(d.get("target", ""))
    if hasattr(page, "carousel_page_lbl"):
        page.carousel_page_lbl.setText(f"1 / {page.drill_carousel.count()}")


# ---------------------------------------------------------------------------
# Advanced coaching
# ---------------------------------------------------------------------------


def update_advanced_coaching(page, adv: dict):
    """Update advanced speech coaching widgets from the coaching dict."""
    if hasattr(page, "pause_efficiency_val") and hasattr(page, "pause_efficiency_progress"):
        pe_pct = adv.get("pause_efficiency_pct", 100.0)
        page.pause_efficiency_val.setText(f"{pe_pct:.1f}%")
        page.pause_efficiency_progress.setValue(int(pe_pct))

    if hasattr(page, "cadence_rating_val") and hasattr(page, "cadence_variety_val"):
        page.cadence_rating_val.setText(adv.get("cadence_rating", "Balanced Flow"))
        page.cadence_variety_val.setText(f"Variety: {adv.get('cadence_variety', 0.0):.1f}")

    if hasattr(page, "readability_grade_val") and hasattr(page, "readability_desc_lbl"):
        page.readability_grade_val.setText(adv.get("gunning_fog_grade", "Standard Conversational"))
        page.readability_desc_lbl.setText(adv.get("readability_desc", ""))

    tone_ratios = adv.get("tone_ratios", {})
    for attr, key, default in [
        ("tone_confident", "confident", 40.0),
        ("tone_thoughtful", "thoughtful", 30.0),
        ("tone_warm", "warm", 20.0),
        ("tone_technical", "technical", 10.0),
    ]:
        val = tone_ratios.get(key, default)
        if hasattr(page, f"{attr}_progress"):
            getattr(page, f"{attr}_progress").setValue(int(val))
        if hasattr(page, f"{attr}_val"):
            getattr(page, f"{attr}_val").setText(f"{val:.1f}%")

    if hasattr(page, "coach_container") and "speech_coach" in adv:
        sc = adv["speech_coach"]
        focus = sc.get("focus_title", "SILENT VOCAL PAUSES")
        page.coach_focus_lbl.setText(focus)
        page.coach_drill_title_lbl.setText(sc.get("drill_title", "The Golden Silence Drill"))
        page.coach_tip_lbl.setText(sc.get("tip", ""))
        page.coach_drill_lbl.setText(sc.get("drill", ""))
        if "FILLER" in focus or "ELIMINATING" in focus:
            border, bg, text = "rgba(248, 113, 113, 0.3)", "rgba(248, 113, 113, 0.08)", "#F87171"
        elif "RANGE" in focus or "VARIETY" in focus:
            border, bg, text = "rgba(192, 132, 252, 0.3)", "rgba(192, 132, 252, 0.08)", "#C084FC"
        elif "PACING" in focus or "SPEED" in focus:
            border, bg, text = "rgba(147, 197, 253, 0.3)", "rgba(147, 197, 253, 0.08)", "#93C5FD"
        elif "VOCABULARY" in focus or "PHRASING" in focus:
            border, bg, text = "rgba(253, 224, 71, 0.3)", "rgba(253, 224, 71, 0.08)", "#FDE047"
        else:
            border, bg, text = "rgba(134, 239, 172, 0.3)", "rgba(134, 239, 172, 0.08)", "#86EFAC"
        page.coach_container.setStyleSheet(
            f"QFrame {{ background: {bg}; border: 1.5px solid {border}; border-radius: 10px; }}"
        )
        page.coach_focus_lbl.setStyleSheet(
            f"font-size: 9px; font-weight: bold; color: {text}; letter-spacing: 0.5px; background: transparent; border: none;"
        )
