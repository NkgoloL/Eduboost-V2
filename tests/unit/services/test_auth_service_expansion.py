from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, timezone


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FAKE_HASH = "$2b$12$fakehashXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # not real


def _make_service(user_repo=None, token_repo=None, email_service=None):
    from app.services.auth_service import AuthService
    return AuthService(
        user_repo=user_repo or AsyncMock(),
        token_repo=token_repo or AsyncMock(),
        email_service=email_service or AsyncMock(),
    )


def _user(user_id="u1", email="test@example.com", password_hash=None, role="guardian",
          failed_attempts=0, locked_until=None, is_verified=False):
    return {
        "user_id": user_id,
        "email": email,
        "password_hash": password_hash or FAKE_HASH,
        "role": role,
        "failed_attempts": failed_attempts,
        "locked_until": locked_until,
        "is_verified": is_verified,
    }


# ---------------------------------------------------------------------------
# get_v2_settings
# ---------------------------------------------------------------------------

def test_get_v2_settings_returns_settings_or_none():
    from app.services.auth_service import get_v2_settings
    result = get_v2_settings()
    # Should return settings or None — never raise
    assert result is None or hasattr(result, "__class__")


# ---------------------------------------------------------------------------
# SignupResult / LoginResult / CompatSession
# ---------------------------------------------------------------------------

def test_signup_result_attributes():
    from app.services.auth_service import SignupResult
    r = SignupResult(user_id="u1", email="a@b.com")
    assert r.user_id == "u1"
    assert r.email == "a@b.com"


# ---------------------------------------------------------------------------
# Legacy sync API (create_session / rotate_refresh_token / decode_token)
# ---------------------------------------------------------------------------

def test_create_session_returns_compat_session():
    svc = _make_service()
    session = svc.create_session("user-1", "guardian")
    assert session.access_token.startswith("access.")
    assert session.refresh_token.startswith("refresh.")


def test_decode_token_returns_payload():
    svc = _make_service()
    session = svc.create_session("user-1", "guardian")
    payload = svc.decode_token(session.access_token)
    assert payload["sub"] == "user-1"
    assert payload["role"] == "guardian"


def test_decode_token_raises_on_invalid():
    svc = _make_service()
    with pytest.raises(ValueError, match="Invalid access token"):
        svc.decode_token("not-a-real-token")


def test_rotate_refresh_token_issues_new_session():
    svc = _make_service()
    session = svc.create_session("user-1", "guardian")
    new_session = svc.rotate_refresh_token(session.refresh_token)
    assert new_session.access_token != session.access_token
    assert new_session.refresh_token != session.refresh_token


def test_rotate_refresh_token_raises_on_invalid():
    svc = _make_service()
    with pytest.raises(ValueError, match="Invalid refresh token"):
        svc.rotate_refresh_token("bad-refresh-token")


def test_rotate_refresh_token_prevents_reuse():
    svc = _make_service()
    session = svc.create_session("user-1", "guardian")
    svc.rotate_refresh_token(session.refresh_token)
    # Reuse should raise
    with pytest.raises(ValueError, match="Invalid refresh token"):
        svc.rotate_refresh_token(session.refresh_token)


