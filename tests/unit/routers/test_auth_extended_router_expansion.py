import uuid
import pytest
from pydantic import ValidationError
from unittest.mock import AsyncMock, MagicMock

from app.api_v2_routers.auth_extended import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
    ProfileUpdateRequest,
    PrivacySettingsUpdate,
    _grade_to_int,
    _check_rate_limit,
)
from fastapi import HTTPException


def test_forgot_password_request_validation():
    req = ForgotPasswordRequest(email="parent@example.com")
    assert req.email == "parent@example.com"

    with pytest.raises(ValidationError):
        ForgotPasswordRequest(email="invalid-email")


def test_reset_password_request_validation():
    # Valid password
    req = ResetPasswordRequest(token="raw-tok", new_password="ValidPass123!")
    assert req.new_password == "ValidPass123!"

    # Short password
    with pytest.raises(ValidationError, match="at least 8 characters"):
        ResetPasswordRequest(token="tok", new_password="Pass1")

    # No uppercase
    with pytest.raises(ValidationError, match="one uppercase letter"):
        ResetPasswordRequest(token="tok", new_password="password123!")

    # No digit
    with pytest.raises(ValidationError, match="one digit"):
        ResetPasswordRequest(token="tok", new_password="PasswordNoDigit!")


def test_profile_update_request_validation():
    req = ProfileUpdateRequest(
        display_name="Learner One",
        grade="5",
        home_language="en",
    )
    assert req.grade == "5"
    assert req.display_name == "Learner One"

    # Empty name
    with pytest.raises(ValidationError, match="display_name cannot be blank"):
        ProfileUpdateRequest(display_name="   ", grade="5", home_language="en")

    # Invalid grade
    with pytest.raises(ValidationError, match="grade must be R or 1–12"):
        ProfileUpdateRequest(display_name="Valid", grade="13", home_language="en")

    # Invalid language
    with pytest.raises(ValidationError, match="home_language must be one of"):
        ProfileUpdateRequest(display_name="Valid", grade="5", home_language="fr")


def test_privacy_settings_update_validation():
    req = PrivacySettingsUpdate(
        analytics_enabled=True,
        ai_improvement=False,
        data_retention_days=365,
    )
    assert req.data_retention_days == 365

    # Invalid retention
    with pytest.raises(ValidationError, match="data_retention_days must be"):
        PrivacySettingsUpdate(data_retention_days=100)


def test_grade_to_int_helper():
    assert _grade_to_int("R") == 0
    assert _grade_to_int("1") == 1
    assert _grade_to_int("12") == 12


def test_check_rate_limit():
    ip = f"192.168.1.{uuid.uuid4().hex[:4]}"
    for _ in range(5):
        _check_rate_limit(ip)

    # 6th attempt should raise 429
    with pytest.raises(HTTPException) as exc_info:
        _check_rate_limit(ip)
    assert exc_info.value.status_code == 429
