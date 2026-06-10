---
title: Security & Local Storage
---

Rota AI is designed under a local-first security architecture. No analytical tracking telemetries exist, and all personal user configurations, voice snippets, dictation history logs, and API credentials are kept strictly on your local machine.

---

### Local SQLite Database
Rota AI stores your structured history logs and snippet shortcuts inside a local SQLite database named `rota.db` under the OS-appropriate storage directory.

#### Database Schema Details

##### 1. Table: `history`
Caches raw transcriptions, AI-cleaned transcriptions, date stamps, and application metadata.
```sql
CREATE TABLE history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    raw_text TEXT NOT NULL,
    cleaned_text TEXT NOT NULL,
    app_name TEXT,
    window_title TEXT,
    backend TEXT
);
```

##### 2. Table: `snippets`
Stores triggers and text expansion templates.
```sql
CREATE TABLE snippets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger_phrase TEXT NOT NULL UNIQUE,
    expansion_text TEXT NOT NULL
);
```

---

### Encrypted API Credential Storage
To prevent malware or unauthorized scripts from scraping your cloud API keys (Groq/Gemini), Rota AI encrypts your configuration file and API secrets at rest using platform-native hardware encryption mechanisms.

#### 1. Windows: Data Protection API (DPAPI)
On Windows, keys are encrypted using DPAPI (`win32crypt.CryptProtectData`).
* **Security Model**: The key is encrypted using the Windows User Account credentials. Only processes running under your specific Windows login session can decrypt the data. Even if files are stolen off the disk, they cannot be decrypted on another machine.

#### 2. macOS: Keychain Services
On macOS, keys are stored in the secure macOS System Keychain.
* **Security Model**: Access permissions are controlled by the OS. The first time Rota AI queries the Keychain, a macOS security popup asks you to grant Rota permission to read the Keychain key.

#### 3. Linux: Secret Service API
On Linux, Rota AI connects to the standard D-Bus Secret Service provider (e.g., `GNOME Keyring` or `KWallet`) via the Python `keyring` module.
* **Security Model**: The database is encrypted using your user login session keyring, unlocked automatically when you sign into your desktop.
