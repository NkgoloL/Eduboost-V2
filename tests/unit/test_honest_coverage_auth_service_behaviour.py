from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from app.services import auth_service
from app.services.auth_service import AuthError, AuthService


def _service():
    users = AsyncMock()
    tokens = AsyncMock()
    email = AsyncMock()
    return AuthService(user_repo=users, token_repo=tokens, email_service=email), users, tokens, email


@pytest.mark.asyncio
async def test_refresh_rejects_expired_reused_and_missing_user_tokens(monkeypatch) -> None:
    service, users, tokens, _email = _service()
    expired_hashes: list[str] = []

    tokens.find_refresh_token.return_value = None
    with pytest.raises(AuthError) as missing:
        await service.refresh("missing-token")
    assert missing.value.code == "invalid_refresh_token"

    tokens.find_refresh_token.return_value = {
        "expires_at": datetime.now(timezone.utc) - timedelta(minutes=1),
        "family_id": "family-1",
        "user_id": "user-1",
    }
    tokens.delete_refresh_token.side_effect = expired_hashes.append
    with pytest.raises(AuthError) as expired:
        await service.refresh("expired-token")
    assert expired.value.code == "refresh_token_expired"
    assert expired_hashes

    tokens.find_refresh_token.return_value = {
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=30),
        "family_id": "family-2",
        "user_id": "user-2",
    }
    monkeypatch.setattr(auth_service, "is_family_revoked", AsyncMock(return_value=True))
    with pytest.raises(AuthError) as reused:
        await service.refresh("reused-token")
    assert reused.value.code == "token_reuse_detected"

    monkeypatch.setattr(auth_service, "is_family_revoked", AsyncMock(return_value=False))
    users.find_by_id.return_value = None
    with pytest.raises(AuthError) as missing_user:
        await service.refresh("orphan-token")
    assert missing_user.value.code == "user_not_found"


@pytest.mark.asyncio
async def test_password_reset_expiry_strength_and_success_revoke_existing_families(monkeypatch) -> None:
    service, users, tokens, _email = _service()
    revoked_families: list[str] = []

    tokens.find_reset_token.return_value = None
    with pytest.raises(AuthError) as missing:
        await service.complete_password_reset("missing", "StrongPass123")
    assert missing.value.code == "invalid_token"

    tokens.find_reset_token.return_value = {
        "user_id": "user-1",
        "expires_at": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    with pytest.raises(AuthError) as expired:
        await service.complete_password_reset("expired", "StrongPass123")
    assert expired.value.code == "token_expired"
    tokens.delete_reset_token.assert_awaited_with("expired")

    tokens.find_reset_token.return_value = {
        "user_id": "user-1",
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    with pytest.raises(AuthError) as weak:
        await service.complete_password_reset("valid", "short")
    assert weak.value.code == "weak_password"

    monkeypatch.setattr(auth_service, "hash_password", lambda password: f"hashed:{password}")
    monkeypatch.setattr(
        auth_service,
        "revoke_token_family",
        AsyncMock(side_effect=lambda family_id: revoked_families.append(family_id)),
    )
    tokens.list_token_families.return_value = ["family-1", "family-2"]

    await service.complete_password_reset("valid", "StrongPass123!")

    users.update_password_hash.assert_awaited_with("user-1", "hashed:StrongPass123!")
    tokens.delete_reset_token.assert_awaited_with("valid")
    assert revoked_families == ["family-1", "family-2"]


@pytest.mark.asyncio
async def test_logout_revokes_access_and_refresh_family_when_present(monkeypatch) -> None:
    service, _users, tokens, _email = _service()
    revoked_jtis: list[tuple[str, int]] = []
    revoked_families: list[str] = []

    monkeypatch.setattr(
        auth_service,
        "revoke_jti",
        AsyncMock(side_effect=lambda jti, ttl_seconds: revoked_jtis.append((jti, ttl_seconds))),
    )
    monkeypatch.setattr(
        auth_service,
        "revoke_token_family",
        AsyncMock(side_effect=lambda family_id: revoked_families.append(family_id)),
    )
    tokens.find_refresh_token.return_value = {"family_id": "family-1"}

    await service.logout("access-jti", refresh_token_hash="refresh-hash")

    assert revoked_jtis == [("access-jti", 900)]
    assert revoked_families == ["family-1"]
    tokens.delete_refresh_token.assert_awaited_with("refresh-hash")


@pytest.mark.asyncio
async def test_lockout_helpers_treat_missing_and_stale_locks_as_not_locked() -> None:
    service, users, _tokens, _email = _service()

    users.find_by_id.return_value = None
    assert await service._is_locked_out("missing") is False

    users.find_by_id.return_value = {
        "user_id": "user-1",
        "locked_until": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
    }
    assert await service._is_locked_out("user-1") is False

    users.find_by_id.return_value = {
        "user_id": "user-1",
        "locked_until": datetime.now(timezone.utc) + timedelta(minutes=1),
    }
    assert await service._is_locked_out("user-1") is True

    await service._lock_account("user-1")
    await service._clear_failed_attempts("user-1")
    users.set_locked_until.assert_awaited()
    users.reset_failed_attempts.assert_awaited_with("user-1")
