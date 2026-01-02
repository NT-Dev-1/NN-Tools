"""Base plugin class for Tools_NNBot plugins."""

from abc import ABC, abstractmethod

from telegram.ext import BaseHandler


class BasePlugin(ABC):
    """Base class for bot plugins."""

    def __init__(self, name: str, description: str, version: str = "1.0.0") -> None:
        """Initialize plugin.

        Args:
            name: Plugin name
            description: Plugin description
            version: Plugin version
        """
        self.name = name
        self.description = description
        self.version = version
        self.enabled = True

    @abstractmethod
    def get_handlers(self) -> list[BaseHandler]:
        """Get list of handlers to register with the bot.

        Returns:
            List of telegram handler objects
        """
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize plugin resources (called on bot startup)."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup plugin resources (called on bot shutdown)."""
        pass

    def get_info(self) -> dict[str, str]:
        """Get plugin information.

        Returns:
            Dictionary with plugin metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "enabled": str(self.enabled),
        }

    def enable(self) -> None:
        """Enable the plugin."""
        self.enabled = True

    def disable(self) -> None:
        """Disable the plugin."""
        self.enabled = False
