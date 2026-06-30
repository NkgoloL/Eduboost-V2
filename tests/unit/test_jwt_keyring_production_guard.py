from __future__ import annotations

import importlib

import pytest


def _reload(monkeypatch, **env):
    for key in ["JWT_KEYRING", "JWT_CURRENT_KID", "JWT_ALGORITHM", "JWT_SECRET", "JWT_SECRET_KEY", "SECRET_KEY", "ACCESS_TOKEN_SECRET_KEY", "ENVIRONMENT", "APP_ENV", "ENV"]:
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    import app.services.jwt_keyring as keyring
    return importlib.reload(keyring)


def test_jwt_secret_only_configuration_wins_over_dev_fallback(monkeypatch):
    keyring = _reload(monkeypatch, JWT_SECRET="configured-jwt-secret", ENVIRONMENT="development")
    assert keyring.current_jwt_signing_key() == "configured-jwt-secret"
    assert keyring.current_jwt_key().kid == "legacy"


def test_legacy_jwt_secret_key_still_supported(monkeypatch):
    keyring = _reload(monkeypatch, JWT_SECRET_KEY="legacy-jwt-secret", ENVIRONMENT="development")
    assert keyring.current_jwt_signing_key() == "legacy-jwt-secret"


def test_keyring_current_previous_encode_decode(monkeypatch):
    keyring = _reload(
        monkeypatch,
        JWT_KEYRING=(
            '[{"kid":"current","secret":"current-secret","algorithm":"HS256","status":"current"},'
            '{"kid":"previous","secret":"previous-secret","algorithm":"HS256","status":"previous"}]'
        ),
        ENVIRONMENT="development",
    )
    token = keyring.encode_jwt_with_keyring({"sub": "user-1"})
    decoded = keyring.decode_jwt_with_keyring(token)
    assert decoded["sub"] == "user-1"


def test_production_rejects_placeholder_fallback(monkeypatch):
    keyring = _reload(monkeypatch, ENVIRONMENT="production")
    with pytest.raises(keyring.JWTKeyringError):
        keyring.validate_jwt_keyring_environment()


def test_production_accepts_configured_jwt_secret(monkeypatch):
    keyring = _reload(monkeypatch, ENVIRONMENT="production", JWT_SECRET="configured-production-secret")
    keyring.validate_jwt_keyring_environment()
    assert keyring.current_jwt_signing_key() == "configured-production-secret"


def test_app_api_v2_imports_with_safe_secret(monkeypatch):
    _reload(monkeypatch, ENVIRONMENT="development", JWT_SECRET="safe-import-secret-32chars-padded!!")
    import app.api_v2
    assert hasattr(app.api_v2, "app")
