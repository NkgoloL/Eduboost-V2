import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.performance_scale_cost import router


@pytest.mark.asyncio
async def test_performance_scale_cost_routes():
    app = FastAPI()
    app.include_router(router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp_readiness = await client.get("/performance-scale-cost/readiness")
        assert resp_readiness.status_code == 200
        data_readiness = resp_readiness.json()
        payload = data_readiness.get("data") or data_readiness
        assert len(payload) > 0

        resp_final = await client.get("/performance-scale-cost/final-assurance")
        assert resp_final.status_code == 200
        data_final = resp_final.json()
        payload_fin = data_final.get("data") or data_final
        assert len(payload_fin) > 0
