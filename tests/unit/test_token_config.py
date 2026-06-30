"""tests/unit/test_token_config.py
Unit tests for JWT token configuration and revocation.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from jose import JWTError

from app.core.token_config import (
    ACCESS_TOKEN_TTL_MINUTES,
    REFRESH_TOKEN_TTL_DAYS,
    RefreshTokenRecord,
    _hash_token,
    _secret_for_kid,
    create_access_token,
    create_refresh_token,
    emergency_revoke_all,
    is_family_revoked,
    revoke_jti,
    revoke_token_family,
    verify_access_token,
)


@pytest.mark.unit
def test_access_token_ttl_default():
    """Verify ACCESS_TOKEN_TTL_MINUTES defaults to 15."""
    assert ACCESS_TOKEN_TTL_MINUTES == 15


@pytest.mark.unit
def test_refresh_token_ttl_days_default():
    """Verify REFRESH_TOKEN_TTL_DAYS defaults to 7."""
    assert REFRESH_TOKEN_TTL_DAYS == 7


@pytest.mark.unit
def test_secret_for_kid_returns_current_key():
    """Verify _secret_for_kid returns current key for current kid."""
    secret = _secret_for_kid("k1")
    assert secret is not None
    assert isinstance(secret, str)


@pytest.mark.unit
def test_secret_for_kid_raises_on_unknown_kid():
    """Verify _secret_for_kid raises JWTError for unknown kid."""
    with pytest.raises(JWTError, match="Unknown signing key id"):
        _secret_for_kid("unknown_kid")


@pytest.mark.unit
def test_create_access_token_with_claims():
    """Verify create_access_token creates valid JWT with claims."""
    token = create_access_token("user-123", "guardian", extra_claims={"custom": "value"})
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.unit
def test_create_access_token_without_extra_claims():
    """Verify create_access_token works without extra claims."""
    token = create_access_token("user-123", "guardian")
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.unit
def test_create_refresh_token_generates_unique_tokens():
    """Verify create_refresh_token generates unique tokens."""
    raw1, hashed1, record1 = create_refresh_token()
    raw2, hashed2, record2 = create_refresh_token()

    assert raw1 != raw2
    assert hashed1 != hashed2
    assert record1.family_id != record2.family_id


@pytest.mark.unit
def test_create_refresh_token_with_family_id():
    """Verify create_refresh_token respects provided family_id."""
    family_id = "family-123"
    raw, hashed, record = create_refresh_token(family_id=family_id)

    assert record.family_id == family_id


@pytest.mark.unit
def test_create_refresh_token_record_fields():
    """Verify RefreshTokenRecord has correct fields."""
    raw, hashed, record = create_refresh_token()

    assert isinstance(record, RefreshTokenRecord)
    assert record.user_id == ""  # caller fills in
    assert isinstance(record.issued_at, datetime)
    assert isinstance(record.expires_at, datetime)
    assert record.expires_at > record.issued_at


@pytest.mark.unit
def test_hash_token_is_deterministic():
    """Verify _hash_token produces consistent hash for same input."""
    raw = "test-token-123"
    hash1 = _hash_token(raw)
    hash2 = _hash_token(raw)

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex length


@pytest.mark.unit
def test_hash_token_is_unique():
    """Verify _hash_token produces different hashes for different inputs."""
    hash1 = _hash_token("token-1")
    hash2 = _hash_token("token-2")

    assert hash1 != hash2


@pytest.mark.unit
async def test_verify_access_token_valid():
    """Verify verify_access_token decodes valid token."""
    token = create_access_token("user-123", "guardian")

    with patch("app.core.token_config.get_redis") as mock_get_redis:
        mock_redis = AsyncMock()
        mock_redis.exists.return_value = 0
        mock_redis.get.return_value = None
        mock_get_redis.return_value = mock_redis

        claims = await verify_access_token(token)

        assert claims["sub"] == "user-123"
        assert claims["role"] == "guardian"
        assert "jti" in claims


@pytest.mark.unit
async def test_verify_access_token_revoked():
    """Verify verify_access_token raises for revoked token."""
    token = create_access_token("user-123", "guardian")

    with patch("app.core.token_config.get_redis") as mock_get_redis:
        mock_redis = AsyncMock()
        mock_redis.exists.return_value = 1  # Token is revoked
        mock_get_redis.return_value = mock_redis

        with pytest.raises(JWTError, match="Token has been revoked"):
            await verify_access_token(token)


@pytest.mark.unit
async def test_verify_access_token_redis_unavailable():
    """Verify verify_access_token raises when Redis unavailable."""
    token = create_access_token("user-123", "guardian")

    with patch("app.core.token_config.get_redis") as mock_get_redis:
        import redis.asyncio as aioredis
        mock_get_redis.side_effect = aioredis.RedisError("Connection failed")

        with pytest.raises(JWTError, match="Revocation store unavailable"):
            await verify_access_token(token)


@pytest.mark.unit
async def test_verify_access_token_global_revoke_epoch():
    """Verify verify_access_token checks global revoke epoch."""
    token = create_access_token("user-123", "guardian")

    with patch("app.core.token_config.get_redis") as mock_get_redis:
        mock_redis = AsyncMock()
        mock_redis.exists.return_value = 0
        # Set epoch to future - token should be rejected
        future_epoch = (datetime.now(tz=timezone.utc) + timedelta(hours=1)).isoformat()
        mock_redis.get.return_value = future_epoch
        mock_get_redis.return_value = mock_redis

        with pytest.raises(JWTError, match="Token predates global revocation epoch"):
            await verify_access_token(token)


@pytest.mark.unit
async def test_revoke_jti_adds_to_redis():
    """Verify revoke_jti adds jti to Redis with TTL."""
    with patch("app.core.token_config.get_redis") as mock_get_redis:
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        await revoke_jti("jti-123", ttl_seconds=3600)

        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert "revoked_jti:jti-123" in call_args[0][0]
        assert call_args[0][1] == 3600


@pytest.mark.unit
async def test_revoke_token_family_adds_to_redis():
    """Verify revoke_token_family adds family to Redis."""
    with patch("app.core.token_config.get_redis") as mock_get_redis:
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        await revoke_token_family("family-123")

        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        assert "token_family:family-123:revoked" in call_args[0][0]


@pytest.mark.unit
async def test_is_family_revoked_true():
    """Verify is_family_revoked returns True when family revoked."""
    with patch("app.core.token_config.get_redis") as mock_get_redis:
        mock_redis = AsyncMock()
        mock_redis.exists.return_value = 1
        mock_get_redis.return_value = mock_redis

        result = await is_family_revoked("family-123")

        assert result is True


@pytest.mark.unit
async def test_is_family_revoked_false():
    """Verify is_family_revoked returns False when family not revoked."""
    with patch("app.core.token_config.get_redis") as mock_get_redis:
        mock_redis = AsyncMock()
        mock_redis.exists.return_value = 0
        mock_get_redis.return_value = mock_redis

        result = await is_family_revoked("family-123")

        assert result is False


@pytest.mark.unit
async def test_emergency_revoke_all_sets_epoch():
    """Verify emergency_revoke_all sets global epoch in Redis."""
    with patch("app.core.token_config.get_redis") as mock_get_redis:
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        epoch = await emergency_revoke_all()

        assert isinstance(epoch, datetime)
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        assert call_args[0][0] == "revoke_all_epoch"


