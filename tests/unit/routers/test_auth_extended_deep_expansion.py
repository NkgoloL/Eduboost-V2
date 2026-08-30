import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.api_v2_routers.auth_extended import (
    _grade_to_int,
    _current_user_id,
    _check_rate_limit,
    _reset_attempts,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ProfileUpdateRequest,
    PrivacySettingsUpdate,
    OnboardingStepUpdate,
)
from app.api_v2_deps.auth import AuthContext


def test_grade_to_int():
    assert _grade_to_int("R") == 0
    assert _grade_to_int("4") == 4
    assert _grade_to_int("12") == 12


def test_current_user_id():
    ctx = AuthContext(
        user_id="usr-123",
        role="parent",
        roles=["parent"],
        email="parent@test.za",
        token_type="access",
        raw_claims={},
        jti="jti-1",
    )
    assert _current_user_id(ctx) == "usr-123"

    dict_user = {"sub": "usr-456"}
    assert _current_user_id(dict_user) == "usr-456"

    with pytest.raises(HTTPException):
        _current_user_id({})


def test_rate_limit_exceeded():
    _reset_attempts.clear()
    ip = "192.168.1.100"
    for _ in range(5):
        _check_rate_limit(ip)

    with pytest.raises(HTTPException) as exc_info:
        _check_rate_limit(ip)
    assert exc_info.value.status_code == 429
    _reset_attempts.clear()


def test_schema_validations():
    req = ResetPasswordRequest(token="tok-123", new_password="Password123")
    assert req.token == "tok-123"

    with pytest.raises(ValueError, match="Password must contain"):
        ResetPasswordRequest(token="tok-123", new_password="weak")

    prof = ProfileUpdateRequest(display_name="Learner", grade="4", home_language="en")
    assert prof.grade == "4"

    priv = PrivacySettingsUpdate(data_retention_days=90)
    assert priv.data_retention_days == 90

    with pytest.raises(ValueError, match="data_retention_days must be"):
        PrivacySettingsUpdate(data_retention_days=45)
