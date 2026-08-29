import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.lessons import router, get_lesson_service
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_complete_lesson_not_found():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "user-123"

    mock_service = AsyncMock()
    mock_service.get_lesson_by_id.return_value = None

    session = AsyncMock()

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_lesson_service] = lambda: mock_service
    app.dependency_overrides[get_db] = lambda: session

    with patch("app.api_v2_routers.lessons.require_lesson_write_access_for_current_user", new=AsyncMock()):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/lessons/lsn-1/complete")
            assert resp.status_code == 404
            assert "Lesson not found" in resp.json()["detail"]
