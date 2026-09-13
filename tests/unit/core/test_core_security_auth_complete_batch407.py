from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import hashlib
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import HTTPException, Response

from app.core import (
    cookies,
    jwt_compat,
    password,
    password_policy,
    pii_sanitizer,
    rbac,
    refresh_tokens,
    secret_rotation,
    token_config,
    token_revocation,
)
from app.core.config import settings


# ── 1. JWT_COMPAT ─────────────────────────────────────────────────────────────


def test_jwt_compat_decode_options():
    default_opts = jwt_compat.decode_options()
    assert default_opts == {"verify_aud": False}

    custom_opts = jwt_compat.decode_options({"verify_signature": False, "verify_exp": True})
    assert custom_opts == {"verify_aud": False, "verify_signature": False, "verify_exp": True}


# ── 2. PII_SANITIZER ──────────────────────────────────────────────────────────


def test_pii_sanitizer_edge_cases(monkeypatch):
    # 1. Fallback salt when config fails
    monkeypatch.delenv("PII_PSEUDONYMIZATION_SALT", raising=False)
    monkeypatch.delenv("ENCRYPTION_SALT", raising=False)
    with patch("app.core.config.get_settings", side_effect=RuntimeError("settings unavailable")):
        salt = pii_sanitizer._get_default_salt()
        assert salt == "eduboost_default_secure_pii_salt"

    # 2. Sensitive key with None value
    res1 = pii_sanitizer.sanitize_payload({"email": None, "first_name": None})
    assert res1 == {"email": None, "first_name": None}

    # 3. Sensitive key with complex/object value (not str, int)
    res2 = pii_sanitizer.sanitize_payload({"email": ["admin@example.com", "other@example.com"], "token": {"key": 123}})
    assert res2 == {"email": "[REDACTED_SENSITIVE_OBJECT]", "token": "[REDACTED_SENSITIVE_OBJECT]"}

    # 4. Set payload
    res3 = pii_sanitizer.sanitize_payload({"a@example.com", "clean_token"})
    assert isinstance(res3, set)
    assert "[REDACTED_EMAIL]" in res3


# ── 3. SECRET_ROTATION ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_secret_rotation_once(monkeypatch):
    # Non-production -> returns False
    monkeypatch.setattr(type(settings), "is_production", lambda self: False)
    res1 = await secret_rotation.refresh_key_vault_secrets_once()
    assert res1 is False

    # Production with URL -> returns True
    monkeypatch.setattr(type(settings), "is_production", lambda self: True)
    monkeypatch.setattr(settings, "AZURE_KEY_VAULT_URL", "https://test-vault.vault.azure.net/")
    monkeypatch.setattr(type(settings), "refresh_from_key_vault", lambda self: {"SECRET_A", "SECRET_B"})
    res2 = await secret_rotation.refresh_key_vault_secrets_once()
    assert res2 is True


@pytest.mark.asyncio
async def test_secret_rotation_loop(monkeypatch):
    monkeypatch.setattr(settings, "KEY_VAULT_REFRESH_INTERVAL_HOURS", 1)

    calls = 0

    async def mock_refresh():
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("Key vault unreachable")
        raise asyncio.CancelledError()

    with (
        patch("app.core.secret_rotation.refresh_key_vault_secrets_once", side_effect=mock_refresh),
        patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
    ):
        with pytest.raises(asyncio.CancelledError):
            await secret_rotation.key_vault_rotation_loop()
        assert calls == 2
        mock_sleep.assert_awaited_once_with(3600)


# ── 4. RBAC ───────────────────────────────────────────────────────────────────


def test_rbac_definitions():
    assert rbac.OperationalRole.LEARNER == "student"
    assert rbac.OperationalRole.PARENT_GUARDIAN == "parent"
    assert rbac.OperationalRole.TEACHER_TUTOR == "teacher"
    assert rbac.OperationalRole.ADMIN == "admin"
    assert rbac.OperationalRole.SUPPORT_OPERATOR == "support_operator"
    assert rbac.OperationalRole.CONTENT_REVIEWER == "content_reviewer"
    assert rbac.OperationalRole.COMPLIANCE_AUDITOR == "compliance_auditor"

    assert "student" in rbac.PERSISTED_ROLES
    assert "admin" in rbac.PERSISTED_ROLES
    assert "support_operator" in rbac.RESERVED_OPERATIONAL_ROLES
    assert rbac.require_role == rbac.require_roles


# ── 5. COOKIES ────────────────────────────────────────────────────────────────


