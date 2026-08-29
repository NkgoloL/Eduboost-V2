import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.billing import router
from app.api_v2_deps.auth import require_parent_or_admin
from app.core.database import get_db
from app.core import providers


@pytest.mark.asyncio
async def test_billing_checkout_endpoint():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "user-123"

    session = AsyncMock()

    app.dependency_overrides[require_parent_or_admin] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: session

    with patch("app.api_v2_routers.billing.StripeService") as MockService:
        mock_instance = AsyncMock()
        mock_instance.create_checkout_session.return_value = "https://stripe.com/test-checkout"
        MockService.return_value = mock_instance

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/billing/checkout")
            assert resp.status_code == 200
            data = resp.json()
            assert (data.get("data") or data).get("checkout_url") == "https://stripe.com/test-checkout"


@pytest.mark.asyncio
async def test_billing_webhook_endpoint():
    app = FastAPI()
    app.include_router(router)

    session = AsyncMock()
    mock_audit = AsyncMock()

    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[providers.get_audit_service] = lambda: mock_audit

    with patch("app.api_v2_routers.billing.StripeService") as MockService:
        mock_instance = AsyncMock()
        mock_instance.handle_webhook.return_value = {"received": True, "event": "invoice.paid"}
        MockService.return_value = mock_instance

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/billing/webhook",
                content=b'{"id": "evt_123"}',
                headers={"stripe-signature": "sig-123"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert (data.get("data") or data).get("received") is True
