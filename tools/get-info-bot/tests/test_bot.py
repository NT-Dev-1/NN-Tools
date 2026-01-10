"""Tests for bot module."""

import pytest
from pytest_mock import MockerFixture
from telegram import CallbackQuery, Message, Update, User
from telegram.ext import ContextTypes

from tools_nn_bot.bot import ToolsNNBot
from tools_nn_bot.config import Settings


@pytest.fixture
def bot_settings() -> Settings:
    """Create test bot settings."""
    return Settings(
        telegram_bot_token="test_token",
        admin_ids=[12345, 67890],
        rate_limit_requests=5,
        rate_limit_window_seconds=60,
    )


@pytest.fixture
def bot(bot_settings: Settings) -> ToolsNNBot:
    """Create test bot instance."""
    return ToolsNNBot(bot_settings)


def test_is_admin(bot: ToolsNNBot) -> None:
    """Test admin check."""
    assert bot._is_admin(12345) is True
    assert bot._is_admin(67890) is True
    assert bot._is_admin(99999) is False


@pytest.mark.asyncio
async def test_start_command_authorized(bot: ToolsNNBot, mocker: MockerFixture) -> None:
    """Test /start command for authorized user."""
    user = User(id=12345, is_bot=False, first_name="Admin")
    message = mocker.Mock(spec=Message)
    message.reply_text = mocker.AsyncMock()
    update = mocker.Mock(spec=Update)
    update.effective_user = user
    update.message = message
    update.callback_query = None
    context = mocker.Mock(spec=ContextTypes.DEFAULT_TYPE)

    await bot.start_command(update, context)

    message.reply_text.assert_called_once()
    call_args = message.reply_text.call_args
    assert "Tools" in call_args[0][0] or "Tools" in str(call_args)


@pytest.mark.asyncio
async def test_start_command_unauthorized(bot: ToolsNNBot, mocker: MockerFixture) -> None:
    """Test /start command for unauthorized user."""
    user = User(id=99999, is_bot=False, first_name="Intruder")
    message = mocker.Mock(spec=Message)
    message.reply_text = mocker.AsyncMock()
    update = mocker.Mock(spec=Update)
    update.effective_user = user
    update.message = message
    update.callback_query = None
    context = mocker.Mock(spec=ContextTypes.DEFAULT_TYPE)

    await bot.start_command(update, context)

    message.reply_text.assert_called_once()
    call_args = message.reply_text.call_args[0][0]
    assert "Access Denied" in call_args or "denied" in call_args.lower()


@pytest.mark.asyncio
async def test_help_command_authorized(bot: ToolsNNBot, mocker: MockerFixture) -> None:
    """Test /help command for authorized user."""
    user = User(id=12345, is_bot=False, first_name="Admin")
    message = mocker.Mock(spec=Message)
    message.reply_text = mocker.AsyncMock()
    update = mocker.Mock(spec=Update)
    update.effective_user = user
    update.message = message
    update.callback_query = None
    context = mocker.Mock(spec=ContextTypes.DEFAULT_TYPE)

    await bot.help_command(update, context)

    message.reply_text.assert_called_once()
    call_args = message.reply_text.call_args[0][0]
    assert "Help" in call_args


@pytest.mark.asyncio
async def test_callback_query_unauthorized(bot: ToolsNNBot, mocker: MockerFixture) -> None:
    """Test callback query for unauthorized user."""
    user = User(id=99999, is_bot=False, first_name="Intruder")
    callback_query = mocker.Mock(spec=CallbackQuery)
    callback_query.answer = mocker.AsyncMock()
    callback_query.data = "dashboard_main"
    update = mocker.Mock(spec=Update)
    update.effective_user = user
    update.callback_query = callback_query
    update.message = None
    context = mocker.Mock(spec=ContextTypes.DEFAULT_TYPE)

    await bot.callback_query_handler(update, context)

    callback_query.answer.assert_called_once()
    # Check that access was denied
    call_args = callback_query.answer.call_args
    assert call_args[1].get("show_alert") is True


@pytest.mark.asyncio
async def test_inline_query_unauthorized(bot: ToolsNNBot, mocker: MockerFixture) -> None:
    """Test inline query for unauthorized user."""
    user = User(id=99999, is_bot=False, first_name="Intruder")
    inline_query = mocker.Mock()
    inline_query.query = "test query"
    inline_query.answer = mocker.AsyncMock()
    update = mocker.Mock(spec=Update)
    update.effective_user = user
    update.inline_query = inline_query
    context = mocker.Mock(spec=ContextTypes.DEFAULT_TYPE)

    await bot.inline_query(update, context)

    inline_query.answer.assert_called_once()
    # Check that unauthorized result was returned
    call_args = inline_query.answer.call_args[0][0]
    assert len(call_args) == 1
    assert call_args[0].id == "unauthorized"


@pytest.mark.asyncio
async def test_inline_query_authorized_with_rate_limit(
    bot: ToolsNNBot, mocker: MockerFixture
) -> None:
    """Test inline query for authorized user with rate limiting."""
    user = User(id=12345, is_bot=False, first_name="Admin")
    inline_query = mocker.Mock()
    inline_query.query = "test query"
    inline_query.id = "query123"
    inline_query.answer = mocker.AsyncMock()
    update = mocker.Mock(spec=Update)
    update.effective_user = user
    update.inline_query = inline_query
    context = mocker.Mock(spec=ContextTypes.DEFAULT_TYPE)

    # Mock rate limiter to allow
    mocker.patch.object(bot.rate_limiter, "check_rate_limit", return_value=(True, 0.0))

    await bot.inline_query(update, context)

    inline_query.answer.assert_called_once()


@pytest.mark.asyncio
async def test_plugin_initialization(bot: ToolsNNBot, mocker: MockerFixture) -> None:
    """Test plugin initialization."""
    # Mock HTTP client
    mock_http_client = mocker.Mock()
    mock_http_client.__aenter__ = mocker.AsyncMock(return_value=mock_http_client)
    bot.http_client = mock_http_client

    await bot._initialize_plugins()

    # Check that plugins were loaded
    assert len(bot.plugins) > 0
    assert "getinfo" in bot.plugins or "system" in bot.plugins
