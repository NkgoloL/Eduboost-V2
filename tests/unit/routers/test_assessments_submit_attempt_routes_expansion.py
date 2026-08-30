import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.assessments import router
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_assessments_submit_attempt_route():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "parent-usr"
    auth_ctx.roles = ["parent"]

    session = AsyncMock()

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session

    with patch("app.api_v2_routers.assessments.require_learner_write_for_current_user"), \
         patch("app.api_v2_routers.assessments.require_active_consent_for_current_user", new=AsyncMock()), \
         patch("app.api_v2_routers.assessments.AssessmentServiceV2") as MockService:

        mock_instance = MagicMock()
        mock_instance.with_db = MagicMock(return_value=mock_instance)
        mock_instance.submit_attempt = AsyncMock(
            return_value={
                "attempt_id": "att-123",
                "assessment_id": "asm-456",
                "learner_id": "lrn-789",
                "score": 85.0,
            }
        )
        MockService.return_value = mock_instance

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "learner_id": "lrn-789",
                "responses": [
                    {
                        "item_id": "itm-1",
                        "selected_option": "B",
                        "answer": "42",
                        "metadata": {},
                    }
                ],
                "time_taken_seconds": 120,
            }
            resp = await client.post("/assessments/asm-456/attempt", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            res = data.get("data") if "data" in data else data
            assert res["attempt_id"] == "att-123"
            assert res["score"] == 85.0
