import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.vertical_journey import router
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_vertical_journey_learner_not_found():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "user-123"

    session = AsyncMock()

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session

    with patch("app.api_v2_routers.vertical_journey.LearnerService") as MockService:
        mock_instance = MagicMock()
        mock_instance.repository.get_by_id = AsyncMock(return_value=None)
        MockService.return_value = mock_instance

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/vertical-journey/learners/lrn-nonexistent")
            assert resp.status_code == 404
            assert "Learner not found" in resp.json()["detail"]
