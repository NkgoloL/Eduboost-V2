import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.learner_content import router, get_learner_read_service
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_learner_content_items_and_lessons_routes():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "learner-usr"
    auth_ctx.roles = ["learner"]

    session = AsyncMock()
    mock_service = MagicMock()
    mock_service.get_diagnostic_items = AsyncMock(return_value=[])
    mock_service.get_lessons = AsyncMock(return_value=[])

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_learner_read_service] = lambda: mock_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Diagnostic items for scope
        resp_items = await client.get("/learner/content/scopes/scope-1/diagnostic-items?caps_ref=CAPS.MATH.G4.1")
        assert resp_items.status_code == 200

        # 2. Lessons for scope
        resp_lessons = await client.get("/learner/content/scopes/scope-1/lessons")
        assert resp_lessons.status_code == 200

        # 3. Diagnostic items by CAPS ref
        resp_caps_items = await client.get("/learner/content/scopes/scope-1/caps/CAPS.MATH.G4.1/diagnostic-items")
        assert resp_caps_items.status_code == 200

        # 4. Lessons by CAPS ref
        resp_caps_lessons = await client.get("/learner/content/scopes/scope-1/caps/CAPS.MATH.G4.1/lessons")
        assert resp_caps_lessons.status_code == 200
