"""tests/unit/test_quota_service.py
Unit tests for QuotaService and SemanticCacheService.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.services.quota_service import (
    _CACHE_KEY,
    _QUOTA_KEY,
    QuotaExceededError,
    QuotaService,
    SemanticCacheService,
)


@pytest.mark.unit
def test_quota_key_formats_with_date():
    """Verify _quota_key formats Redis key with current date."""
    mock_redis = AsyncMock()
    service = QuotaService(mock_redis)

    with patch("app.services.quota_service.datetime") as mock_datetime:
        mock_datetime.now.return_value.strftime.return_value = "2026-05-28"
        key = service._quota_key("guardian-123")
        assert key == "quota:guardian-123:2026-05-28"


@pytest.mark.unit
async def test_check_and_reserve_raises_429_when_quota_exceeded():
    """Verify check_and_reserve raises HTTP 429 when quota exceeded."""
    mock_redis = AsyncMock()
    mock_redis.incrby = AsyncMock(return_value=15000)
    mock_redis.decrby = AsyncMock()

    service = QuotaService(mock_redis)

    with patch("app.services.quota_service.settings") as mock_settings:
        mock_settings.daily_token_quota_free = 10000
        with pytest.raises(Exception):  # HTTPException
            await service.check_and_reserve("guardian-123", 5000, "free")


@pytest.mark.unit
async def test_check_and_reserve_sets_expiry_on_first_increment():
    """Verify check_and_reserve sets expiry on first daily increment."""
    mock_redis = AsyncMock()
    mock_redis.incrby = AsyncMock(return_value=5000)
    mock_redis.expire = AsyncMock()

    service = QuotaService(mock_redis)

    with patch("app.services.quota_service.settings") as mock_settings:
        mock_settings.daily_token_quota_free = 10000
        await service.check_and_reserve("guardian-123", 5000, "free")
        mock_redis.expire.assert_called_once()


@pytest.mark.unit
async def test_get_usage_returns_zero_when_no_data():
    """Verify get_usage returns (0, 0) when no quota data exists."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)

    service = QuotaService(mock_redis)
    tokens, reqs = await service.get_usage("guardian-123")

    assert tokens == 0
    assert reqs == 0


@pytest.mark.unit
async def test_get_usage_returns_values_from_redis():
    """Verify get_usage returns parsed values from Redis."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(side_effect=["5000", "10"])

    service = QuotaService(mock_redis)
    tokens, reqs = await service.get_usage("guardian-123")

    assert tokens == 5000
    assert reqs == 10


@pytest.mark.unit
async def test_increment_requests_increments_counter():
    """Verify increment_requests increments request counter."""
    mock_redis = AsyncMock()
    mock_redis.incr = AsyncMock()
    mock_redis.expire = AsyncMock()

    service = QuotaService(mock_redis)
    await service.increment_requests("guardian-123")

    mock_redis.incr.assert_called_once()
    mock_redis.expire.assert_called_once()


@pytest.mark.unit
def test_build_cache_key_creates_deterministic_hash():
    """Verify build_cache_key creates deterministic cache key."""
    key = SemanticCacheService.build_cache_key(
        subject="Mathematics",
        topic="Numbers",
        grade_level="4",
        language="en",
        archetype="visual",
    )
    assert key.startswith("semcache:")
    assert len(key) == len("semcache:") + 32


@pytest.mark.unit
def test_build_cache_key_normalizes_input():
    """Verify build_cache_key normalizes subject and topic to lowercase."""
    key1 = SemanticCacheService.build_cache_key(
        subject="Mathematics",
        topic="Numbers",
        grade_level="4",
        language="en",
        archetype="visual",
    )
    key2 = SemanticCacheService.build_cache_key(
        subject="MATHEMATICS",
        topic="NUMBERS",
        grade_level="4",
        language="en",
        archetype="visual",
    )
    assert key1 == key2


@pytest.mark.unit
def test_build_cache_key_handles_none_archetype():
    """Verify build_cache_key handles None archetype as default."""
    key1 = SemanticCacheService.build_cache_key(
        subject="Mathematics",
        topic="Numbers",
        grade_level="4",
        language="en",
        archetype=None,
    )
    key2 = SemanticCacheService.build_cache_key(
        subject="Mathematics",
        topic="Numbers",
        grade_level="4",
        language="en",
        archetype="default",
    )
    assert key1 == key2


@pytest.mark.unit
async def test_semantic_cache_get_returns_none_when_disabled():
    """Verify get returns None when semantic cache disabled."""
    mock_redis = AsyncMock()
    service = SemanticCacheService(mock_redis)

    with patch("app.services.quota_service.settings") as mock_settings:
        mock_settings.semantic_cache_enabled = False
        result = await service.get("cache-key-123")
        assert result is None


@pytest.mark.unit
async def test_semantic_cache_get_returns_cached_value():
    """Verify get returns cached value when available."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=b'{"lesson": "data"}')
    service = SemanticCacheService(mock_redis)

    with patch("app.services.quota_service.settings") as mock_settings, \
         patch("app.services.quota_service.logger") as mock_logger:
        mock_settings.semantic_cache_enabled = True
        result = await service.get("cache-key-123")
        assert result == '{"lesson": "data"}'
        mock_logger.debug.assert_called_once()


