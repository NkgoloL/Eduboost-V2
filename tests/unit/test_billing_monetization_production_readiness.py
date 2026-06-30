from __future__ import annotations

from datetime import datetime, timezone
import subprocess
import sys
from pathlib import Path

import pytest

from app.modules.billing.production_readiness_contracts import (
    DEFAULT_PRICING_POLICY,
    DEFAULT_PROVIDER_DECISION,
    DEFAULT_RETRY_POLICY,
    SubscriptionState,
    WebhookIdempotencyStore,
    compute_webhook_signature,
    validate_subscription_transition,
    verify_webhook_signature,
)
from scripts.check_billing_monetization_production_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_billing_monetization_production_readiness_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_billing_monetization_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_billing_monetization_production_readiness.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Billing monetization production readiness check" in result.stdout


@pytest.mark.unit
def test_billing_provider_pricing_and_retry_contracts_validate() -> None:
    assert DEFAULT_PROVIDER_DECISION.validate() == []
    assert DEFAULT_PRICING_POLICY.validate() == []
    assert DEFAULT_RETRY_POLICY.validate() == []


@pytest.mark.unit
def test_webhook_signature_valid_invalid_and_replay_cases() -> None:
    payload = {"id": "evt_123", "type": "invoice.payment_succeeded"}
    now = int(datetime.now(tz=timezone.utc).timestamp())
    header = compute_webhook_signature("secret", now, payload)

    assert verify_webhook_signature(secret="secret", header=header, payload=payload, now_timestamp=now)
    assert not verify_webhook_signature(secret="wrong", header=header, payload=payload, now_timestamp=now)
    assert not verify_webhook_signature(secret="secret", header=header, payload=payload, now_timestamp=now + 999)


@pytest.mark.unit
def test_webhook_idempotency_duplicate_and_dead_letter() -> None:
    store = WebhookIdempotencyStore()

    assert store.process("evt_1", "invoice.created", 1) == "processed"
    assert store.process("evt_1", "invoice.created", 1) == "duplicate"

    store.mark_dead_letter("evt_2", "out_of_order")
    assert "processed:evt_1:invoice.created:1" in store.audit_log
    assert "duplicate:evt_1:invoice.created" in store.audit_log
    assert store.dead_letter == ["evt_2:out_of_order"]


@pytest.mark.unit
def test_subscription_state_machine_allows_expected_transitions() -> None:
    assert validate_subscription_transition(None, SubscriptionState.TRIAL)
    assert validate_subscription_transition(SubscriptionState.TRIAL, SubscriptionState.ACTIVE)
    assert validate_subscription_transition(SubscriptionState.ACTIVE, SubscriptionState.PAST_DUE)
    assert validate_subscription_transition(SubscriptionState.PAST_DUE, SubscriptionState.ACTIVE)
    assert not validate_subscription_transition(SubscriptionState.CANCELED, SubscriptionState.ACTIVE)
    assert not validate_subscription_transition(SubscriptionState.EXPIRED, SubscriptionState.ACTIVE)


@pytest.mark.unit
def test_makefile_exposes_billing_monetization_target() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "billing-monetization-production-readiness-check:" in text
    assert "scripts/check_billing_monetization_production_readiness.py" in text
