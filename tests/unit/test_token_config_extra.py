"""tests/unit/test_token_config_extra.py
Extra unit tests for app/core/token_config to improve coverage.
"""
from __future__ import annotations

import sys
import types
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from jose import JWTError, jwt

from app.core import token_config as tc
from app.core.token_config import (
    ACCESS_TOKEN_TTL_MINUTES,
    add_persistent_revocation_fallback,
    verify_access_token,
)


@pytest.mark.unit
async def test_verify_access_token_missing_jti_raises():
    """Token without jti should be rejected before any Redis calls."""
    now = datetime.now(tz=timezone.utc)
    claims = {
        "sub": "user-123",
        "role": "guardian",
        # Use numeric timestamps as expected by decoder
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES)).timestamp()),
        # intentionally no jti
    }
    token = jwt.encode(claims, tc.CURRENT_KEY, algorithm=tc.ALGORITHM, headers={"kid": tc.CURRENT_KID})

    with pytest.raises(JWTError, match="Token missing jti claim"):
        await verify_access_token(token)


@pytest.mark.unit
async def test_verify_access_token_with_previous_key_succeeds():
    """A token signed with a previous key validates via kid lookup in _KEY_STORE."""
    prev_kid = "k_prev_for_test"
    prev_secret = "prev-secret-key-for-test"
    # Inject a previous key entry
    tc._KEY_STORE[prev_kid] = prev_secret  # type: ignore[attr-defined]

    now = datetime.now(tz=timezone.utc)
    claims = {
        "sub": "user-123",
        "role": "guardian",
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES)).timestamp()),
    }
    token = jwt.encode(claims, prev_secret, algorithm=tc.ALGORITHM, headers={"kid": prev_kid})

    # No revocation present in Redis
    with patch("app.core.token_config.get_redis") as mock_get_redis:
        mock_redis = AsyncMock()
        mock_redis.exists.return_value = 0
        mock_redis.get.return_value = None
        mock_get_redis.return_value = mock_redis
        decoded = await verify_access_token(token)
        assert decoded["sub"] == "user-123"


@pytest.mark.unit
async def test_add_persistent_revocation_fallback_calls_db_and_redis():
    """Ensure lazy-imported DB fallback is invoked alongside Redis revocation."""
    # Inject a fake module for app.repositories.revocation_repository
    repo_mod = types.ModuleType("app.repositories.revocation_repository")
    fake_persist = AsyncMock()
    setattr(repo_mod, "persist_revocation", fake_persist)
    sys.modules["app.repositories.revocation_repository"] = repo_mod

    # Patch revoke_jti to avoid real Redis
    with patch("app.core.token_config.revoke_jti", new_callable=AsyncMock) as mock_revoke:
        expires_at = datetime.now(tz=timezone.utc) + timedelta(hours=1)
        await add_persistent_revocation_fallback("jti-xyz", expires_at)
        mock_revoke.assert_called_once()
        fake_persist.assert_called_once_with("jti-xyz", expires_at)