@pytest.mark.unit
async def test_semantic_cache_set_skips_when_disabled():
    """Verify set skips storage when semantic cache disabled."""
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock()
    service = SemanticCacheService(mock_redis)

    with patch("app.services.quota_service.settings") as mock_settings:
        mock_settings.semantic_cache_enabled = False
        await service.set("cache-key-123", '{"lesson": "data"}')
        mock_redis.setex.assert_not_called()


@pytest.mark.unit
async def test_semantic_cache_set_stores_with_ttl():
    """Verify set stores value with TTL when enabled."""
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock()
    service = SemanticCacheService(mock_redis)

    with patch("app.services.quota_service.settings") as mock_settings, \
         patch("app.services.quota_service.logger") as mock_logger:
        mock_settings.semantic_cache_enabled = True
        mock_settings.redis_cache_ttl_seconds = 3600
        await service.set("cache-key-123", '{"lesson": "data"}')
        mock_redis.setex.assert_called_once_with("cache-key-123", 3600, '{"lesson": "data"}')
        mock_logger.debug.assert_called_once()


@pytest.mark.unit
async def test_check_and_reserve_uses_premium_limit():
    """Verify check_and_reserve uses premium limit for premium tier."""
    mock_redis = AsyncMock()
    mock_redis.incrby = AsyncMock(return_value=5000)
    mock_redis.expire = AsyncMock()

    service = QuotaService(mock_redis)

    with patch("app.services.quota_service.settings") as mock_settings:
        mock_settings.daily_token_quota_premium = 50000
        mock_settings.daily_token_quota_free = 10000
        await service.check_and_reserve("guardian-123", 5000, "premium")
        # Should not raise with premium limit
        mock_redis.expire.assert_called_once()


@pytest.mark.unit
async def test_check_and_reserve_rolls_back_on_exceed():
    """Verify check_and_reserve rolls back increment when quota exceeded."""
    mock_redis = AsyncMock()
    mock_redis.incrby = AsyncMock(return_value=15000)
    mock_redis.decrby = AsyncMock()

    service = QuotaService(mock_redis)

    with patch("app.services.quota_service.settings") as mock_settings, \
         patch("app.services.quota_service.logger") as mock_logger:
        mock_settings.daily_token_quota_free = 10000
        with pytest.raises(Exception):  # HTTPException
            await service.check_and_reserve("guardian-123", 5000, "free")
        mock_redis.decrby.assert_called_once()
        mock_logger.warning.assert_called_once()


@pytest.mark.unit
async def test_check_and_reserve_allows_exact_limit():
    """Verify check_and_reserve allows usage up to exact limit."""
    mock_redis = AsyncMock()
    mock_redis.incrby = AsyncMock(return_value=10000)
    mock_redis.expire = AsyncMock()

    service = QuotaService(mock_redis)

    with patch("app.services.quota_service.settings") as mock_settings:
        mock_settings.daily_token_quota_free = 10000
        await service.check_and_reserve("guardian-123", 10000, "free")
        # Should not raise at exact limit


@pytest.mark.unit
async def test_semantic_cache_get_returns_none_on_miss():
    """Verify get returns None when cache miss."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)
    service = SemanticCacheService(mock_redis)

    with patch("app.services.quota_service.settings") as mock_settings:
        mock_settings.semantic_cache_enabled = True
        result = await service.get("cache-key-123")
        assert result is None


@pytest.mark.unit
async def test_semantic_cache_get_handles_string_response():
    """Verify get handles string response (not bytes)."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value='{"lesson": "data"}')
    service = SemanticCacheService(mock_redis)

    with patch("app.services.quota_service.settings") as mock_settings:
        mock_settings.semantic_cache_enabled = True
        result = await service.get("cache-key-123")
        assert result == '{"lesson": "data"}'


