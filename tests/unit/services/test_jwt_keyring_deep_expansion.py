"""Comprehensive unit tests for JWT keyring secrets, keys, and environment detection."""
from __future__ import annotations

import os
from unittest.mock import patch
import pytest

from app.services.jwt_keyring import (
    PLACEHOLDER_JWT_SECRETS,
    JWTKey,
    JWTKeyringError,
    current_environment,
)


class TestJWTKeyringModels:
    def test_placeholder_jwt_secrets_set(self):
        assert "dev-insecure-secret-change-me" in PLACEHOLDER_JWT_SECRETS
        assert "changeme" in PLACEHOLDER_JWT_SECRETS
        assert "super-secret" in PLACEHOLDER_JWT_SECRETS

    def test_jwt_key_dataclass(self):
        key = JWTKey(
            kid="key-v1",
            secret="secure_secret_value_12345678901234567890",
            algorithm="HS256",
            status="current",
        )
        assert key.kid == "key-v1"
        assert key.algorithm == "HS256"
        assert key.status == "current"

    def test_jwt_keyring_error_type(self):
        err = JWTKeyringError("Missing signing key")
        assert isinstance(err, RuntimeError)
        assert str(err) == "Missing signing key"

    def test_current_environment_detection(self):
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=False):
            assert current_environment() == "production"

        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}, clear=False):
            assert current_environment() == "staging"
