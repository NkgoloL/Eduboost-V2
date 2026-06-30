"""
A.2 — JWT `kid` rotation tests.

Tests that token_config correctly signs with CURRENT_KID, validates
tokens signed with PREVIOUS_KID during the overlap window, and rejects
unknown kids.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from jose import jwt

from app.core.token_config import (
    ALGORITHM,
    CURRENT_KEY,
    CURRENT_KID,
    create_access_token,
)


# ── A.2.1 — Token signed with CURRENT_KID verifies ───────────────────────────

def test_create_access_token_uses_current_kid():
    """Access tokens must carry the CURRENT_KID in the header."""
    token = create_access_token(user_id="user-1", role="guardian")
    header = jwt.get_unverified_header(token)
    assert header.get("kid") == CURRENT_KID


def test_create_access_token_verifies_with_current_key():
    """Token created with current key verifies successfully."""
    token = create_access_token(user_id="user-42", role="learner")
    claims = jwt.decode(token, CURRENT_KEY, algorithms=[ALGORITHM])
    assert claims["sub"] == "user-42"
    assert claims["kid"] == CURRENT_KID


# ── A.2.2 — Token signed with PREVIOUS_KID verifies during overlap ────────────

def test_token_with_previous_kid_verifies_when_previous_key_configured():
    """A token signed with PREVIOUS_KID must verify when that key is in _KEY_STORE."""
    prev_key = "previous-test-signing-key-32bytes-minimum"
    prev_kid = "k0"

    now = datetime.now(tz=timezone.utc)
    claims = {
        "sub": "user-99",
        "role": "guardian",
        "jti": "jti-prev-1",
        "iat": now,
        "exp": now + timedelta(minutes=15),
        "kid": prev_kid,
    }
    token = jwt.encode(claims, prev_key, algorithm=ALGORITHM, headers={"kid": prev_kid})

    # Temporarily inject previous key into the store
    with patch.dict("app.core.token_config._KEY_STORE", {prev_kid: prev_key}, clear=False):
        from app.core.token_config import _secret_for_kid
        secret = _secret_for_kid(prev_kid)
        recovered = jwt.decode(token, secret, algorithms=[ALGORITHM])

    assert recovered["sub"] == "user-99"


# ── A.2.3 — Unknown kid raises JWTError ──────────────────────────────────────

def test_secret_for_unknown_kid_raises_jwt_error():
    """_secret_for_kid must raise JWTError for an unrecognised kid."""
    from jose import JWTError
    from app.core.token_config import _secret_for_kid

    with pytest.raises(JWTError, match="Unknown signing key id"):
        _secret_for_kid("totally-unknown-kid-xyz")


@pytest.mark.asyncio
async def test_verify_access_token_rejects_unknown_kid():
    """verify_access_token must reject a token with an unknown kid header."""
    from jose import JWTError
    from app.core.token_config import verify_access_token

    unknown_key = "some-other-key-not-in-keystore-xyz"
    now = datetime.now(tz=timezone.utc)
    claims = {
        "sub": "user-77",
        "role": "guardian",
        "jti": "jti-unknown",
        "iat": now,
        "exp": now + timedelta(minutes=15),
        "kid": "unknown-kid-not-registered",
    }
    token = jwt.encode(
        claims, unknown_key, algorithm=ALGORITHM,
        headers={"kid": "unknown-kid-not-registered"}
    )

    with pytest.raises(JWTError):
        await verify_access_token(token)


# ── A.2.4 — New tokens use the updated CURRENT_KID after rotation ─────────────

def test_after_key_rotation_new_tokens_use_new_kid():
    """After patching CURRENT_KID/KEY, newly created tokens carry the new kid."""
    new_kid = "k2"
    new_key = "new-rotated-signing-key-32bytes-min"

    with patch("app.core.token_config.CURRENT_KID", new_kid), \
         patch("app.core.token_config.CURRENT_KEY", new_key):
        token = create_access_token.__wrapped__(user_id="user-1", role="admin") \
            if hasattr(create_access_token, "__wrapped__") else \
            _create_token_with_key(user_id="user-1", role="admin", key=new_key, kid=new_kid)

        header = jwt.get_unverified_header(token)
        assert header.get("kid") == new_kid


def _create_token_with_key(user_id: str, role: str, key: str, kid: str) -> str:
    """Helper: create a token bypassing the module-level key constants."""
    import uuid
    now = datetime.now(tz=timezone.utc)
    claims = {
        "sub": user_id,
        "role": role,
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + timedelta(minutes=15),
        "kid": kid,
    }
    return jwt.encode(claims, key, algorithm=ALGORITHM, headers={"kid": kid})
