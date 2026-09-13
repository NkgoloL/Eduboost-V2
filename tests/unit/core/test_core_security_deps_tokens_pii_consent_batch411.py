"""
tests/unit/core/test_core_security_deps_tokens_pii_consent_batch411.py
=======================================================================
Batch 411: >=90% deterministic unit-test coverage for:
  - app/core/consent_gate.py
  - app/core/dependencies.py
  - app/core/pii_sanitizer.py
  - app/core/refresh_tokens.py
  - app/core/security.py
  - app/core/token_config.py
  - app/core/token_revocation.py

All tests are deterministic; no network or real-Redis connections used.
"""
from __future__ import annotations

import asyncio
import hashlib
import time
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.core import consent_gate as core_consent_gate
from app.core import dependencies as core_deps
from app.core import pii_sanitizer as core_pii
from app.core import refresh_tokens as core_refresh
from app.core import security as core_security
from app.core import token_config as core_token_config
from app.core import token_revocation as core_token_rev
from app.core.config import Settings, settings
from app.models import UserRole


# ── 1. PII SANITIZER ─────────────────────────────────────────────────────────


def test_pii_sanitizer_hash_pseudonym():
    result = core_pii.hash_pseudonym("user@example.com", salt="test-salt")
    assert result.startswith("pseudonym_")
    assert result == core_pii.hash_pseudonym("user@example.com", salt="test-salt")
    assert result != core_pii.hash_pseudonym("other@example.com", salt="test-salt")


def test_pii_sanitizer_hash_pseudonym_no_salt():
    result = core_pii.hash_pseudonym("user@example.com")
    assert result.startswith("pseudonym_")


def test_pii_sanitizer_get_default_salt_from_pii_env(monkeypatch):
    monkeypatch.setenv("PII_PSEUDONYMIZATION_SALT", "env-pii-salt")
    salt = core_pii._get_default_salt()
    assert salt == "env-pii-salt"


def test_pii_sanitizer_get_default_salt_from_encryption_env(monkeypatch):
    monkeypatch.delenv("PII_PSEUDONYMIZATION_SALT", raising=False)
    monkeypatch.setenv("ENCRYPTION_SALT", "enc-salt")
    salt = core_pii._get_default_salt()
    assert salt == "enc-salt"


def test_pii_sanitizer_get_default_salt_settings_exception(monkeypatch):
    monkeypatch.delenv("PII_PSEUDONYMIZATION_SALT", raising=False)
    monkeypatch.delenv("ENCRYPTION_SALT", raising=False)
    # patch the get_settings import inside the function
    with patch("app.core.config.get_settings", side_effect=Exception("fail")):
        salt = core_pii._get_default_salt()
    # Falls back to settings attribute or hardcoded default
    assert isinstance(salt, str) and len(salt) > 0


def test_pii_sanitizer_sanitize_string_value():
    assert "[REDACTED_EMAIL]" in core_pii.sanitize_string_value("user@example.com info")
    assert "[REDACTED_ID]" in core_pii.sanitize_string_value("ID: 9201015009087")
    assert "[REDACTED_PHONE]" in core_pii.sanitize_string_value("Call +27821234567")
    assert core_pii.sanitize_string_value("No PII here") == "No PII here"


def test_pii_sanitizer_sanitize_payload_dict():
    payload = {
        "email": "user@example.com",
        "name": "Jane",
        "age": 25,
        "token": "secret",
        "nested_email": "other@example.com",
    }
    result = core_pii.sanitize_payload(payload, salt="test-salt")
    assert result["email"].startswith("pseudonym_")
    assert result["name"].startswith("pseudonym_")
    assert result["age"] == 25
    assert result["token"].startswith("pseudonym_")
    assert "[REDACTED_EMAIL]" in result["nested_email"]


def test_pii_sanitizer_sanitize_payload_none_sensitive():
    result = core_pii.sanitize_payload({"email": None}, salt="test-salt")
    assert result["email"] is None


def test_pii_sanitizer_sanitize_payload_int_sensitive():
    result = core_pii.sanitize_payload({"password_hash": 12345}, salt="test-salt")
    assert result["password_hash"].startswith("pseudonym_")


def test_pii_sanitizer_sanitize_payload_object_sensitive():
    result = core_pii.sanitize_payload({"token": {"nested": "dict"}}, salt="test-salt")
    assert result["token"] == "[REDACTED_SENSITIVE_OBJECT]"


