# Tools_NNBot

An admin-only Telegram bot with a plugin-based architecture for administrative tools. Built with modern Python async patterns, comprehensive testing, and security best practices.

## Features

- **🔐 Admin-Only Access**: Restricted to configured admin user IDs
- **🎨 Inline Dashboard**: Interactive keyboard-based navigation
- **🔌 Plugin System**: Modular architecture for extensibility
- **📊 Built-in Plugins**:
  - **Get-Info**: Fetch information about URLs and process search queries
  - **System**: System diagnostics and status monitoring
- **⚡ Rate Limiting**: Per-user rate limiting to prevent abuse
- **🔄 Async HTTP Client**: Built with `httpx` including retries and exponential backoff
- **📝 Structured Logging**: JSON and console logging with `structlog`
- **🛡️ Type Safety**: Full type hints and Pydantic configuration
- **🔒 Security**: No hardcoded secrets, environment-based configuration
- **🧪 Testing**: Comprehensive test suite with pytest, pytest-asyncio, respx, and pytest-mock
- **🐳 Containerization**: Docker support for easy deployment
- **🚀 CI/CD**: GitHub Actions workflow for automated testing

## Requirements

- Python 3.10 or higher
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))
- Admin Telegram User IDs

## Installation

### Using pip

```bash
cd tools/get-info-bot
pip install -e .
```

### Using Docker

```bash
cd tools/get-info-bot
docker build -t tools-nn-bot .
docker run -e TELEGRAM_BOT_TOKEN=your_token -e ADMIN_IDS="[123456,789012]" tools-nn-bot
```

## Configuration

Configure the bot using environment variables. Create a `.env` file or set them in your environment:

```bash
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ADMIN_IDS=[123456789,987654321]  # List of authorized admin user IDs

# Optional (with defaults)
WELCOME_MESSAGE="🤖 *Welcome to Tools\\_NNBot*..."  # Custom welcome message
RATE_LIMIT_REQUESTS=5                # Max requests per time window
RATE_LIMIT_WINDOW_SECONDS=60         # Time window in seconds
HTTP_TIMEOUT=30                       # HTTP request timeout
HTTP_MAX_RETRIES=3                    # Max HTTP retry attempts
HTTP_RETRY_WAIT_MIN=1.0               # Min wait between retries
HTTP_RETRY_WAIT_MAX=10.0              # Max wait between retries
LOG_LEVEL=INFO                        # Logging level
LOG_FORMAT=json                       # Log format (json or console)
MAX_RESPONSE_LENGTH=4096              # Max bot response length
```

### Getting Your Admin ID

