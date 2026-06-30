"""tests/unit/test_token_revocation.py
Unit tests for token revocation service.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from redis.exceptions import RedisError

from app.core.token_revocation import (
    _redis_set_with_ttl,
    is_token_revoked,
    is_user_revoked,
    revoke_token,
    revoke_user_tokens,
)


@pytest.mark.unit
async def test_redis_set_with_ttl_setex():
    """Verify _redis_set_with_ttl uses setex when available."""
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock()

    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        await _redis_set_with_ttl("key-123", 3600, "value")

        mock_redis.setex.assert_called_once_with("key-123", 3600, "value")


@pytest.mark.unit
async def test_redis_set_with_ttl_set_ex():
    """Verify _redis_set_with_ttl uses set with ex parameter."""
    mock_redis = MagicMock()
    mock_redis.set = MagicMock(return_value=AsyncMock())
    del mock_redis.setex  # Remove setex to test fallback

    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        await _redis_set_with_ttl("key-123", 3600, "value")

        mock_redis.set.assert_called_once()


@pytest.mark.unit
async def test_redis_set_with_ttl_set_no_ex():
    """Verify _redis_set_with_ttl uses set without ex when TypeError."""
    mock_redis = MagicMock()
    # First call with ex raises TypeError, second call without ex succeeds
    mock_redis.set = MagicMock(side_effect=[TypeError, AsyncMock()])
    del mock_redis.setex  # Remove setex to test fallback

    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        await _redis_set_with_ttl("key-123", 3600, "value")

        # Should call set twice (once with ex, once without)
        assert mock_redis.set.call_count == 2


@pytest.mark.unit
async def test_redis_set_with_ttl_data_attr():
    """Verify _redis_set_with_ttl uses _data attribute for test fakes."""
    mock_redis = MagicMock()
    mock_redis._data = {}
    del mock_redis.setex
    del mock_redis.set

    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        await _redis_set_with_ttl("key-123", 3600, "value")

        assert mock_redis._data["key-123"] == "value"


@pytest.mark.unit
async def test_redis_set_with_ttl_store_attr():
    """Verify _redis_set_with_ttl uses store attribute for test fakes."""
    mock_redis = MagicMock()
    mock_redis.store = {}
    del mock_redis.setex
    del mock_redis.set
    del mock_redis._data

    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        await _redis_set_with_ttl("key-123", 3600, "value")

        assert mock_redis.store["key-123"] == "value"


@pytest.mark.unit
async def test_redis_set_with_ttl_setattr_fallback():
    """Verify _redis_set_with_ttl uses setattr as final fallback."""
    mock_redis = MagicMock()
    del mock_redis.setex
    del mock_redis.set
    del mock_redis._data
    del mock_redis.store

    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        await _redis_set_with_ttl("key-123", 3600, "value")

        assert getattr(mock_redis, "key-123") == "value"


@pytest.mark.unit
async def test_revoke_token_calculates_ttl():
    """Verify revoke_token calculates TTL from exp_timestamp."""
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock()

    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        # Set exp to 1 hour from now
        exp_timestamp = int((datetime.now(UTC) + timedelta(hours=1)).timestamp())
        await revoke_token("jti-123", exp_timestamp)

        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert "revoked_jti:jti-123" in call_args[0][0]
        # TTL should be approximately 3600 seconds
        assert 3500 < call_args[0][1] < 3700


@pytest.mark.unit
async def test_revoke_token_min_ttl():
    """Verify revoke_token uses minimum TTL of 1 second."""
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock()

    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        # Set exp to past (should result in min TTL of 1)
        exp_timestamp = int((datetime.now(UTC) - timedelta(hours=1)).timestamp())
        await revoke_token("jti-123", exp_timestamp)

        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][1] == 1


@pytest.mark.unit
async def test_revoke_token_redis_error():
    """Verify revoke_token handles RedisError gracefully."""
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock(side_effect=RedisError("Connection failed"))

    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        # Should not raise exception
        await revoke_token("jti-123", 9999999999)


@pytest.mark.unit
async def test_is_token_revoked_true():
    """Verify is_token_revoked returns True when token is revoked."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value="1")

    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        result = await is_token_revoked("jti-123")

        assert result is True
        mock_redis.get.assert_called_once_with("revoked_jti:jti-123")


@pytest.mark.unit
async def test_is_token_revoked_false():
    """Verify is_token_revoked returns False when token not revoked."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)

    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        result = await is_token_revoked("jti-123")

        assert result is False


@pytest.mark.unit
async def test_is_token_revoked_redis_error():
    """Verify is_token_revoked returns False on RedisError."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(side_effect=RedisError("Connection failed"))

    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        result = await is_token_revoked("jti-123")

        assert result is False


@pytest.mark.unit
async def test_revoke_user_tokens():
    """Verify revoke_user_tokens sets user-level revocation."""
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock()

    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        await revoke_user_tokens("user-123")

        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert "revoked_user:user-123" in call_args[0][0]
        # TTL should be 30 days
        assert 2591900 < call_args[0][1] < 2592100  # 30 days in seconds


@pytest.mark.unit
async def test_revoke_user_tokens_redis_error():
    """Verify revoke_user_tokens handles RedisError gracefully."""
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock(side_effect=RedisError("Connection failed"))

    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        # Should not raise exception
        await revoke_user_tokens("user-123")


@pytest.mark.unit
async def test_is_user_revoked_true():
    """Verify is_user_revoked returns True when user revoked."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value="1")

    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        result = await is_user_revoked("user-123")

        assert result is True
        mock_redis.get.assert_called_once_with("revoked_user:user-123")


@pytest.mark.unit
async def test_is_user_revoked_false():
    """Verify is_user_revoked returns False when user not revoked."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)

    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        result = await is_user_revoked("user-123")

        assert result is False


@pytest.mark.unit
async def test_is_user_revoked_redis_error():
    """Verify is_user_revoked returns False on RedisError."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(side_effect=RedisError("Connection failed"))

    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        result = await is_user_revoked("user-123")

        assert result is False