def test_pii_sanitizer_sanitize_payload_list():
    result = core_pii.sanitize_payload(["user@example.com", "clean", {"email": "a@b.com"}], salt="s")
    assert "[REDACTED_EMAIL]" in result[0]
    assert result[1] == "clean"
    assert result[2]["email"].startswith("pseudonym_")


def test_pii_sanitizer_sanitize_payload_tuple():
    result = core_pii.sanitize_payload(("user@example.com", "clean"), salt="s")
    assert isinstance(result, tuple)
    assert "[REDACTED_EMAIL]" in result[0]


def test_pii_sanitizer_sanitize_payload_set():
    result = core_pii.sanitize_payload({"user@example.com", "clean"}, salt="s")
    assert isinstance(result, (set, frozenset))
    assert any("[REDACTED_EMAIL]" in str(i) for i in result)


def test_pii_sanitizer_sanitize_payload_non_string_scalars():
    assert core_pii.sanitize_payload(42) == 42
    assert core_pii.sanitize_payload(None) is None
    assert core_pii.sanitize_payload(True) is True


# ── 2. TOKEN REVOCATION ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_token_revocation_setex_branch():
    mock_redis = MagicMock()
    mock_redis.setex = MagicMock(return_value=None)
    mock_redis.get = AsyncMock(return_value=None)

    exp_ts = int(time.time()) + 3600
    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        await core_token_rev.revoke_token("jti_1", exp_ts)
        mock_redis.setex.assert_called_once()

        result = await core_token_rev.is_token_revoked("jti_1")
        assert result is False

        mock_redis.get = AsyncMock(return_value="1")
        result = await core_token_rev.is_token_revoked("jti_1")
        assert result is True


@pytest.mark.asyncio
async def test_token_revocation_set_branch_no_setex():
    mock_redis = MagicMock(spec=["set"])
    mock_redis.set = MagicMock(return_value=None)
    exp_ts = int(time.time()) + 3600
    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        await core_token_rev.revoke_token("jti_set", exp_ts)
    mock_redis.set.assert_called()


@pytest.mark.asyncio
async def test_token_revocation_set_typeerror_branch():
    def _set_side_effect(*a, **kw):
        if "ex" in kw:
            raise TypeError("no ex")
        return None

    mock_redis = MagicMock(spec=["set"])
    mock_redis.set = MagicMock(side_effect=_set_side_effect)
    exp_ts = int(time.time()) + 3600
    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        await core_token_rev.revoke_token("jti_typeerror", exp_ts)
    assert mock_redis.set.call_count == 2


@pytest.mark.asyncio
async def test_token_revocation_data_branch():
    mock_redis = SimpleNamespace(_data={})
    exp_ts = int(time.time()) + 3600
    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        await core_token_rev.revoke_token("jti_data", exp_ts)
    assert any("jti_data" in k for k in mock_redis._data)


@pytest.mark.asyncio
async def test_token_revocation_store_branch():
    mock_redis = SimpleNamespace(store={})
    exp_ts = int(time.time()) + 3600
    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        await core_token_rev.revoke_token("jti_store", exp_ts)
    assert any("jti_store" in k for k in mock_redis.store)


@pytest.mark.asyncio
async def test_token_revocation_setattr_fallback_branch():
    mock_redis = SimpleNamespace()
    exp_ts = int(time.time()) + 3600
    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        await core_token_rev.revoke_token("jti_setattr_fb", exp_ts)


@pytest.mark.asyncio
async def test_token_revocation_setex_awaitable():
    async def _coro():
        return None
    mock_redis = MagicMock()
    mock_redis.setex = MagicMock(return_value=_coro())
    exp_ts = int(time.time()) + 3600
    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        await core_token_rev.revoke_token("jti_await", exp_ts)


@pytest.mark.asyncio
async def test_token_revocation_set_awaitable():
    async def _coro():
        return None
    mock_redis = MagicMock(spec=["set"])
    mock_redis.set = MagicMock(return_value=_coro())
    exp_ts = int(time.time()) + 3600
    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        await core_token_rev.revoke_token("jti_set_await", exp_ts)


@pytest.mark.asyncio
async def test_token_revocation_redis_error_revoke():
    from redis.exceptions import RedisError
    mock_redis = MagicMock()
    mock_redis.setex = MagicMock(side_effect=RedisError("down"))
    exp_ts = int(time.time()) + 3600
    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        await core_token_rev.revoke_token("jti_err", exp_ts)


@pytest.mark.asyncio
async def test_token_revocation_redis_error_is_revoked():
    from redis.exceptions import RedisError
    mock_redis = MagicMock()
    mock_redis.get = AsyncMock(side_effect=RedisError("down"))
    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        result = await core_token_rev.is_token_revoked("jti_err")
    assert result is False


