from __future__ import annotations

import importlib

import pytest
from jose import jwt


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
