"""
error_reporter.py — one-click bug reporting via GitHub Issues.

Opens a pre-filled GitHub new-issue page in the browser.
No API key required — user reviews and submits the report themselves.
"""

from __future__ import annotations

import platform
import sys
import urllib.parse
import webbrowser
from datetime import datetime

_REPO = "krthik20050/Rota-AI"
_NEW_ISSUE_URL = f"https://github.com/{_REPO}/issues/new"


def open_github_report(title: str, body: str) -> None:
    """Open a pre-filled GitHub issue in the default browser."""
    params = urllib.parse.urlencode(
        {
            "title": title[:200],
            "body": body[:5000],
            "labels": "bug",
        }
    )
    webbrowser.open(f"{_NEW_ISSUE_URL}?{params}")


def build_error_body(error_detail: str, traceback_text: str = "", context: str = "") -> str:
    """Build a structured GitHub issue body with system info."""
    try:
        from app.version import __version__

        version = f"v{__version__}"
    except Exception:
        version = "unknown"

    lines = [
        "## Error Report",
        "",
        f"**Rota AI Version**: {version}",
        f"**OS**: {platform.system()} {platform.release()}",
        f"**Python**: {sys.version.split()[0]}",
        f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Error",
        "",
        "```",
        error_detail.strip(),
        "```",
        "",
    ]

    if context:
        lines += [
            "## Where it happened",
            "",
            context,
            "",
        ]

    if traceback_text:
        lines += [
            "## Traceback",
            "",
            "```",
            traceback_text.strip()[:2000],
            "```",
            "",
        ]

    lines += [
        "## Steps to reproduce",
        "",
        "<!-- Describe what you were doing when this error occurred -->",
        "1. ",
        "",
        "## Expected behavior",
        "",
        "<!-- What should have happened? -->",
    ]

    return "\n".join(lines)
