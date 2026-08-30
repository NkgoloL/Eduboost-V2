import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.gamification import router
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_gamification_profile_and_award_xp_404_routes():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "parent-usr"
    auth_ctx.roles = ["parent"]

    session = AsyncMock()

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session

    with patch("app.api_v2_routers.gamification.LearnerService") as MockService:
        mock_instance = MagicMock()
        mock_instance.get_learner_summary = AsyncMock(return_value=None)
        MockService.return_value = mock_instance

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Test get profile 404
            resp_prof = await client.get("/gamification/profile/lrn-nonexistent")
            assert resp_prof.status_code == 404
            assert "Learner not found" in resp_prof.json()["detail"]

            # 2. Test award xp 404
            resp_award = await client.post(
                "/gamification/award-xp",
                json={"learner_id": "lrn-nonexistent", "xp_amount": 50},
            )
            assert resp_award.status_code == 404
            assert "Learner not found" in resp_award.json()["detail"]
