import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.content_factory import router, get_content_coverage_service
from app.api_v2_deps.auth import require_admin
from app.core.database import get_db


@pytest.mark.asyncio
async def test_content_factory_health_and_status():
    app = FastAPI()
    app.include_router(router)

    app.dependency_overrides[require_admin] = lambda: {"role": "admin"}
    app.dependency_overrides[get_db] = lambda: AsyncMock()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp_health = await client.get("/admin/content-factory/health")
        assert resp_health.status_code == 200
        data_health = resp_health.json()
        assert data_health["status"] == "ok"

        resp_etl = await client.get("/admin/content-factory/etl/status")
        assert resp_etl.status_code == 200
        data_etl = resp_etl.json()
        assert data_etl["status"] == "available"


@pytest.mark.asyncio
async def test_content_factory_scopes():
    app = FastAPI()
    app.include_router(router)

    app.dependency_overrides[require_admin] = lambda: {"role": "admin"}
    app.dependency_overrides[get_db] = lambda: AsyncMock()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/admin/content-factory/scopes")
        assert resp.status_code == 200
        scopes = resp.json()
        assert isinstance(scopes, list)
        assert len(scopes) > 0
