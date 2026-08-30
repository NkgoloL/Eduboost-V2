import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.diagnostics import router
from app.api_v2_deps.auth import require_auth_context
from app.core.database import get_db


@pytest.mark.asyncio
async def test_diagnostic_sessions_recovery_404():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "user-123"

    session = AsyncMock()

    app.dependency_overrides[require_auth_context] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session

    sess_id = uuid.uuid4()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Recover unknown session
        resp_rec = await client.get(f"/diagnostics/sessions/{sess_id}/recover")
        assert resp_rec.status_code == 404
        assert "No recoverable diagnostic session" in resp_rec.json()["detail"]

        # Next item unknown session
        resp_nxt = await client.get(f"/diagnostics/sessions/{sess_id}/next-item?caps_ref=4.M.1.1")
        assert resp_nxt.status_code == 404
        assert "No recoverable diagnostic session" in resp_nxt.json()["detail"]

        # Respond unknown session
        resp_resp = await client.post(
            f"/diagnostics/sessions/{sess_id}/respond",
            json={"item_id": str(uuid.uuid4()), "correct": True},
        )
        assert resp_resp.status_code == 404
        assert "No recoverable diagnostic session" in resp_resp.json()["detail"]