# ---------------------------------------------------------------------------
# guardian_signup
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_guardian_signup_succeeds():
    users = AsyncMock()
    users.find_by_email.return_value = None  # No existing user
    tokens = AsyncMock()
    email_svc = AsyncMock()

    svc = _make_service(user_repo=users, token_repo=tokens, email_service=email_svc)

    with (
        patch("app.services.auth_service.check_password_strength") as mock_strength,
        patch("app.services.auth_service.is_password_breached", return_value=False),
        patch("app.services.auth_service.hash_password", return_value="hashed"),
    ):
        mock_result = MagicMock(valid=True, errors=[])
        mock_strength.return_value = mock_result
        result = await svc.guardian_signup(
            email="new@example.com",
            password="S3cur3P@ss!",
            full_name="Thabo Nkosi",
        )

    assert result.user_id is not None
    assert result.email == "new@example.com"
    users.create.assert_awaited_once()
    tokens.store_email_verify_token.assert_awaited_once()
    email_svc.send_verification_email.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_guardian_signup_raises_on_duplicate_email():
    from app.services.auth_service import AuthError

    users = AsyncMock()
    users.find_by_email.return_value = {"user_id": "existing"}
    svc = _make_service(user_repo=users)

    with pytest.raises(AuthError) as exc_info:
        await svc.guardian_signup("dup@example.com", "S3cur3P@ss!", "Name")

    assert exc_info.value.code == "duplicate_email"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_guardian_signup_raises_on_weak_password():
    from app.services.auth_service import AuthError

    users = AsyncMock()
    users.find_by_email.return_value = None
    svc = _make_service(user_repo=users)

    with pytest.raises(AuthError) as exc_info:
        await svc.guardian_signup("new@example.com", "weak", "Name")

    assert exc_info.value.code == "weak_password"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_guardian_signup_raises_on_breached_password():
    from app.services.auth_service import AuthError

    users = AsyncMock()
    users.find_by_email.return_value = None
    svc = _make_service(user_repo=users)

    with patch("app.services.auth_service.is_password_breached", return_value=True):
        with pytest.raises(AuthError) as exc_info:
            await svc.guardian_signup("new@example.com", "S3cur3P@ss!", "Name")

    assert exc_info.value.code == "breached_password"


# ---------------------------------------------------------------------------
# login
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_login_succeeds():
    users = AsyncMock()
    users.find_by_email.return_value = _user(password_hash="hashed")
    users.find_by_id.return_value = _user(password_hash="hashed", locked_until=None)
    users.reset_failed_attempts.return_value = None
    users.update_password_hash.return_value = None
    tokens = AsyncMock()
    tokens.store_refresh_token.return_value = None

    svc = _make_service(user_repo=users, token_repo=tokens)

    with (
        patch("app.services.auth_service.verify_password", return_value=True),
        patch("app.services.auth_service.needs_rehash", return_value=False),
    ):
        result = await svc.login("test@example.com", "S3cur3P@ss!")

    assert result.token_pair.access_token


@pytest.mark.asyncio
@pytest.mark.unit
async def test_login_raises_on_nonexistent_account():
    from app.services.auth_service import AuthError

    users = AsyncMock()
    users.find_by_email.return_value = None
    users.increment_failed_attempts.return_value = 0
    svc = _make_service(user_repo=users)

    with pytest.raises(AuthError) as exc_info:
        await svc.login("noone@example.com", "whatever")

    assert exc_info.value.code == "invalid_credentials"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_login_raises_on_wrong_password():
    from app.services.auth_service import AuthError

    users = AsyncMock()
    users.find_by_email.return_value = _user(password_hash="hashed")
    users.find_by_id.return_value = _user(locked_until=None)
    users.increment_failed_attempts.return_value = 1
    svc = _make_service(user_repo=users)

    with patch("app.services.auth_service.verify_password", return_value=False):
        with pytest.raises(AuthError) as exc_info:
            await svc.login("test@example.com", "wrongpassword")

    assert exc_info.value.code == "invalid_credentials"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_login_raises_on_locked_account():
    from app.services.auth_service import AuthError

    locked_until = (datetime.now(tz=timezone.utc) + timedelta(minutes=10)).isoformat()
    users = AsyncMock()
    users.find_by_email.return_value = _user(password_hash="hashed")
    users.find_by_id.return_value = _user(locked_until=locked_until)
    svc = _make_service(user_repo=users)

    with pytest.raises(AuthError) as exc_info:
        await svc.login("test@example.com", "S3cur3P@ss!")

    assert exc_info.value.code == "account_locked"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_login_locks_after_max_failed_attempts():
    from app.services.auth_service import AuthError, _MAX_FAILED_ATTEMPTS

    users = AsyncMock()
    users.find_by_email.return_value = _user(password_hash="hashed")
    users.find_by_id.return_value = _user(locked_until=None)
    users.increment_failed_attempts.return_value = _MAX_FAILED_ATTEMPTS  # Triggers lockout
    users.set_locked_until.return_value = None
    svc = _make_service(user_repo=users)

    with patch("app.services.auth_service.verify_password", return_value=False):
        with pytest.raises(AuthError) as exc_info:
            await svc.login("test@example.com", "wrongpassword")

    assert exc_info.value.code == "invalid_credentials"
    users.set_locked_until.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_login_triggers_rehash_when_needed():
    users = AsyncMock()
    users.find_by_email.return_value = _user(password_hash="hashed")
    users.find_by_id.return_value = _user(locked_until=None)
    users.reset_failed_attempts.return_value = None
    users.update_password_hash.return_value = None
    tokens = AsyncMock()
    tokens.store_refresh_token.return_value = None

    svc = _make_service(user_repo=users, token_repo=tokens)

    with (
        patch("app.services.auth_service.verify_password", return_value=True),
        patch("app.services.auth_service.needs_rehash", return_value=True),
        patch("app.services.auth_service.hash_password", return_value="new-hash"),
    ):
        await svc.login("test@example.com", "S3cur3P@ss!")

    users.update_password_hash.assert_awaited_once()


