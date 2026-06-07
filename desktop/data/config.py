from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any

from utils.log import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# SECURITY: API key encryption at rest.
# Windows: DPAPI via win32crypt (existing)
# Linux:   keyring via FreeDesktop Secret Service (GNOME Keyring / KWallet)
# ---------------------------------------------------------------------------

_IS_LINUX = sys.platform.startswith("linux")
_IS_WINDOWS = sys.platform == "win32"
_IS_MACOS = sys.platform == "darwin"
_ENCRYPTED_KEYS = frozenset({"groq_api_key", "gemini_api_key", "per_app_config"})


def _encrypt(plaintext: str, key_name: str | None = None) -> str | None:
    """Encrypt a string. Returns encrypted blob or None on failure."""
    if not plaintext:
        return None
    if _IS_LINUX or _IS_MACOS:
        return _keyring_encrypt(plaintext, key_name=key_name)
    else:
        return _dpapi_encrypt(plaintext)


def _decrypt(blob: str, key_name: str | None = None) -> str | None:
    """Decrypt a blob. Returns plaintext or None on failure."""
    if not blob:
        return None
    if blob.startswith("dpapi:"):
        return _dpapi_decrypt(blob[6:])
    if _IS_LINUX or _IS_MACOS:
        return _keyring_decrypt(blob, key_name=key_name)
    return blob  # legacy plaintext


def _keyring_encrypt(plaintext: str, key_name: str | None = None) -> str | None:
    try:
        from plat.linux_secrets import encrypt_secret

        return encrypt_secret(plaintext, account=key_name or "api_keys")
    except Exception:
        logger.warning("keyring_encrypt_failed")
        return None


def _keyring_decrypt(stored: str, key_name: str | None = None) -> str | None:
    try:
        from plat.linux_secrets import decrypt_secret

        return decrypt_secret(stored, account=key_name)
    except Exception:
        logger.warning("keyring_decrypt_failed")
        return None


def _dpapi_encrypt(plaintext: str) -> str | None:
    """Encrypt a string via DPAPI. Returns base64 blob or None on failure."""
    if _IS_LINUX or _IS_MACOS or not plaintext:
        return None
    try:
        import base64
        import importlib as _importlib

        win32crypt = _importlib.import_module("win32crypt")
        encrypted = win32crypt.CryptProtectData(plaintext.encode("utf-8"), None, None, None, 0)
        return "dpapi:" + base64.b64encode(encrypted).decode("ascii")
    except Exception:
        logger.warning("dpapi_encrypt_failed")
        return None


def _dpapi_decrypt(blob_b64: str) -> str | None:
    """Decrypt a DPAPI base64 blob. Returns plaintext or None on failure."""
    if _IS_LINUX or _IS_MACOS or not blob_b64:
        return None
    try:
        import base64
        import importlib as _importlib

        win32crypt = _importlib.import_module("win32crypt")
        encrypted = base64.b64decode(blob_b64)
        _, plaintext = win32crypt.CryptUnprotectData(encrypted, None, None, None, None, 0)
        return plaintext.decode("utf-8")
    except Exception:
        logger.warning("dpapi_decrypt_failed")
        return None


# SECURITY: Allowed Ollama URL patterns (localhost/private networks only)
_OLLAMA_URL_ALLOWED_PATTERNS = [
    re.compile(r"^https?://localhost(:\d+)?(/.*)?$", re.I),
    re.compile(r"^https?://127\.0\.0\.1(:\d+)?(/.*)?$", re.I),
    re.compile(r"^https?://10\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?(/.*)?$", re.I),
    re.compile(r"^https?://172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}(:\d+)?(/.*)?$", re.I),
    re.compile(r"^https?://192\.168\.\d{1,3}\.\d{1,3}(:\d+)?(/.*)?$", re.I),
    re.compile(r"^https?://\[::1\](:\d+)?(/.*)?$", re.I),
]
# SECURITY: Block these URL patterns (cloud metadata, link-local, etc.)
_OLLAMA_URL_BLOCKED_PATTERNS = [
    re.compile(r"^https?://169\.254\.\d{1,3}\.\d{1,3}", re.I),  # AWS/cloud metadata
    re.compile(r"^https?://metadata\.google\.internal", re.I),  # GCP metadata
    re.compile(r"^https?://\[fd00", re.I),  # IPv6 link-local
]


