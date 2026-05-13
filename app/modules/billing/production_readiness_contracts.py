"""Repository-verifiable billing, subscription, payment, and monetization contracts.

This module intentionally avoids calling a payment processor. It defines deterministic
contracts and helpers that can be unit-tested without network access while preserving
the production boundary requirements for provider selection, subscription state,
webhook verification, idempotency, pricing rules, billing audit, and cancellation
policy.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Any, Mapping


class BillingProvider(StrEnum):
    """Supported billing-provider decision values."""

    STRIPE = "stripe"
    PAYSTACK = "paystack"
    YOCO = "yoco"
    MANUAL_SPONSORSHIP = "manual_sponsorship"


class SubscriptionState(StrEnum):
    """Canonical subscription lifecycle states."""

    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    PAUSED = "paused"
    CANCELED = "canceled"
    EXPIRED = "expired"


class BillingPlan(StrEnum):
    """Canonical product-plan categories."""

    FREE = "free"
    PARENT = "parent"
    SCHOOL = "school"
    SPONSORED_LEARNER = "sponsored_learner"
    NGO_COMMUNITY = "ngo_community"


@dataclass(frozen=True)
class BillingProviderDecision:
    provider: BillingProvider
    adr_path: str
    architecture_doc_path: str
    checkout_hosted: bool
    stores_raw_card_data: bool
    webhook_signature_required: bool
    idempotency_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.adr_path.startswith("docs/adr/"):
            issues.append("billing provider decision must be documented in docs/adr/")
        if not self.architecture_doc_path.startswith("docs/billing/"):
            issues.append("billing architecture must be documented in docs/billing/")
        if self.stores_raw_card_data:
            issues.append("application must not store raw card data")
        if not self.webhook_signature_required:
            issues.append("webhook signature verification is mandatory")
        if not self.idempotency_required:
            issues.append("webhook idempotency is mandatory")
        return issues


@dataclass(frozen=True)
class PricingPolicy:
    free_tier_enabled: bool
    parent_plan_enabled: bool
    school_plan_enabled: bool
    sponsored_learner_plan_enabled: bool
    ngo_community_plan_enabled: bool
    trial_length_days: int
    payment_failure_grace_days: int
    cancellation_policy: str
    refund_policy: str
    data_access_after_cancellation_days: int
    invoices_enabled: bool
    receipts_enabled: bool
    coupons_enabled: bool
    sponsorships_enabled: bool
    admin_config_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if self.trial_length_days < 0:
            issues.append("trial length cannot be negative")
        if self.payment_failure_grace_days < 0:
            issues.append("payment failure grace period cannot be negative")
        if self.data_access_after_cancellation_days < 0:
            issues.append("data access after cancellation cannot be negative")
        if not self.cancellation_policy:
            issues.append("cancellation policy is required")
        if not self.refund_policy:
            issues.append("refund policy is required")
        if not self.invoices_enabled:
            issues.append("invoice support is required")
        if not self.receipts_enabled:
            issues.append("receipt support is required")
        return issues


ALLOWED_TRANSITIONS: Mapping[SubscriptionState | None, set[SubscriptionState]] = {
    None: {SubscriptionState.TRIAL, SubscriptionState.ACTIVE},
    SubscriptionState.TRIAL: {
        SubscriptionState.ACTIVE,
        SubscriptionState.PAST_DUE,
        SubscriptionState.CANCELED,
        SubscriptionState.EXPIRED,
    },
    SubscriptionState.ACTIVE: {
        SubscriptionState.PAST_DUE,
        SubscriptionState.PAUSED,
        SubscriptionState.CANCELED,
        SubscriptionState.EXPIRED,
    },
    SubscriptionState.PAST_DUE: {
        SubscriptionState.ACTIVE,
        SubscriptionState.CANCELED,
        SubscriptionState.EXPIRED,
    },
    SubscriptionState.PAUSED: {
        SubscriptionState.ACTIVE,
        SubscriptionState.CANCELED,
        SubscriptionState.EXPIRED,
    },
    SubscriptionState.CANCELED: set(),
    SubscriptionState.EXPIRED: set(),
}


def validate_subscription_transition(
    current: SubscriptionState | None,
    target: SubscriptionState,
) -> bool:
    """Return whether a subscription-state transition is allowed."""

    return target in ALLOWED_TRANSITIONS.get(current, set())


@dataclass(frozen=True)
class SubscriptionSnapshot:
    account_id: str
    plan: BillingPlan
    state: SubscriptionState
    provider_customer_id: str | None
    provider_subscription_id: str | None
    current_period_end_utc: datetime | None
    sponsored_by_account_id: str | None = None
    school_account_id: str | None = None

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.account_id:
            issues.append("account_id is required")
        if self.plan in {BillingPlan.PARENT, BillingPlan.SCHOOL} and not self.provider_subscription_id:
            issues.append("paid plans require provider_subscription_id")
        if self.plan == BillingPlan.SPONSORED_LEARNER and not self.sponsored_by_account_id:
            issues.append("sponsored learner plan requires sponsor account")
        if self.plan == BillingPlan.SCHOOL and not self.school_account_id:
            issues.append("school plan requires school account")
        if self.state == SubscriptionState.EXPIRED and self.current_period_end_utc is None:
            issues.append("expired subscriptions require period end")
        return issues


def _canonical_payload(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_webhook_signature(secret: str, timestamp: int, payload: Mapping[str, Any]) -> str:
    """Compute a deterministic HMAC-SHA256 webhook signature header."""

    if not secret:
        raise ValueError("webhook secret is required")
    signed_payload = f"{timestamp}.{_canonical_payload(payload)}".encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


def _parse_signature_header(header: str) -> dict[str, str]:
    """Parse a comma-separated payment webhook signature header."""

    parsed: dict[str, str] = {}
    for part in (header or "").split(","):
        key, separator, value = part.strip().partition("=")
        if separator and key:
            parsed[key] = value
    return parsed


def verify_webhook_signature(
    *,
    secret: str,
    header: str,
    payload: Mapping[str, Any],
    now_timestamp: int,
    tolerance_seconds: int = 300,
) -> bool:
    """Verify webhook signature and timestamp replay window."""

    parsed = _parse_signature_header(header)
    timestamp_value = parsed.get("t")
    signature_value = parsed.get("v1")
    if not timestamp_value or not signature_value:
        return False
    if not re.fullmatch(r"\d+", timestamp_value):
        return False
    if not re.fullmatch(r"[a-fA-F0-9]{64}", signature_value):
        return False

    timestamp = int(timestamp_value)
    if abs(now_timestamp - timestamp) > tolerance_seconds:
        return False

    expected = compute_webhook_signature(secret, timestamp, payload)
    expected_digest = expected.split("v1=", 1)[1]
    return hmac.compare_digest(expected_digest, signature_value)


@dataclass
class WebhookIdempotencyStore:
    """Minimal deterministic in-memory idempotency store for tests and contracts."""

    processed_event_ids: set[str] = field(default_factory=set)
    audit_log: list[str] = field(default_factory=list)
    dead_letter: list[str] = field(default_factory=list)

    def process(self, event_id: str, event_type: str, created_at_timestamp: int) -> str:
        if not event_id:
            raise ValueError("event_id is required")
        if event_id in self.processed_event_ids:
            self.audit_log.append(f"duplicate:{event_id}:{event_type}")
            return "duplicate"
        self.processed_event_ids.add(event_id)
        self.audit_log.append(f"processed:{event_id}:{event_type}:{created_at_timestamp}")
        return "processed"

    def mark_dead_letter(self, event_id: str, reason: str) -> None:
        self.dead_letter.append(f"{event_id}:{reason}")


@dataclass(frozen=True)
class WebhookRetryPolicy:
    max_attempts: int
    backoff_seconds: tuple[int, ...]

    def validate(self) -> list[str]:
        issues: list[str] = []
        if self.max_attempts < 1:
            issues.append("max_attempts must be at least 1")
        if not self.backoff_seconds:
            issues.append("backoff schedule is required")
        if any(value <= 0 for value in self.backoff_seconds):
            issues.append("backoff values must be positive")
        return issues


@dataclass(frozen=True)
class BillingAuditEvent:
    event_id: str
    event_type: str
    account_id: str
    provider: BillingProvider
    occurred_at_utc: datetime
    request_id: str
    idempotency_key: str
    raw_payload_retained: bool = False

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.event_id:
            issues.append("event_id is required")
        if not self.account_id:
            issues.append("account_id is required")
        if self.occurred_at_utc.tzinfo is None:
            issues.append("occurred_at_utc must be timezone-aware")
        if not self.request_id:
            issues.append("request_id is required")
        if not self.idempotency_key:
            issues.append("idempotency_key is required")
        if self.raw_payload_retained:
            issues.append("raw provider payloads must not be retained without redaction")
        return issues


DEFAULT_PROVIDER_DECISION = BillingProviderDecision(
    provider=BillingProvider.STRIPE,
    adr_path="docs/adr/ADR-009-billing-provider.md",
    architecture_doc_path="docs/billing/production_billing_provider_architecture_contract.md",
    checkout_hosted=True,
    stores_raw_card_data=False,
    webhook_signature_required=True,
    idempotency_required=True,
)

DEFAULT_PRICING_POLICY = PricingPolicy(
    free_tier_enabled=True,
    parent_plan_enabled=True,
    school_plan_enabled=True,
    sponsored_learner_plan_enabled=True,
    ngo_community_plan_enabled=True,
    trial_length_days=14,
    payment_failure_grace_days=7,
    cancellation_policy="cancel at period end with immediate learner data export access",
    refund_policy="manual review with audit record and provider reference",
    data_access_after_cancellation_days=30,
    invoices_enabled=True,
    receipts_enabled=True,
    coupons_enabled=True,
    sponsorships_enabled=True,
    admin_config_required=True,
)

DEFAULT_RETRY_POLICY = WebhookRetryPolicy(max_attempts=5, backoff_seconds=(60, 300, 900, 3600, 10800))


def default_billing_readiness_report() -> dict[str, Any]:
    """Return a deterministic repository-side billing readiness summary."""

    sample_payload = {"id": "evt_test_001", "type": "invoice.payment_succeeded"}
    timestamp = int(datetime.now(tz=timezone.utc).timestamp())
    signature = compute_webhook_signature("test-secret", timestamp, sample_payload)

    return {
        "provider_decision_issues": DEFAULT_PROVIDER_DECISION.validate(),
        "pricing_policy_issues": DEFAULT_PRICING_POLICY.validate(),
        "retry_policy_issues": DEFAULT_RETRY_POLICY.validate(),
        "subscription_states": [state.value for state in SubscriptionState],
        "billing_plans": [plan.value for plan in BillingPlan],
        "signature_verification_sample": verify_webhook_signature(
            secret="test-secret",
            header=signature,
            payload=sample_payload,
            now_timestamp=timestamp,
        ),
        "state_transition_sample": validate_subscription_transition(
            SubscriptionState.TRIAL,
            SubscriptionState.ACTIVE,
        ),
    }
