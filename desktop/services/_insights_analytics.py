from __future__ import annotations

import re
from typing import Any, Dict, List

from utils.text_metrics import calculate_text_metrics
from services._insights_models import CRUTCH_SYNONYMS


class InsightsAnalyticsMixin:
    """Analytics methods for EnhancedInsightsService.

    Expects ``self.session_store`` to be a SessionStore instance and
    ``self.get_lexical_diversity`` to be available (defined on the mixin itself).
    """

    def get_speech_profile(self) -> Dict:
        history = self.session_store.get_history(limit=1000)
        if not history:
            return {
                "archetype_name": "The Observer",
                "archetype_title": "Silent Voice",
                "archetype_description": "Not enough dictation history to analyze your style. Start dictating to unlock your archetype!",
                "archetype_icon": "🧭",
                "avg_wpm": 0,
                "pacing_feedback": "No data yet.",
                "filler_rate_pct": 0.0,
                "total_fillers": 0,
            }

        avg_wpm = int(sum(h.get("wpm", 0) for h in history) / len(history))
        avg_filler_ratio = sum(h.get("filler_ratio", 0) for h in history) / len(history)
        total_fillers = sum(h.get("filler_count", 0) for h in history)

        if avg_wpm > 150 and avg_filler_ratio < 0.05:
            name = "The Sprinter"
            title = "Dynamic Communicator"
            desc = "You speak at a rapid, high-energy pace with remarkable clarity. Your ideas flow seamlessly and you maintain strong audience engagement."
            icon = "⚡"
        elif avg_wpm > 140 and avg_filler_ratio >= 0.05:
            name = "The Storyteller"
            title = "Expressive Speaker"
            desc = "Your speaking speed is high and expressive, though punctuated by natural conversational habits. Your tone is engaging and highly accessible."
            icon = "🎙️"
        elif 110 <= avg_wpm <= 140 and avg_filler_ratio < 0.03:
            name = "The Laser Focus"
            title = "Executive Presenter"
            desc = "You deliver thoughts with precise, deliberate pacing and exceptionally low filler words. Highly professional and clear."
            icon = "🎯"
        elif 110 <= avg_wpm <= 140 and avg_filler_ratio >= 0.03:
            name = "The Conversationalist"
            title = "Balanced Speaker"
            desc = "You have a highly natural speaking speed, balancing spontaneous flow with clarity. Very relatable and easy to listen to."
            icon = "💬"
        else:
            name = "The Thinker"
            title = "Measured Communicator"
            desc = "You speak at a calm, methodical pace. You value accuracy and take time to structure your thoughts flawlessly."
            icon = "🧠"

        if avg_wpm > 150:
            pacing = "Fast-paced. Good for excitement, but try introducing silent gaps to let key points sink in."
        elif 120 <= avg_wpm <= 150:
            pacing = "Perfect rhythm. Conversational and highly professional speaking speed."
        else:
            pacing = "Measured delivery. Clear and deliberate, though you might try slightly increasing energy for dynamic pitches."

        return {
            "archetype_name": name,
            "archetype_title": title,
            "archetype_description": desc,
            "archetype_icon": icon,
            "avg_wpm": avg_wpm,
            "pacing_feedback": pacing,
            "filler_rate_pct": round(avg_filler_ratio * 100, 1),
            "total_fillers": total_fillers,
        }

    def get_crutch_words(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Scans raw dictations for verbal crutches like 'basically', 'actually', 'literally'."""
        history = self.session_store.get_history(limit=100)
        crutch_candidates = [
            "basically", "actually", "literally", "seriously",
            "obviously", "essentially", "you know", "i mean", "so",
        ]
        counts = {word: 0 for word in crutch_candidates}

        for h in history:
            text = (h.get("transcript_text") or "").lower()
            for word in crutch_candidates:
                counts[word] += len(re.findall(rf"\b{re.escape(word)}\b", text))

        sorted_crutches = sorted(counts.items(), key=lambda x: x[1], reverse=True)

        results = []
        for word, count in sorted_crutches:
            if count > 0:
                results.append({
                    "phrase": word,
                    "count": count,
                    "rank": len(results) + 1,
                    "synonyms": CRUTCH_SYNONYMS.get(word, ["[pause]"])
                })
        return results[:limit]

    def get_lexical_diversity(self) -> float:
        """Calculates speaking vocabulary richness (unique / total words)."""
        history = self.session_store.get_history(limit=15)
        if not history:
            return 1.0

        all_words = []
        for h in history:
            text = (h.get("transcript_text") or "").lower()
            words = re.findall(r"\b[\w']+\b", text)
            all_words.extend(words)

        if not all_words:
            return 1.0

        return round(len(set(all_words)) / len(all_words), 2)

    def get_active_hours_breakdown(self) -> Dict[str, Any]:
        """Categorizes when dictations take place into active diurnal zones."""
        from datetime import datetime

        history = self.session_store.get_history(limit=100)
        breakdown = {
            "Morning": 0,    # 6:00 - 11:59
            "Afternoon": 0,  # 12:00 - 16:59
            "Evening": 0,    # 17:00 - 21:59
            "Night": 0,      # 22:00 - 5:59
        }

        for h in history:
            created_at_str = h.get("created_at")
            if not created_at_str:
                continue
            try:
                if "T" in created_at_str:
                    dt = datetime.fromisoformat(created_at_str)
                else:
                    dt = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
                hour = dt.hour
                if 6 <= hour < 12:
                    breakdown["Morning"] += 1
                elif 12 <= hour < 17:
                    breakdown["Afternoon"] += 1
                elif 17 <= hour < 22:
                    breakdown["Evening"] += 1
                else:
                    breakdown["Night"] += 1
            except Exception:
                continue

        total = sum(breakdown.values())
        percentages = {k: round((v / max(1, total)) * 100, 1) for k, v in breakdown.items()}
        peak_period = max(breakdown, key=breakdown.get) if total > 0 else "Morning"

        descriptions = {
            "Morning": "You dictate most in the morning—perfect for organizing your day and drafting emails early.",
            "Afternoon": "You speak most in the afternoon—staying productive and keeping up team momentum.",
            "Evening": "You are most active in the evening—wrapping up tasks and reviewing daily highlights.",
            "Night": "You speak most at night—deep focus and late-night ideas flow beautifully.",
        }

        return {
            "counts": breakdown,
            "percentages": percentages,
            "peak_period": peak_period,
            "description": descriptions.get(peak_period, ""),
            "total_sessions": total,
        }

    def get_trends_data(self, limit: int = 10) -> Dict[str, List]:
        """Provides historical data points for custom trend visualization."""
        history = self.session_store.get_history(limit=limit)
        reversed_history = list(reversed(history))

        labels = []
        wpm_values = []
        clarity_values = []
        conciseness_values = []

        for i, h in enumerate(reversed_history):
            labels.append(f"S{i+1}")
            wpm_values.append(h.get("wpm", 0))
            clarity_values.append(h.get("clarity_score", 0))
            conciseness_values.append(h.get("conciseness_score", 0))

        return {
            "labels": labels,
            "wpm": wpm_values,
            "clarity": clarity_values,
            "conciseness": conciseness_values,
        }

    def get_productivity_stats(self) -> Dict[str, Any]:
        """Compares dictation performance against manual typing benchmarks."""
        history = self.session_store.get_history(limit=1000)
        total_words = sum(h.get("words", 0) for h in history)
        total_time_seconds = sum(h.get("recording_seconds", 0) for h in history)

        avg_wpm = int(total_words / (total_time_seconds / 60)) if total_time_seconds > 0 else 0

        typing_baseline = 40.0
        dictation_wpm = max(120.0, float(avg_wpm)) if avg_wpm > 0 else 135.0

        typing_time_mins = total_words / typing_baseline
        dictation_time_mins = total_time_seconds / 60.0
        time_saved_mins = max(0.0, typing_time_mins - dictation_time_mins)

        multiplier = round(dictation_wpm / typing_baseline, 1)

        return {
            "total_words": total_words,
            "total_time_seconds": round(total_time_seconds, 1),
            "avg_wpm": avg_wpm,
            "time_saved_minutes": round(time_saved_mins, 1),
            "typing_multiplier": multiplier,
            "typing_baseline": int(typing_baseline),
        }

    def get_advanced_speech_coaching(self) -> Dict:
        history = self.session_store.get_history(limit=15)
        if not history:
            return {
                "pause_efficiency_pct": 100.0,
                "cadence_variety": 0.0,
                "cadence_rating": "Balanced Flow",
                "gunning_fog_grade": "Standard Conversational",
                "readability_desc": "Highly accessible standard speech structure.",
                "tone_ratios": {"confident": 40.0, "thoughtful": 30.0, "warm": 20.0, "technical": 10.0},
                "speech_coach": {
                    "focus_title": "SILENT VOCAL PAUSES",
                    "drill_title": "The Golden Silence Drill",
                    "tip": "Swallow or take a breath instead of speaking a filler word.",
                    "drill": "Tap your thigh and pause for one beat when you feel like saying 'um'."
                }
            }

        all_text = " ".join((h.get("transcript_text") or "") for h in history)
        metrics = calculate_text_metrics(all_text)

        cadence_variety = metrics.cadence_variety
        if cadence_variety >= 6.0:
            cadence_rating = "Highly Expressive"
        elif cadence_variety >= 3.0:
            cadence_rating = "Balanced Flow"
        elif cadence_variety >= 1.0:
            cadence_rating = "Structured / Formal"
        else:
            cadence_rating = "Uniform / Monotonic"

        fog = metrics.gunning_fog
        if fog >= 16.0:
            readability_desc = "Highly complex. Uses technical/dense academic jargon structures."
        elif fog >= 12.0:
            readability_desc = "Professional. Best for formal presentations and executive reports."
        elif fog >= 8.0:
            readability_desc = "Clear and professional. Accessible to general audiences."
        elif fog >= 5.0:
            readability_desc = "Highly conversational, friendly, and easy to follow."
        else:
            readability_desc = "Direct, simple, and punchy statements."

        avg_wpm = int(sum(h.get("wpm", 0) for h in history) / len(history)) if history else 0
        lex = self.get_lexical_diversity()

        if metrics.pause_efficiency < 75.0:
            coach_focus = {
                "focus_title": "ELIMINATING FILLER WORDS WITH SILENT GAPS",
                "drill_title": "The Golden Silence Drill",
                "tip": "Silent pauses sound authoritative and give your audience time to absorb information; filler words ('um', 'like', 'so') dilute your impact.",
                "drill": "Read a short article aloud. Every time you feel a filler word coming, tap your finger against your desk and force exactly one full second of silent pause."
            }
        elif cadence_variety < 3.0:
            coach_focus = {
                "focus_title": "ADDING DYNAMIC VOCAL RANGE & VARIETY",
                "drill_title": "The Sentence-Length Accordion",
                "tip": "Monotony risks losing audience attention. Alternate between punchy, single-thought short statements and detailed descriptive clauses.",
                "drill": "Speak for two minutes on a familiar topic. Alternate deliberately: speak one very short sentence (under 5 words), then one long descriptive sentence (over 15 words)."
            }
        elif avg_wpm > 150:
            coach_focus = {
                "focus_title": "PACING CONTROL & ARTICULATION SPEED",
                "drill_title": "The Anchored Pace Method",
                "tip": "Speaking too fast makes you hard to follow. Professional speakers slow down on critical technical details and key takeaways.",
                "drill": "Practice reading a paragraph at half your normal speed, making sure to fully pronounce the final consonants of every word (e.g. '-ing', '-ed'). Aim for 120-130 WPM."
            }
        elif lex < 0.5:
            coach_focus = {
                "focus_title": "ENRICHING VOCABULARY & PHRASING DIVERSITY",
                "drill_title": "Synonym Substitution Practice",
                "tip": "Repeating the same phrases (e.g., 'very good', 'basically') makes your presentation feel flat. Practice word variety.",
                "drill": "Identify your three most repeated words (e.g. 'actually', 'awesome'). Write down 5 synonyms for each, and practice using them in your next three dictations."
            }
        else:
            coach_focus = {
                "focus_title": "MASTERING ADVANCED EXECUTIVE PRESENCE",
                "drill_title": "The Resonance Warm-up",
                "tip": "Your vocal clarity, pacing, and vocabulary variety are in the top 5%! Elevate your authority by using deep vocal resonance and strategic pauses.",
                "drill": "Before any important presentation, do the 'hum-and-buzz' lip trill for 30 seconds to relax your vocal cords and open up your chest resonance."
            }

        return {
            "pause_efficiency_pct": round(metrics.pause_efficiency, 1),
            "cadence_variety": round(cadence_variety, 2),
            "cadence_rating": cadence_rating,
            "gunning_fog_grade": metrics.grade_level,
            "readability_desc": readability_desc,
            "tone_ratios": metrics.tone_ratios,
            "speech_coach": coach_focus,
            "hedging_rate": round(metrics.hedging_rate, 1),
            "hesitation_rate": round(metrics.hesitation_rate, 1),
            "pacing_label": metrics.pacing_label,
        }

    def get_vocal_drills(self) -> List[Dict]:
        """Returns 3 interactive vocal drill slides for the carousel."""
        history = self.session_store.get_history(limit=15)
        all_text = " ".join((h.get("transcript_text") or "") for h in history)
        metrics = calculate_text_metrics(all_text)
        avg_wpm = int(sum(h.get("wpm", 0) for h in history) / max(1, len(history)))
        lex = self.get_lexical_diversity()

        if metrics.pause_efficiency < 75.0:
            slide1 = {
                "title": "Filler Elimination",
                "icon": "🎯",
                "subtitle": "Your biggest area for improvement",
                "drill": "Read a paragraph aloud. Every time you feel a filler word coming, tap your desk and hold a 2-second silent pause instead.",
                "metric_name": "Pause Efficiency",
                "metric_value": f"{metrics.pause_efficiency:.0f}%",
                "target": "Target: 85%+",
            }
        elif metrics.cadence_variety < 3.0:
            slide1 = {
                "title": "Cadence Variation",
                "icon": "🎵",
                "subtitle": "Your biggest area for improvement",
                "drill": "Alternate deliberately: speak one very short sentence (under 5 words), then one detailed sentence (over 15 words). Repeat for 2 minutes.",
                "metric_name": "Cadence Variety",
                "metric_value": f"{metrics.cadence_variety:.1f}",
                "target": "Target: 5.0+",
            }
        elif avg_wpm > 150:
            slide1 = {
                "title": "Pace Control",
                "icon": "⏱️",
                "subtitle": "Your biggest area for improvement",
                "drill": "Read at half speed, fully pronouncing final consonants (-ing, -ed). Aim for 120-130 WPM.",
                "metric_name": "Speaking Pace",
                "metric_value": f"{avg_wpm} WPM",
                "target": "Target: 120-140 WPM",
            }
        else:
            slide1 = {
                "title": "Vocabulary Enrichment",
                "icon": "📚",
                "subtitle": "Expand your word variety",
                "drill": "Identify your 3 most repeated words. Write 5 synonyms for each and use them in your next dictation.",
                "metric_name": "Lexical Diversity",
                "metric_value": f"{lex*100:.0f}%",
                "target": "Target: 70%+",
            }

        slide2 = {
            "title": "Vocal Warmup",
            "icon": "🫁",
            "subtitle": "Resonance & diaphragm exercises",
            "drill": "1. Diaphragmatic breathing: 4 counts in, hold 4, out 8.\n2. Lip trills: Buzz lips for 30 seconds on a comfortable pitch.\n3. Hum scales: Start low, slide up, then back down.",
            "metric_name": "Warm-up",
            "metric_value": "Daily",
            "target": "Best before presentations",
        }

        slide3 = {
            "title": "Rhetorical Delivery",
            "icon": "🎤",
            "subtitle": "Advanced speaking techniques",
            "drill": "1. The 3-Second Pause: After key points, pause 3 full seconds.\n2. Rule of Three: Group ideas in threes for memorability.\n3. Power positioning: End sentences on a downward pitch.",
            "metric_name": "Delivery",
            "metric_value": "Pro",
            "target": "Practice weekly",
        }

        return [slide1, slide2, slide3]
