from __future__ import annotations

import importlib

import pytest
from app.core.jwt_compat import jwt


RESET_ENV_KEYS = [
    "JWT_KEYRING",
    "JWT_CURRENT_KID",
    "JWT_ALGORITHM",
    "JWT_SECRET",
    "JWT_SECRET_KEY",
    "SECRET_KEY",
    "ACCESS_TOKEN_SECRET_KEY",
    "ENVIRONMENT",
    "APP_ENV",
    "ENV",
]


def _reload(monkeypatch: pytest.MonkeyPatch, **env: str):
    for key in RESET_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    import app.services.jwt_keyring as keyring

    return importlib.reload(keyring)


def test_parse_semicolon_keyring_normalizes_status_and_defaults(monkeypatch: pytest.MonkeyPatch):
    keyring = _reload(monkeypatch)

    keys = keyring.parse_jwt_keyring("current:secret-a::primary;old:secret-b:HS512:legacy")

    assert [key.kid for key in keys] == ["current", "old"]
    assert keys[0].algorithm == "HS256"
    assert keys[0].status == "current"
    assert keys[1].algorithm == "HS512"
    assert keys[1].status == "previous"


def test_parse_invalid_json_raises(monkeypatch: pytest.MonkeyPatch):
    keyring = _reload(monkeypatch)

    with pytest.raises(keyring.JWTKeyringError, match="Invalid JWT_KEYRING JSON"):
        keyring.parse_jwt_keyring("[{not-json}")


def test_parse_entry_validation_errors(monkeypatch: pytest.MonkeyPatch):
    keyring = _reload(monkeypatch)

    with pytest.raises(keyring.JWTKeyringError, match="Invalid JWT key-ring entry"):
        keyring.parse_jwt_keyring("invalid-entry")

    with pytest.raises(keyring.JWTKeyringError, match="missing kid"):
        keyring.parse_jwt_keyring("[{\"secret\":\"abc\",\"status\":\"current\"}]")

    with pytest.raises(keyring.JWTKeyringError, match="missing secret"):
        keyring.parse_jwt_keyring("[{\"kid\":\"x\",\"status\":\"current\"}]")


def test_parse_requires_non_empty_and_current_key(monkeypatch: pytest.MonkeyPatch):
    keyring = _reload(monkeypatch)

    with pytest.raises(keyring.JWTKeyringError, match="cannot be empty"):
        keyring.parse_jwt_keyring(" ; ")

    with pytest.raises(keyring.JWTKeyringError, match="must contain one current key"):
        keyring.parse_jwt_keyring("old:secret-a:HS256:previous")


def test_current_jwt_algorithm_and_headers(monkeypatch: pytest.MonkeyPatch):
    keyring = _reload(monkeypatch, JWT_CURRENT_KID="kid-a", JWT_SECRET="secret-a")

    assert keyring.current_jwt_algorithm(default="HS512") == "HS256"
    assert keyring.current_jwt_headers() == {"kid": "kid-a"}


def test_decode_keyring_tries_other_keys_and_raises_last_error(monkeypatch: pytest.MonkeyPatch):
    keyring = _reload(
        monkeypatch,
        ENVIRONMENT="development",
        JWT_KEYRING=(
            "[{\"kid\":\"current\",\"secret\":\"current-secret\",\"algorithm\":\"HS256\",\"status\":\"current\"},"
            "{\"kid\":\"previous\",\"secret\":\"previous-secret\",\"algorithm\":\"HS256\",\"status\":\"previous\"}]"
        ),
    )

    token = jwt.encode({"sub": "u-1"}, "previous-secret", algorithm="HS256", headers={"kid": "unknown"})
    decoded = keyring.decode_jwt_with_keyring(token)
    assert decoded["sub"] == "u-1"

    bad_token = jwt.encode({"sub": "u-2"}, "wrong-secret", algorithm="HS256", headers={"kid": "current"})
    with pytest.raises(Exception):
        keyring.decode_jwt_with_keyring(bad_token)


def test_parse_semicolon_entry_rejects_blank_kid_or_secret(monkeypatch: pytest.MonkeyPatch):
    keyring = _reload(monkeypatch)

    with pytest.raises(keyring.JWTKeyringError, match="Invalid JWT key-ring entry"):
        keyring.parse_jwt_keyring(":secret-a:HS256:current")

    with pytest.raises(keyring.JWTKeyringError, match="Invalid JWT key-ring entry"):
        keyring.parse_jwt_keyring("kid-a::HS256:current")


def test_current_jwt_key_raises_without_current_key(monkeypatch: pytest.MonkeyPatch):
    keyring = _reload(monkeypatch)

    with pytest.raises(keyring.JWTKeyringError, match="No current JWT key configured"):
        keyring.current_jwt_key([keyring.JWTKey(kid="old", secret="s", status="previous")])


def test_is_placeholder_secret_handles_none(monkeypatch: pytest.MonkeyPatch):
    keyring = _reload(monkeypatch)

    assert keyring.is_placeholder_secret(None) is True
    assert keyring.is_placeholder_secret("change_me_later") is True
    assert keyring.is_placeholder_secret("placeholder_key") is True
    assert keyring.is_placeholder_secret("super-strong-production-key-12345678") is False


def test_production_environment_and_keyring_validation(monkeypatch: pytest.MonkeyPatch):
    # 1. Environment checks
    keyring = _reload(monkeypatch, ENVIRONMENT="production")
    assert keyring.is_production_environment() is True

    keyring = _reload(monkeypatch, ENVIRONMENT="live")
    assert keyring.is_production_environment() is True

    keyring = _reload(monkeypatch, ENVIRONMENT="development")
    assert keyring.is_production_environment() is False

    # 2. Production with placeholder secret fails closed
    keyring = _reload(
        monkeypatch,
        ENVIRONMENT="production",
        JWT_KEYRING="kid-1:dev-insecure-secret-change-me:HS256:current",
    )
    with pytest.raises(keyring.JWTKeyringError, match="Production environment cannot use placeholder JWT secrets"):
        keyring.validate_jwt_keyring_environment()

    # 3. Production with strong key passes
    keyring = _reload(
        monkeypatch,
        ENVIRONMENT="production",
        JWT_KEYRING="kid-prod:super-secure-production-secret-999:HS256:current",
    )
    keyring.validate_jwt_keyring_environment()


def test_encode_and_decode_roundtrip(monkeypatch: pytest.MonkeyPatch):
    keyring = _reload(
        monkeypatch,
        ENVIRONMENT="test",
        JWT_KEYRING="kid-1:secure-key-1:HS256:current",
    )
    token = keyring.encode_jwt_with_keyring({"sub": "user-42", "role": "guardian"})
    payload = keyring.decode_jwt_with_keyring(token)
    assert payload["sub"] == "user-42"
    assert payload["role"] == "guardian"


def test_parse_json_non_list_raises(monkeypatch: pytest.MonkeyPatch):
    keyring = _reload(monkeypatch)

    with pytest.raises(keyring.JWTKeyringError, match="JSON must be a list"):
        keyring.parse_jwt_keyring("{\"kid\": \"k1\", \"secret\": \"s1\"}")
