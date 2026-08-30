import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.consent_renewal import router
from app.api_v2_deps.auth import require_admin


@pytest.mark.asyncio
async def test_consent_renewal_trigger_reminders_route():
    app = FastAPI()
    app.include_router(router)

    admin_ctx = MagicMock()
    admin_ctx.user_id = "00000000-0000-0000-0000-000000000001"
    admin_ctx.roles = ["admin"]
    admin_ctx.is_admin = True

    app.dependency_overrides[require_admin] = lambda: admin_ctx

    with patch("app.api_v2_routers.consent_renewal.enqueue_durable", new=AsyncMock(return_value="job-consent-remind-999")):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/admin/consent/trigger-renewal-reminders")
            assert resp.status_code == 202
            data = resp.json()
            payload = data.get("data") if "data" in data else data
            assert payload["job_id"] == "job-consent-remind-999"
            assert payload["operation"] == "consent_renewal_reminders"
            assert payload["status"] == "queued"
