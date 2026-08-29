import pytest
from app.api_v2_routers.auth_extended import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ProfileUpdateRequest,
    PrivacySettingsUpdate,
    _grade_to_int,
    VALID_ONBOARDING_STEPS,
)


def test_auth_extended_models_and_validators():
    req = ForgotPasswordRequest(email="user@example.com")
    assert req.email == "user@example.com"

    reset_req = ResetPasswordRequest(token="token123", new_password="Password123!")
    assert reset_req.token == "token123"

    with pytest.raises(ValueError, match="Password must contain"):
        ResetPasswordRequest(token="t", new_password="weak")

    profile_req = ProfileUpdateRequest(
        display_name="John Doe",
        grade="5",
        home_language="en",
    )
    assert profile_req.display_name == "John Doe"

    privacy_req = PrivacySettingsUpdate(data_retention_days=365)
    assert privacy_req.data_retention_days == 365

    with pytest.raises(ValueError, match="data_retention_days must be"):
        PrivacySettingsUpdate(data_retention_days=10)


def test_grade_conversion_and_onboarding_steps():
    assert _grade_to_int("R") == 0
    assert _grade_to_int("10") == 10
    assert "email_verified" in VALID_ONBOARDING_STEPS
    assert "diagnostic_done" in VALID_ONBOARDING_STEPS
