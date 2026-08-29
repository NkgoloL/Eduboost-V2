import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.audit import router
from app.api_v2_deps.auth import require_auth_context


@pytest.mark.asyncio
async def test_audit_routes():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "auditor-usr"
    app.dependency_overrides[require_auth_context] = lambda: auth_ctx

    with patch("app.api_v2_routers.audit.AuditService") as MockService:
        mock_instance = MagicMock()
        mock_instance.get_recent_events = AsyncMock(
            return_value=[
                {
                    "event_id": "evt-001",
                    "actor_id": "usr-1",
                    "action": "login",
                    "timestamp": "2026-08-29T12:00:00Z",
                }
            ]
        )
        MockService.return_value = mock_instance

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp1 = await client.get("/audit")
            assert resp1.status_code == 200
            data1 = resp1.json()
            events1 = data1.get("data") if "data" in data1 else data1
            assert len(events1) == 1

            resp2 = await client.get("/audit/feed")
            assert resp2.status_code == 200
            data2 = resp2.json()
            events2 = data2.get("data") if "data" in data2 else data2
            assert len(events2) == 1
