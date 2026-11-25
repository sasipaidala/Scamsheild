import pytest

from core.config import PROJECT_ROOT, Settings


def test_settings_use_project_relative_database_path(monkeypatch):
    monkeypatch.setenv("SCAMSHIELD_ENV", "test")
    monkeypatch.setenv("SCAMSHIELD_DATABASE_PATH", "tmp/test.db")
    monkeypatch.setenv("SCAMSHIELD_LOG_LEVEL", "DEBUG")

    settings = Settings.from_env()

    assert settings.environment == "test"
    assert settings.database_path == (PROJECT_ROOT / "tmp/test.db").resolve()
    assert settings.log_level == "DEBUG"


def test_invalid_environment_is_rejected(monkeypatch):
    monkeypatch.setenv("SCAMSHIELD_ENV", "staging-ish")
    with pytest.raises(ValueError, match="SCAMSHIELD_ENV"):
        Settings.from_env()


def test_invalid_log_level_is_rejected(monkeypatch):
    monkeypatch.setenv("SCAMSHIELD_LOG_LEVEL", "TRACE")
    with pytest.raises(ValueError, match="SCAMSHIELD_LOG_LEVEL"):
        Settings.from_env()