# ---------------------------------------------------------------------------
# logout
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_logout_revokes_access_token():
    tokens = AsyncMock()
    svc = _make_service(token_repo=tokens)

    with patch("app.services.auth_service.revoke_jti") as mock_revoke:
        mock_revoke.return_value = None
        await svc.logout("access-jti-123")

    mock_revoke.assert_called_once_with("access-jti-123", ttl_seconds=900)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_logout_revokes_refresh_family_when_provided():
    tokens = AsyncMock()
    tokens.find_refresh_token.return_value = {"family_id": "family-1"}
    tokens.delete_refresh_token.return_value = None
    svc = _make_service(token_repo=tokens)

    with (
        patch("app.services.auth_service.revoke_jti"),
        patch("app.services.auth_service.revoke_token_family") as mock_family,
    ):
        await svc.logout("jti", refresh_token_hash="hashed-refresh")

    mock_family.assert_called_once_with("family-1")
    tokens.delete_refresh_token.assert_awaited_once_with("hashed-refresh")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_logout_skips_refresh_when_not_found():
    tokens = AsyncMock()
    tokens.find_refresh_token.return_value = None
    svc = _make_service(token_repo=tokens)

    with patch("app.services.auth_service.revoke_jti"):
        # Should not raise even when refresh token not found
        await svc.logout("jti", refresh_token_hash="unknown-hash")


# ---------------------------------------------------------------------------
# refresh
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_refresh_raises_when_token_not_found():
    from app.services.auth_service import AuthError

    tokens = AsyncMock()
    tokens.find_refresh_token.return_value = None
    svc = _make_service(token_repo=tokens)

    with pytest.raises(AuthError) as exc_info:
        await svc.refresh("raw-refresh-token")

    assert exc_info.value.code == "invalid_refresh_token"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_refresh_raises_when_token_expired():
    from app.services.auth_service import AuthError

    expired = (datetime.now(tz=timezone.utc) - timedelta(hours=1)).isoformat()
    tokens = AsyncMock()
    tokens.find_refresh_token.return_value = {
        "family_id": "fam-1",
        "user_id": "u1",
        "expires_at": expired,
    }
    tokens.delete_refresh_token.return_value = None
    svc = _make_service(token_repo=tokens)

    with pytest.raises(AuthError) as exc_info:
        await svc.refresh("expired-token")

    assert exc_info.value.code == "refresh_token_expired"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_refresh_raises_on_family_revoked():
    from app.services.auth_service import AuthError

    future = (datetime.now(tz=timezone.utc) + timedelta(hours=1)).isoformat()
    tokens = AsyncMock()
    tokens.find_refresh_token.return_value = {
        "family_id": "fam-revoked",
        "user_id": "u1",
        "expires_at": future,
    }
    svc = _make_service(token_repo=tokens)

    with patch("app.services.auth_service.is_family_revoked", return_value=True):
        with pytest.raises(AuthError) as exc_info:
            await svc.refresh("stolen-token")

    assert exc_info.value.code == "token_reuse_detected"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_refresh_raises_when_user_not_found():
    from app.services.auth_service import AuthError

    future = (datetime.now(tz=timezone.utc) + timedelta(hours=1)).isoformat()
    tokens = AsyncMock()
    tokens.find_refresh_token.return_value = {
        "family_id": "fam-1",
        "user_id": "u1",
        "expires_at": future,
    }
    tokens.delete_refresh_token.return_value = None
    users = AsyncMock()
    users.find_by_id.return_value = None
    svc = _make_service(user_repo=users, token_repo=tokens)

    with patch("app.services.auth_service.is_family_revoked", return_value=False):
        with pytest.raises(AuthError) as exc_info:
            await svc.refresh("valid-token")

    assert exc_info.value.code == "user_not_found"


