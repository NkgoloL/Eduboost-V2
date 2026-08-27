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
