"""Tests for HTTP client module."""

import httpx
import pytest
import respx

from tools_nn_bot.config import Settings
from tools_nn_bot.http_client import HTTPClient


@pytest.fixture
def settings() -> Settings:
    """Create test settings."""
    return Settings(
        telegram_bot_token="test_token",
        http_timeout=10,
        http_max_retries=3,
    )


@pytest.mark.asyncio
async def test_http_client_fetch_url_success(settings: Settings) -> None:
    """Test successful URL fetch."""
    url = "https://example.com"
    html_content = "<html><head><title>Example Domain</title></head></html>"

    with respx.mock:
        respx.get(url).mock(
            return_value=httpx.Response(
                200,
                text=html_content,
                headers={
                    "content-type": "text/html",
                    "content-length": "1234",
                    "server": "nginx",
                },
            )
        )

        async with HTTPClient(settings) as client:
            info = await client.fetch_url_info(url)

        assert info["status_code"] == "200"
        assert info["content_type"] == "text/html"
        assert info["title"] == "Example Domain"
        assert info["server"] == "nginx"


@pytest.mark.asyncio
async def test_http_client_fetch_url_404(settings: Settings) -> None:
    """Test URL fetch with 404 error."""
    url = "https://example.com/notfound"

    with respx.mock:
        respx.get(url).mock(return_value=httpx.Response(404))

        async with HTTPClient(settings) as client:
            info = await client.fetch_url_info(url)

        assert "error" in info
        assert info["status_code"] == "404"


@pytest.mark.asyncio
async def test_http_client_fetch_url_timeout(settings: Settings) -> None:
    """Test URL fetch with timeout."""
    url = "https://example.com"

    with respx.mock:
        respx.get(url).mock(side_effect=httpx.TimeoutException("Timeout"))

        async with HTTPClient(settings) as client:
            info = await client.fetch_url_info(url)

        assert "error" in info
        assert "timeout" in info["error"].lower()


@pytest.mark.asyncio
async def test_http_client_fetch_url_network_error(settings: Settings) -> None:
    """Test URL fetch with network error."""
    url = "https://example.com"

    with respx.mock:
        respx.get(url).mock(side_effect=httpx.NetworkError("Network error"))

        async with HTTPClient(settings) as client:
            info = await client.fetch_url_info(url)

        assert "error" in info
        assert "network" in info["error"].lower()


@pytest.mark.asyncio
async def test_http_client_extract_title(settings: Settings) -> None:
    """Test title extraction from HTML."""
    async with HTTPClient(settings) as client:
        # Test with title
        html = "<html><head><title>Test Title</title></head></html>"
        title = client._extract_title(html)
        assert title == "Test Title"

        # Test without title
        html = "<html><head></head></html>"
        title = client._extract_title(html)
        assert title == "No title found"

        # Test with title tag in different case
        html = "<HTML><HEAD><TITLE>UPPERCASE TITLE</TITLE></HEAD></HTML>"
        title = client._extract_title(html)
        assert title == "UPPERCASE TITLE"


@pytest.mark.asyncio
async def test_http_client_search_query(settings: Settings) -> None:
    """Test search query processing."""
    async with HTTPClient(settings) as client:
        info = await client.search_query("test query")

        assert info["query"] == "test query"
        assert "result" in info


@pytest.mark.asyncio
async def test_http_client_context_manager(settings: Settings) -> None:
    """Test HTTP client context manager."""
    client = HTTPClient(settings)

    # Client should not be initialized yet
    assert client._client is None

    async with client:
        # Client should be initialized
        assert client._client is not None

    # Client should be closed after exiting context
    # We can't directly check if closed, but we can verify no errors occur
