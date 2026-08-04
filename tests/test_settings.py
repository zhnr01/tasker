import pytest

from app.config import Settings, get_settings


def test_defaults_load():
    s = Settings(_env_file=None)  # ignore any local .env for a clean baseline
    assert s.ENVIRONMENT == "local"
    assert s.DEFAULT_PAGE_SIZE == 20
    assert s.is_production is False


def test_production_requires_real_secret(monkeypatch):
    # In production the insecure default must be rejected at construction.
    monkeypatch.setenv("TASKER_ENVIRONMENT", "production")
    monkeypatch.setenv("TASKER_SECRET_KEY", "dev-only-insecure-change-me")
    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(_env_file=None)


def test_get_settings_is_cached():
    get_settings.cache_clear()
    a = get_settings()
    b = get_settings()
    assert a is b  # same instance — the lazy singleton works