@pytest.mark.asyncio
async def test_token_revocation_revoke_user():
    mock_redis = MagicMock()
    mock_redis.setex = MagicMock(return_value=None)
    mock_redis.get = AsyncMock(return_value="1")
    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        await core_token_rev.revoke_user_tokens("user_1")
        assert await core_token_rev.is_user_revoked("user_1") is True


@pytest.mark.asyncio
async def test_token_revocation_revoke_user_redis_error():
    from redis.exceptions import RedisError
    mock_redis = MagicMock()
    mock_redis.setex = MagicMock(side_effect=RedisError("down"))
    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        await core_token_rev.revoke_user_tokens("user_err")


@pytest.mark.asyncio
async def test_token_revocation_is_user_revoked_redis_error():
    from redis.exceptions import RedisError
    mock_redis = MagicMock()
    mock_redis.get = AsyncMock(side_effect=RedisError("down"))
    with patch("app.core.token_revocation.get_redis", return_value=mock_redis):
        result = await core_token_rev.is_user_revoked("user_err")
    assert result is False


# ── 3. SECURITY ───────────────────────────────────────────────────────────────


def test_security_hash_password_verify():
    h = core_security.hash_password("Str0ng@Pass!")
    assert core_security.verify_password("Str0ng@Pass!", h) is True
    assert core_security.verify_password("Wrong", h) is False


def test_security_verify_password_invalid_hash():
    assert core_security.verify_password("anything", "not_bcrypt") is False


def test_security_hash_email():
    result = core_security.hash_email("User@Example.com")
    assert result == hashlib.sha256("user@example.com".encode()).hexdigest()


def test_security_create_and_decode_access_token():
    tok = core_security.create_access_token("u1", UserRole.STUDENT)
    payload = core_security.decode_token(tok)
    assert payload["sub"] == "u1"
    assert payload["type"] == "access"


def test_security_create_refresh_token():
    tok = core_security.create_refresh_token("u1", UserRole.STUDENT)
    payload = core_security.decode_token(tok)
    assert payload["type"] == "refresh"


def test_security_create_refresh_token_with_family():
    tok = core_security.create_refresh_token("u1", UserRole.ADMIN, family_id="fam_1")
    payload = core_security.decode_token(tok)
    assert payload["family"] == "fam_1"


def test_security_decode_token_invalid():
    with pytest.raises(HTTPException) as exc:
        core_security.decode_token("not.a.valid.token")
    assert exc.value.status_code == 401


def test_security_encrypt_decrypt_pii():
    cipher = core_security.encrypt_pii("secret@example.com")
    assert len(cipher) > 0
    assert core_security.decrypt_pii(cipher) == "secret@example.com"


def test_security_encrypt_empty():
    assert core_security.encrypt_pii("") == ""


def test_security_decrypt_empty():
    assert core_security.decrypt_pii("") == ""


@pytest.mark.asyncio
async def test_security_get_current_user_no_creds():
    with pytest.raises(HTTPException) as exc:
        await core_security.get_current_user(None)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_security_get_current_user_wrong_type():
    rtok = core_security.create_refresh_token("u1", UserRole.STUDENT)
    creds = SimpleNamespace(credentials=rtok)
    with patch("app.core.security.is_token_revoked", new_callable=AsyncMock, return_value=False):
        with patch("app.core.security.is_user_revoked", new_callable=AsyncMock, return_value=False):
            with pytest.raises(HTTPException) as exc:
                await core_security.get_current_user(creds)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_security_get_current_user_revoked_jti():
    tok = core_security.create_access_token("u1", UserRole.STUDENT)
    creds = SimpleNamespace(credentials=tok)
    with patch("app.core.security.is_token_revoked", new_callable=AsyncMock, return_value=True):
        with pytest.raises(HTTPException) as exc:
            await core_security.get_current_user(creds)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_security_get_current_user_revoked_user():
    tok = core_security.create_access_token("u1", UserRole.STUDENT)
    creds = SimpleNamespace(credentials=tok)
    with patch("app.core.security.is_token_revoked", new_callable=AsyncMock, return_value=False):
        with patch("app.core.security.is_user_revoked", new_callable=AsyncMock, return_value=True):
            with pytest.raises(HTTPException) as exc:
                await core_security.get_current_user(creds)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_security_get_current_user_valid():
    tok = core_security.create_access_token("u1", UserRole.STUDENT)
    creds = SimpleNamespace(credentials=tok)
    with patch("app.core.security.is_token_revoked", new_callable=AsyncMock, return_value=False):
        with patch("app.core.security.is_user_revoked", new_callable=AsyncMock, return_value=False):
            payload = await core_security.get_current_user(creds)
    assert payload["sub"] == "u1"


