import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.auth_extended import (
    router,
    PrivacySettings,
    OnboardingState,
)
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_privacy_settings_flow():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "usr-1"
    auth_ctx.raw_claims = {"sub": "usr-1"}

    session = AsyncMock()
    mock_ps = MagicMock()
    mock_ps.to_dict.return_value = {"user_id": "usr-1", "marketing_emails": True}
    mock_ps.export_requested_at = None
    mock_ps.deletion_requested_at = None

    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = mock_ps
    session.execute.return_value = mock_res

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Get privacy
        resp_get = await client.get("/auth/privacy")
        assert resp_get.status_code == 200

        # Request export
        resp_exp = await client.post("/auth/privacy/request-export")
        assert resp_exp.status_code == 202

        # Request deletion
        resp_del = await client.post("/auth/privacy/request-deletion")
        assert resp_del.status_code == 202