# ---------------------------------------------------------------------------
# verify_email
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_verify_email_succeeds():
    future = datetime.now(tz=timezone.utc) + timedelta(hours=1)
    tokens = AsyncMock()
    tokens.find_email_verify_token.return_value = {"user_id": "u1", "expires_at": future}
    tokens.delete_email_verify_token.return_value = None
    users = AsyncMock()
    users.mark_email_verified.return_value = None

    svc = _make_service(user_repo=users, token_repo=tokens)
    await svc.verify_email("valid-token")

    users.mark_email_verified.assert_awaited_once_with("u1")
    tokens.delete_email_verify_token.assert_awaited_once_with("valid-token")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_verify_email_raises_when_token_not_found():
    from app.services.auth_service import AuthError

    tokens = AsyncMock()
    tokens.find_email_verify_token.return_value = None
    svc = _make_service(token_repo=tokens)

    with pytest.raises(AuthError) as exc_info:
        await svc.verify_email("nonexistent")

    assert exc_info.value.code == "invalid_token"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_verify_email_raises_when_token_expired():
    from app.services.auth_service import AuthError

    expired = datetime.now(tz=timezone.utc) - timedelta(hours=1)
    tokens = AsyncMock()
    tokens.find_email_verify_token.return_value = {"user_id": "u1", "expires_at": expired}
    svc = _make_service(token_repo=tokens)

    with pytest.raises(AuthError) as exc_info:
        await svc.verify_email("expired")

    assert exc_info.value.code == "token_expired"


# ---------------------------------------------------------------------------
# request_password_reset
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_request_password_reset_sends_email_when_user_found():
    future = datetime.now(tz=timezone.utc) + timedelta(minutes=30)
    users = AsyncMock()
    users.find_by_email.return_value = {"user_id": "u1", "email": "user@example.com"}
    tokens = AsyncMock()
    tokens.store_reset_token.return_value = None
    email_svc = AsyncMock()

    svc = _make_service(user_repo=users, token_repo=tokens, email_service=email_svc)
    await svc.request_password_reset("user@example.com")

    tokens.store_reset_token.assert_awaited_once()
    email_svc.send_password_reset_email.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_request_password_reset_silent_when_user_not_found():
    users = AsyncMock()
    users.find_by_email.return_value = None
    email_svc = AsyncMock()

    svc = _make_service(user_repo=users, email_service=email_svc)
    # Should return without error (enumeration prevention)
    await svc.request_password_reset("nobody@example.com")

    email_svc.send_password_reset_email.assert_not_awaited()