@pytest.mark.asyncio
async def test_security_get_current_user_optional_none():
    assert await core_security.get_current_user_optional(None) is None


@pytest.mark.asyncio
async def test_security_get_current_user_optional_valid():
    tok = core_security.create_access_token("u2", UserRole.ADMIN)
    creds = SimpleNamespace(credentials=tok)
    with patch("app.core.security.is_token_revoked", new_callable=AsyncMock, return_value=False):
        with patch("app.core.security.is_user_revoked", new_callable=AsyncMock, return_value=False):
            result = await core_security.get_current_user_optional(creds)
    assert result["sub"] == "u2"


def test_security_require_roles():
    dep = core_security.require_roles(UserRole.ADMIN)
    assert callable(dep)


def test_security_role_constants():
    assert core_security.require_admin is not None
    assert core_security.require_parent_or_admin is not None
    assert core_security.require_teacher_or_admin is not None


# ── 4. TOKEN CONFIG ───────────────────────────────────────────────────────────


def test_token_config_create_access_token():
    tok = core_token_config.create_access_token("u1", "admin")
    assert isinstance(tok, str)


def test_token_config_create_access_token_extra_claims():
    tok = core_token_config.create_access_token("u1", "admin", extra_claims={"custom": "val"})
    from app.core.jwt_compat import jwt
    header = jwt.get_unverified_header(tok)
    assert header.get("kid") == core_token_config.CURRENT_KID


def test_token_config_create_refresh_token():
    raw, hashed, record = core_token_config.create_refresh_token()
    assert isinstance(raw, str)
    assert hashed == hashlib.sha256(raw.encode()).hexdigest()
    assert record.family_id is not None


def test_token_config_create_refresh_token_with_family():
    _, _, record = core_token_config.create_refresh_token(family_id="fam_123")
    assert record.family_id == "fam_123"


def test_token_config_hash_token():
    raw = "raw_token_value"
    assert core_token_config._hash_token(raw) == hashlib.sha256(raw.encode()).hexdigest()


def test_token_config_secret_for_kid_known():
    secret = core_token_config._secret_for_kid(core_token_config.CURRENT_KID)
    assert secret == core_token_config.CURRENT_KEY


def test_token_config_secret_for_kid_unknown():
    from app.core.jwt_compat import JWTError
    with pytest.raises(JWTError):
        core_token_config._secret_for_kid("unknown_kid_xyz")


def test_token_config_token_pair_model():
    pair = core_token_config.TokenPair(access_token="tok")
    assert pair.token_type == "bearer"
    assert pair.expires_in == core_token_config.ACCESS_TOKEN_TTL_MINUTES * 60


def test_token_config_refresh_record_model():
    now = datetime.now(tz=timezone.utc)
    rec = core_token_config.RefreshTokenRecord(
        family_id="f1", user_id="u1", issued_at=now, expires_at=now
    )
    assert rec.family_id == "f1"


@pytest.mark.asyncio
async def test_token_config_get_redis_cached():
    import app.core.token_config as tc
    original = tc._redis
    tc._redis = None
    try:
        mock_inst = AsyncMock()
        with patch("app.core.token_config.aioredis.from_url", return_value=mock_inst):
            r1 = await tc.get_redis()
            r2 = await tc.get_redis()
        assert r1 is r2
    finally:
        tc._redis = original


@pytest.mark.asyncio
async def test_token_config_verify_access_token_valid():
    tok = core_token_config.create_access_token("u1", "admin")
    mock_redis = AsyncMock()
    mock_redis.exists = AsyncMock(return_value=0)
    mock_redis.get = AsyncMock(return_value=None)
    with patch("app.core.token_config.get_redis", new_callable=AsyncMock, return_value=mock_redis):
        claims = await core_token_config.verify_access_token(tok)
    assert claims["sub"] == "u1"


@pytest.mark.asyncio
async def test_token_config_verify_access_token_revoked():
    from app.core.jwt_compat import JWTError
    tok = core_token_config.create_access_token("u1", "admin")
    mock_redis = AsyncMock()
    mock_redis.exists = AsyncMock(return_value=1)
    with patch("app.core.token_config.get_redis", new_callable=AsyncMock, return_value=mock_redis):
        with pytest.raises(JWTError, match="revoked"):
            await core_token_config.verify_access_token(tok)


