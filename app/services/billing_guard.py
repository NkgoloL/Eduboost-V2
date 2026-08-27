"""Billing and Payment Authority Guard (TSR-11.16).

Enforces hard fail-closed lock on live payment processing and webhooks
until explicit commercial release authorization is granted in the register.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status


class BillingLockError(HTTPException):
    def __init__(self, detail: str = "Live payment processing is disabled (Fail-Closed)."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            headers={"X-Billing-Lock": "LOCKED_FAIL_CLOSED"},
        )


def check_live_billing_authorization(root_dir: Path | str = ".") -> bool:
    """Read true_state_remediation_register.json and check payment authorization."""
    path = Path(root_dir) / "docs/roadmap/production_readiness/true_state_remediation_register.json"
    if not path.exists():
        # Fail-closed if register is missing
        return False

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        boundaries = data.get("authority_boundaries", {})
        live_payments = boundaries.get("live_payment_processing_authorised", False)
        billing_launch = boundaries.get("billing_launch_authorised", False)
        return bool(live_payments and billing_launch)
    except Exception:
        # Fail-closed on parse error
        return False


def assert_billing_authorized(root_dir: Path | str = ".") -> None:
    """Assert payment authorization; raise HTTP 403 BillingLockError if locked."""
    if not check_live_billing_authorization(root_dir):
        raise BillingLockError(
            "Commercial Release Boundary Lock: Live payment processing and Stripe charges are "
            "strictly disabled in this environment. Set 'live_payment_processing_authorised' "
            "to true in the authority register to unlock."
        )


def sanitize_billing_webhook(payload: dict[str, Any], root_dir: Path | str = ".") -> dict[str, Any]:
    """Process or reject incoming billing webhook events."""
    assert_billing_authorized(root_dir)
    return {"status": "processed", "event_id": payload.get("id")}
