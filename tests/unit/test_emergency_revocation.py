"""
A.3 — Emergency revoke-all tests.

Tests that emergency_revoke_all:
  - invalidates all tokens created before the epoch
  - does not invalidate tokens created after the epoch
  - is idempotent (calling twice overwrites with the latest epoch)
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from jose import JWTError

from app.services.auth_service import AuthService


# ── A.3.1 — emergency_revoke_all invalidates pre-epoch tokens ─────────────────

@pytest.mark.asyncio
async def test_emergency_revoke_all_sets_epoch():
    """emergency_revoke_all must set the global revocation epoch in Redis."""
    svc = AuthService(user_repo=AsyncMock(), token_repo=AsyncMock(), email_service=AsyncMock())

    mock_epoch = datetime(2026, 6, 12, 10, 0, 0, tzinfo=timezone.utc)
    with patch("app.services.auth_service.emergency_revoke_all", new=AsyncMock(return_value=mock_epoch)) as mock_fn:
        result = await svc.emergency_revoke_all_tokens(initiated_by="admin-1")

    mock_fn.assert_awaited_once()
    assert result == mock_epoch


@pytest.mark.asyncio
async def test_verify_access_token_rejects_token_before_epoch():
    """Tokens with iat before the revoke-all epoch are rejected."""
    from app.core.token_config import create_access_token, verify_access_token

    # Simulate epoch set to 5 minutes from now
    epoch = datetime.now(tz=timezone.utc) + timedelta(minutes=5)

    token = create_access_token(user_id="user-epoch-test", role="guardian")

    # Mock Redis: epoch is in the future → all current tokens predate it
    mock_redis = AsyncMock()
    mock_redis.exists = AsyncMock(return_value=0)             # not individually revoked
    mock_redis.get    = AsyncMock(return_value=epoch.isoformat())  # epoch set

    with patch("app.core.token_config.get_redis", new=AsyncMock(return_value=mock_redis)):
        with pytest.raises(JWTError, match="predates global revocation epoch"):
            await verify_access_token(token)


@pytest.mark.asyncio
async def test_verify_access_token_accepts_token_after_epoch():
    """Tokens issued after the revoke-all epoch are accepted."""
    from app.core.token_config import create_access_token, verify_access_token

    # Epoch is 10 minutes in the past → newly issued tokens postdate it
    past_epoch = datetime.now(tz=timezone.utc) - timedelta(minutes=10)
    token = create_access_token(user_id="user-after-epoch", role="guardian")

    mock_redis = AsyncMock()
    mock_redis.exists = AsyncMock(return_value=0)
    mock_redis.get    = AsyncMock(return_value=past_epoch.isoformat())

    with patch("app.core.token_config.get_redis", new=AsyncMock(return_value=mock_redis)):
        claims = await verify_access_token(token)

    assert claims["sub"] == "user-after-epoch"


# ── A.3.2 — Tokens created after revoke-all are not pre-emptively invalidated ─

@pytest.mark.asyncio
async def test_new_tokens_valid_after_emergency_revoke():
    """Tokens issued after an emergency revoke-all should be valid."""
    from app.core.token_config import create_access_token, verify_access_token

    # A very old epoch — all new tokens postdate it
    ancient_epoch = datetime(2020, 1, 1, tzinfo=timezone.utc)
    token = create_access_token(user_id="fresh-user", role="learner")

    mock_redis = AsyncMock()
    mock_redis.exists = AsyncMock(return_value=0)
    mock_redis.get    = AsyncMock(return_value=ancient_epoch.isoformat())

    with patch("app.core.token_config.get_redis", new=AsyncMock(return_value=mock_redis)):
        claims = await verify_access_token(token)

    assert claims["sub"] == "fresh-user"


# ── A.3.3 — emergency_revoke_all is idempotent ────────────────────────────────

@pytest.mark.asyncio
async def test_emergency_revoke_all_idempotent():
    """Calling emergency_revoke_all twice overwrites with the latest epoch."""
    from app.core.token_config import emergency_revoke_all

    stored: dict[str, str] = {}

    async def mock_set(key, value, **kwargs):
        stored[key] = value

    async def mock_get(key):
        return stored.get(key)

    mock_redis = AsyncMock()
    mock_redis.set = mock_set
    mock_redis.get = mock_get

    with patch("app.core.token_config.get_redis", new=AsyncMock(return_value=mock_redis)):
        epoch1 = await emergency_revoke_all()
        epoch2 = await emergency_revoke_all()

    assert epoch2 >= epoch1
    assert stored.get("revoke_all_epoch") == epoch2.isoformat()