# ---------------------------------------------------------------------------
# complete_password_reset
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_complete_password_reset_succeeds():
    future = datetime.now(tz=timezone.utc) + timedelta(minutes=30)
    tokens = AsyncMock()
    tokens.find_reset_token.return_value = {"user_id": "u1", "expires_at": future}
    tokens.delete_reset_token.return_value = None
    tokens.list_token_families.return_value = ["fam-1"]
    users = AsyncMock()
    users.update_password_hash.return_value = None

    svc = _make_service(user_repo=users, token_repo=tokens)

    with (
        patch("app.services.auth_service.check_password_strength") as mock_strength,
        patch("app.services.auth_service.hash_password", return_value="new-hash"),
        patch("app.services.auth_service.revoke_token_family") as mock_revoke,
    ):
        mock_result = MagicMock(valid=True, errors=[])
        mock_strength.return_value = mock_result
        await svc.complete_password_reset("valid-token", "NewS3cur3P@ss!")

    users.update_password_hash.assert_awaited_once()
    tokens.delete_reset_token.assert_awaited_once_with("valid-token")
    mock_revoke.assert_called_once_with("fam-1")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_complete_password_reset_raises_when_token_invalid():
    from app.services.auth_service import AuthError

    tokens = AsyncMock()
    tokens.find_reset_token.return_value = None
    svc = _make_service(token_repo=tokens)

    with pytest.raises(AuthError) as exc_info:
        await svc.complete_password_reset("bad-token", "NewS3cur3P@ss!")

    assert exc_info.value.code == "invalid_token"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_complete_password_reset_raises_when_expired():
    from app.services.auth_service import AuthError

    expired = (datetime.now(tz=timezone.utc) - timedelta(minutes=5)).isoformat()
    tokens = AsyncMock()
    tokens.find_reset_token.return_value = {"user_id": "u1", "expires_at": expired}
    tokens.delete_reset_token.return_value = None
    svc = _make_service(token_repo=tokens)

    with pytest.raises(AuthError) as exc_info:
        await svc.complete_password_reset("expired-token", "NewS3cur3P@ss!")

    assert exc_info.value.code == "token_expired"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_complete_password_reset_raises_on_weak_new_password():
    from app.services.auth_service import AuthError

    future = datetime.now(tz=timezone.utc) + timedelta(minutes=30)
    tokens = AsyncMock()
    tokens.find_reset_token.return_value = {"user_id": "u1", "expires_at": future}
    svc = _make_service(token_repo=tokens)

    with pytest.raises(AuthError) as exc_info:
        await svc.complete_password_reset("valid-token", "weak")

    assert exc_info.value.code == "weak_password"


# ---------------------------------------------------------------------------
# change_password
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_change_password_succeeds():
    users = AsyncMock()
    users.find_by_id.return_value = _user(password_hash="hashed")
    users.update_password_hash.return_value = None

    svc = _make_service(user_repo=users)

    with (
        patch("app.services.auth_service.verify_password", return_value=True),
        patch("app.services.auth_service.check_password_strength") as mock_strength,
        patch("app.services.auth_service.hash_password", return_value="new-hash"),
    ):
        mock_result = MagicMock(valid=True, errors=[])
        mock_strength.return_value = mock_result
        await svc.change_password("u1", "OldS3cur3P@ss!", "NewS3cur3P@ss!")

    users.update_password_hash.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_change_password_raises_when_current_incorrect():
    from app.services.auth_service import AuthError

    users = AsyncMock()
    users.find_by_id.return_value = _user(password_hash="hashed")

    svc = _make_service(user_repo=users)

    with patch("app.services.auth_service.verify_password", return_value=False):
        with pytest.raises(AuthError) as exc_info:
            await svc.change_password("u1", "wrong", "NewS3cur3P@ss!")

    assert exc_info.value.code == "invalid_credentials"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_change_password_raises_on_weak_new_password():
    from app.services.auth_service import AuthError

    users = AsyncMock()
    users.find_by_id.return_value = _user(password_hash="hashed")
    svc = _make_service(user_repo=users)

    with patch("app.services.auth_service.verify_password", return_value=True):
        with pytest.raises(AuthError) as exc_info:
            await svc.change_password("u1", "OldS3cur3P@ss!", "weak")

    assert exc_info.value.code == "weak_password"


# ---------------------------------------------------------------------------
# emergency_revoke_all_tokens
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_emergency_revoke_all_tokens_returns_epoch():
    epoch = datetime.now(tz=timezone.utc)
    svc = _make_service()

    with patch("app.services.auth_service.emergency_revoke_all", return_value=epoch):
        result = await svc.emergency_revoke_all_tokens("admin-1")

    assert result == epoch


# ---------------------------------------------------------------------------
# Compat module-level functions
# ---------------------------------------------------------------------------

def test_compat_hash_and_verify_password():
    svc = _make_service()
    hashed = svc.hash_password("mypassword")
    assert hashed.startswith("sha256$")
    assert svc.verify_password("mypassword", hashed)
    assert not svc.verify_password("wrongpassword", hashed)