@pytest.mark.asyncio
async def test_token_config_verify_access_token_global_epoch():
    from app.core.jwt_compat import JWTError
    tok = core_token_config.create_access_token("u1", "admin")
    future_epoch = datetime.now(tz=timezone.utc).replace(year=2035)
    mock_redis = AsyncMock()
    mock_redis.exists = AsyncMock(return_value=0)
    mock_redis.get = AsyncMock(return_value=future_epoch.isoformat())
    with patch("app.core.token_config.get_redis", new_callable=AsyncMock, return_value=mock_redis):
        with pytest.raises(JWTError, match="predates global revocation epoch"):
            await core_token_config.verify_access_token(tok)


@pytest.mark.asyncio
async def test_token_config_verify_access_token_redis_unavailable():
    from app.core.jwt_compat import JWTError
    import redis.asyncio as aioredis
    tok = core_token_config.create_access_token("u1", "admin")
    mock_redis = AsyncMock()
    mock_redis.exists = AsyncMock(side_effect=aioredis.RedisError("down"))
    with patch("app.core.token_config.get_redis", new_callable=AsyncMock, return_value=mock_redis):
        with pytest.raises(JWTError, match="Revocation store unavailable"):
            await core_token_config.verify_access_token(tok)


@pytest.mark.asyncio
async def test_token_config_verify_access_token_invalid():
    from app.core.jwt_compat import JWTError
    with pytest.raises(JWTError):
        await core_token_config.verify_access_token("not.a.token")


@pytest.mark.asyncio
async def test_token_config_revoke_jti():
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock(return_value=None)
    with patch("app.core.token_config.get_redis", new_callable=AsyncMock, return_value=mock_redis):
        await core_token_config.revoke_jti("jti_999")
    mock_redis.setex.assert_called_once()


@pytest.mark.asyncio
async def test_token_config_revoke_token_family():
    mock_redis = AsyncMock()
    mock_redis.set = AsyncMock(return_value=None)
    with patch("app.core.token_config.get_redis", new_callable=AsyncMock, return_value=mock_redis):
        await core_token_config.revoke_token_family("fam_xyz")
    mock_redis.set.assert_called_once()


@pytest.mark.asyncio
async def test_token_config_is_family_revoked_true():
    mock_redis = AsyncMock()
    mock_redis.exists = AsyncMock(return_value=1)
    with patch("app.core.token_config.get_redis", new_callable=AsyncMock, return_value=mock_redis):
        assert await core_token_config.is_family_revoked("fam_xyz") is True


@pytest.mark.asyncio
async def test_token_config_is_family_revoked_false():
    mock_redis = AsyncMock()
    mock_redis.exists = AsyncMock(return_value=0)
    with patch("app.core.token_config.get_redis", new_callable=AsyncMock, return_value=mock_redis):
        assert await core_token_config.is_family_revoked("fam_xyz") is False


@pytest.mark.asyncio
async def test_token_config_emergency_revoke_all():
    mock_redis = AsyncMock()
    mock_redis.set = AsyncMock(return_value=None)
    with patch("app.core.token_config.get_redis", new_callable=AsyncMock, return_value=mock_redis):
        epoch = await core_token_config.emergency_revoke_all()
    assert isinstance(epoch, datetime)


@pytest.mark.asyncio
async def test_token_config_add_persistent_revocation_fallback():
    import sys
    from datetime import timedelta
    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock(return_value=None)
    expires_at = datetime.now(tz=timezone.utc) + timedelta(hours=1)
    mock_revoc_module = MagicMock()
    mock_revoc_module.persist_revocation = AsyncMock(return_value=None)
    with patch("app.core.token_config.get_redis", new_callable=AsyncMock, return_value=mock_redis):
        with patch.dict(sys.modules, {"app.repositories.revocation_repository": mock_revoc_module}):
            await core_token_config.add_persistent_revocation_fallback("jti_p", expires_at)


# ── 5. REFRESH TOKENS ─────────────────────────────────────────────────────────


def test_refresh_tokens_token_hash():
    result = core_refresh.token_hash("abc")
    assert result == hashlib.sha256(b"abc").hexdigest()


def test_refresh_tokens_key_helpers():
    assert core_refresh._refresh_key("j1") == "refresh:j1"
    assert core_refresh._family_key("f1", "j1") == "refresh_family:f1:j1"
    assert core_refresh._user_session_key("s1", "j1") == "refresh_user:s1:j1"
    assert core_refresh._family_revoked_key("f1") == "refresh_family_revoked:f1"


