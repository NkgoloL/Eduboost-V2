"""
A.1 — Auth abuse-path tests: lockout, cooldown, security alert.

Tests that AuthService enforces §3.1 P1:
  - account lockout after _MAX_FAILED_ATTEMPTS consecutive failures
  - lockout resets after admin unlock (reset_failed_attempts + clear locked_until)
  - security alert event emitted on suspicious auth patterns
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.auth_service import (
    AuthError,
    AuthService,
    _LOCKOUT_DURATION_MINUTES,
    _MAX_FAILED_ATTEMPTS,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _user(failed_attempts: int = 0, locked_until: datetime | None = None) -> dict:
    return {
        "user_id": "user-123",
        "email": "test@eduboost.co.za",
        "password_hash": "$2b$12$placeholder",
        "role": "guardian",
        "failed_attempts": failed_attempts,
        "locked_until": locked_until,
    }


def _make_service(user: dict | None = None) -> tuple[AuthService, MagicMock, MagicMock]:
    user_repo = AsyncMock()
    token_repo = AsyncMock()
    email_svc  = AsyncMock()

    user_repo.find_by_email.return_value = user
    user_repo.find_by_id.return_value    = user
    user_repo.increment_failed_attempts  = AsyncMock(return_value=_MAX_FAILED_ATTEMPTS)
    user_repo.reset_failed_attempts      = AsyncMock()
    user_repo.set_locked_until           = AsyncMock()
    token_repo.store_refresh_token       = AsyncMock()

    svc = AuthService(user_repo=user_repo, token_repo=token_repo, email_service=email_svc)
    return svc, user_repo, token_repo


# ── A.1.1 — Account locks out after _MAX_FAILED_ATTEMPTS failures ─────────────

@pytest.mark.asyncio
async def test_login_raises_account_locked_after_max_failures():
    """After _MAX_FAILED_ATTEMPTS wrong-password attempts, next attempt is locked out."""
    locked_until = datetime.now(timezone.utc) + timedelta(minutes=_LOCKOUT_DURATION_MINUTES)
    user = _user(failed_attempts=_MAX_FAILED_ATTEMPTS, locked_until=locked_until)
    svc, _, _ = _make_service(user)

    with pytest.raises(AuthError) as exc:
        await svc.login("test@eduboost.co.za", "wrong-password", ip="1.2.3.4")

    assert exc.value.code == "account_locked"


@pytest.mark.asyncio
async def test_lock_account_called_on_max_failures():
    """_lock_account is called when failed attempts reach the threshold."""
    user = _user(failed_attempts=0)
    svc, user_repo, _ = _make_service(user)
    user_repo.find_by_id.return_value = _user(locked_until=None)  # not yet locked

    with patch("app.services.auth_service.verify_password", return_value=False):
        with pytest.raises(AuthError) as exc:
            await svc.login("test@eduboost.co.za", "wrong", ip="1.2.3.4")

    # set_locked_until must have been called
    user_repo.set_locked_until.assert_awaited_once()
    call_args = user_repo.set_locked_until.call_args
    assert call_args[0][0] == "user-123"
    locked_until: datetime = call_args[0][1]
    assert locked_until > datetime.now(timezone.utc)
    assert exc.value.code == "invalid_credentials"


# ── A.1.2 — Lockout resets after admin unlock ────────────────────────────────

@pytest.mark.asyncio
async def test_lockout_clears_on_successful_login_after_unlock():
    """After admin unlocks an account (locked_until=None, failed=0), login succeeds."""
    user = _user(failed_attempts=0, locked_until=None)
    svc, user_repo, token_repo = _make_service(user)
    token_repo.store_refresh_token = AsyncMock()
    user_repo.update_password_hash = AsyncMock()

    with patch("app.services.auth_service.verify_password", return_value=True), \
         patch("app.services.auth_service.needs_rehash", return_value=False), \
         patch("app.services.auth_service.create_access_token", return_value="access.tok"), \
         patch("app.services.auth_service.create_refresh_token", return_value=(
             "raw", "hashed",
             MagicMock(family_id="fam-1", user_id="", expires_at=datetime.now(timezone.utc),
                       model_copy=lambda update: MagicMock(family_id="fam-1", user_id=update.get("user_id", "")))
         )):
        result = await svc.login("test@eduboost.co.za", "correct-password", ip="1.2.3.4")

    user_repo.reset_failed_attempts.assert_awaited_once_with("user-123")
    assert result is not None


@pytest.mark.asyncio
async def test_is_locked_out_returns_false_when_locked_until_in_past():
    """Account is not locked when locked_until has elapsed."""
    past = datetime.now(timezone.utc) - timedelta(minutes=1)
    user = _user(locked_until=past)
    svc, user_repo, _ = _make_service(user)

    result = await svc._is_locked_out("user-123")
    assert result is False


@pytest.mark.asyncio
async def test_is_locked_out_returns_true_when_locked_until_in_future():
    """Account is locked when locked_until is still in the future."""
    future = datetime.now(timezone.utc) + timedelta(minutes=10)
    user = _user(locked_until=future)
    svc, user_repo, _ = _make_service(user)
    user_repo.find_by_id.return_value = user

    result = await svc._is_locked_out("user-123")
    assert result is True


# ── A.1.3 — Security alert emitted on lockout ────────────────────────────────

@pytest.mark.asyncio
async def test_security_alert_emitted_on_account_lockout():
    """_emit_security_alert is called when an account is locked due to failures."""
    user = _user(failed_attempts=0, locked_until=None)
    svc, user_repo, token_repo = _make_service(user)

    with patch("app.services.auth_service.verify_password", return_value=False), \
         patch.object(svc, "_emit_security_alert", new=AsyncMock()) as mock_alert:
        with pytest.raises(AuthError):
            await svc.login("test@eduboost.co.za", "wrong", ip="10.0.0.1")

    mock_alert.assert_awaited_once()
    call_kwargs = mock_alert.call_args[0]
    assert call_kwargs[0] == "account_locked_after_failures"


@pytest.mark.asyncio
async def test_emit_security_alert_logs_warning(caplog):
    """_emit_security_alert emits a structured warning log with correct fields."""
    import logging
    svc, _, _ = _make_service()
    user = _user()

    with caplog.at_level(logging.WARNING, logger="eduboost.auth"):
        await svc._emit_security_alert("account_locked_after_failures", user, "192.168.1.1")

    # Should have logged at WARNING level
    assert len(caplog.records) >= 1
    assert any(r.levelno == logging.WARNING for r in caplog.records)


# ── A.1.4 — Nonexistent user does not reveal account existence ────────────────

@pytest.mark.asyncio
async def test_nonexistent_user_raises_same_error_as_wrong_password():
    """Login with nonexistent email returns 'invalid_credentials' (no enumeration)."""
    svc, user_repo, _ = _make_service(user=None)
    user_repo.find_by_email.return_value = None

    with pytest.raises(AuthError) as exc:
        await svc.login("nobody@eduboost.co.za", "any-password", ip="1.2.3.4")

    assert exc.value.code == "invalid_credentials"
    assert "Invalid email or password" in str(exc.value)
