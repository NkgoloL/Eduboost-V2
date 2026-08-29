import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.parents import router
from app.api_v2_deps.auth import AuthContext, require_parent_or_admin
from app.core.database import get_db


@pytest.mark.asyncio
async def test_parent_dashboard_guardian_not_found():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = AuthContext(
        user_id=str(uuid.uuid4()),
        role="parent",
        roles=["parent"],
        email="parent@family.za",
        token_type="access",
        raw_claims={"role": "parent"},
        jti=str(uuid.uuid4()),
    )

    mock_db = AsyncMock()
    mock_db.get.return_value = None  # Guardian not found

    app.dependency_overrides[require_parent_or_admin] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: mock_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/parents/dashboard")
        assert resp.status_code == 404
