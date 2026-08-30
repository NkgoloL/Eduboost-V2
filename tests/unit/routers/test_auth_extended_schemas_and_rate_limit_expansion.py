"""Comprehensive unit tests for auth extended schemas, strong password validation, and rate limiting."""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.api_v2_routers.auth_extended import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    _check_rate_limit,
    _reset_attempts,
)


class TestAuthExtendedSchemas:
    def test_forgot_password_request_valid_and_invalid(self):
        req = ForgotPasswordRequest(email="guardian@example.com")
        assert req.email == "guardian@example.com"

        with pytest.raises(Exception):
            ForgotPasswordRequest(email="not-an-email")

    def test_reset_password_strong_password_validator(self):
        # Valid strong password
        req = ResetPasswordRequest(token="token123", new_password="SecurePassword123!")
        assert req.token == "token123"

        # Too short
        with pytest.raises(ValueError, match="at least 8 characters"):
            ResetPasswordRequest(token="token123", new_password="Sh1!")

        # Missing uppercase
        with pytest.raises(ValueError, match="one uppercase letter"):
            ResetPasswordRequest(token="token123", new_password="lowercase123!")

        # Missing digit
        with pytest.raises(ValueError, match="one digit"):
            ResetPasswordRequest(token="token123", new_password="NoDigitsPassword!")


class TestAuthExtendedRateLimiting:
    def test_check_rate_limit_allows_then_blocks(self):
        ip = "192.168.100.1"
        _reset_attempts[ip].clear()

        # 5 allowed attempts
        for _ in range(5):
            _check_rate_limit(ip)

        # 6th attempt triggers 429
        with pytest.raises(HTTPException) as exc_info:
            _check_rate_limit(ip)
        assert exc_info.value.status_code == 429
        assert "Retry-After" in exc_info.value.headers