def test_refresh_tokens_ttl_from_payload_numeric():
    future = int(time.time()) + 3600
    ttl = core_refresh._ttl_from_payload({"exp": future})
    assert ttl > 0


def test_refresh_tokens_ttl_from_payload_non_numeric():
    ttl = core_refresh._ttl_from_payload({"exp": "bad"})
    assert ttl == core_refresh.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600


@pytest.mark.asyncio
async def test_refresh_tokens_require_refresh_payload_not_refresh_type():
    tok = core_security.create_access_token("u1", UserRole.STUDENT)
    with pytest.raises(HTTPException) as exc:
        core_refresh._require_refresh_payload(tok)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_tokens_store_and_consume():
    rtok = core_security.create_refresh_token("u1", UserRole.STUDENT)
    store: dict = {}

    async def _set(key, value, ttl=None):
        store[key] = value

    async def _get(key):
        return store.get(key)

    async def _delete(key):
        store.pop(key, None)

    async def _delete_pattern(pat):
        return 0

    with patch("app.core.refresh_tokens.cache_set", side_effect=_set):
        with patch("app.core.refresh_tokens.cache_get", side_effect=_get):
            with patch("app.core.refresh_tokens.cache_delete", side_effect=_delete):
                with patch("app.core.refresh_tokens.is_refresh_family_revoked", new_callable=AsyncMock, return_value=False):
                    with patch("app.core.refresh_tokens.cache_delete_pattern", side_effect=_delete_pattern):
                        await core_refresh.store_refresh_token(rtok)
                        assert len(store) > 0
                        payload = await core_refresh.consume_refresh_token(rtok)
    assert payload["sub"] == "u1"
    assert payload["type"] == "refresh"


@pytest.mark.asyncio
async def test_refresh_tokens_consume_family_revoked():
    rtok = core_security.create_refresh_token("u1", UserRole.STUDENT)
    with patch("app.core.refresh_tokens.is_refresh_family_revoked", new_callable=AsyncMock, return_value=True):
        with pytest.raises(HTTPException) as exc:
            await core_refresh.consume_refresh_token(rtok)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_tokens_consume_hash_mismatch():
    rtok = core_security.create_refresh_token("u1", UserRole.STUDENT)
    with patch("app.core.refresh_tokens.is_refresh_family_revoked", new_callable=AsyncMock, return_value=False):
        with patch("app.core.refresh_tokens.cache_get", new_callable=AsyncMock, return_value="wrong_hash"):
            with patch("app.core.refresh_tokens.revoke_refresh_family", new_callable=AsyncMock):
                with pytest.raises(HTTPException) as exc:
                    await core_refresh.consume_refresh_token(rtok)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_tokens_consume_not_found():
    rtok = core_security.create_refresh_token("u1", UserRole.STUDENT)
    with patch("app.core.refresh_tokens.is_refresh_family_revoked", new_callable=AsyncMock, return_value=False):
        with patch("app.core.refresh_tokens.cache_get", new_callable=AsyncMock, return_value=None):
            with patch("app.core.refresh_tokens.revoke_refresh_family", new_callable=AsyncMock):
                with pytest.raises(HTTPException) as exc:
                    await core_refresh.consume_refresh_token(rtok)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_tokens_revoke_token():
    rtok = core_security.create_refresh_token("u1", UserRole.STUDENT)
    with patch("app.core.refresh_tokens.cache_delete", new_callable=AsyncMock) as m:
        await core_refresh.revoke_refresh_token(rtok)
    assert m.called


@pytest.mark.asyncio
async def test_refresh_tokens_revoke_jti_all():
    with patch("app.core.refresh_tokens.cache_delete", new_callable=AsyncMock) as m:
        await core_refresh.revoke_refresh_token_jti("j1", subject="u1", family_id="f1")
    assert m.call_count == 3


@pytest.mark.asyncio
async def test_refresh_tokens_revoke_jti_no_jti():
    with patch("app.core.refresh_tokens.cache_delete", new_callable=AsyncMock) as m:
        await core_refresh.revoke_refresh_token_jti(None)
    m.assert_not_called()


@pytest.mark.asyncio
async def test_refresh_tokens_revoke_jti_no_family_no_subject():
    with patch("app.core.refresh_tokens.cache_delete", new_callable=AsyncMock) as m:
        await core_refresh.revoke_refresh_token_jti("j1")
    assert m.call_count == 1