To find your Telegram user ID:
1. Message [@userinfobot](https://t.me/userinfobot)
2. It will reply with your user ID
3. Add this ID to the `ADMIN_IDS` configuration

## Usage

### Command Line

```bash
# Install the package
pip install -e .

# Run the bot
tools-nn-bot

# Or run directly with Python
python -m tools_nn_bot.cli
```

### Telegram Commands

Once the bot is running, authorized admins can use these commands:

- `/start` - Show welcome message and inline dashboard
- `/help` - Display detailed help information
- `/info <url>` - Get information about a URL (via get-info plugin)
- `/info <query>` - Process a search query (via get-info plugin)
- `/system` - Show system status and diagnostics

### Inline Dashboard

The bot features an interactive inline keyboard dashboard accessible via `/start`:

- **📊 System Status** - View bot uptime and system information
- **🔌 Plugins** - Manage and view installed plugins
- **ℹ️ Help** - Quick help reference
- **⚙️ Settings** - View current bot configuration
- **🔄 Refresh** - Refresh the dashboard

### Inline Mode

Authorized admins can use the bot in inline mode in any chat:

```
@your_bot_name <query>
```

## Architecture

### Plugin System

Tools_NNBot uses a modular plugin architecture for easy extensibility:

```python
from tools_nn_bot.plugins import BasePlugin

class MyPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="my-plugin",
            description="My custom plugin",
            version="1.0.0"
        )
    
    def get_handlers(self):
        return [CommandHandler("mycommand", self.my_handler)]
    
    async def initialize(self):
        # Setup code
        pass
    
    async def cleanup(self):
        # Cleanup code
        pass
```

### Current Plugins

#### Get-Info Plugin
- Fetches URL information (status, headers, title)
- Processes search queries
- Includes retry logic and error handling

#### System Plugin
- Displays bot uptime
- Shows system information
- Monitors plugin status

### Components

- **`config.py`**: Pydantic-based configuration with admin access control
- **`logging_config.py`**: Structured logging setup with structlog
- **`rate_limiter.py`**: Per-user sliding window rate limiter
- **`http_client.py`**: Async HTTP client with retry logic
- **`bot.py`**: Main bot with admin checks and plugin management
- **`dashboard.py`**: Inline keyboard dashboard definitions
- **`plugins/`**: Plugin system and built-in plugins
  - `base.py`: Base plugin class
  - `get_info.py`: URL/query information plugin
  - `system_info.py`: System diagnostics plugin
- **`cli.py`**: Command-line interface entry point

### Design Decisions

1. **Admin-Only Access**: All commands require authorization via configured admin IDs
2. **Plugin Architecture**: Modular design for easy extensibility
3. **Inline Dashboard**: User-friendly navigation via inline keyboards
4. **Async All The Way**: Uses `asyncio` throughout for efficient I/O operations
5. **Type Safety**: Full type hints for better IDE support and error detection
6. **Configuration**: Environment-based configuration following 12-factor app principles
7. **Structured Logging**: Better observability and debugging
8. **Rate Limiting**: Per-user limits with sliding window to prevent abuse
9. **Retry Logic**: Exponential backoff for HTTP requests

## Development

### Setup Development Environment

```bash
# Clone the repository
cd tools/get-info-bot

# Install with development dependencies
pip install -e ".[dev]"

# Create .env file with your credentials
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_token_here
ADMIN_IDS=[your_user_id]
LOG_LEVEL=DEBUG
LOG_FORMAT=console
EOF
```

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_bot.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=tools_nn_bot --cov-report=html
```

### Code Quality

```bash
# Format code with black
black src tests

# Lint with ruff
ruff check src tests

# Type checking with mypy
mypy src
```

### Adding New Plugins

1. Create a new file in `src/tools_nn_bot/plugins/`
2. Inherit from `BasePlugin`
3. Implement required methods: `get_handlers()`, `initialize()`, `cleanup()`
4. Register in `bot.py` `_initialize_plugins()` method
5. Add tests in `tests/test_plugins.py`

## Security Considerations

- **Admin-Only Access**: All functionality restricted to configured admin IDs
- **No Hardcoded Secrets**: All sensitive data loaded from environment variables
- **Rate Limiting**: Prevents abuse and DoS attacks
- **Input Validation**: URL validation before processing
- **Timeout Protection**: HTTP requests have configurable timeouts
- **Error Handling**: Graceful error handling prevents information leakage
- **Structured Logging**: Logs don't expose sensitive data

## CVE Research & Best Practices

This bot was developed following current security best practices:

1. **Dependency Management**: Using latest stable versions with known vulnerability checks
2. **Environment Variables**: Secrets never committed to version control
3. **Input Validation**: User input sanitized and validated
4. **Admin Authorization**: All access restricted to authorized users
5. **Rate Limiting**: Protection against abuse
6. **Logging**: Structured logging without exposing sensitive data
7. **HTTP Security**: Using HTTPS, timeout protection, and retry limits
8. **Container Security**: Minimal Docker image with non-root user

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t tools-nn-bot .

# Run container
docker run -d \
  --name tools-nn-bot \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e ADMIN_IDS="[123456,789012]" \
  -e LOG_LEVEL=INFO \
  tools-nn-bot
```

### Docker Compose

```yaml
version: '3.8'
services:
  bot:
    build: .
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - ADMIN_IDS=${ADMIN_IDS}
      - LOG_LEVEL=INFO
      - LOG_FORMAT=json
    restart: unless-stopped
```

## Troubleshooting

### Bot Not Responding

1. Check bot token is correct
2. Verify your user ID is in ADMIN_IDS list
3. Check logs for errors: `docker logs tools-nn-bot`

### Access Denied Messages

- Ensure your Telegram user ID is correctly added to ADMIN_IDS
- Format should be: `ADMIN_IDS=[123456,789012]` (as a JSON list)

### Rate Limit Issues

Adjust rate limit settings in environment variables:

```bash
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW_SECONDS=60
```

### HTTP Timeout Errors

Increase timeout settings:

```bash
HTTP_TIMEOUT=60
HTTP_MAX_RETRIES=5
```

## License

MIT License - See repository license for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the test suite
5. Submit a pull request

## Support

For issues and questions, please open an issue in the GitHub repository.
