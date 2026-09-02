"""Branch coverage expansion for AuthService."""
from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.core.token_config import TokenPair
from app.services.auth_service import (
    AuthError,
    AuthService,
    CompatSession,
    LoginResult,
    SignupResult,
    _compat_create_session,
    _compat_decode_token,
    _compat_hash_password,
    _compat_rotate_refresh_token,
    _compat_verify_password,
    get_v2_settings,
)


@pytest.mark.unit
def test_get_v2_settings_and_models():
    settings = get_v2_settings()
    assert settings is not None

    with patch.dict(sys.modules, {"app.core.config": None}):
        with patch("builtins.__import__", side_effect=ImportError("no module")):
            assert get_v2_settings() is None

    # SignupResult and LoginResult
    sr = SignupResult(user_id="u1", email="test@test.com")
    assert sr.user_id == "u1"
    assert sr.email == "test@test.com"

    lr = LoginResult(token_pair=TokenPair(access_token="acc-1"), raw_refresh_token="raw-ref-1")
    assert lr.raw_refresh_token == "raw-ref-1"


@pytest.mark.unit
def test_decode_token_and_session_rotation():
    svc = AuthService()

    # 1. Create session and decode valid token
    session = svc.create_session("u1", "admin")
    decoded = svc.decode_token(session.access_token)
    assert decoded["sub"] == "u1"
    assert decoded["role"] == "admin"

    # 2. Decode invalid token
    with pytest.raises(ValueError, match="Invalid access token"):
        svc.decode_token("invalid-token-xyz")

    # 3. Rotate refresh token successfully
    rotated = svc.rotate_refresh_token(session.refresh_token)
    assert rotated.access_token != session.access_token

    # 4. Rotate invalid refresh token
    with pytest.raises(ValueError, match="Invalid refresh token"):
        svc.rotate_refresh_token("invalid-refresh-xyz")


@pytest.mark.unit
def test_compat_functions_without_attributes():
    # Calling compat functions on an arbitrary object that does not yet have _compat_* dicts
    dummy = SimpleNamespace()

    session = _compat_create_session(dummy, "u2", "guardian")
    assert hasattr(dummy, "_compat_refresh_tokens")
    assert hasattr(dummy, "_compat_access_tokens")
    assert session.access_token.startswith("access.")

    decoded = _compat_decode_token(dummy, session.access_token)
    assert decoded["sub"] == "u2"

    with pytest.raises(ValueError, match="Invalid access token"):
        _compat_decode_token(dummy, "missing")

@pytest.mark.asyncio
async def test_refresh_token_rotation_flow():
    user_repo = AsyncMock()
    token_repo = AsyncMock()
    svc = AuthService(user_repo=user_repo, token_repo=token_repo)

    user = {"user_id": "u1", "role": "student"}
    user_repo.find_by_id = AsyncMock(return_value=user)

    token_record = {
        "user_id": "u1",
        "family_id": "fam-1",
        "expires_at": "2099-01-01T00:00:00+00:00",
    }
    token_repo.find_refresh_token = AsyncMock(return_value=token_record)
    token_repo.delete_refresh_token = AsyncMock()
    token_repo.store_refresh_token = AsyncMock()

    with patch("app.services.auth_service.is_family_revoked", new=AsyncMock(return_value=False)):
        res = await svc.refresh("some-raw-token")
        assert res.token_pair.access_token is not None
        assert res.raw_refresh_token is not None
        token_repo.delete_refresh_token.assert_awaited_once()
        token_repo.store_refresh_token.assert_awaited_once()


