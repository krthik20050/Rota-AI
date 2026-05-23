"""Tests for services/updater.py — no network calls, no Qt."""
from __future__ import annotations

import json
import time
import unittest
from unittest.mock import MagicMock, patch

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "desktop"))

from services.updater import _version_tuple, check_for_update


class TestVersionTuple(unittest.TestCase):
    def test_basic(self):
        assert _version_tuple("1.2.3") == (1, 2, 3)

    def test_v_prefix(self):
        assert _version_tuple("v1.2.3") == (1, 2, 3)

    def test_single_segment(self):
        assert _version_tuple("2") == (2,)

    def test_comparison_newer(self):
        assert _version_tuple("1.1.0") > _version_tuple("1.0.0")

    def test_comparison_same(self):
        assert _version_tuple("1.0.0") == _version_tuple("1.0.0")

    def test_comparison_older(self):
        assert _version_tuple("0.9.9") < _version_tuple("1.0.0")

    def test_invalid_returns_zero(self):
        assert _version_tuple("not-a-version") == (0,)


class TestCheckForUpdate(unittest.TestCase):
    def _fake_response(self, tag: str, html_url: str = "https://example.com/release"):
        payload = json.dumps({"tag_name": tag, "html_url": html_url}).encode()
        mock_resp = MagicMock()
        mock_resp.read.return_value = payload
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    def test_newer_version_calls_callback(self):
        called = []

        with patch("urllib.request.urlopen", return_value=self._fake_response("v1.1.0")):
            check_for_update("1.0.0", lambda v, u: called.append((v, u)))

        deadline = time.time() + 3
        while not called and time.time() < deadline:
            time.sleep(0.05)

        assert called, "on_update_found was not called"
        assert called[0][0] == "1.1.0"

    def test_same_version_no_callback(self):
        called = []

        with patch("urllib.request.urlopen", return_value=self._fake_response("v1.0.0")):
            check_for_update("1.0.0", lambda v, u: called.append((v, u)))

        time.sleep(0.3)
        assert not called, "on_update_found should not fire for same version"

    def test_older_version_no_callback(self):
        called = []

        with patch("urllib.request.urlopen", return_value=self._fake_response("v0.9.0")):
            check_for_update("1.0.0", lambda v, u: called.append((v, u)))

        time.sleep(0.3)
        assert not called

    def test_network_error_no_crash(self):
        import urllib.error
        called = []

        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
            check_for_update("1.0.0", lambda v, u: called.append((v, u)))

        time.sleep(0.3)
        assert not called

    def test_empty_tag_no_callback(self):
        called = []
        payload = json.dumps({"tag_name": "", "html_url": ""}).encode()
        mock_resp = MagicMock()
        mock_resp.read.return_value = payload
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_resp):
            check_for_update("1.0.0", lambda v, u: called.append((v, u)))

        time.sleep(0.3)
        assert not called


if __name__ == "__main__":
    unittest.main()
