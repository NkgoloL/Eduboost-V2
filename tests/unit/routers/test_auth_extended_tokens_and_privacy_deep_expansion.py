import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import HTTPException

from app.api_v2_routers.auth_extended import (
    TokenPurpose,
    _create_secure_token,
    _consume_token,
    _invalidate_existing_tokens,
    get_privacy_settings,
    update_privacy_settings,
    request_data_export,
    request_account_deletion,
    update_onboarding_step,
    update_learner_profile,
    verify_email,
    ProfileUpdateRequest,
    OnboardingStepUpdate,
    PrivacySettingsUpdate,
)
from app.models.auth_extensions import (
    OnboardingState,
    PrivacySettings,
    SecureToken,
)
from app.api_v2_deps.auth import AuthContext, TokenType


@pytest.mark.asyncio
async def test_secure_tokens_lifecycle():
    session = AsyncMock()
    user_id = str(uuid.uuid4())

    with patch("app.api_v2_routers.auth_extended.pwd_ctx.hash", return_value="hashed_token_val"), \
         patch("app.api_v2_routers.auth_extended.pwd_ctx.verify", side_effect=lambda raw, hashed: hashed == "hashed_token_val"):
        # 1. Create secure token
        raw_token = await _create_secure_token(
            session=session,
            user_id=user_id,
            purpose=TokenPurpose.PASSWORD_RESET,
            ttl_seconds=1800,
        )
        assert isinstance(raw_token, str)
        assert len(raw_token) > 20
        session.add.assert_called_once()
        session.flush.assert_awaited_once()

        # 2. Invalidate prior tokens
        token_obj = MagicMock(spec=SecureToken)
        token_obj.used_at = None
        mock_res = MagicMock()
        mock_res.scalars.return_value = [token_obj]
        session.execute.return_value = mock_res

        await _invalidate_existing_tokens(session, user_id, TokenPurpose.PASSWORD_RESET)
        assert token_obj.used_at is not None

        # 3. Consume token success
        valid_token = MagicMock(spec=SecureToken, token_hash="hashed_token_val", used_at=None)
        mock_consume_res = MagicMock()
        mock_consume_res.scalars.return_value = [valid_token]
        session.execute.return_value = mock_consume_res

        consumed = await _consume_token(session, raw_token, TokenPurpose.PASSWORD_RESET)
        assert consumed == valid_token
        assert valid_token.used_at is not None

        # 4. Consume token failure raises 400
        mock_consume_res.scalars.return_value = []
        with pytest.raises(HTTPException) as exc:
            await _consume_token(session, "invalid_raw_token", TokenPurpose.PASSWORD_RESET)
        assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_privacy_settings_endpoints_when_missing():
    session = AsyncMock()
    now = datetime.now(timezone.utc)
    async def mock_refresh(ps_inst):
        ps_inst.created_at = now
        ps_inst.updated_at = now
    session.refresh.side_effect = mock_refresh

    user_id = str(uuid.uuid4())
    auth_ctx = AuthContext(
        user_id=user_id,
        token_type=TokenType.ACCESS,
        jti="test-jti",
        raw_claims={"sub": user_id},
    )

    # 1. get_privacy_settings creates default row
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = None
    session.execute.return_value = mock_res

    ps_dict = await get_privacy_settings(current_user=auth_ctx, session=session)
    assert "analytics_enabled" in ps_dict
    assert session.add.called
    assert session.commit.awaited


    # 2. update_privacy_settings creates default row if missing
    mock_res.scalar_one_or_none.return_value = None
    session.add.reset_mock()
    update_payload = PrivacySettingsUpdate(analytics_enabled=False)
    updated_dict = await update_privacy_settings(
        body=update_payload,
        current_user=auth_ctx,
        session=session,
    )
    assert updated_dict["analytics_enabled"] is False
    assert session.add.called

    # 3. request_data_export creates row if missing and succeeds
    mock_res.scalar_one_or_none.return_value = None
    session.add.reset_mock()
    export_res = await request_data_export(current_user=auth_ctx, session=session)
    assert "Data export requested" in export_res["detail"]
    assert session.add.called

    # 4. request_account_deletion creates row if missing and succeeds
    mock_res.scalar_one_or_none.return_value = None
    session.add.reset_mock()
    deletion_res = await request_account_deletion(current_user=auth_ctx, session=session)
    assert "Deletion request received" in deletion_res["detail"]
    assert session.add.called


@pytest.mark.asyncio
async def test_onboarding_and_email_verify_edge_branches():
    session = AsyncMock()
    user_id = str(uuid.uuid4())
    auth_ctx = AuthContext(
        user_id=user_id,
        token_type=TokenType.ACCESS,
        jti="test-jti",
        raw_claims={"sub": user_id},
    )

    # 1. update_onboarding_step when state is None & state completes
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = None
    session.execute.return_value = mock_res

    guardian_user = MagicMock(display_name="Guardian Name", email="guardian@example.com")
    with patch("app.api_v2_routers.auth_extended._get_guardian", AsyncMock(return_value=guardian_user)), \
         patch("app.api_v2_routers.auth_extended.send_onboarding_complete_email", AsyncMock()):
        step_update = OnboardingStepUpdate(step="diagnostic_done", value=True)
        res_step = await update_onboarding_step(
            body=step_update,
            current_user=auth_ctx,
            session=session,
        )
        assert res_step["diagnostic_done"] is True

    # 2. update_learner_profile when learner exists and state is None
    mock_learner = MagicMock()
    mock_res_learner = MagicMock()
    mock_res_learner.scalar_one_or_none.return_value = mock_learner
    mock_res_state = MagicMock()
    mock_res_state.scalar_one_or_none.return_value = None
    session.execute.side_effect = [mock_res_learner, mock_res_state]

    profile_payload = ProfileUpdateRequest(
        display_name="New Name",
        grade="4",
        home_language="en",
    )
    mock_user = MagicMock(id=user_id)
    with patch("app.api_v2_routers.auth_extended._get_guardian", AsyncMock(return_value=mock_user)):
        prof_res = await update_learner_profile(
            body=profile_payload,
            current_user=auth_ctx,
            session=session,
        )
        assert prof_res["detail"] == "Profile saved."
        assert mock_learner.display_name == "New Name"

    # 3. verify_email when state is None
    token_record = MagicMock(user_id=user_id)
    mock_user_verified = MagicMock(id=user_id, email_verified=False)
    mock_user_res = MagicMock()
    mock_user_res.scalar_one_or_none.return_value = mock_user_verified
    mock_state_res = MagicMock()
    mock_state_res.scalar_one_or_none.return_value = None
    session.execute.side_effect = [mock_user_res, mock_state_res]

    with patch("app.api_v2_routers.auth_extended._consume_token", AsyncMock(return_value=token_record)), \
         patch("app.api_v2_routers.auth_extended._get_guardian", AsyncMock(return_value=mock_user_verified)):
        verify_res = await verify_email(
            token="dummy-verify-token",
            session=session,
        )
        assert verify_res["detail"] == "Email verified successfully."
