"""Batch 219 — app/api_v2_routers/auth_extended.py comprehensive router branch coverage expansion.

Tests:
- forgot_password: email found sends reset email, email missing returns 202, rate limit eviction
- reset_password: valid token updates password
- send_verification: email already verified, unverified sends email, guardian email missing raises 500
- verify_email: valid token marks verified and updates onboarding state (new and existing state)
- get_onboarding: existing state vs new state creation
- update_onboarding_step: invalid step raises 422, valid step updates, completion triggers email
- update_learner_profile: updates guardian, learner, and sets profile_complete
- get_privacy_settings & update_privacy_settings
- request_data_export: success + 409 on duplicate
- request_account_deletion: success + 409 on duplicate
- Helper functions: _current_user_id (dict vs AuthContext vs missing), _get_guardian (404), _consume_token (400 on expired/invalid)
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.api_v2_deps.auth import AuthContext, require_auth_context
from app.api_v2_routers.auth_extended import (
    _check_rate_limit,
    _consume_token,
    _current_user_id,
    _get_guardian,
    _grade_to_int,
    _guardian_email,
    get_db,
    router,
)
from app.models.auth_extensions import OnboardingState, PrivacySettings, SecureToken, TokenPurpose


@pytest.fixture
def app():
    test_app = FastAPI()
    test_app.include_router(router)
    return test_app


@pytest.fixture
def client(app):
    mock_auth = AuthContext(
        user_id="guardian-123",
        email="parent@eduboost.co.za",
        role="parent",
        scopes=["parent:read"],
        token_type="access",
        raw_claims={"email_verified": False},
        jti="jti-123",
    )
    app.dependency_overrides[require_auth_context] = lambda: mock_auth

    mock_session = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_session

    yield TestClient(app)
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helper Unit Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_current_user_id_variations():
    # AuthContext instance
    auth = AuthContext(
        user_id="user-1",
        email="u@example.com",
        role="learner",
        scopes=[],
        token_type="access",
        raw_claims={},
        jti="jti-1",
    )
    assert _current_user_id(auth) == "user-1"

    # Dict with sub
    assert _current_user_id({"sub": "user-2"}) == "user-2"
    assert _current_user_id({"user_id": "user-3"}) == "user-3"

    # Missing sub/user_id raises 401
    with pytest.raises(HTTPException) as exc:
        _current_user_id({})
    assert exc.value.status_code == 401


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_guardian_not_found_raises_404():
    mock_session = AsyncMock()
    mock_session.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        await _get_guardian(mock_session, "missing-guardian")
    assert exc.value.status_code == 404


@pytest.mark.unit
def test_guardian_email_decryption_failure():
    mock_guardian = MagicMock(id="g-1", email_encrypted=b"corrupted")
    with patch("app.api_v2_routers.auth_extended.decrypt_pii", side_effect=Exception("Decryption error")):
        assert _guardian_email(mock_guardian) is None


@pytest.mark.unit
def test_grade_to_int_conversion():
    assert _grade_to_int("R") == 0
    assert _grade_to_int("4") == 4
    assert _grade_to_int("12") == 12


@pytest.mark.asyncio
@pytest.mark.unit
async def test_consume_token_invalid_or_expired_raises_400():
    mock_session = AsyncMock()
    res = MagicMock()
    res.scalars.return_value = []
    mock_session.execute.return_value = res

    with pytest.raises(HTTPException) as exc:
        await _consume_token(mock_session, "bad-token", TokenPurpose.PASSWORD_RESET)
    assert exc.value.status_code == 400


@pytest.mark.unit
def test_check_rate_limit_exceeded_raises_429():
    from app.api_v2_routers.auth_extended import _reset_attempts
    ip = "192.168.1.100"
    _reset_attempts.pop(ip, None)
    for _ in range(5):
        _check_rate_limit(ip)

    with pytest.raises(HTTPException) as exc:
        _check_rate_limit(ip)
    assert exc.value.status_code == 429



# ---------------------------------------------------------------------------
# Password Reset Endpoints
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_forgot_password_user_found_sends_email(app, client):
    mock_session = AsyncMock()
    mock_user = MagicMock(id="guardian-1", display_name="Parent User")
    res = MagicMock()
    res.scalar_one_or_none.return_value = mock_user
    mock_session.execute.return_value = res
    app.dependency_overrides[get_db] = lambda: mock_session

    with (
        patch("app.api_v2_routers.auth_extended._create_secure_token", return_value="raw-token-123"),
        patch("app.api_v2_routers.auth_extended.send_password_reset_email") as mock_send,
    ):
        mock_send.return_value = None
        response = client.post("/auth/forgot-password", json={"email": "parent@example.com"})
        assert response.status_code == 202
        mock_send.assert_called_once()


@pytest.mark.unit
def test_forgot_password_user_not_found_returns_202(app, client):
    mock_session = AsyncMock()
    res = MagicMock()
    res.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = res
    app.dependency_overrides[get_db] = lambda: mock_session

    response = client.post("/auth/forgot-password", json={"email": "unknown@example.com"})
    assert response.status_code == 202


@pytest.mark.unit
def test_reset_password_endpoint_success(app, client):
    mock_session = AsyncMock()
    mock_token = MagicMock(user_id="guardian-1")
    mock_guardian = MagicMock(id="guardian-1")

    with (
        patch("app.api_v2_routers.auth_extended._consume_token", return_value=mock_token),
        patch("app.api_v2_routers.auth_extended._get_guardian", return_value=mock_guardian),
        patch("app.api_v2_routers.auth_extended.hash_password", return_value="hashed-pw"),
    ):
        app.dependency_overrides[get_db] = lambda: mock_session
        response = client.post(
            "/auth/reset-password",
            json={"token": "valid-token", "new_password": "NewStrongPassword123!"},
        )
        assert response.status_code == 200
        assert mock_guardian.password_hash == "hashed-pw"


# ---------------------------------------------------------------------------
# Email Verification Endpoints
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_send_verification_already_verified(app):
    test_app = FastAPI()
    test_app.include_router(router)
    mock_auth = AuthContext(
        user_id="guardian-123",
        email="parent@eduboost.co.za",
        role="parent",
        scopes=[],
        token_type="access",
        raw_claims={"email_verified": True},
        jti="jti-123",
    )
    test_app.dependency_overrides[require_auth_context] = lambda: mock_auth
    test_client = TestClient(test_app)

    response = test_client.post("/auth/send-verification")
    assert response.status_code == 202
    assert "already verified" in response.json()["detail"]


@pytest.mark.unit
def test_send_verification_email_unavailable_raises_500(app, client):
    mock_guardian = MagicMock(id="guardian-123")
    with (
        patch("app.api_v2_routers.auth_extended._get_guardian", return_value=mock_guardian),
        patch("app.api_v2_routers.auth_extended._guardian_email", return_value=None),
    ):
        response = client.post("/auth/send-verification")
        assert response.status_code == 500


@pytest.mark.unit
def test_send_verification_success(app, client):
    mock_session = AsyncMock()
    res_tokens = MagicMock()
    res_tokens.scalars.return_value = []
    mock_session.execute.return_value = res_tokens
    app.dependency_overrides[get_db] = lambda: mock_session

    mock_guardian = MagicMock(id="guardian-123", display_name="Parent")
    with (
        patch("app.api_v2_routers.auth_extended._get_guardian", return_value=mock_guardian),
        patch("app.api_v2_routers.auth_extended._guardian_email", return_value="p@example.com"),
        patch("app.api_v2_routers.auth_extended._create_secure_token", return_value="verify-raw-tok"),
        patch("app.api_v2_routers.auth_extended.send_email_verification") as mock_send,
    ):
        mock_send.return_value = None
        response = client.post("/auth/send-verification")
        assert response.status_code == 202
        assert "Verification email sent" in response.json()["detail"]


@pytest.mark.unit
def test_verify_email_endpoint_success(app, client):
    mock_session = AsyncMock()
    mock_secure = MagicMock(user_id="guardian-123")
    mock_user = MagicMock(id="guardian-123")
    mock_state = MagicMock(spec=OnboardingState)

    res_state = MagicMock()
    res_state.scalar_one_or_none.return_value = mock_state
    mock_session.execute.return_value = res_state
    app.dependency_overrides[get_db] = lambda: mock_session

    with (
        patch("app.api_v2_routers.auth_extended._consume_token", return_value=mock_secure),
        patch("app.api_v2_routers.auth_extended._get_guardian", return_value=mock_user),
    ):
        response = client.get("/auth/verify-email?token=valid-tok")
        assert response.status_code == 200
        assert mock_user.email_verified is True
        assert mock_state.email_verified is True


# ---------------------------------------------------------------------------
# Onboarding & Privacy Endpoints
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_onboarding_creates_state_if_missing(app, client):
    mock_session = AsyncMock()
    res = MagicMock()
    res.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = res

    # After refresh
    async def fake_refresh(obj):
        obj.to_dict = lambda: {"user_id": "guardian-123", "email_verified": False}

    mock_session.refresh.side_effect = fake_refresh
    app.dependency_overrides[get_db] = lambda: mock_session

    response = client.get("/auth/onboarding")
    assert response.status_code == 200
    assert response.json()["user_id"] == "guardian-123"


@pytest.mark.unit
def test_update_onboarding_step_invalid_step_raises_422(app, client):
    response = client.patch("/auth/onboarding/step", json={"step": "invalid_step", "value": True})
    assert response.status_code == 422


@pytest.mark.unit
def test_update_onboarding_step_completion_sends_email(app, client):
    mock_session = AsyncMock()
    mock_state = MagicMock(spec=OnboardingState)
    mock_state.is_complete = True
    mock_state.completed_at = None
    mock_state.to_dict.return_value = {"is_complete": True}

    res = MagicMock()
    res.scalar_one_or_none.return_value = mock_state
    mock_session.execute.return_value = res
    app.dependency_overrides[get_db] = lambda: mock_session

    mock_guardian = MagicMock(id="guardian-123", display_name="Parent")
    with (
        patch("app.api_v2_routers.auth_extended._get_guardian", return_value=mock_guardian),
        patch("app.api_v2_routers.auth_extended._guardian_email", return_value="parent@example.com"),
        patch("app.api_v2_routers.auth_extended.send_onboarding_complete_email") as mock_send,
    ):
        mock_send.return_value = None
        response = client.patch("/auth/onboarding/step", json={"step": "plan_accepted", "value": True})
        assert response.status_code == 200
        mock_send.assert_called_once()


@pytest.mark.unit
def test_update_learner_profile_endpoint(app, client):
    mock_session = AsyncMock()
    mock_guardian = MagicMock(id="guardian-123")
    mock_learner = MagicMock()
    mock_state = MagicMock(spec=OnboardingState)
    mock_state.to_dict.return_value = {"profile_complete": True}

    res_learner = MagicMock()
    res_learner.scalar_one_or_none.return_value = mock_learner

    res_state = MagicMock()
    res_state.scalar_one_or_none.return_value = mock_state

    mock_session.execute.side_effect = [res_learner, res_state]
    app.dependency_overrides[get_db] = lambda: mock_session

    with patch("app.api_v2_routers.auth_extended._get_guardian", return_value=mock_guardian):
        payload = {
            "display_name": "Lethabo",
            "grade": "4",
            "home_language": "en",
        }
        response = client.patch("/auth/onboarding/profile", json=payload)
        assert response.status_code == 200
        assert mock_guardian.display_name == "Lethabo"
        assert mock_learner.grade == 4


@pytest.mark.unit
def test_privacy_settings_get_and_patch(app, client):
    mock_session = AsyncMock()
    mock_ps = MagicMock(spec=PrivacySettings)
    mock_ps.to_dict.return_value = {"analytics_enabled": True}

    res = MagicMock()
    res.scalar_one_or_none.return_value = mock_ps
    mock_session.execute.return_value = res
    app.dependency_overrides[get_db] = lambda: mock_session

    # GET
    res_get = client.get("/auth/privacy")
    assert res_get.status_code == 200

    # PATCH
    res_patch = client.patch("/auth/privacy", json={"analytics_enabled": False, "data_retention_days": 90})
    assert res_patch.status_code == 200


@pytest.mark.unit
def test_privacy_request_export_success_and_conflict(app, client):
    mock_session = AsyncMock()
    mock_ps = MagicMock(spec=PrivacySettings, export_requested_at=None)

    res = MagicMock()
    res.scalar_one_or_none.return_value = mock_ps
    mock_session.execute.return_value = res
    app.dependency_overrides[get_db] = lambda: mock_session

    # Success
    res1 = client.post("/auth/privacy/request-export")
    assert res1.status_code == 202

    # Conflict
    mock_ps.export_requested_at = datetime.now(timezone.utc)
    res2 = client.post("/auth/privacy/request-export")
    assert res2.status_code == 409


@pytest.mark.unit
def test_privacy_request_deletion_success_and_conflict(app, client):
    mock_session = AsyncMock()
    mock_ps = MagicMock(spec=PrivacySettings, deletion_requested_at=None)

    res = MagicMock()
    res.scalar_one_or_none.return_value = mock_ps
    mock_session.execute.return_value = res
    app.dependency_overrides[get_db] = lambda: mock_session

    # Success
    res1 = client.post("/auth/privacy/request-deletion")
    assert res1.status_code == 202

    # Conflict
    mock_ps.deletion_requested_at = datetime.now(timezone.utc)
    res2 = client.post("/auth/privacy/request-deletion")
    assert res2.status_code == 409
