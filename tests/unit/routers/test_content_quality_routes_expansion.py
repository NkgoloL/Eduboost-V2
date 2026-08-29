import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.content_quality import router


@pytest.mark.asyncio
async def test_content_quality_routes():
    app = FastAPI()
    app.include_router(router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp_readiness = await client.get("/content-quality/grade4-mathematics/readiness")
        assert resp_readiness.status_code == 200
        data_readiness = resp_readiness.json()
        payload = data_readiness.get("data") or data_readiness
        assert "readiness_verdict" in payload or "is_ready" in payload or "gate_status" in payload or "scope" in payload or len(payload) > 0

        resp_acceptance = await client.get("/content-quality/grade4-mathematics/final-acceptance")
        assert resp_acceptance.status_code == 200
        data_acceptance = resp_acceptance.json()
        payload_acc = data_acceptance.get("data") or data_acceptance
        assert len(payload_acc) > 0
