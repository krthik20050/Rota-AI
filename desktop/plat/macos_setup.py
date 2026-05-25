"""
macOS first-run dependency checker and auto-installer.
No Qt imports — pure logic only, called from the setup wizard.

Checks:
  1. PortAudio         — required for audio recording (sounddevice)
  2. pyobjc frameworks — required for hotkeys and text injection
  3. Accessibility     — required permission (user must grant)
  4. Input Monitoring  — optional permission (improves hotkey reliability)
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass

_SETUP_FLAG = os.path.expanduser("~/Library/Application Support/RotaAI/.macos_setup_done")


@dataclass
class CheckResult:
    key: str  # unique identifier used by the wizard
    label: str  # display name
    detail: str  # current status description shown to user
    ok: bool  # True = no action needed
    critical: bool  # False = optional, user can skip
    can_install: bool  # True = we can auto-fix this via subprocess
    needs_user: bool  # True = requires user to open System Settings


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_portaudio() -> CheckResult:
    """Check if PortAudio is available (sounddevice loads it at import)."""
    ok = False
    try:
        import sounddevice  # noqa: F401

        ok = True
    except Exception:
        ok = False
    return CheckResult(
        key="portaudio",
        label="PortAudio (audio recording)",
        detail="Ready" if ok else "Not found — required for audio recording",
        ok=ok,
        critical=True,
        can_install=True,
        needs_user=False,
    )


def check_pyobjc() -> CheckResult:
    """Check if pyobjc frameworks are importable."""
    # Skip check when running from a PyInstaller bundle — already bundled.
    if getattr(sys, "frozen", False):
        return CheckResult(
            key="pyobjc",
            label="macOS System Frameworks",
            detail="Bundled",
            ok=True,
            critical=True,
            can_install=False,
            needs_user=False,
        )
    ok = False
    try:
        import AppKit  # noqa: F401
        import ApplicationServices  # noqa: F401

        ok = True
    except ImportError:
        ok = False
    return CheckResult(
        key="pyobjc",
        label="macOS System Frameworks",
        detail="Ready" if ok else "Missing — needed for hotkeys and text injection",
        ok=ok,
        critical=True,
        can_install=True,
        needs_user=False,
    )


def check_accessibility() -> CheckResult:
    """Check if Accessibility permission is granted."""
    ok = False
    try:
        from ApplicationServices import AXIsProcessTrustedWithOptions

        ok = bool(AXIsProcessTrustedWithOptions(None))
    except Exception:
        ok = False
    return CheckResult(
        key="accessibility",
        label="Accessibility Permission",
        detail="Granted" if ok else "Required — allows hotkey capture and text injection",
        ok=ok,
        critical=True,
        can_install=False,
        needs_user=True,
    )


def check_input_monitoring() -> CheckResult:
    """Check if Input Monitoring permission is granted (Quartz CGEventTap)."""
    ok = False
    try:
        from Quartz import (  # type: ignore
            CGEventTapCreate,
            kCGHeadInsertEventTap,
            kCGSessionEventTap,
        )

        tap = CGEventTapCreate(
            kCGSessionEventTap,
            kCGHeadInsertEventTap,
            1,  # kCGEventTapOptionDefault — active tap just to test creation
            0,  # mask = 0
            lambda _p, _t, _e, _r: _e,
            None,
        )
        ok = tap is not None
    except Exception:
        ok = False
    return CheckResult(
        key="input_monitoring",
        label="Input Monitoring (optional)",
        detail="Granted" if ok else "Optional — improves hotkey reliability, skip if unsure",
        ok=ok,
        critical=False,
        can_install=False,
        needs_user=True,
    )


def run_checks() -> list[CheckResult]:
    """Run all checks. Safe to call from a background thread."""
    return [
        check_portaudio(),
        check_pyobjc(),
        check_accessibility(),
        check_input_monitoring(),
    ]


# ---------------------------------------------------------------------------
# Installers (blocking — always run in a background thread)
# ---------------------------------------------------------------------------


def install_portaudio() -> tuple[bool, str]:
    """
    Install PortAudio via Homebrew.
    Installs Homebrew first if not present.
    Returns (success, message).
    """
    brew = _find_brew()
    if not brew:
        ok, msg = _install_homebrew()
        if not ok:
            return False, f"Homebrew install failed: {msg}"
        brew = _find_brew()
        if not brew:
            return (
                False,
                "Homebrew installed but 'brew' not found. "
                "Open a new Terminal and run: brew install portaudio",
            )

    try:
        result = subprocess.run(
            [brew, "install", "portaudio"],
            capture_output=True,
            text=True,
            timeout=180,
        )
        if result.returncode == 0:
            return True, "PortAudio installed"
        return False, (result.stderr or result.stdout)[:400]
    except subprocess.TimeoutExpired:
        return False, "Install timed out after 3 minutes"
    except Exception as exc:
        return False, str(exc)


def install_pyobjc() -> tuple[bool, str]:
    """Install pyobjc packages via pip. Returns (success, message)."""
    if getattr(sys, "frozen", False):
        return True, "Already bundled"

    packages = [
        "pyobjc-core>=10.0",
        "pyobjc-framework-Cocoa>=10.0",
        "pyobjc-framework-ApplicationServices>=10.0",
        "pyobjc-framework-Quartz>=10.0",
    ]
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", *packages],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode == 0:
            return True, "macOS frameworks installed"
        return False, (result.stderr or result.stdout)[:400]
    except subprocess.TimeoutExpired:
        return False, "Install timed out after 5 minutes"
    except Exception as exc:
        return False, str(exc)


# ---------------------------------------------------------------------------
# Permission helpers
# ---------------------------------------------------------------------------


def open_accessibility_settings() -> None:
    """Open System Settings → Privacy & Security → Accessibility."""
    subprocess.Popen(
        [
            "open",
            "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility",
        ]
    )


def open_input_monitoring_settings() -> None:
    """Open System Settings → Privacy & Security → Input Monitoring."""
    subprocess.Popen(
        [
            "open",
            "x-apple.systempreferences:com.apple.preference.security?Privacy_ListenEvent",
        ]
    )


# ---------------------------------------------------------------------------
# Setup completion flag
# ---------------------------------------------------------------------------


def is_setup_done() -> bool:
    """Return True if the user has completed (or skipped) first-run setup."""
    return os.path.exists(_SETUP_FLAG)


def mark_setup_done() -> None:
    """Persist the setup-complete flag."""
    flag_dir = os.path.dirname(_SETUP_FLAG)
    os.makedirs(flag_dir, exist_ok=True)
    with open(_SETUP_FLAG, "w", encoding="utf-8") as f:
        f.write("done")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _find_brew() -> str | None:
    """Return path to the brew binary, or None if Homebrew is not installed."""
    for candidate in ("/opt/homebrew/bin/brew", "/usr/local/bin/brew"):
        if os.path.isfile(candidate):
            return candidate
    result = subprocess.run(["which", "brew"], capture_output=True, text=True)
    if result.returncode == 0:
        path = result.stdout.strip()
        if path:
            return path
    return None


def _install_homebrew() -> tuple[bool, str]:
    """
    Install Homebrew non-interactively.
    Very slow (up to 10 min) — must run in a background thread.
    """
    try:
        result = subprocess.run(
            [
                "/bin/bash",
                "-c",
                "NONINTERACTIVE=1 /bin/bash -c "
                '"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            ],
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode == 0:
            return True, "Homebrew installed"
        return False, (result.stderr or result.stdout)[:400]
    except subprocess.TimeoutExpired:
        return False, "Homebrew install timed out (10 min)"
    except Exception as exc:
        return False, str(exc)
