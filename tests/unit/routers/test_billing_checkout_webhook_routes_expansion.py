import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api_v2_routers.billing import router
from app.api_v2_deps.auth import require_parent_or_admin
from app.core.database import get_db
from app.core import providers


@pytest.mark.asyncio
async def test_billing_create_checkout_and_webhook():
    app = FastAPI()
    app.include_router(router)

    auth_ctx = MagicMock()
    auth_ctx.user_id = "00000000-0000-0000-0000-000000000001"
    auth_ctx.roles = ["parent"]

    mock_db = AsyncMock()
    mock_audit = MagicMock()
    mock_audit.record = AsyncMock()

    app.dependency_overrides[require_parent_or_admin] = lambda: auth_ctx
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[providers.get_audit_service] = lambda: mock_audit

    with patch("app.api_v2_routers.billing.StripeService") as mock_stripe_cls:
        stripe_inst = MagicMock()
        stripe_inst.create_checkout_session = AsyncMock(return_value="https://checkout.stripe.com/c/pay_test123")
        stripe_inst.handle_webhook = AsyncMock(return_value={"status": "received", "event_type": "checkout.session.completed"})
        mock_stripe_cls.return_value = stripe_inst

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Create checkout session
            resp_chk = await client.post("/billing/checkout")
            assert resp_chk.status_code == 200
            data_chk = resp_chk.json()
            payload_chk = data_chk.get("data") if "data" in data_chk else data_chk
            assert payload_chk["checkout_url"] == "https://checkout.stripe.com/c/pay_test123"

            # 2. Process Stripe webhook
            resp_wh = await client.post(
                "/billing/webhook",
                content=b'{"id": "evt_123"}',
                headers={"stripe-signature": "t=123,v1=sig_abc"},
            )
            assert resp_wh.status_code == 200
            data_wh = resp_wh.json()
            payload_wh = data_wh.get("data") if "data" in data_wh else data_wh
            assert payload_wh["status"] == "received"
