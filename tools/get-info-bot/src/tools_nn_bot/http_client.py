"""HTTP client with retries and exponential backoff."""

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .config import Settings
from .logging_config import get_logger

logger = get_logger(__name__)


class HTTPClient:
    """Async HTTP client with retry logic and structured logging."""

    def __init__(self, settings: Settings) -> None:
        """Initialize HTTP client.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "HTTPClient":
        """Enter async context manager."""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.settings.http_timeout),
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; GetInfoBot/1.0)",
            },
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def fetch_url_info(self, url: str) -> dict[str, str]:
        """Fetch information about a URL with retries.

        Args:
            url: URL to fetch information about

        Returns:
            Dictionary containing URL information

        Raises:
            httpx.HTTPError: If request fails after retries
        """
        if not self._client:
            raise RuntimeError("HTTP client not initialized. Use 'async with' context.")

        logger.info("fetching_url", url=url)

        try:
            response = await self._client.get(url)
            response.raise_for_status()

            # Extract basic information
            info = {
                "url": str(response.url),
                "status_code": str(response.status_code),
                "content_type": response.headers.get("content-type", "unknown"),
                "content_length": response.headers.get("content-length", "unknown"),
                "server": response.headers.get("server", "unknown"),
                "title": self._extract_title(response.text),
            }

            logger.info("url_fetched", url=url, status_code=response.status_code)
            return info

        except httpx.HTTPStatusError as e:
            logger.error("http_status_error", url=url, status_code=e.response.status_code)
            return {
                "url": url,
                "error": f"HTTP {e.response.status_code}",
                "status_code": str(e.response.status_code),
            }
        except httpx.TimeoutException:
            logger.error("http_timeout", url=url)
            return {"url": url, "error": "Request timeout"}
        except httpx.NetworkError as e:
            logger.error("network_error", url=url, error=str(e))
            return {"url": url, "error": "Network error"}
        except Exception as e:
            logger.error("unexpected_error", url=url, error=str(e))
            return {"url": url, "error": f"Unexpected error: {type(e).__name__}"}

    def _extract_title(self, html: str) -> str:
        """Extract title from HTML content.

        Args:
            html: HTML content

        Returns:
            Extracted title or 'No title found'
        """
        import re

        # Simple regex to extract title
        title_match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
        return "No title found"

    async def search_query(self, query: str) -> dict[str, str]:
        """Process a search query (placeholder for future implementation).

        Args:
            query: Search query string

        Returns:
            Dictionary containing query results
        """
        logger.info("processing_query", query=query)
        # For now, return a simple response
        # In a production system, this would integrate with a search API
        return {
            "query": query,
            "result": f"Query processed: {query}",
            "note": "Full search integration pending",
        }
