import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.assessments import router
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_list_assessments_endpoint():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "user-123"

    session = AsyncMock()

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session

    with patch("app.api_v2_routers.assessments.AssessmentServiceV2") as MockService:
        mock_instance = MagicMock()
        mock_instance.with_db.return_value = mock_instance
        mock_instance.list_assessments = AsyncMock(return_value=[{"assessment_id": "asm-1", "title": "Maths G4"}])
        MockService.return_value = mock_instance

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/assessments?limit=10&offset=0")
            assert resp.status_code == 200
            data = resp.json()
            assert len(data.get("data") or data) == 1
