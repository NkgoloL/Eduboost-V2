from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.core.stripe_client import StripeService


@pytest.mark.asyncio
async def test_invoice_payment_failed_downgrades_to_free(monkeypatch):
    db = object()
    service = StripeService.__new__(StripeService)
    service._db = db
    service._event_repo = SimpleNamespace()

    async def fake_get_by_customer(customer_id: str):
        return SimpleNamespace(id="guardian-1") if customer_id == "cus_123" else None

    service._guardian_repo = SimpleNamespace(get_by_stripe_customer_id=fake_get_by_customer)

    calls: list[str] = []

    class FakeSubscriptionService:
        def __init__(self, _db):
            pass

        async def downgrade_to_free(self, guardian_id: str) -> None:
            calls.append(guardian_id)

    monkeypatch.setattr("app.core.stripe_client.SubscriptionService", FakeSubscriptionService)

    await StripeService._handle_invoice_payment_failed(service, {"subscription": "sub_123", "customer": "cus_123"})

    assert calls == ["guardian-1"]
