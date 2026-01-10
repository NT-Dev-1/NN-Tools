"""Test configuration module."""

import pytest

from tools_nn_bot.config import Settings


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        telegram_bot_token="test_token_12345",
        admin_ids=[12345, 67890],
        rate_limit_requests=5,
        rate_limit_window_seconds=60,
        http_timeout=10,
        http_max_retries=3,
        log_level="DEBUG",
        log_format="console",
    )
