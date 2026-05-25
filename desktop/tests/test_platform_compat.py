"""Cross-platform compatibility regression tests."""

from unittest.mock import MagicMock, patch

from app.health_check import StartupHealthChecker
from audio.audio_control import SystemAudioController
from plat.linux_secrets import decrypt_secret, encrypt_secret


class MockConfig:
    def __init__(self, data):
        self.data = data

    def get(self, key, default=None):
        return self.data.get(key, default)


def test_keyring_secrets_are_stored_per_config_key():
    store = {}
    fake_keyring = MagicMock()
    fake_keyring.get_keyring.return_value.name = "fake-keyring"
    fake_keyring.set_password.side_effect = lambda service, account, value: store.__setitem__(
        (service, account), value
    )
    fake_keyring.get_password.side_effect = lambda service, account: store.get((service, account))

    with patch.dict("sys.modules", {"keyring": fake_keyring}):
        groq_ref = encrypt_secret("groq-secret", account="groq_api_key")
        gemini_ref = encrypt_secret("gemini-secret", account="gemini_api_key")

        assert groq_ref == "keyring:groq_api_key"
        assert gemini_ref == "keyring:gemini_api_key"
        assert decrypt_secret(groq_ref, account="groq_api_key") == "groq-secret"
        assert decrypt_secret(gemini_ref, account="gemini_api_key") == "gemini-secret"


@patch("audio.audio_control._IS_MACOS", True)
@patch("audio.audio_control._IS_WINDOWS", False)
def test_macos_mute_mode_uses_macos_volume_control():
    config = MockConfig({"bg_audio_control": "mute"})
    controller = SystemAudioController(config)

    with patch.object(controller, "_macos_set_output_muted", return_value=True) as mute:
        controller.pause_or_mute()
        assert controller._muted_by_us is True
        mute.assert_called_once_with(True)

        controller.resume_or_unmute()
        assert controller._muted_by_us is False
        mute.assert_any_call(False)


@patch("app.health_check.sys.platform", "linux")
@patch("app.health_check.shutil.which", return_value=None)
def test_linux_health_check_reports_missing_integration_tools(_which):
    checker = StartupHealthChecker(appdata_dir=".", model_size="small.en")

    with patch.dict("sys.modules", {"evdev": None}):
        item = checker._check_platform_integration()

    assert item.name == "platform_integration"
    assert item.status == "failed"
    assert item.critical is True
    assert "Linux integration missing" in item.message


@patch("app.health_check.sys.platform", "darwin")
def test_macos_health_check_reports_missing_pyobjc():
    checker = StartupHealthChecker(appdata_dir=".", model_size="small.en")

    with patch.dict("sys.modules", {"AppKit": None, "ApplicationServices": None, "Quartz": None}):
        item = checker._check_platform_integration()

    assert item.name == "platform_integration"
    assert item.status == "failed"
    assert item.critical is True
    assert "macOS integration incomplete" in item.message