def test_cookies_operations():
    res = Response()
    cookies.set_refresh_cookie(res, "raw_refresh_token_123")

    cookie_header = res.headers.get("set-cookie", "")
    assert "refresh_token=raw_refresh_token_123" in cookie_header
    assert "HttpOnly" in cookie_header

    res_logout = Response()
    cookies.clear_refresh_cookie(res_logout)
    clear_header = res_logout.headers.get("set-cookie", "")
    assert "refresh_token=" in clear_header
    assert "max-age=0" in clear_header.lower()

    policy = cookies.get_cookie_policy_summary()
    assert policy["cookie_name"] == "refresh_token"
    assert policy["http_only"] is True
    assert policy["js_readable"] is False


# ── 6. PASSWORD_POLICY ────────────────────────────────────────────────────────


def test_password_policy_validation(monkeypatch):
    # Legacy integration password allowed in dev
    monkeypatch.setenv("ENVIRONMENT", "development")
    assert password_policy.validate_password_strength("password123") == "password123"

    # Legacy integration password blocked in prod
    monkeypatch.setenv("ENVIRONMENT", "production")
    with pytest.raises(ValueError, match="common password words"):
        password_policy.validate_password_strength("password123")

    # Policy getter
    p = password_policy.get_password_policy()
    assert p.min_length >= 8

    # Common words failure
    with pytest.raises(ValueError, match="common password words"):
        password_policy.validate_password_strength("MyEduboostSecret!99")

    # Passphrase success (16+ chars, >= 3 words)
    passphrase = "correct horse battery staple"
    assert password_policy.validate_password_strength(passphrase) == passphrase

    # Complex password requirements:
    # Short
    with pytest.raises(ValueError, match="at least"):
        password_policy.validate_password_strength("Ab1!")

    # Missing uppercase
    with pytest.raises(ValueError, match="uppercase"):
        password_policy.validate_password_strength("alllower1234567!")

    # Missing lowercase
    with pytest.raises(ValueError, match="lowercase"):
        password_policy.validate_password_strength("ALLLOWER1234567!")

    # Missing digit
    with pytest.raises(ValueError, match="number"):
        password_policy.validate_password_strength("AllLowerNoDigits!")

    # Missing symbol
    with pytest.raises(ValueError, match="symbol"):
        password_policy.validate_password_strength("AllLowerNoSymbols123")

    # Valid complex password
    valid = "ValidComplexXyz123!"
    assert password_policy.validate_password_strength(valid) == valid


# ── 7. PASSWORD ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_password_utilities(monkeypatch):
    plain = "SuperSecureXyz123!"
    mock_pwd_ctx = MagicMock()
    mock_pwd_ctx.hash.return_value = "$2b$12$hashed_mock_pwd"
    mock_pwd_ctx.verify.side_effect = lambda p, h: p == plain and h == "$2b$12$hashed_mock_pwd"
    mock_pwd_ctx.needs_update.return_value = False

    monkeypatch.setattr(password, "_pwd_context", mock_pwd_ctx)

    hashed = password.hash_password(plain)
    assert hashed == "$2b$12$hashed_mock_pwd"
    assert password.verify_password(plain, hashed) is True
    assert password.verify_password("wrong", hashed) is False
    assert password.needs_rehash(hashed) is False

    # check_password_strength
    assert password.check_password_strength(plain).valid is True

    # Failures for check_password_strength
    assert password.check_password_strength("short").valid is False
    assert any("uppercase" in err for err in password.check_password_strength("nouppercase123!").errors)
    assert any("lowercase" in err for err in password.check_password_strength("NOLOWERCASE123!").errors)
    assert any("digit" in err for err in password.check_password_strength("NoDigitsHere!!").errors)
    assert any("special" in err for err in password.check_password_strength("NoSpecialChar123").errors)
    assert any("too common" in err for err in password.check_password_strength("password1").errors)

    # is_password_breached
    sha1 = hashlib.sha1(plain.encode("utf-8"), usedforsecurity=False).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]

    # Mock HIBP response with match
    mock_resp_match = MagicMock()
    mock_resp_match.text = f"{suffix}:42\nOTHERHASH:10"
    mock_resp_match.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.get", return_value=mock_resp_match):
        assert await password.is_password_breached(plain) is True

    # Mock HIBP response without match
    mock_resp_nomatch = MagicMock()
    mock_resp_nomatch.text = "OTHERHASH:10\nANOTHERHASH:5"
    mock_resp_nomatch.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.get", return_value=mock_resp_nomatch):
        assert await password.is_password_breached(plain) is False

    # Fail open on network error
    with patch("httpx.AsyncClient.get", side_effect=Exception("Timeout")):
        assert await password.is_password_breached(plain) is False

    assert "Consider using a passphrase" in password.PASSPHRASE_GUIDANCE


