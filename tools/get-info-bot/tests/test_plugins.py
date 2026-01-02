"""Tests for plugin system."""

import pytest
from pytest_mock import MockerFixture
from telegram import Message, Update, User
from telegram.ext import ContextTypes

from tools_nn_bot.config import Settings
from tools_nn_bot.http_client import HTTPClient
from tools_nn_bot.plugins.get_info import GetInfoPlugin
from tools_nn_bot.plugins.system_info import SystemPlugin


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        telegram_bot_token="test_token",
        admin_ids=[12345],
        http_timeout=10,
    )


@pytest.mark.asyncio
async def test_get_info_plugin_initialization(test_settings: Settings) -> None:
    """Test get-info plugin initialization."""
    async with HTTPClient(test_settings) as http_client:
        plugin = GetInfoPlugin(test_settings, http_client)
        await plugin.initialize()

        assert plugin.name == "get-info"
        assert plugin.enabled is True
        assert len(plugin.get_handlers()) > 0

        await plugin.cleanup()


@pytest.mark.asyncio
async def test_system_plugin_initialization() -> None:
    """Test system plugin initialization."""
    plugin = SystemPlugin()
    await plugin.initialize()

    assert plugin.name == "system"
    assert plugin.enabled is True
    assert len(plugin.get_handlers()) > 0

    info = plugin.get_info()
    assert info["name"] == "system"
    assert info["version"] == "1.0.0"

    await plugin.cleanup()


@pytest.mark.asyncio
async def test_get_info_plugin_info_command_no_args(
    test_settings: Settings, mocker: MockerFixture
) -> None:
    """Test get-info plugin /info command without args."""
    async with HTTPClient(test_settings) as http_client:
        plugin = GetInfoPlugin(test_settings, http_client)

        user = User(id=12345, is_bot=False, first_name="Test")
        message = mocker.Mock(spec=Message)
        message.reply_text = mocker.AsyncMock()
        update = mocker.Mock(spec=Update)
        update.effective_user = user
        update.message = message
        context = mocker.Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.args = []

        await plugin.info_command(update, context)

        message.reply_text.assert_called_once()
        call_args = message.reply_text.call_args[0][0]
        assert "Usage" in call_args


@pytest.mark.asyncio
async def test_system_plugin_system_command(mocker: MockerFixture) -> None:
    """Test system plugin /system command."""
    plugin = SystemPlugin()
    await plugin.initialize()

    user = User(id=12345, is_bot=False, first_name="Test")
    message = mocker.Mock(spec=Message)
    message.reply_text = mocker.AsyncMock()
    update = mocker.Mock(spec=Update)
    update.effective_user = user
    update.message = message
    context = mocker.Mock(spec=ContextTypes.DEFAULT_TYPE)

    await plugin.system_command(update, context)

    message.reply_text.assert_called_once()
    call_args = message.reply_text.call_args[0][0]
    assert "System Status" in call_args

    await plugin.cleanup()


def test_plugin_enable_disable() -> None:
    """Test plugin enable/disable functionality."""
    plugin = SystemPlugin()

    assert plugin.enabled is True

    plugin.disable()
    assert plugin.enabled is False

    plugin.enable()
    assert plugin.enabled is True