def _is_ollama_url_allowed(url: str) -> bool:
    """Validate that the Ollama URL points to a local/private address."""
    if not url:
        return False
    # Check blocked patterns first
    for pattern in _OLLAMA_URL_BLOCKED_PATTERNS:
        if pattern.match(url):
            return False
    # Check allowed patterns
    for pattern in _OLLAMA_URL_ALLOWED_PATTERNS:
        if pattern.match(url):
            return True
    return False


# ---------------------------------------------------------------------------
# Typed config dataclass
# ---------------------------------------------------------------------------


@dataclass
class AppConfig:
    """
    Strongly-typed application configuration.

    Every field has a default that matches ConfigManager.DEFAULT_CONFIG.
    Use with ConfigManager.get_typed() / ConfigManager.apply_typed().
    """

    # ── API keys ────────────────────────────────────────────────────────
    groq_api_key: str = ""
    gemini_api_key: str = ""

    # ── Hotkey ──────────────────────────────────────────────────────────
    hotkey: str = "tab"
    hotkey_mode: str = "toggle"  # "toggle" | "hold"

    # ── Transcription ───────────────────────────────────────────────────
    model_size: str = "small.en"
    transcription_quality: str = "fast"  # "fast" | "balanced" | "accurate"
    live_transcription_enabled: bool = True
    cpu_threads: int = 0  # 0 = auto
    auto_stop_silence_s: float = 2.5
    denoise_enabled: bool = False

    # ── AI Processing ───────────────────────────────────────────────────
    ai_enabled: bool = True
    ai_provider: str = "gemini"  # "gemini" | "groq" | "ollama"
    writing_mode: str = "clean"  # "clean" | "raw" | "smart"
    ollama_model: str = "qwen3.5:latest"
    ollama_url: str = "http://localhost:11434"

    # ── UI ──────────────────────────────────────────────────────────────
    startup_enabled: bool = False
    bg_audio_control: str = "pause"  # "pause" | "mute" | "ignore"
    date_display: str = "relative"  # "relative" | "absolute"
    history_days: int = 2
    ui_font_scope: str = "app"  # "app" | "system"

    # ── Per-app & advanced ──────────────────────────────────────────────
    per_app_config: dict[str, Any] = field(default_factory=dict)
    auto_backup_enabled: bool = True

    # ── Validation ──────────────────────────────────────────────────────

    def __post_init__(self) -> None:
        """Validate field values after initialization."""
        valid_modes = {"toggle", "hold"}
        if self.hotkey_mode not in valid_modes:
            logger.warning("invalid_hotkey_mode", value=self.hotkey_mode)
            object.__setattr__(self, "hotkey_mode", "toggle")

        valid_providers = {"gemini", "groq", "ollama"}
        if self.ai_provider not in valid_providers:
            logger.warning("invalid_ai_provider", value=self.ai_provider)
            object.__setattr__(self, "ai_provider", "gemini")

        valid_qualities = {"fast", "balanced", "accurate"}
        if self.transcription_quality not in valid_qualities:
            logger.warning("invalid_transcription_quality", value=self.transcription_quality)
            object.__setattr__(self, "transcription_quality", "fast")

        # Clamp numeric ranges
        if self.cpu_threads < 0:
            object.__setattr__(self, "cpu_threads", 0)
        if self.auto_stop_silence_s < 0.5:
            object.__setattr__(self, "auto_stop_silence_s", 0.5)
        if self.history_days < 0:
            object.__setattr__(self, "history_days", 0)

    def to_dict(self) -> dict[str, Any]:
        """Convert to a plain dict (for serialization)."""
        result: dict[str, Any] = {}
        for f in __dataclass_fields__:
            result[f] = getattr(self, f)
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppConfig:
        """
        Create an AppConfig from a dict (e.g., loaded from JSON).
        Unknown keys are silently ignored; missing keys use defaults.
        """
        valid_keys = {f.name for f in __dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


__dataclass_fields__ = AppConfig.__dataclass_fields__  # type: ignore[name-defined]


class ConfigManager:
    """
    Manages application configuration stored in a JSON file.
    Default storage: %APPDATA%/RotaAI/config.json

    SECURITY: API keys stored in config.json should be encrypted at rest.
    The onboarding wizard writes keys here; they are loaded into memory at runtime.
    """

    DEFAULT_CONFIG = {
        "groq_api_key": "",
        "gemini_api_key": "",
        "hotkey": "tab",
        "hotkey_mode": "toggle",
        "model_size": "small.en",
        "ai_enabled": True,
        "ai_provider": "gemini",
        "bg_audio_control": "pause",
        "startup_enabled": False,
        "writing_mode": "clean",
        "ollama_model": "qwen3.5:latest",
        "ollama_url": "http://localhost:11434",
        "auto_stop_silence_s": 2.5,
        "transcription_quality": "fast",
        "live_transcription_enabled": True,
        "cpu_threads": 0,
        "date_display": "relative",
        "history_days": 2,
        "ui_font_scope": "app",
        "denoise_enabled": False,
        "per_app_config": {},
        "auto_backup_enabled": True,
    }

    def __init__(self, config_path=None):
        if config_path is None:
            if _IS_LINUX:
                config_dir = os.path.join(
                    os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "rota-ai"
                )
            elif _IS_MACOS:
                config_dir = os.path.join(
                    os.path.expanduser("~/Library/Application Support"), "RotaAI"
                )
            else:
                config_dir = os.path.join(os.environ.get("APPDATA", "."), "RotaAI")
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            config_path = os.path.join(config_dir, "config.json")

        self.config_path = config_path
        self.config = self.DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        """Loads configuration from JSON file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    # SECURITY: Validate Ollama URL on load
                    if "ollama_url" in loaded_config:
                        if not _is_ollama_url_allowed(loaded_config["ollama_url"]):
                            logger.warning(
                                "ollama_url_blocked", blocked_url=loaded_config["ollama_url"]
                            )
                            loaded_config["ollama_url"] = self.DEFAULT_CONFIG["ollama_url"]
                    # SECURITY: Decrypt DPAPI-protected keys. The stored value is
                    # either a "dpapi:<blob>" string or a legacy plaintext key.
                    for key in _ENCRYPTED_KEYS:
                        raw = loaded_config.get(key, "")
                        if raw and raw.startswith("dpapi:"):
                            decrypted = _decrypt(raw)
                            if decrypted is not None:
                                loaded_config[key] = decrypted
                            else:
                                # Can't decrypt (different machine/user?); clear it
                                logger.warning("dpapi_key_unreadable", config_key=key)
                                loaded_config[key] = ""
                        elif raw and raw.startswith("keyring:"):
                            decrypted = _decrypt(raw, key_name=key)
                            if decrypted is not None:
                                loaded_config[key] = decrypted
                            else:
                                logger.warning("keyring_key_unreadable", config_key=key)
                                loaded_config[key] = ""
                    self.config.update(loaded_config)
            except Exception:
                logger.exception("Failed to load config file: %s", self.config_path)

        # Migration: "hold" -> "toggle"
        if self.config.get("hotkey_mode") == "hold":
            self.config["hotkey_mode"] = "toggle"
            self.save()

    def save(self):
        """Saves current configuration to JSON file."""
        try:
            # SECURITY: Encrypt sensitive keys with DPAPI before persisting.
            # We write a copy so in-memory values stay as plaintext for the session.
            save_config = dict(self.config)
            for key in _ENCRYPTED_KEYS:
                plaintext = save_config.get(key, "")
                if (
                    plaintext
                    and not plaintext.startswith("dpapi:")
                    and not plaintext.startswith("keyring:")
                ):
                    blob = _encrypt(plaintext, key_name=key)
                    if blob:
                        save_config[key] = blob
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(save_config, f, indent=4)

            self._handle_startup()
        except Exception:
            logger.exception("Failed to save config file: %s", self.config_path)

    def get(self, key, default=None):
        """Gets a configuration value."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Sets a configuration value."""
        # SECURITY: Validate Ollama URL when changed
        if key == "ollama_url" and value:
            if not _is_ollama_url_allowed(value):
                logger.warning("ollama_url_set_blocked", url=value)
                raise ValueError(
                    f"Ollama URL '{value}' is not allowed. "
                    "Only localhost and private network addresses are permitted."
                )
        self.config[key] = value

    def get_typed(self) -> AppConfig:
        """
        Return the current config as a typed AppConfig dataclass.
        All validation rules in AppConfig.__post_init__ apply.
        This is the safe, typed way to consume configuration.
        """
        return AppConfig.from_dict(self.config)

    def apply_typed(self, cfg: AppConfig) -> None:
        """
        Apply an AppConfig dataclass to the manager and persist.
        This is the safe, typed way to update configuration.
        """
        for f in __dataclass_fields__:
            self.config[f] = getattr(cfg, f)
        self.save()

    def update_from_typed(self, cfg: AppConfig) -> None:
        """
        Apply only the non-default fields from an AppConfig.
        Useful for partial updates (e.g., per-app overrides).
        """
        defaults = AppConfig()
        for f in __dataclass_fields__:
            new_val = getattr(cfg, f)
            if new_val != getattr(defaults, f):
                self.config[f] = new_val
        self.save()

    def _handle_startup(self):
        """
        Registers/unregisters the application for session startup.

        Windows: Uses winreg (HKCU\\...\\Run)
        macOS:   Uses launchd plist (~/Library/LaunchAgents/)
        Linux:   Uses XDG autostart .desktop file
        """
        if _IS_LINUX:
            self._handle_startup_linux()
        elif _IS_MACOS:
            self._handle_startup_macos()
        else:
            self._handle_startup_windows()

    def _handle_startup_macos(self):
        """Register/unregister via launchd plist."""
        try:
            from plat.macos_startup import register_startup, unregister_startup

            if self.config.get("startup_enabled"):
                exe_path = sys.executable
                if exe_path and os.path.isfile(exe_path):
                    register_startup(exe_path)
                else:
                    logger.error("startup_invalid_exe_path", path=exe_path)
            else:
                unregister_startup()
        except Exception:
            logger.exception("Failed to update macOS startup registration")

    def _handle_startup_linux(self):
        """Register/unregister via XDG autostart."""
        try:
            from plat.linux_startup import register_startup, unregister_startup

            if self.config.get("startup_enabled"):
                exe_path = sys.executable
                if exe_path and os.path.isfile(exe_path):
                    register_startup(exe_path)
                else:
                    logger.error("startup_invalid_exe_path", path=exe_path)
            else:
                unregister_startup()
        except Exception:
            logger.exception("Failed to update startup registration")

    def _handle_startup_windows(self):
        """Register/unregister via Windows registry (HKCU\\Run)."""
        import importlib as _importlib

        reg = _importlib.import_module("winreg")
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "RotaAI"

        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
        except Exception:
            logger.exception("Failed to open startup registry key")
            return

        try:
            if self.config.get("startup_enabled"):
                exe_path = sys.executable

                # SECURITY: Validate executable path
                if not exe_path or not os.path.isfile(exe_path):
                    logger.error("startup_invalid_exe_path", path=exe_path)
                    return

                # SECURITY: Block paths in temp directories
                temp_dirs = [
                    os.environ.get("TEMP", ""),
                    os.environ.get("TMP", ""),
                    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp"),
                ]
                exe_lower = exe_path.lower()
                for temp_dir in temp_dirs:
                    if temp_dir and exe_lower.startswith(temp_dir.lower()):
                        logger.error("startup_blocked_temp_path", path=exe_path)
                        return

                if "pythonw.exe" in exe_lower or "python.exe" in exe_lower:
                    script_path = os.path.abspath(sys.argv[0])
                    value = f'"{exe_path}" "{script_path}"'
                else:
                    value = f'"{exe_path}"'
                reg.SetValueEx(key, app_name, 0, reg.REG_SZ, value)
            else:
                try:
                    reg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
        except Exception:
            logger.exception("Failed to update startup registry value")
        finally:
            reg.CloseKey(key)
