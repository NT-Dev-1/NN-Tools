"""Configuration module for Tools_NNBot using Pydantic settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Telegram Bot Configuration
    telegram_bot_token: str = Field(
        ...,
        description="Telegram Bot API token from @BotFather",
    )

    # Admin Configuration
    admin_ids: list[int] = Field(
        default_factory=list,
        description="Comma-separated list of admin Telegram user IDs",
    )

    # Welcome Message (raw - will be escaped for MarkdownV2 when displayed)
    welcome_message: str = Field(
        default=(
            "🤖 *Welcome to Tools_NNBot*\n\n"
            "Your personal administrative assistant bot.\n\n"
            "Available commands:\n"
            "• /start - Show this dashboard\n"
            "• /info <url|query> - Fetch URL/query information\n"
            "• /system - System status and diagnostics\n"
            "• /help - Detailed help information\n\n"
            "Use inline mode: @botname <command>\n\n"
            "_This bot is restricted to authorized administrators._"
        ),
        description="Custom welcome message shown to admins (will be escaped for MarkdownV2)",
    )

    # Rate Limiting Configuration
    rate_limit_requests: int = Field(
        default=5,
        description="Maximum number of requests per user per time window",
    )
    rate_limit_window_seconds: int = Field(
        default=60,
        description="Time window for rate limiting in seconds",
    )

    # HTTP Client Configuration
    http_timeout: int = Field(
        default=30,
        description="HTTP request timeout in seconds",
    )
    http_max_retries: int = Field(
        default=3,
        description="Maximum number of HTTP retry attempts",
    )
    http_retry_wait_min: float = Field(
        default=1.0,
        description="Minimum wait time between retries in seconds",
    )
    http_retry_wait_max: float = Field(
        default=10.0,
        description="Maximum wait time between retries in seconds",
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    log_format: str = Field(
        default="json",
        description="Log format (json or console)",
    )

    # Application Configuration
    max_response_length: int = Field(
        default=4096,
        description="Maximum length of bot response messages",
    )


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()
