"""Tests for the compositor detection utility."""

from __future__ import annotations

import os

import pytest

from plat.compositor import CompositorInfo, detect_compositor


class TestCompositorInfo:
    def test_defaults(self):
        info = CompositorInfo()
        assert info.name == "unknown"
        assert info.display_server == "unknown"
        assert not info.is_wayland
        assert not info.is_x11
        assert not info.supports_portal
        assert not info.needs_pynput

    def test_gnome_supports_portal(self):
        info = CompositorInfo(name="gnome", display_server="wayland")
        assert info.supports_portal
        assert info.is_wayland

    def test_kde_supports_portal(self):
        info = CompositorInfo(name="kde", display_server="wayland")
        assert info.supports_portal

    def test_sway_supports_portal(self):
        info = CompositorInfo(name="sway", display_server="wayland")
        assert info.supports_portal

    def test_hyprland_supports_portal(self):
        info = CompositorInfo(name="hyprland", display_server="wayland")
        assert info.supports_portal

    def test_unknown_does_not_support_portal(self):
        info = CompositorInfo(name="unknown", display_server="wayland")
        assert not info.supports_portal

    def test_x11_needs_pynput(self):
        info = CompositorInfo(name="x11", display_server="x11")
        assert info.needs_pynput

    def test_wayland_does_not_need_pynput(self):
        info = CompositorInfo(name="gnome", display_server="wayland")
        assert not info.needs_pynput

    def test_short_summary_x11(self):
        info = CompositorInfo(name="x11", display_server="x11", desktop_env="GNOME")
        assert "X11" in info.short_summary()
        assert "GNOME" in info.short_summary()

    def test_short_summary_wayland(self):
        info = CompositorInfo(name="gnome", display_server="wayland")
        assert "Wayland" in info.short_summary()
        assert "Gnome" in info.short_summary() or "gnome" in info.short_summary()

    def test_setup_guide_gnome(self):
        info = CompositorInfo(name="gnome")
        guide = info.setup_guide()
        assert "GNOME" in guide
        assert "pip install jeepney" in guide

    def test_setup_guide_kde(self):
        info = CompositorInfo(name="kde")
        guide = info.setup_guide()
        assert "KDE" in guide

    def test_setup_guide_sway(self):
        info = CompositorInfo(name="sway")
        guide = info.setup_guide()
        assert "Sway" in guide
        assert "xdg-desktop-portal-wlr" in guide

    def test_setup_guide_hyprland(self):
        info = CompositorInfo(name="hyprland")
        guide = info.setup_guide()
        assert "Hyprland" in guide
        assert "xdg-desktop-portal-hyprland" in guide

    def test_setup_guide_unknown(self):
        info = CompositorInfo(name="unknown")
        guide = info.setup_guide()
        assert "pip install pynput" in guide
        assert "sudo usermod" in guide


class TestDetectCompositor:
    def test_gnome_detection(self, monkeypatch):
        monkeypatch.setenv("XDG_CURRENT_DESKTOP", "GNOME")
        monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
        monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
        monkeypatch.delenv("DISPLAY", raising=False)
        info = detect_compositor()
        assert info.name == "gnome"
        assert info.is_wayland
        assert info.supports_portal

    def test_kde_detection(self, monkeypatch):
        monkeypatch.setenv("XDG_CURRENT_DESKTOP", "KDE")
        monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
        monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
        monkeypatch.delenv("DISPLAY", raising=False)
        info = detect_compositor()
        assert info.name == "kde"
        assert info.is_wayland

    def test_sway_detection(self, monkeypatch):
        monkeypatch.setenv("XDG_CURRENT_DESKTOP", "sway")
        monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
        monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
        monkeypatch.setenv("SWAYSOCK", "/run/user/1000/sway-ipc.sock")
        monkeypatch.delenv("DISPLAY", raising=False)
        info = detect_compositor()
        assert info.name == "sway"
        assert info.is_wayland

    def test_sway_detection_via_swaysock(self, monkeypatch):
        monkeypatch.delenv("XDG_CURRENT_DESKTOP", raising=False)
        monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
        monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
        monkeypatch.setenv("SWAYSOCK", "/run/user/1000/sway-ipc.sock")
        monkeypatch.delenv("DISPLAY", raising=False)
        info = detect_compositor()
        assert info.name == "sway"

    def test_hyprland_detection(self, monkeypatch):
        monkeypatch.setenv("XDG_CURRENT_DESKTOP", "Hyprland")
        monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
        monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
        monkeypatch.setenv("HYPRLAND_INSTANCE_SIGNATURE", "abc123")
        monkeypatch.delenv("DISPLAY", raising=False)
        info = detect_compositor()
        assert info.name == "hyprland"
        assert info.is_wayland

    def test_x11_detection(self, monkeypatch):
        monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
        monkeypatch.setenv("DISPLAY", ":0")
        monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
        monkeypatch.setenv("XDG_CURRENT_DESKTOP", "GNOME")
        info = detect_compositor()
        # On X11 with GNOME, name is "gnome" but display_server is "x11"
        # Portal backend is Wayland-only, so pynput is still needed on X11
        assert info.name == "gnome"
        assert info.is_x11
        assert not info.is_wayland
        assert info.needs_pynput

    def test_x11_without_xdg(self, monkeypatch):
        monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
        monkeypatch.setenv("DISPLAY", ":0")
        monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)
        monkeypatch.delenv("XDG_CURRENT_DESKTOP", raising=False)
        info = detect_compositor()
        assert info.name == "x11"
        assert info.is_x11

    def test_unknown_detection(self, monkeypatch):
        monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
        monkeypatch.delenv("DISPLAY", raising=False)
        monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)
        monkeypatch.delenv("XDG_CURRENT_DESKTOP", raising=False)
        info = detect_compositor()
        assert info.name == "unknown"
        assert info.display_server == "unknown"

    def test_other_wayland_detection(self, monkeypatch):
        monkeypatch.setenv("XDG_CURRENT_DESKTOP", "river")
        monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")
        monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
        monkeypatch.delenv("DISPLAY", raising=False)
        info = detect_compositor()
        assert info.name == "river"

    def test_tty_session(self, monkeypatch):
        monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
        monkeypatch.delenv("DISPLAY", raising=False)
        monkeypatch.setenv("XDG_SESSION_TYPE", "tty")
        info = detect_compositor()
        assert info.display_server == "tty"

    def test_gnome_x11_fallback(self, monkeypatch):
        # GNOME running on X11, not Wayland
        monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
        monkeypatch.setenv("DISPLAY", ":0")
        monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
        monkeypatch.setenv("XDG_CURRENT_DESKTOP", "GNOME")
        info = detect_compositor()
        # GNOME on X11: name reflects DE, display_server reflects protocol
        assert info.name == "gnome"
        assert info.is_x11
        assert not info.is_wayland
        assert info.display_server == "x11"
