"""Integration test for Live Payment Fail-Closed Lock (TSR-11.16)."""
from __future__ import annotations

import json
from pathlib import Path
import pytest
from fastapi import HTTPException

from app.services.billing_guard import (
    assert_billing_authorized,
    check_live_billing_authorization,
    sanitize_billing_webhook,
    BillingLockError,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_billing_lock_defaults_to_fail_closed():
    # Production register has live_payment_processing_authorised == False
    is_authorized = check_live_billing_authorization(REPO_ROOT)
    assert is_authorized is False

    with pytest.raises(HTTPException) as exc:
        assert_billing_authorized(REPO_ROOT)

    assert exc.value.status_code == 403
    assert "Commercial Release Boundary Lock" in exc.value.detail
    assert exc.value.headers.get("X-Billing-Lock") == "LOCKED_FAIL_CLOSED"


@pytest.mark.unit
def test_simulated_live_stripe_webhook_is_blocked():
    stripe_event = {
        "id": "evt_test_charge_succeeded_12345",
        "type": "charge.succeeded",
        "data": {"object": {"amount": 5000, "currency": "zar"}},
    }

    with pytest.raises(BillingLockError) as exc:
        sanitize_billing_webhook(stripe_event, REPO_ROOT)

    assert exc.value.status_code == 403
    assert "Live payment processing is disabled" in exc.value.detail or "Commercial Release Boundary Lock" in exc.value.detail


@pytest.mark.unit
def test_missing_or_corrupted_register_fails_closed(tmp_path: Path):
    # Empty directory with no register
    assert check_live_billing_authorization(tmp_path) is False

    # Corrupted JSON register
    reg_file = tmp_path / "docs/roadmap/production_readiness/true_state_remediation_register.json"
    reg_file.parent.mkdir(parents=True, exist_ok=True)
    reg_file.write_text("INVALID_JSON", encoding="utf-8")

    assert check_live_billing_authorization(tmp_path) is False


@pytest.mark.unit
def test_http_billing_routes_fail_closed_in_live_app():
    """Verify live HTTP endpoints return 403 fail-closed when hit via FastAPI router."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.api_v2_routers.billing import router as billing_router
    from app.api_v2_deps.auth import require_parent_or_admin, AuthContext, TokenType
    from app.models import UserRole

    app = FastAPI()
    app.include_router(billing_router, prefix="/api/v2")

    # Mock authentication to allow parent role
    parent_auth = AuthContext(
        user_id="guardian-test-uuid",
        roles=[UserRole.PARENT],
        token_type=TokenType.ACCESS,
        raw_claims={"sub": "guardian-test-uuid", "role": "parent"},
        jti="test-jti",
    )
    app.dependency_overrides[require_parent_or_admin] = lambda: parent_auth

    client = TestClient(app, raise_server_exceptions=False)

    # 1. Checkout endpoint fails closed
    resp_checkout = client.post("/api/v2/billing/checkout")
    assert resp_checkout.status_code == 403
    assert resp_checkout.headers.get("X-Billing-Lock") == "LOCKED_FAIL_CLOSED"
    assert "Commercial Release Boundary Lock" in resp_checkout.text

    # 2. Alternate create-checkout-session endpoint fails closed
    resp_create = client.post("/api/v2/billing/create-checkout-session")
    assert resp_create.status_code == 403
    assert resp_create.headers.get("X-Billing-Lock") == "LOCKED_FAIL_CLOSED"

    # 3. Webhook endpoint fails closed
    resp_webhook = client.post(
        "/api/v2/billing/webhook",
        headers={"stripe-signature": "sig_test"},
        content=b'{"id":"evt_test"}',
    )
    assert resp_webhook.status_code == 403
    assert resp_webhook.headers.get("X-Billing-Lock") == "LOCKED_FAIL_CLOSED"

