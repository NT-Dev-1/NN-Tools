"""Command-line interface for Tools_NNBot."""

import asyncio
import sys

from .bot import ToolsNNBot
from .config import get_settings
from .logging_config import configure_logging, get_logger


def main() -> None:
    """Main entry point for the CLI."""
    try:
        # Load settings
        settings = get_settings()

        # Configure logging
        configure_logging(log_level=settings.log_level, log_format=settings.log_format)
        logger = get_logger(__name__)

        logger.info("starting_application", bot="Tools_NNBot", version="0.1.0")

        # Create and run bot
        bot = ToolsNNBot(settings)
        asyncio.run(bot.run())

    except KeyboardInterrupt:
        logger = get_logger(__name__)
        logger.info("shutdown_requested")
        sys.exit(0)
    except Exception as e:
        logger = get_logger(__name__)
        logger.error("application_error", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
