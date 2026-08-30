import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.commercial_launch import router


@pytest.mark.asyncio
async def test_commercial_launch_routes():
    app = FastAPI()
    app.include_router(router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp_readiness = await client.get("/commercial-launch/readiness")
        assert resp_readiness.status_code == 200
        data_readiness = resp_readiness.json()
        payload = data_readiness.get("data") or data_readiness
        assert len(payload) > 0

        resp_remediation = await client.get("/commercial-launch/runtime-audit-remediation")
        assert resp_remediation.status_code == 200
        data_remediation = resp_remediation.json()
        payload_rem = data_remediation.get("data") or data_remediation
        assert len(payload_rem) > 0
