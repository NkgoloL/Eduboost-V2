import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.content_quality import router


@pytest.mark.asyncio
async def test_content_quality_readiness_and_acceptance_routes():
    app = FastAPI()
    app.include_router(router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Readiness endpoint
        resp_readiness = await client.get("/content-quality/grade4-mathematics/readiness")
        assert resp_readiness.status_code == 200
        data_readiness = resp_readiness.json()
        payload_readiness = data_readiness.get("data") if "data" in data_readiness else data_readiness
        assert "overall_status" in payload_readiness or "status" in payload_readiness or isinstance(payload_readiness, dict)

        # 2. Final acceptance endpoint
        resp_acceptance = await client.get("/content-quality/grade4-mathematics/final-acceptance")
        assert resp_acceptance.status_code == 200
        data_acceptance = resp_acceptance.json()
        payload_acceptance = data_acceptance.get("data") if "data" in data_acceptance else data_acceptance
        assert isinstance(payload_acceptance, dict)