@pytest.mark.asyncio
async def test_refresh_tokens_revoke_family():
    with patch("app.core.refresh_tokens.cache_set", new_callable=AsyncMock) as ms:
        with patch("app.core.refresh_tokens.cache_delete_pattern", new_callable=AsyncMock) as md:
            await core_refresh.revoke_refresh_family("f1")
    ms.assert_called_once()
    md.assert_called_once()


@pytest.mark.asyncio
async def test_refresh_tokens_revoke_family_none():
    with patch("app.core.refresh_tokens.cache_set", new_callable=AsyncMock) as ms:
        await core_refresh.revoke_refresh_family(None)
    ms.assert_not_called()


@pytest.mark.asyncio
async def test_refresh_tokens_is_family_revoked_true():
    with patch("app.core.refresh_tokens.cache_get", new_callable=AsyncMock, return_value="1"):
        assert await core_refresh.is_refresh_family_revoked("f1") is True


@pytest.mark.asyncio
async def test_refresh_tokens_is_family_revoked_false():
    with patch("app.core.refresh_tokens.cache_get", new_callable=AsyncMock, return_value=None):
        assert await core_refresh.is_refresh_family_revoked("f1") is False


@pytest.mark.asyncio
async def test_refresh_tokens_is_family_revoked_none():
    assert await core_refresh.is_refresh_family_revoked(None) is False


@pytest.mark.asyncio
async def test_refresh_tokens_revoke_all_for_user():
    with patch("app.core.refresh_tokens.cache_delete_pattern", new_callable=AsyncMock, return_value=3):
        count = await core_refresh.revoke_all_refresh_tokens_for_user("u1")
    assert count == 3


@pytest.mark.asyncio
async def test_refresh_tokens_list_user_refresh_sessions():
    mock_redis = AsyncMock()

    async def _scan_iter(*a, match=None, **kw):
        yield "refresh_user:u1:jti_abc"

    mock_redis.scan_iter = _scan_iter
    mock_redis.ttl = AsyncMock(return_value=3600)

    with patch("app.core.refresh_tokens.get_redis", return_value=mock_redis):
        with patch("app.core.refresh_tokens.cache_get", new_callable=AsyncMock, return_value="fam_1"):
            sessions = await core_refresh.list_user_refresh_sessions("u1")
    assert len(sessions) == 1
    assert sessions[0]["jti"] == "jti_abc"
    assert sessions[0]["ttl_seconds"] == 3600


# ── 6. CONSENT GATE ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_consent_gate_learner_id_from_path():
    uid = str(uuid.uuid4())
    req = MagicMock()
    req.path_params = {"learner_id": uid}
    result = await core_consent_gate._get_learner_id_from_request(req)
    assert str(result) == uid


@pytest.mark.asyncio
async def test_consent_gate_learner_id_from_state():
    uid = str(uuid.uuid4())
    req = MagicMock()
    req.path_params = {}
    req.state = SimpleNamespace(learner_id=uid)
    result = await core_consent_gate._get_learner_id_from_request(req)
    assert str(result) == uid


@pytest.mark.asyncio
async def test_consent_gate_learner_id_missing():
    req = MagicMock()
    req.path_params = {}
    req.state = SimpleNamespace()
    with pytest.raises(HTTPException) as exc:
        await core_consent_gate._get_learner_id_from_request(req)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_consent_gate_learner_id_invalid_uuid():
    req = MagicMock()
    req.path_params = {"learner_id": "not-a-uuid"}
    with pytest.raises(HTTPException) as exc:
        await core_consent_gate._get_learner_id_from_request(req)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_consent_gate_require_active_consent_ok():
    uid = str(uuid.uuid4())
    req = MagicMock()
    req.path_params = {"learner_id": uid}
    mock_svc = AsyncMock()
    mock_record = MagicMock()
    mock_svc.assert_active_consent = AsyncMock(return_value=mock_record)
    result = await core_consent_gate.require_active_consent(req, mock_svc)
    assert result is mock_record


@pytest.mark.asyncio
async def test_consent_gate_require_active_consent_denied():
    uid = str(uuid.uuid4())
    req = MagicMock()
    req.path_params = {"learner_id": uid}
    mock_svc = AsyncMock()
    mock_svc.assert_active_consent = AsyncMock(side_effect=PermissionError("denied"))
    with pytest.raises(HTTPException) as exc:
        await core_consent_gate.require_active_consent(req, mock_svc)
    assert exc.value.status_code == 403


# ── 7. DEPENDENCIES ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_deps_get_consent_repo():
    from app.repositories.consent_repository import ConsentRepository
    repo = await core_deps.get_consent_repo()
    assert isinstance(repo, ConsentRepository)


