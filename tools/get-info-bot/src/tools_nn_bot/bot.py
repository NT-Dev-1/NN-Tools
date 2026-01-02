"""Tools_NNBot - Admin-only Telegram bot with plugin system."""

import asyncio
from typing import Dict, List, Optional

from telegram import CallbackQuery, InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    InlineQueryHandler,
)

from .config import Settings
from .dashboard import (
    create_back_button,
    create_main_dashboard,
    create_plugins_dashboard,
)
from .http_client import HTTPClient
from .logging_config import get_logger
from .plugins import BasePlugin, GetInfoPlugin, SystemPlugin
from .rate_limiter import RateLimiter

logger = get_logger(__name__)


class ToolsNNBot:
    """Admin-only Telegram bot with plugin system and inline dashboard."""

    def __init__(self, settings: Settings) -> None:
        """Initialize bot.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.rate_limiter = RateLimiter(
            max_requests=settings.rate_limit_requests,
            window_seconds=settings.rate_limit_window_seconds,
        )
        self.http_client: Optional[HTTPClient] = None
        self.plugins: Dict[str, BasePlugin] = {}

    def _is_admin(self, user_id: int) -> bool:
        """Check if user is an admin.

        Args:
            user_id: Telegram user ID

        Returns:
            True if user is admin, False otherwise
        """
        if not self.settings.admin_ids:
            logger.warning("no_admins_configured", message="No admin IDs configured, denying access")
            return False
        return user_id in self.settings.admin_ids

    async def _check_admin_access(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> bool:
        """Check if user has admin access and respond accordingly.

        Args:
            update: Telegram update
            context: Callback context

        Returns:
            True if user is admin, False otherwise
        """
        user = update.effective_user
        if not user:
            return False

        if not self._is_admin(user.id):
            logger.warning("unauthorized_access_attempt", user_id=user.id)
            # Send unauthorized message
            message = (
                "⛔️ *Access Denied*\n\n"
                "This bot is restricted to authorized administrators only\\.\n\n"
                "_Contact the bot owner if you believe this is an error\\._"
            )
            if update.message:
                await update.message.reply_text(message, parse_mode="MarkdownV2")
            elif update.callback_query:
                await update.callback_query.answer("Access denied", show_alert=True)
            return False

        return True


    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command - show welcome and inline dashboard.

        Args:
            update: Telegram update
            context: Callback context
        """
        if not await self._check_admin_access(update, context):
            return

        user = update.effective_user
        logger.info("start_command", user_id=user.id if user else None)

        # Send custom welcome message with inline dashboard
        await update.message.reply_text(
            self.settings.welcome_message,
            reply_markup=create_main_dashboard(),
            parse_mode="MarkdownV2",
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command.

        Args:
            update: Telegram update
            context: Callback context
        """
        if not await self._check_admin_access(update, context):
            return

        user = update.effective_user
        logger.info("help_command", user_id=user.id if user else None)

        # Build help message with plugin information
        help_lines = [
            "📚 *Tools\\_NNBot Help*\n",
            "*Core Commands:*",
            "• `/start` \\- Show dashboard",
            "• `/help` \\- This help message",
            "",
            "*Available Plugins:*",
        ]

        for plugin_name, plugin in self.plugins.items():
            status = "✅" if plugin.enabled else "❌"
            help_lines.append(
                f"{status} *{plugin.name}* \\- {plugin.description}"
            )

        help_lines.extend([
            "",
            f"*Rate Limiting:* {self.settings.rate_limit_requests} requests per "
            f"{self.settings.rate_limit_window_seconds} seconds",
            "",
            "_Use the inline dashboard for quick access to features\\._",
        ])

        help_message = "\n".join(help_lines)
        await update.message.reply_text(
            help_message, 
            reply_markup=create_back_button(),
            parse_mode="MarkdownV2"
        )


    async def callback_query_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle inline keyboard button callbacks.

        Args:
            update: Telegram update
            context: Callback context
        """
        if not await self._check_admin_access(update, context):
            return

        query = update.callback_query
        if not query:
            return

        await query.answer()

        callback_data = query.data
        logger.info("callback_query", data=callback_data)

        # Route to appropriate handler
        if callback_data == "dashboard_main" or callback_data == "dashboard_refresh":
            await self._handle_main_dashboard(query)
        elif callback_data == "dashboard_system":
            await self._handle_system_dashboard(query)
        elif callback_data == "dashboard_plugins":
            await self._handle_plugins_dashboard(query)
        elif callback_data == "dashboard_help":
            await self._handle_help_dashboard(query)
        elif callback_data == "dashboard_settings":
            await self._handle_settings_dashboard(query)
        elif callback_data.startswith("plugin_info_"):
            plugin_name = callback_data.replace("plugin_info_", "")
            await self._handle_plugin_info(query, plugin_name)

    async def _handle_main_dashboard(self, query: CallbackQuery) -> None:
        """Handle main dashboard callback.

        Args:
            query: Callback query
        """
        await query.edit_message_text(
            self.settings.welcome_message,
            reply_markup=create_main_dashboard(),
            parse_mode="MarkdownV2",
        )

    async def _handle_system_dashboard(self, query: CallbackQuery) -> None:
        """Handle system dashboard callback.

        Args:
            query: Callback query
        """
        # Get system plugin if available
        system_plugin = self.plugins.get("system")
        if system_plugin and isinstance(system_plugin, SystemPlugin):
            uptime = asyncio.get_event_loop().time()
            uptime_formatted = system_plugin._format_uptime(uptime)

            message = (
                "⚙️ *System Status*\n\n"
                f"*Uptime:* `{uptime_formatted}`\n"
                f"*Loaded Plugins:* {len(self.plugins)}\n"
                f"*Rate Limiter:* Active\n"
                f"*Admin Count:* {len(self.settings.admin_ids)}\n"
            )
        else:
            message = "⚙️ *System Status*\n\nSystem plugin not available\\."

        await query.edit_message_text(
            message,
            reply_markup=create_back_button(),
            parse_mode="MarkdownV2",
        )

    async def _handle_plugins_dashboard(self, query: CallbackQuery) -> None:
        """Handle plugins dashboard callback.

        Args:
            query: Callback query
        """
        plugin_list = []
        for plugin_name, plugin in self.plugins.items():
            status = "✅" if plugin.enabled else "❌"
            plugin_list.append(f"{status} *{plugin.name}* v{plugin.version}")

        if not plugin_list:
            plugin_list.append("_No plugins loaded_")

        message = "🔌 *Installed Plugins*\n\n" + "\n".join(plugin_list)
        message += "\n\n_Tap a button below for details\\._"

        await query.edit_message_text(
            message,
            reply_markup=create_plugins_dashboard(),
            parse_mode="MarkdownV2",
        )

    async def _handle_help_dashboard(self, query: CallbackQuery) -> None:
        """Handle help dashboard callback.

        Args:
            query: Callback query
        """
        help_lines = [
            "📚 *Quick Help*\n",
            "*Commands:*",
            "• `/start` \\- Dashboard",
            "• `/help` \\- Full help",
            "• `/info <url>` \\- Get URL info",
            "• `/system` \\- System status",
            "",
            "_Use inline mode: @botname \\<query\\>_",
        ]

        message = "\n".join(help_lines)
        await query.edit_message_text(
            message,
            reply_markup=create_back_button(),
            parse_mode="MarkdownV2",
        )

    async def _handle_settings_dashboard(self, query: CallbackQuery) -> None:
        """Handle settings dashboard callback.

        Args:
            query: Callback query
        """
        message = (
            "⚙️ *Bot Settings*\n\n"
            f"*Rate Limit:* {self.settings.rate_limit_requests} per "
            f"{self.settings.rate_limit_window_seconds}s\n"
            f"*HTTP Timeout:* {self.settings.http_timeout}s\n"
            f"*Log Level:* `{self.settings.log_level}`\n"
            f"*Authorized Admins:* {len(self.settings.admin_ids)}\n"
        )

        await query.edit_message_text(
            message,
            reply_markup=create_back_button(),
            parse_mode="MarkdownV2",
        )

    async def _handle_plugin_info(self, query: CallbackQuery, plugin_name: str) -> None:
        """Handle plugin info callback.

        Args:
            query: Callback query
            plugin_name: Name of the plugin
        """
        plugin = self.plugins.get(plugin_name)
        if not plugin:
            message = f"❌ Plugin '{plugin_name}' not found\\."
        else:
            status = "✅ Enabled" if plugin.enabled else "❌ Disabled"
            message = (
                f"🔌 *{plugin.name}*\n\n"
                f"*Version:* `{plugin.version}`\n"
                f"*Status:* {status}\n"
                f"*Description:* {plugin.description}\n"
            )

        await query.edit_message_text(
            message,
            reply_markup=create_back_button(),
            parse_mode="MarkdownV2",
        )


    async def inline_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle inline queries (admin-only).

        Args:
            update: Telegram update
            context: Callback context
        """
        query = update.inline_query
        if not query:
            return

        user = update.effective_user
        if not user:
            return

        # Check admin access for inline queries
        if not self._is_admin(user.id):
            logger.warning("unauthorized_inline_query", user_id=user.id)
            result = InlineQueryResultArticle(
                id="unauthorized",
                title="⛔️ Access Denied",
                input_message_content=InputTextMessageContent(
                    "This bot is restricted to authorized administrators only."
                ),
            )
            await query.answer([result], cache_time=5)
            return

        query_text = query.query.strip()
        if not query_text:
            return

        logger.info("inline_query", user_id=user.id, query=query_text)

        # Check rate limit
        is_allowed, retry_after = await self.rate_limiter.check_rate_limit(user.id)
        if not is_allowed:
            result = InlineQueryResultArticle(
                id="rate_limit",
                title="⚠️ Rate Limit Exceeded",
                input_message_content=InputTextMessageContent(
                    f"Rate limit exceeded. Try again in {int(retry_after)} seconds."
                ),
            )
            await query.answer([result], cache_time=5)
            return

        # Simple inline query response
        result = InlineQueryResultArticle(
            id=query.id,
            title=f"Tools NNBot: {query_text[:50]}",
            input_message_content=InputTextMessageContent(
                f"🤖 Processing: {query_text}\n\nUse /info {query_text} for detailed results."
            ),
            description=query_text[:100],
        )

        await query.answer([result], cache_time=60)


    async def run(self) -> None:
        """Run the bot."""
        logger.info("starting_bot", bot_name="Tools_NNBot")

        # Validate configuration
        if not self.settings.admin_ids:
            logger.error("no_admin_ids_configured")
            raise ValueError("No admin IDs configured. Set ADMIN_IDS environment variable.")

        logger.info("admin_ids_configured", count=len(self.settings.admin_ids))

        # Initialize HTTP client
        self.http_client = HTTPClient(self.settings)
        await self.http_client.__aenter__()

        # Initialize plugins
        await self._initialize_plugins()

        # Create application
        application = Application.builder().token(self.settings.telegram_bot_token).build()

        # Add core handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CallbackQueryHandler(self.callback_query_handler))
        application.add_handler(InlineQueryHandler(self.inline_query))

        # Add plugin handlers
        for plugin_name, plugin in self.plugins.items():
            if plugin.enabled:
                for handler in plugin.get_handlers():
                    application.add_handler(handler)
                logger.info("plugin_handlers_registered", plugin=plugin_name)

        # Start cleanup task
        cleanup_task = asyncio.create_task(self._cleanup_loop())

        try:
            # Run the bot
            logger.info("bot_started", plugins=len(self.plugins))
            await application.run_polling(allowed_updates=Update.ALL_TYPES)
        finally:
            cleanup_task.cancel()
            await self._cleanup_plugins()
            if self.http_client:
                await self.http_client.__aexit__(None, None, None)
            logger.info("bot_stopped")

    async def _initialize_plugins(self) -> None:
        """Initialize all plugins."""
        logger.info("initializing_plugins")

        # Initialize Get Info plugin
        if self.http_client:
            get_info_plugin = GetInfoPlugin(self.settings, self.http_client)
            await get_info_plugin.initialize()
            self.plugins["getinfo"] = get_info_plugin
            logger.info("plugin_loaded", name="get-info")

        # Initialize System plugin
        system_plugin = SystemPlugin()
        await system_plugin.initialize()
        self.plugins["system"] = system_plugin
        logger.info("plugin_loaded", name="system")

        logger.info("plugins_initialized", count=len(self.plugins))

    async def _cleanup_plugins(self) -> None:
        """Cleanup all plugins."""
        logger.info("cleaning_up_plugins")
        for plugin_name, plugin in self.plugins.items():
            try:
                await plugin.cleanup()
                logger.info("plugin_cleaned_up", plugin=plugin_name)
            except Exception as e:
                logger.error("plugin_cleanup_error", plugin=plugin_name, error=str(e))

    async def _cleanup_loop(self) -> None:
        """Periodic cleanup of rate limiter entries."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self.rate_limiter.cleanup_old_entries()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("cleanup_error", error=str(e))
