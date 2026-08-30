import pytest
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.api_v2 import app, lifespan


@pytest.mark.asyncio
async def test_api_v2_root_and_health_routes():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Root
        resp_root = await client.get("/")
        assert resp_root.status_code == 200
        assert "Ngiyabonga" in resp_root.json()["message"]

        # 2. Health
        resp_health = await client.get("/health")
        assert resp_health.status_code == 200
        assert resp_health.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_api_v2_lifespan():
    async with lifespan(app):
        assert True
