"""Contract tests for billing router Stripe delegation."""
from __future__ import annotations

from dataclasses import dataclass, field
import asyncio
from typing import Any

import pytest

from app.api_v2_deps.auth import AuthContext, TokenType
from app.api_v2_routers import billing
from app.models import UserRole


PARENT = {"sub": "guardian-1", "role": "parent"}


def _auth_context(payload: dict[str, Any]) -> AuthContext:
    return AuthContext(
        user_id=payload["sub"],
        roles=[UserRole(payload["role"])],
        token_type=TokenType.ACCESS,
        raw_claims=payload,
        jti="test-jti",
    )


@dataclass
class FakeStripeService:
    checkout_calls: list[dict[str, Any]] = field(default_factory=list)
    webhook_calls: list[dict[str, Any]] = field(default_factory=list)

    async def create_checkout_session(self, guardian_id: str, email_plaintext: str) -> str:
        self.checkout_calls.append({"guardian_id": guardian_id, "email_plaintext": email_plaintext})
        return "https://checkout.stripe.test/session"

    async def handle_webhook(self, payload: bytes, signature: str) -> dict:
        self.webhook_calls.append({"payload_len": len(payload), "signature": signature})
        return {"event_type": "checkout.session.completed", "status": "processed"}


@dataclass
class FakeFourthEstate:
    records: list[tuple[str, dict]] = field(default_factory=list)

    async def record(self, event_type: str, payload: dict) -> None:
        self.records.append((event_type, payload))


class DummyRequest:
    def __init__(self, payload: bytes):
        self._payload = payload

    async def body(self) -> bytes:
        return self._payload


@pytest.mark.unit
def test_create_checkout_blocked_when_billing_locked():
    """Verify POST /billing/checkout fails closed with 403 when commercial authorization is False."""
    from app.services.billing_guard import BillingLockError

    async def run() -> None:
        with pytest.raises(BillingLockError) as exc:
            await billing.create_checkout(db=object(), current_user=_auth_context(PARENT))
        assert exc.value.status_code == 403
        assert "Commercial Release Boundary Lock" in exc.value.detail

    asyncio.run(run())


@pytest.mark.unit
def test_stripe_webhook_blocked_when_billing_locked():
    """Verify POST /billing/webhook fails closed with 403 when commercial authorization is False."""
    from app.services.billing_guard import BillingLockError

    async def run() -> None:
        with pytest.raises(BillingLockError) as exc:
            await billing.stripe_webhook(
                request=DummyRequest(b'{"type":"checkout.session.completed"}'),
                db=object(),
                stripe_signature="sig_test",
                audit=FakeFourthEstate(),
            )
        assert exc.value.status_code == 403
        assert "Commercial Release Boundary Lock" in exc.value.detail

    asyncio.run(run())


@pytest.mark.unit
def test_create_checkout_delegates_to_stripe_service_when_authorized(monkeypatch: pytest.MonkeyPatch):
    """Verify checkout session creation succeeds when explicitly authorized."""
    monkeypatch.setattr("app.api_v2_routers.billing.assert_billing_authorized", lambda: None)
    stripe = FakeStripeService()
    billing.StripeService = lambda _db: stripe  # type: ignore[misc,assignment]

    async def run() -> None:
        result = await billing.create_checkout(db=object(), current_user=_auth_context(PARENT))
        assert result.checkout_url == "https://checkout.stripe.test/session"

    asyncio.run(run())
    assert stripe.checkout_calls[0]["guardian_id"] == PARENT["sub"]


@pytest.mark.unit
def test_stripe_webhook_records_audit_trail_when_authorized(monkeypatch: pytest.MonkeyPatch):
    """Verify webhook handling succeeds and audits when explicitly authorized."""
    monkeypatch.setattr("app.api_v2_routers.billing.assert_billing_authorized", lambda: None)
    stripe = FakeStripeService()
    audit = FakeFourthEstate()
    billing.StripeService = lambda _db: stripe  # type: ignore[misc,assignment]

    async def run() -> None:
        result = await billing.stripe_webhook(
            request=DummyRequest(b'{"type":"checkout.session.completed"}'),
            db=object(),
            stripe_signature="sig_test",
            audit=audit,
        )
        assert result["status"] == "processed"

    asyncio.run(run())
    assert stripe.webhook_calls[0]["signature"] == "sig_test"
    assert audit.records[0][0] == "STRIPE_WEBHOOK"
    assert audit.records[0][1]["event_type"] == "checkout.session.completed"

