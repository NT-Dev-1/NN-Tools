"""Tests for rate limiter module."""

import asyncio

import pytest

from tools_nn_bot.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_allows_within_limit() -> None:
    """Test that requests within limit are allowed."""
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    user_id = 12345

    # First 3 requests should be allowed
    for _ in range(3):
        is_allowed, retry_after = await limiter.check_rate_limit(user_id)
        assert is_allowed is True
        assert retry_after == 0.0


@pytest.mark.asyncio
async def test_rate_limiter_blocks_over_limit() -> None:
    """Test that requests over limit are blocked."""
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    user_id = 12345

    # Use up the limit
    for _ in range(3):
        await limiter.check_rate_limit(user_id)

    # Next request should be blocked
    is_allowed, retry_after = await limiter.check_rate_limit(user_id)
    assert is_allowed is False
    assert retry_after > 0.0


@pytest.mark.asyncio
async def test_rate_limiter_sliding_window() -> None:
    """Test that rate limiter uses sliding window."""
    limiter = RateLimiter(max_requests=2, window_seconds=1)
    user_id = 12345

    # Use up the limit
    await limiter.check_rate_limit(user_id)
    await limiter.check_rate_limit(user_id)

    # Should be blocked
    is_allowed, _ = await limiter.check_rate_limit(user_id)
    assert is_allowed is False

    # Wait for window to pass
    await asyncio.sleep(1.1)

    # Should be allowed again
    is_allowed, _ = await limiter.check_rate_limit(user_id)
    assert is_allowed is True


@pytest.mark.asyncio
async def test_rate_limiter_per_user() -> None:
    """Test that rate limiter tracks per user."""
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    user1 = 11111
    user2 = 22222

    # User 1 uses up limit
    await limiter.check_rate_limit(user1)
    await limiter.check_rate_limit(user1)

    # User 1 should be blocked
    is_allowed, _ = await limiter.check_rate_limit(user1)
    assert is_allowed is False

    # User 2 should still be allowed
    is_allowed, _ = await limiter.check_rate_limit(user2)
    assert is_allowed is True


@pytest.mark.asyncio
async def test_rate_limiter_cleanup() -> None:
    """Test cleanup of old entries."""
    limiter = RateLimiter(max_requests=5, window_seconds=1)
    user_id = 12345

    # Make some requests
    await limiter.check_rate_limit(user_id)
    await limiter.check_rate_limit(user_id)

    # Verify user is tracked
    assert user_id in limiter._user_requests

    # Wait for window to pass plus extra buffer time
    await asyncio.sleep(2.5)

    # Run cleanup - cleanup uses 2x window as cutoff
    await limiter.cleanup_old_entries()

    # User should be removed after cleanup since no recent requests beyond 2x window
    assert user_id not in limiter._user_requests


@pytest.mark.asyncio
async def test_rate_limiter_retry_after_calculation() -> None:
    """Test retry_after calculation."""
    limiter = RateLimiter(max_requests=1, window_seconds=10)
    user_id = 12345

    # Use up limit
    await limiter.check_rate_limit(user_id)

    # Check retry_after
    is_allowed, retry_after = await limiter.check_rate_limit(user_id)
    assert is_allowed is False
    assert 0 < retry_after <= 10