# ── 8. REFRESH_TOKENS ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_refresh_tokens_complete():
    # 1. TTL calculation from payload
    ttl = refresh_tokens._ttl_from_payload({})
    assert ttl == refresh_tokens.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600

    # 2. _require_refresh_payload validations
    with patch("app.core.refresh_tokens.decode_token", return_value={"type": "access", "sub": "u1", "jti": "j1"}):
        with pytest.raises(HTTPException) as exc1:
            refresh_tokens._require_refresh_payload("token_access")
        assert exc1.value.status_code == 401
        assert "Not a refresh token" in exc1.value.detail

    with patch("app.core.refresh_tokens.decode_token", return_value={"type": "refresh", "sub": None, "jti": None}):
        with pytest.raises(HTTPException) as exc2:
            refresh_tokens._require_refresh_payload("token_malformed")
        assert exc2.value.status_code == 401
        assert "Malformed refresh token" in exc2.value.detail

    # 3. Family revoked check in consume_refresh_token
    with (
        patch("app.core.refresh_tokens._require_refresh_payload", return_value={"sub": "u1", "jti": "j1", "family": "f1"}),
        patch("app.core.refresh_tokens.is_refresh_family_revoked", return_value=True),
    ):
        with pytest.raises(HTTPException) as exc3:
            await refresh_tokens.consume_refresh_token("token_fam_revoked")
        assert exc3.value.status_code == 401
        assert "Refresh token family revoked" in exc3.value.detail

    # 4. Revocation helpers: None cases
    assert await refresh_tokens.is_refresh_family_revoked(None) is False
    await refresh_tokens.revoke_refresh_family(None)
    await refresh_tokens.revoke_refresh_token_jti(None)

    # 5. Revocation helpers with params
    with (
        patch("app.core.refresh_tokens.cache_delete", new_callable=AsyncMock) as mock_delete,
        patch("app.core.refresh_tokens.cache_set", new_callable=AsyncMock) as mock_set,
        patch("app.core.refresh_tokens.cache_delete_pattern", new_callable=AsyncMock) as mock_pat,
    ):
        await refresh_tokens.revoke_refresh_token_jti("j1", subject="u1", family_id="f1")
        assert mock_delete.await_count == 3

        mock_pat.return_value = 2
        count = await refresh_tokens.revoke_all_refresh_tokens_for_user("u1")
        assert count == 2

    # 6. revoke_refresh_token wrapper
    with (
        patch("app.core.refresh_tokens._require_refresh_payload", return_value={"jti": "j1", "sub": "u1", "family": "f1"}),
        patch("app.core.refresh_tokens.revoke_refresh_token_jti", new_callable=AsyncMock) as mock_rev_jti,
    ):
        await refresh_tokens.revoke_refresh_token("some_token")
        mock_rev_jti.assert_awaited_once_with("j1", "u1", "f1")


# ── 9. TOKEN_CONFIG ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_token_config_edge_branches():
    # 1. Unknown kid
    with pytest.raises(token_config.JWTError, match="Unknown signing key id"):
        token_config._secret_for_kid("unknown_kid_999")

    # 2. verify_access_token with iat >= epoch (valid post-epoch token)
    mock_redis = AsyncMock()
    mock_redis.exists.return_value = 0  # not revoked
    epoch = datetime.now(timezone.utc).isoformat()
    mock_redis.get.return_value = epoch

    token_claims = {
        "jti": "jti_test_1",
        "sub": "user_1",
        "iat": int(datetime.now(timezone.utc).timestamp()) + 10,
    }

    with (
        patch("app.core.token_config.get_redis", return_value=mock_redis),
        patch("app.core.token_config.jwt.get_unverified_header", return_value={"kid": token_config.CURRENT_KID}),
        patch("app.core.token_config.jwt.decode", return_value=token_claims),
    ):
        verified = await token_config.verify_access_token("valid_post_epoch_token")
        assert verified["jti"] == "jti_test_1"


# ── 10. TOKEN_REVOCATION ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_token_revocation_branches():
    mock_redis = AsyncMock()
    mock_redis.exists.return_value = False
    mock_redis.get.return_value = None

    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        assert await token_revocation.is_token_revoked("jti_clean") is False