@pytest.mark.asyncio
async def test_deps_get_current_user_id_no_creds():
    from app.core.exceptions import AuthenticationError
    with pytest.raises(AuthenticationError):
        await core_deps.get_current_user_id(None)


@pytest.mark.asyncio
async def test_deps_get_current_user_id_valid():
    uid = str(uuid.uuid4())
    tok = core_security.create_access_token(uid, UserRole.STUDENT)
    creds = SimpleNamespace(credentials=tok)
    user_id = await core_deps.get_current_user_id(creds)
    assert str(user_id) == uid


@pytest.mark.asyncio
async def test_deps_get_current_user_id_invalid_token():
    # decode_token converts JWTError → HTTPException(401); that propagates out
    # since dependencies.get_current_user_id only catches (JWTError, ValueError)
    creds = SimpleNamespace(credentials="bad.token")
    with pytest.raises(HTTPException) as exc:
        await core_deps.get_current_user_id(creds)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_deps_get_current_guardian_id():
    uid = uuid.uuid4()
    result = await core_deps.get_current_guardian_id(uid)
    assert result == uid


@pytest.mark.asyncio
async def test_deps_require_active_consent_ok():
    learner_id = uuid.uuid4()
    mock_db = AsyncMock()
    mock_repo = AsyncMock()
    mock_repo.get_active = AsyncMock(return_value=MagicMock())
    await core_deps.require_active_consent(learner_id, mock_db, mock_repo)


@pytest.mark.asyncio
async def test_deps_require_active_consent_missing():
    from app.core.exceptions import ConsentRequiredError
    learner_id = uuid.uuid4()
    mock_db = AsyncMock()
    mock_repo = AsyncMock()
    mock_repo.get_active = AsyncMock(return_value=None)
    with patch("app.core.dependencies.consent_gate_blocks_total") as m:
        m.labels.return_value.inc = MagicMock()
        with pytest.raises(ConsentRequiredError):
            await core_deps.require_active_consent(learner_id, mock_db, mock_repo)
    m.labels.return_value.inc.assert_called_once()


@pytest.mark.asyncio
async def test_deps_get_request_id_from_contextvar():
    req = MagicMock()
    with patch("app.core.dependencies.context.get_request_id", return_value="ctx-1"):
        result = await core_deps.get_request_id(req)
    assert result == "ctx-1"


@pytest.mark.asyncio
async def test_deps_get_request_id_from_header():
    req = MagicMock()
    req.headers = {"X-Request-ID": "hdr-1"}
    with patch("app.core.dependencies.context.get_request_id", return_value=None):
        result = await core_deps.get_request_id(req)
    assert result == "hdr-1"


@pytest.mark.asyncio
async def test_deps_get_request_id_fallback():
    req = MagicMock()
    req.headers.get = MagicMock(return_value="unknown")
    with patch("app.core.dependencies.context.get_request_id", return_value=None):
        result = await core_deps.get_request_id(req)
    assert result == "unknown"


@pytest.mark.asyncio
async def test_deps_require_consent_for_current_learner_ok():
    learner_id = uuid.uuid4()
    mock_db = AsyncMock()
    mock_repo = AsyncMock()
    mock_repo.get_active = AsyncMock(return_value=MagicMock())
    mock_learner = SimpleNamespace(id=str(learner_id))
    mock_lr = AsyncMock()
    mock_lr.get_by_id = AsyncMock(return_value=mock_learner)
    current_user = {"role": "admin"}
    with patch("app.core.dependencies.LearnerRepository", return_value=mock_lr):
        with patch("app.core.dependencies.assert_can_access_learner") as ma:
            result = await core_deps.require_active_consent_for_current_learner(
                learner_id, mock_db, mock_repo, current_user
            )
    assert result == learner_id
    ma.assert_called_once()


@pytest.mark.asyncio
async def test_deps_require_consent_for_current_learner_not_found():
    learner_id = uuid.uuid4()
    mock_db = AsyncMock()
    mock_repo = AsyncMock()
    mock_lr = AsyncMock()
    mock_lr.get_by_id = AsyncMock(return_value=None)
    current_user = {"role": "admin"}
    with patch("app.core.dependencies.LearnerRepository", return_value=mock_lr):
        with pytest.raises(HTTPException) as exc:
            await core_deps.require_active_consent_for_current_learner(
                learner_id, mock_db, mock_repo, current_user
            )
    assert exc.value.status_code == 404
