"""
EduBoost V2 — Token Revocation Service
Redis-backed JTI (JWT ID) blacklist for logout and forced token invalidation.
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from app.core.config import settings
from app.core.redis import redis_client

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
    if not redis_client:
        logger.warning("Redis not available; token revocation skipped (dev mode)")
        return
    
    # Calculate remaining TTL: token should stay in blacklist until it naturally expires
    now = datetime.now(UTC).timestamp()
    ttl_seconds = max(int(exp_timestamp - now), 1)
    
    key = f"{_REVOKED_JTI_PREFIX}{jti}"
    await redis_client.setex(key, ttl_seconds, "1")
    logger.info("token_revoked", jti=jti, ttl_seconds=ttl_seconds)


async def is_token_revoked(jti: str) -> bool:
    """Check if a token (by JTI) has been revoked."""
    if not redis_client:
        # In dev mode without Redis, assume no revocations
        return False
    
    key = f"{_REVOKED_JTI_PREFIX}{jti}"
    result = await redis_client.get(key)
    is_revoked = result is not None
    
    if is_revoked:
        logger.info("token_blacklist_hit", jti=jti)
    
    return is_revoked


async def revoke_user_tokens(user_id: str) -> None:
    """
    Revoke all tokens for a specific user.
    This uses a user-level blacklist that lasts for a longer period.
    """
    if not redis_client:
        logger.warning("Redis not available; user token revocation skipped")
        return
    
    # Set user-level revocation to last for a long period (e.g., 30 days)
    key = f"revoked_user:{user_id}"
    ttl_seconds = int(timedelta(days=30).total_seconds())
    await redis_client.setex(key, ttl_seconds, "1")
    logger.info("user_tokens_revoked", user_id=user_id)


async def is_user_revoked(user_id: str) -> bool:
    """Check if all tokens for a user have been revoked."""
    if not redis_client:
        return False
    
    key = f"revoked_user:{user_id}"
    result = await redis_client.get(key)
    return result is not None
