"""
EduBoost V2 — Token Revocation Service
Redis-backed JTI (JWT ID) blacklist for logout and forced token invalidation.
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from redis.exceptions import RedisError

from app.core.redis import get_redis

logger = logging.getLogger(__name__)

# Redis key prefix for revoked JTIs
_REVOKED_JTI_PREFIX = "revoked_jti:"


async def revoke_token(jti: str, exp_timestamp: int) -> None:
    """
    Revoke a token by adding its JTI to a Redis blacklist.
    
    Args:
        jti: The JWT ID (jti claim)
        exp_timestamp: Unix timestamp of token expiration (used to set TTL)
    """
    # Calculate remaining TTL: token should stay in blacklist until it naturally expires
    now = datetime.now(UTC).timestamp()
    ttl_seconds = max(int(exp_timestamp - now), 1)
    
    key = f"{_REVOKED_JTI_PREFIX}{jti}"
    try:
        await get_redis().setex(key, ttl_seconds, "1")
    except RedisError:
        logger.warning("Redis unavailable; token revocation skipped", exc_info=True)
        return
    logger.info("token_revoked", extra={"jti": jti, "ttl_seconds": ttl_seconds})


async def is_token_revoked(jti: str) -> bool:
    """Check if a token (by JTI) has been revoked."""
    key = f"{_REVOKED_JTI_PREFIX}{jti}"
    try:
        result = await get_redis().get(key)
    except RedisError:
        logger.warning("Redis unavailable; assuming token is not revoked", exc_info=True)
        return False
    is_revoked = result is not None
    
    if is_revoked:
        logger.info("token_blacklist_hit", extra={"jti": jti})
    
    return is_revoked


async def revoke_user_tokens(user_id: str) -> None:
    """
    Revoke all tokens for a specific user.
    This uses a user-level blacklist that lasts for a longer period.
    """
    # Set user-level revocation to last for a long period (e.g., 30 days)
    key = f"revoked_user:{user_id}"
    ttl_seconds = int(timedelta(days=30).total_seconds())
    try:
        await get_redis().setex(key, ttl_seconds, "1")
    except RedisError:
        logger.warning("Redis unavailable; user token revocation skipped", exc_info=True)
        return
    logger.info("user_tokens_revoked", extra={"user_id": user_id})


async def is_user_revoked(user_id: str) -> bool:
    """Check if all tokens for a user have been revoked."""
    key = f"revoked_user:{user_id}"
    try:
        result = await get_redis().get(key)
    except RedisError:
        logger.warning("Redis unavailable; assuming user tokens are not revoked", exc_info=True)
        return False
    return result is not None
