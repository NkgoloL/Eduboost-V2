"""Contract tests for billing router Stripe delegation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api_v2_deps.auth import AuthContext, TokenType, require_parent_or_admin
from app.api_v2_routers import billing
from app.core.database import get_db
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


def _client(stripe: FakeStripeService, audit: FakeFourthEstate) -> TestClient:
    app = FastAPI()
    app.include_router(billing.router, prefix="/api/v2")

    app.dependency_overrides[require_parent_or_admin] = lambda: _auth_context(PARENT)
    app.dependency_overrides[get_db] = lambda: object()

    billing.StripeService = lambda _db: stripe  # type: ignore[misc,assignment]
    billing.FourthEstateService = lambda _db: audit  # type: ignore[misc,assignment]
    return TestClient(app, raise_server_exceptions=True)


@pytest.mark.unit
def test_create_checkout_delegates_to_stripe_service():
    stripe = FakeStripeService()
    audit = FakeFourthEstate()
    client = _client(stripe, audit)

    response = client.post("/api/v2/billing/checkout")
    assert response.status_code == 200
    body = response.json().get("data", response.json())
    assert body["checkout_url"] == "https://checkout.stripe.test/session"
    assert stripe.checkout_calls[0]["guardian_id"] == PARENT["sub"]


@pytest.mark.unit
def test_stripe_webhook_records_audit_trail():
    stripe = FakeStripeService()
    audit = FakeFourthEstate()
    client = _client(stripe, audit)

    response = client.post(
        "/api/v2/billing/webhook",
        content=b'{"type":"checkout.session.completed"}',
        headers={"stripe-signature": "sig_test"},
    )
    assert response.status_code == 200
    assert stripe.webhook_calls[0]["signature"] == "sig_test"
    assert audit.records[0][0] == "STRIPE_WEBHOOK"
    assert audit.records[0][1]["event_type"] == "checkout.session.completed"
