import base64
import json
import os
import sys
from utils.log import get_logger
import re

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# SECURITY: API key encryption at rest using Windows DPAPI
# Keys stored in config.json are opaque blobs; only the current Windows user
# account can decrypt them (CryptProtectData / CryptUnprotectData).
# On non-Windows platforms this falls back to plaintext with a log warning.
# ---------------------------------------------------------------------------

_ENCRYPTED_KEYS = frozenset({"groq_api_key", "gemini_api_key"})


def _dpapi_encrypt(plaintext: str) -> str | None:
    """Encrypt a string via DPAPI. Returns base64 blob or None on failure."""
    if sys.platform != "win32" or not plaintext:
        return None
    try:
        import win32crypt
        encrypted = win32crypt.CryptProtectData(
            plaintext.encode("utf-8"), None, None, None, None, 0
        )
        return base64.b64encode(encrypted).decode("ascii")
    except Exception:
        logger.warning("dpapi_encrypt_failed")
        return None


def _dpapi_decrypt(blob_b64: str) -> str | None:
    """Decrypt a DPAPI base64 blob. Returns plaintext or None on failure."""
    if sys.platform != "win32" or not blob_b64:
        return None
    try:
        import win32crypt
        encrypted = base64.b64decode(blob_b64)
        _, plaintext = win32crypt.CryptUnprotectData(encrypted, None, None, None, 0)
        return plaintext.decode("utf-8")
    except Exception:
        logger.warning("dpapi_decrypt_failed")
        return None

# SECURITY: Allowed Ollama URL patterns (localhost/private networks only)
_OLLAMA_URL_ALLOWED_PATTERNS = [
    re.compile(r'^https?://localhost(:\d+)?(/.*)?$', re.I),
    re.compile(r'^https?://127\.0\.0\.1(:\d+)?(/.*)?$', re.I),
    re.compile(r'^https?://10\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?(/.*)?$', re.I),
    re.compile(r'^https?://172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}(:\d+)?(/.*)?$', re.I),
    re.compile(r'^https?://192\.168\.\d{1,3}\.\d{1,3}(:\d+)?(/.*)?$', re.I),
    re.compile(r'^https?://\[::1\](:\d+)?(/.*)?$', re.I),
]
# SECURITY: Block these URL patterns (cloud metadata, link-local, etc.)
_OLLAMA_URL_BLOCKED_PATTERNS = [
    re.compile(r'^https?://169\.254\.\d{1,3}\.\d{1,3}', re.I),  # AWS/cloud metadata
    re.compile(r'^https?://metadata\.google\.internal', re.I),   # GCP metadata
    re.compile(r'^https?://\[fd00', re.I),                        # IPv6 link-local
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
        "hotkey": "f9",
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
        "transcription_quality": "balanced",
        "live_transcription_enabled": True,
        "cpu_threads": 0,
        "date_display": "relative",
        "history_days": 2,
        "ui_font_scope": "app",
    }

    def __init__(self, config_path=None):
        if config_path is None:
            appdata_dir = os.path.join(os.environ.get("APPDATA", "."), "RotaAI")
            if not os.path.exists(appdata_dir):
                os.makedirs(appdata_dir)
            config_path = os.path.join(appdata_dir, "config.json")

        self.config_path = config_path
        self.config = self.DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        """Loads configuration from JSON file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # SECURITY: Validate Ollama URL on load
                    if "ollama_url" in loaded_config:
                        if not _is_ollama_url_allowed(loaded_config["ollama_url"]):
                            logger.warning("ollama_url_blocked", blocked_url=loaded_config["ollama_url"])
                            loaded_config["ollama_url"] = self.DEFAULT_CONFIG["ollama_url"]
                    # SECURITY: Decrypt DPAPI-protected keys. The stored value is
                    # either a "dpapi:<blob>" string or a legacy plaintext key.
                    for key in _ENCRYPTED_KEYS:
                        raw = loaded_config.get(key, "")
                        if raw and raw.startswith("dpapi:"):
                            decrypted = _dpapi_decrypt(raw[6:])
                            if decrypted is not None:
                                loaded_config[key] = decrypted
                            else:
                                # Can't decrypt (different machine/user?); clear it
                                logger.warning("dpapi_key_unreadable", config_key=key)
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
                if plaintext and not plaintext.startswith("dpapi:"):
                    blob = _dpapi_encrypt(plaintext)
                    if blob:
                        save_config[key] = "dpapi:" + blob
                    else:
                        # DPAPI unavailable (non-Windows / test env) — log once
                        logger.warning("dpapi_unavailable_storing_plaintext", config_key=key)
            with open(self.config_path, 'w', encoding='utf-8') as f:
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

    def _handle_startup(self):
        """
        Registers/unregisters the application for Windows startup.

        SECURITY: Validates the executable path before writing to the registry
        to prevent persistence via malicious executables.
        """
        if sys.platform != "win32":
            return

        import winreg as reg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "RotaAI"

        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
            if self.config.get("startup_enabled"):
                exe_path = sys.executable

                # SECURITY: Validate executable path
                if not exe_path or not os.path.isfile(exe_path):
                    logger.error("startup_invalid_exe_path", path=exe_path)
                    reg.CloseKey(key)
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
                        reg.CloseKey(key)
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
            reg.CloseKey(key)
        except Exception:
            logger.exception("Failed to update startup registry value")
