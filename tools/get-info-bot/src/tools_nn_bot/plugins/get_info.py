"""Get-Info plugin for fetching URL and query information."""

import re

from telegram import Update
from telegram.ext import BaseHandler, CommandHandler, ContextTypes

from ..config import Settings
from ..http_client import HTTPClient
from ..logging_config import get_logger
from .base import BasePlugin

logger = get_logger(__name__)


class GetInfoPlugin(BasePlugin):
    """Plugin for fetching URL/query information."""

    def __init__(self, settings: Settings, http_client: HTTPClient) -> None:
        """Initialize get-info plugin.

        Args:
            settings: Application settings
            http_client: HTTP client instance
        """
        super().__init__(
            name="get-info",
            description="Fetch information about URLs and search queries",
            version="1.0.0",
        )
        self.settings = settings
        self.http_client = http_client

    def get_handlers(self) -> list[BaseHandler]:
        """Get plugin handlers.

        Returns:
            List of command handlers
        """
        return [
            CommandHandler("info", self.info_command),
        ]

    async def initialize(self) -> None:
        """Initialize plugin resources."""
        logger.info("get_info_plugin_initialized")

    async def cleanup(self) -> None:
        """Cleanup plugin resources."""
        logger.info("get_info_plugin_cleanup")

    async def info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /info command.

        Args:
            update: Telegram update
            context: Callback context
        """
        user = update.effective_user
        if not user:
            return

        logger.info("info_command", user_id=user.id)

        # Get query/URL from command arguments
        if not context.args:
            await update.message.reply_text(
                "📝 *Get Info Plugin*\n\n"
                "Usage: `/info <url|query>`\n\n"
                "Examples:\n"
                "• `/info https://example.com`\n"
                "• `/info python programming`",
                parse_mode="Markdown",
            )
            return

        query_text = " ".join(context.args)
        result = await self._process_info_request(query_text)

        # Truncate if too long
        if len(result) > self.settings.max_response_length:
            result = result[: self.settings.max_response_length - 100] + "\n\n[Truncated...]"

        await update.message.reply_text(result, parse_mode="Markdown")

    async def _process_info_request(self, text: str) -> str:
        """Process an info request for URL or query.

        Args:
            text: URL or search query

        Returns:
            Formatted result string
        """
        # Check if it's a URL
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
            r"localhost|"  # localhost
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # or IP
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        if url_pattern.match(text):
            # It's a URL
            info = await self.http_client.fetch_url_info(text)
            return self._format_url_info(info)
        else:
            # It's a search query
            info = await self.http_client.search_query(text)
            return self._format_query_info(info)

    def _format_url_info(self, info: dict[str, str]) -> str:
        """Format URL information for display.

        Args:
            info: URL information dictionary

        Returns:
            Formatted string
        """
        if "error" in info:
            return f"❌ *Error fetching URL*\n\n`{info.get('error', 'Unknown error')}`"

        lines = ["🔗 *URL Information*\n"]
        lines.append(f"*URL:* `{info.get('url', 'N/A')}`")
        lines.append(f"*Status:* `{info.get('status_code', 'N/A')}`")
        lines.append(f"*Content Type:* `{info.get('content_type', 'N/A')}`")
        lines.append(f"*Content Length:* `{info.get('content_length', 'N/A')}`")
        lines.append(f"*Server:* `{info.get('server', 'N/A')}`")

        if "title" in info:
            # Escape markdown special characters in title
            title = (
                info["title"]
                .replace("_", "\\_")
                .replace("*", "\\*")
                .replace("[", "\\[")
                .replace("`", "\\`")
            )
            lines.append(f"*Title:* {title}")

        return "\n".join(lines)

    def _format_query_info(self, info: dict[str, str]) -> str:
        """Format query information for display.

        Args:
            info: Query information dictionary

        Returns:
            Formatted string
        """
        lines = ["🔍 *Query Results*\n"]
        lines.append(f"*Query:* `{info.get('query', 'N/A')}`")
        lines.append(f"*Result:* {info.get('result', 'N/A')}")

        if "note" in info:
            lines.append(f"\n_Note: {info['note']}_")

        return "\n".join(lines)
