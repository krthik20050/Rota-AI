"""
Linux secure storage backend -- replaces Windows DPAPI (pywin32).

Uses the `keyring` library which provides:
- Windows: Windows Credential Locker
- macOS: macOS Keychain
- Linux: Freedesktop Secret Service (GNOME Keyring / KWallet)

Reference: https://github.com/jaraco/keyring
"""

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)

# Keys that should be encrypted at rest
_ENCRYPTED_KEYS = frozenset({"groq_api_key", "gemini_api_key"})

_SERVICE_NAME = "rota-ai"


def encrypt_secret(plaintext: str) -> str:
    """
    Store a secret in the OS keychain.
    Returns "keyring:success" on success, or "plaintext" on failure.
    On Linux, this uses the Freedesktop Secret Service (GNOME Keyring).
    """
    if not plaintext:
        return plaintext

    try:
        import keyring
        keyring.set_password(_SERVICE_NAME, "api_keys", plaintext)
        logger.info("secret_stored_in_keychain", backend=keyring.get_keyring().name)
        return "keyring:success"
    except Exception as e:
        logger.warning("keychain_store_failed", error=str(e))
        # Fallback: return as-is (caller handles plaintext storage)
        return plaintext


def decrypt_secret(stored_value: str) -> str | None:
    """
    Retrieve a secret from the OS keychain.
    If stored_value starts with "keyring:", fetch from keychain.
    Otherwise return as-is (legacy plaintext).
    """
    if not stored_value:
        return None

    if stored_value == "keyring:success":
        # The actual value is stored in the keychain
        try:
            import keyring
            value = keyring.get_password(_SERVICE_NAME, "api_keys")
            if value:
                return value
        except Exception as e:
            logger.warning("keychain_read_failed", error=str(e))
        return None

    if stored_value.startswith("keyring:"):
        # Legacy format: the blob is after the prefix
        # For backward compat with DPAPI-style "dpapi:" prefix
        return None

    # Plaintext (legacy)
    return stored_value


def store_api_key(key_name: str, value: str) -> str:
    """
    Store an API key securely.
    Returns the value to write to config.json (either "keyring:success" or plaintext).
    """
    if key_name in _ENCRYPTED_KEYS and value:
        result = encrypt_secret(value)
        if result == "keyring:success":
            return "keyring:success"
    return value


def load_api_key(key_name: str, stored_value: str) -> str:
    """
    Load an API key, decrypting if necessary.
    """
    if key_name in _ENCRYPTED_KEYS and stored_value:
        if stored_value == "keyring:success":
            decrypted = decrypt_secret(stored_value)
            if decrypted:
                return decrypted
            logger.warning("api_key_unreadable", key=key_name)
            return ""
    return stored_value or ""
