import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.controlled_beta import router


@pytest.mark.asyncio
async def test_controlled_beta_routes():
    app = FastAPI()
    app.include_router(router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp_preflight = await client.get("/controlled-beta/preflight")
        assert resp_preflight.status_code == 200
        data_preflight = resp_preflight.json()
        payload = data_preflight.get("data") or data_preflight
        assert len(payload) > 0

        resp_auth = await client.get("/controlled-beta/final-authorisation")
        assert resp_auth.status_code == 200
        data_auth = resp_auth.json()
        payload_auth = data_auth.get("data") or data_auth
        assert len(payload_auth) > 0
