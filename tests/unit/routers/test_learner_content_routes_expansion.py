import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.learner_content import router, get_learner_read_service
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_learner_content_get_scope_summary():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "user-123"

    mock_service = AsyncMock()
    mock_service.get_scope_content_summary.return_value = {
        "scope_id": "scope-123",
        "diagnostic_items_count": 5,
        "lessons_count": 10,
        "total_artifacts_count": 15,
        "last_promotion_at": None,
    }

    session = AsyncMock()

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_learner_read_service] = lambda: mock_service
    app.dependency_overrides[get_db] = lambda: session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/learner/content/scopes/scope-123/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("scope_id") == "scope-123"
        assert data.get("diagnostic_items_count") == 5
