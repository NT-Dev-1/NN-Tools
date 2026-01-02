# Get Info Bot

A production-ready Telegram bot for fetching information about URLs and processing search queries. Built with modern Python async patterns, comprehensive testing, and security best practices.

## Features

- **Telegram Bot Integration**: `/info` command and inline query support
- **Rate Limiting**: Per-user rate limiting to prevent abuse
- **Async HTTP Client**: Built with `httpx` including retries and exponential backoff
- **Structured Logging**: JSON and console logging with `structlog`
- **Type Safety**: Full type hints and Pydantic configuration
- **Security**: No hardcoded secrets, environment-based configuration
- **Testing**: Comprehensive test suite with pytest, pytest-asyncio, respx, and pytest-mock
- **Containerization**: Docker support for easy deployment
- **CI/CD**: GitHub Actions workflow for automated testing

## Requirements

- Python 3.10 or higher
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))

## Installation

### Using pip

```bash
cd tools/get-info-bot
pip install -e .
```

### Using Docker

```bash
cd tools/get-info-bot
docker build -t get-info-bot .
docker run -e TELEGRAM_BOT_TOKEN=your_token get-info-bot
```

## Configuration

Configure the bot using environment variables. Create a `.env` file or set them in your environment:

```bash
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Optional (with defaults)
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

## Usage

### Command Line

```bash
# Install the package
pip install -e .

# Run the bot
get-info-bot

# Or run directly with Python
python -m get_info_bot.cli
```

### Telegram Commands

Once the bot is running, use these commands in Telegram:

- `/start` - Welcome message and bot overview
- `/help` - Display help information
- `/info <url>` - Get information about a URL
- `/info <query>` - Process a search query

### Inline Mode

You can also use the bot in inline mode in any chat:

```
@your_bot_name https://example.com
@your_bot_name search query
```

## Development

### Setup Development Environment

```bash
# Clone the repository
cd tools/get-info-bot

# Install with development dependencies
pip install -e ".[dev]"

# Create .env file with your bot token
echo "TELEGRAM_BOT_TOKEN=your_token" > .env
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
pytest --cov=get_info_bot --cov-report=html
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

## Architecture

### Components

- **`config.py`**: Pydantic-based configuration management
- **`logging_config.py`**: Structured logging setup with structlog
- **`rate_limiter.py`**: Per-user sliding window rate limiter
- **`http_client.py`**: Async HTTP client with retry logic
- **`bot.py`**: Main bot implementation with command handlers
- **`cli.py`**: Command-line interface entry point

### Design Decisions

1. **Async All The Way**: Uses `asyncio` throughout for efficient I/O operations
2. **Type Safety**: Full type hints for better IDE support and error detection
3. **Configuration**: Environment-based configuration following 12-factor app principles
4. **Logging**: Structured logging for better observability and debugging
5. **Rate Limiting**: Per-user limits with sliding window to prevent abuse
6. **Retry Logic**: Exponential backoff for HTTP requests with configurable limits
7. **Testing**: Comprehensive test coverage with mocking for external dependencies

## Security Considerations

- **No Hardcoded Secrets**: All sensitive data loaded from environment variables
- **Rate Limiting**: Prevents abuse and DoS attacks
- **Input Validation**: URL validation before processing
- **Timeout Protection**: HTTP requests have configurable timeouts
- **Error Handling**: Graceful error handling prevents information leakage

## CVE Research & Best Practices

This bot was developed following current security best practices:

1. **Dependency Management**: Using latest stable versions with known vulnerability checks
2. **Environment Variables**: Secrets never committed to version control
3. **Input Validation**: User input sanitized and validated
4. **Rate Limiting**: Protection against abuse
5. **Logging**: Structured logging without exposing sensitive data
6. **HTTP Security**: Using HTTPS, timeout protection, and retry limits
7. **Container Security**: Minimal Docker image with non-root user

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t get-info-bot .

# Run container
docker run -d \
  --name get-info-bot \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e LOG_LEVEL=INFO \
  get-info-bot
```

### Docker Compose

```yaml
version: '3.8'
services:
  bot:
    build: .
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - LOG_LEVEL=INFO
      - LOG_FORMAT=json
    restart: unless-stopped
```

## Troubleshooting

### Bot Not Responding

1. Check bot token is correct
2. Verify bot has permissions in target chat
3. Check logs for errors: `docker logs get-info-bot`

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
