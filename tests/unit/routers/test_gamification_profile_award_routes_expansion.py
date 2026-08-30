import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.gamification import router
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_gamification_profile_and_award_xp_success():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "00000000-0000-0000-0000-000000000001"
    auth_ctx.roles = ["parent"]

    learner_id = "00000000-0000-0000-0000-000000000002"
    mock_learner = MagicMock()
    mock_learner.id = learner_id
    mock_learner.pseudonym_id = "pseudo-123"

    mock_db = AsyncMock()
    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("app.api_v2_routers.gamification.LearnerService") as mock_lrn_svc_cls, \
         patch("app.api_v2_routers.gamification.GamificationServiceV2") as mock_gam_cls, \
         patch("app.api_v2_routers.gamification.FourthEstateService") as mock_fe_cls, \
         patch("app.api_v2_routers.gamification.require_learner_read_for_current_user"), \
         patch("app.api_v2_routers.gamification.require_learner_write_for_current_user"), \
         patch("app.api_v2_routers.gamification.require_active_consent_for_current_user", new=AsyncMock()):

        lrn_svc = MagicMock()
        lrn_svc.get_learner_summary = AsyncMock(return_value=mock_learner)
        mock_lrn_svc_cls.return_value = lrn_svc

        gam_svc = MagicMock()
        gam_svc.get_profile = AsyncMock(return_value={"learner_id": learner_id, "xp": 150, "level": 2})
        gam_svc.award_xp = AsyncMock()
        mock_gam_cls.from_session.return_value = gam_svc

        fe_svc = MagicMock()
        fe_svc.record = AsyncMock()
        mock_fe_cls.return_value = fe_svc

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Get profile
            resp_prof = await client.get(f"/gamification/profile/{learner_id}")
            assert resp_prof.status_code == 200
            data_prof = resp_prof.json()
            payload_prof = data_prof.get("data") if "data" in data_prof else data_prof
            assert payload_prof["xp"] == 150

            # 2. Award XP
            resp_award = await client.post(
                "/gamification/award-xp",
                json={
                    "learner_id": learner_id,
                    "xp_amount": 50,
                    "event_type": "lesson_completed",
                    "lesson_id": "lsn-1",
                },
            )
            assert resp_award.status_code == 200
            data_award = resp_award.json()
            payload_award = data_award.get("data") if "data" in data_award else data_award
            assert payload_award["awarded"] is True
            assert payload_award["xp_amount"] == 50
