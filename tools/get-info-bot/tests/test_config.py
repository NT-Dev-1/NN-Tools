"""Tests for configuration module."""

import os

import pytest
from pydantic import ValidationError

from tools_nn_bot.config import Settings, get_settings


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test settings loaded from environment variables."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
    monkeypatch.setenv("ADMIN_IDS", "[12345,67890]")
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "10")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = get_settings()

    assert settings.telegram_bot_token == "test_token"
    assert settings.rate_limit_requests == 10
    assert settings.log_level == "DEBUG"


def test_settings_defaults() -> None:
    """Test default settings values."""
    settings = Settings(telegram_bot_token="test_token", admin_ids=[12345])

    assert settings.rate_limit_requests == 5
    assert settings.rate_limit_window_seconds == 60
    assert settings.http_timeout == 30
    assert settings.http_max_retries == 3
    assert settings.log_level == "INFO"
    assert settings.log_format == "json"


def test_settings_missing_required_field() -> None:
    """Test that missing required field raises validation error."""
    with pytest.raises(ValidationError):
        Settings()


def test_settings_custom_values() -> None:
    """Test settings with custom values."""
    settings = Settings(
        telegram_bot_token="custom_token",
        admin_ids=[11111, 22222],
        rate_limit_requests=20,
        rate_limit_window_seconds=120,
        http_timeout=60,
        log_level="ERROR",
    )

    assert settings.telegram_bot_token == "custom_token"
    assert settings.admin_ids == [11111, 22222]
    assert settings.rate_limit_requests == 20
    assert settings.rate_limit_window_seconds == 120
    assert settings.http_timeout == 60
    assert settings.log_level == "ERROR"


def test_settings_admin_ids_list() -> None:
    """Test that admin_ids is properly configured as a list."""
    settings = Settings(
        telegram_bot_token="test_token",
        admin_ids=[123, 456, 789],
    )

    assert isinstance(settings.admin_ids, list)
    assert len(settings.admin_ids) == 3
    assert 123 in settings.admin_ids
