import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.system import router


@pytest.mark.asyncio
async def test_system_capabilities_and_health_routes():
    app = FastAPI()
    app.include_router(router)

    with patch("app.api_v2_routers.system.SystemServiceV2") as MockService, \
         patch("app.api_v2_routers.system.capabilities_payload") as mock_cap:

        mock_instance = MagicMock()
        mock_instance.health = AsyncMock(return_value={"status": "healthy", "service": "v2"})
        mock_instance.pillars = AsyncMock(return_value={"pillars": ["pedagogy", "privacy", "security"]})
        mock_instance.schema_status = AsyncMock(return_value={"schema": "aligned", "drift": False})
        MockService.return_value = mock_instance

        mock_cap.return_value = {"offline_mode": True, "ai_tutor": True}

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Health
            resp_h = await client.get("/system/health")
            assert resp_h.status_code == 200
            assert resp_h.json()["data"]["status"] == "healthy"

            # 2. Pillars
            resp_p = await client.get("/system/pillars")
            assert resp_p.status_code == 200
            assert "pedagogy" in resp_p.json()["data"]["pillars"]

            # 3. Schema status
            resp_s = await client.get("/system/schema-status")
            assert resp_s.status_code == 200
            assert resp_s.json()["data"]["schema"] == "aligned"

            # 4. Capabilities
            resp_c = await client.get("/system/capabilities")
            assert resp_c.status_code == 200
            assert resp_c.json()["data"]["offline_mode"] is True