@pytest.mark.unit
async def test_semantic_cache_set_with_custom_ttl():
    """Verify set uses configured TTL from settings."""
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock()
    service = SemanticCacheService(mock_redis)

    with patch("app.services.quota_service.settings") as mock_settings:
        mock_settings.semantic_cache_enabled = True
        mock_settings.redis_cache_ttl_seconds = 7200
        await service.set("cache-key-123", '{"lesson": "data"}')
        mock_redis.setex.assert_called_once_with("cache-key-123", 7200, '{"lesson": "data"}')


@pytest.mark.unit
async def test_get_usage_with_only_tokens():
    """Verify get_usage handles case with tokens but no request count."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(side_effect=["5000", None])

    service = QuotaService(mock_redis)
    tokens, reqs = await service.get_usage("guardian-123")

    assert tokens == 5000
    assert reqs == 0


@pytest.mark.unit
async def test_get_usage_with_only_requests():
    """Verify get_usage handles case with requests but no token count."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(side_effect=[None, "10"])

    service = QuotaService(mock_redis)
    tokens, reqs = await service.get_usage("guardian-123")

    assert tokens == 0
    assert reqs == 10


@pytest.mark.unit
def test_quota_key_constant_defined():
    """Verify _QUOTA_KEY constant is defined correctly."""
    assert _QUOTA_KEY == "quota:{guardian_id}:{date}"


@pytest.mark.unit
def test_cache_key_constant_defined():
    """Verify _CACHE_KEY constant is defined correctly."""
    assert _CACHE_KEY == "semcache:{hash}"


@pytest.mark.unit
def test_quota_exceeded_error_defined():
    """Verify QuotaExceededError is defined as RuntimeError subclass."""
    assert issubclass(QuotaExceededError, RuntimeError)


@pytest.mark.unit
def test_quota_service_init_stores_redis_client():
    """Verify QuotaService constructor stores Redis client."""
    mock_redis = AsyncMock()
    service = QuotaService(mock_redis)
    assert service._redis is mock_redis


@pytest.mark.unit
def test_semantic_cache_service_init_stores_redis_client():
    """Verify SemanticCacheService constructor stores Redis client."""
    mock_redis = AsyncMock()
    service = SemanticCacheService(mock_redis)
    assert service._redis is mock_redis


@pytest.mark.unit
async def test_check_and_reserve_does_not_set_expiry_on_subsequent_increment():
    """Verify check_and_reserve does not set expiry on subsequent increments."""
    mock_redis = AsyncMock()
    mock_redis.incrby = AsyncMock(return_value=10000)  # Not first increment
    mock_redis.expire = AsyncMock()

    service = QuotaService(mock_redis)

    with patch("app.services.quota_service.settings") as mock_settings:
        mock_settings.daily_token_quota_free = 15000
        await service.check_and_reserve("guardian-123", 5000, "free")
        mock_redis.expire.assert_not_called()


@pytest.mark.unit
async def test_increment_requests_sets_expiry():
    """Verify increment_requests sets expiry on request counter."""
    mock_redis = AsyncMock()
    mock_redis.incr = AsyncMock()
    mock_redis.expire = AsyncMock()

    service = QuotaService(mock_redis)
    await service.increment_requests("guardian-123")

    mock_redis.expire.assert_called_once()


@pytest.mark.unit
async def test_check_and_reserve_raises_with_correct_error_details():
    """Verify check_and_reserve raises HTTPException with correct details."""
    mock_redis = AsyncMock()
    mock_redis.incrby = AsyncMock(return_value=15000)
    mock_redis.decrby = AsyncMock()

    service = QuotaService(mock_redis)

    with patch("app.services.quota_service.settings") as mock_settings:
        mock_settings.daily_token_quota_free = 10000
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await service.check_and_reserve("guardian-123", 5000, "free")
        assert exc.value.status_code == 429
        assert "daily_quota_exhausted" in exc.value.detail["error"]
        assert exc.value.detail["tokens_used"] == 10000
        assert exc.value.detail["quota"] == 10000
