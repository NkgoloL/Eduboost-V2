import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.parents import router
from app.api_v2_deps.auth import require_parent_or_admin
from app.core.database import get_db


@pytest.mark.asyncio
async def test_parent_trust_dashboard_forbidden():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "user-123"
    auth_ctx.is_admin = False

    session = AsyncMock()

    app.dependency_overrides[require_parent_or_admin] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/parents/other-guardian-456/dashboard")
        assert resp.status_code == 403
        assert "Not authorised" in resp.json()["detail"]
