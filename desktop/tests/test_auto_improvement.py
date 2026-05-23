"""
Tests for the Auto-Improvement System.
"""
import os
import json
import tempfile
import time
from unittest.mock import MagicMock
import pytest

from ai.auto_improvement import AutoImprovementSystem
from ai.ai_processor import PersonalDictionary


def test_auto_improvement_init_and_persistence():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "auto_improvement_log.json")
        
        # Initialize
        sys_auto = AutoImprovementSystem(log_path=log_path)
        assert len(sys_auto.get_corrections()) == 0
        
        # Manually log a correction
        sys_auto._log_correction("india", "India")
        assert len(sys_auto.get_corrections()) == 1
        assert sys_auto.get_corrections()[0]["original"] == "india"
        assert sys_auto.get_corrections()[0]["corrected"] == "India"
        
        # Re-initialize to verify loading from disk
        sys_auto_2 = AutoImprovementSystem(log_path=log_path)
        assert len(sys_auto_2.get_corrections()) == 1
        assert sys_auto_2.get_corrections()[0]["original"] == "india"
        assert sys_auto_2.get_corrections()[0]["corrected"] == "India"


def test_track_injections():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "auto_improvement_log.json")
        sys_auto = AutoImprovementSystem(log_path=log_path)
        
        # Test empty text tracking is ignored
        sys_auto.track_injection("sess_1", "")
        assert len(sys_auto._recent_injections) == 0
        
        # Test valid tracking
        sys_auto.track_injection("sess_2", "hello world")
        assert len(sys_auto._recent_injections) == 1
        assert sys_auto._recent_injections[0]["session_id"] == "sess_2"
        assert sys_auto._recent_injections[0]["text"] == "hello world"
        
        # Test rolling buffer capacity limit (last 10)
        for i in range(15):
            sys_auto.track_injection(f"sess_bulk_{i}", f"some text {i}")
        
        assert len(sys_auto._recent_injections) <= 10
        assert sys_auto._recent_injections[-1]["session_id"] == "sess_bulk_14"


def test_analyze_field_for_corrections_no_edits():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "auto_improvement_log.json")
        sys_auto = AutoImprovementSystem(log_path=log_path)
        
        # No injections
        assert sys_auto.analyze_field_for_corrections("hello world") == []
        
        # Injection matched perfectly
        sys_auto.track_injection("sess_1", "we are going to a party tonight")
        assert sys_auto.analyze_field_for_corrections("we are going to a party tonight") == []


def test_analyze_field_for_corrections_single_word():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "auto_improvement_log.json")
        
        # Mock PersonalDictionary
        mock_pd = MagicMock()
        
        sys_auto = AutoImprovementSystem(log_path=log_path, personal_dict=mock_pd)
        
        # User corrected "india" -> "India"
        sys_auto.track_injection("sess_1", "we focus mainly outside of india to build this")
        
        corrections = sys_auto.analyze_field_for_corrections("we focus mainly outside of India to build this")
        
        assert len(corrections) == 1
        assert corrections[0] == ("india", "India")
        
        # Check that it got logged and fed back to PersonalDictionary
        mock_pd.add_term.assert_called_once_with("India")
        assert len(sys_auto.get_corrections()) == 1
        assert sys_auto.get_corrections()[0]["original"] == "india"
        assert sys_auto.get_corrections()[0]["corrected"] == "India"


def test_analyze_field_for_corrections_structural_difference_ignored():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "auto_improvement_log.json")
        sys_auto = AutoImprovementSystem(log_path=log_path)
        
        # Injection tracked
        sys_auto.track_injection("sess_1", "we are going to a party tonight")
        
        # Text cleared or vastly different: ignore
        assert sys_auto.analyze_field_for_corrections("") == []
        assert sys_auto.analyze_field_for_corrections("completely unrelated new message here") == []
        assert len(sys_auto.get_corrections()) == 0


def test_no_duplicate_corrections():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "auto_improvement_log.json")
        sys_auto = AutoImprovementSystem(log_path=log_path)
        
        sys_auto._log_correction("obsidian", "Obsidian")
        sys_auto._log_correction("obsidian", "Obsidian")
        
        assert len(sys_auto.get_corrections()) == 1
