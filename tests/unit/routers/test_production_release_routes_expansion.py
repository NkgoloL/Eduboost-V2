import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.production_release import router


@pytest.mark.asyncio
async def test_production_release_routes():
    app = FastAPI()
    app.include_router(router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp_preflight = await client.get("/production-release/preflight")
        assert resp_preflight.status_code == 200
        data_preflight = resp_preflight.json()
        payload = data_preflight.get("data") or data_preflight
        assert len(payload) > 0

        resp_baseline = await client.get("/production-release/true-state-runtime-baseline")
        assert resp_baseline.status_code == 200
        data_baseline = resp_baseline.json()
        payload_base = data_baseline.get("data") or data_baseline
        assert len(payload_base) > 0
