"""Per-user rate limiting implementation."""

import asyncio
import time
from collections import defaultdict
from typing import DefaultDict, Tuple

from .logging_config import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Per-user rate limiter with sliding window."""

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        """Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._user_requests: DefaultDict[int, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check_rate_limit(self, user_id: int) -> Tuple[bool, float]:
        """Check if user has exceeded rate limit.

        Args:
            user_id: Telegram user ID

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        async with self._lock:
            current_time = time.time()
            cutoff_time = current_time - self.window_seconds

            # Remove old requests outside the window
            self._user_requests[user_id] = [
                req_time
                for req_time in self._user_requests[user_id]
                if req_time > cutoff_time
            ]

            request_count = len(self._user_requests[user_id])

            if request_count >= self.max_requests:
                # Calculate retry after based on oldest request in window
                oldest_request = self._user_requests[user_id][0]
                retry_after = oldest_request + self.window_seconds - current_time
                logger.warning(
                    "rate_limit_exceeded",
                    user_id=user_id,
                    request_count=request_count,
                    retry_after=retry_after,
                )
                return False, max(0.0, retry_after)

            # Add current request
            self._user_requests[user_id].append(current_time)
            logger.debug(
                "rate_limit_checked",
                user_id=user_id,
                request_count=request_count + 1,
                max_requests=self.max_requests,
            )
            return True, 0.0

    async def cleanup_old_entries(self) -> None:
        """Clean up old entries to prevent memory growth."""
        async with self._lock:
            current_time = time.time()
            cutoff_time = current_time - self.window_seconds * 2  # Keep extra buffer
            
            users_to_remove = []
            for user_id, requests in self._user_requests.items():
                # Filter old requests
                recent_requests = [req for req in requests if req > cutoff_time]
                if recent_requests:
                    self._user_requests[user_id] = recent_requests
                else:
                    users_to_remove.append(user_id)
            
            # Remove users with no recent requests
            for user_id in users_to_remove:
                del self._user_requests[user_id]
            
            if users_to_remove:
                logger.debug("rate_limiter_cleanup", removed_users=len(users_to_remove))
