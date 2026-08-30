import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.onboarding import router
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_onboarding_submit_routes():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "parent-usr"
    auth_ctx.roles = ["parent"]

    session = AsyncMock()
    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session

    with patch("app.api_v2_routers.onboarding.LearnerService") as MockService, \
         patch("app.api_v2_routers.onboarding.require_learner_write_for_current_user"), \
         patch("app.api_v2_routers.onboarding.require_active_consent_for_current_user", new=AsyncMock()):

        mock_instance = MagicMock()
        MockService.return_value = mock_instance

        # 1. 404 Learner not found
        mock_instance.get_learner_summary = AsyncMock(return_value=None)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp_404 = await client.post(
                "/onboarding/submit",
                json={
                    "learner_id": "lrn-404",
                    "answers": [{"question_id": 1, "answer": "visual"}],
                },
            )
            assert resp_404.status_code == 404
            assert "Learner not found" in resp_404.json()["detail"]

        # 2. Success submission
        mock_learner = MagicMock()
        mock_learner.learner_id = "lrn-123"
        mock_instance.get_learner_summary = AsyncMock(return_value=mock_learner)
        mock_instance.process_onboarding = AsyncMock(
            return_value={
                "learner_id": "lrn-123",
                "archetype": "Visual Explorer",
                "description": "Learns best with visual diagrams and maps",
                "probabilities": {"visual": 0.8, "auditory": 0.2},
            }
        )

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp_200 = await client.post(
                "/onboarding/archetype",
                json={
                    "learner_id": "lrn-123",
                    "answers": [{"question_id": 1, "answer": "visual"}],
                },
            )
            assert resp_200.status_code == 200
            data = resp_200.json()
            payload = data.get("data") if "data" in data else data
            assert payload["learner_id"] == "lrn-123"
            assert payload["archetype"] == "Visual Explorer"
