import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.consent_renewal import router
from app.api_v2_deps.auth import require_admin


@pytest.mark.asyncio
async def test_trigger_renewal_reminders_endpoint():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "admin-123"

    app.dependency_overrides[require_admin] = lambda: auth_ctx

    with patch("app.api_v2_routers.consent_renewal.enqueue_durable", new=AsyncMock(return_value="job-renewal-1")):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/admin/consent/trigger-renewal-reminders")
            assert resp.status_code == 202
            data = resp.json()
            assert (data.get("data") or data).get("job_id") == "job-renewal-1"
            assert (data.get("data") or data).get("operation") == "consent_renewal_reminders"
            assert (data.get("data") or data).get("status") == "queued"
