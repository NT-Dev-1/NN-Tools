"""System plugin for bot diagnostics and status."""

import asyncio
import platform
import sys
from datetime import datetime
from typing import List

from telegram import Update
from telegram.ext import BaseHandler, CommandHandler, ContextTypes

from ..logging_config import get_logger
from .base import BasePlugin

logger = get_logger(__name__)


class SystemPlugin(BasePlugin):
    """Plugin for system information and diagnostics."""

    def __init__(self) -> None:
        """Initialize system plugin."""
        super().__init__(
            name="system",
            description="System information and diagnostics",
            version="1.0.0",
        )
        self.start_time = datetime.now()

    def get_handlers(self) -> List[BaseHandler]:
        """Get plugin handlers.

        Returns:
            List of command handlers
        """
        return [
            CommandHandler("system", self.system_command),
        ]

    async def initialize(self) -> None:
        """Initialize plugin resources."""
        logger.info("system_plugin_initialized")
        self.start_time = datetime.now()

    async def cleanup(self) -> None:
        """Cleanup plugin resources."""
        logger.info("system_plugin_cleanup")

    async def system_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /system command.

        Args:
            update: Telegram update
            context: Callback context
        """
        user = update.effective_user
        if not user:
            return

        logger.info("system_command", user_id=user.id)

        # Calculate uptime
        uptime = datetime.now() - self.start_time
        uptime_str = self._format_uptime(uptime.total_seconds())

        # Get system information
        system_info = [
            "⚙️ *System Status*\n",
            f"*Bot Uptime:* `{uptime_str}`",
            f"*Python Version:* `{sys.version.split()[0]}`",
            f"*Platform:* `{platform.system()} {platform.release()}`",
            f"*Start Time:* `{self.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}`",
            f"\n*Process Info:*",
            f"• PID: `{asyncio.current_task().get_name() if asyncio.current_task() else 'N/A'}`",
        ]

        message = "\n".join(system_info)
        await update.message.reply_text(message, parse_mode="Markdown")

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format.

        Args:
            seconds: Uptime in seconds

        Returns:
            Formatted uptime string
        """
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")

        return " ".join(parts)
