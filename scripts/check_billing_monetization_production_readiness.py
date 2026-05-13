#!/usr/bin/env python3
"""Validate production-readiness item 09: billing, subscriptions, payments, and monetization."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import importlib.util
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "app/modules/billing/__init__.py",
    "app/modules/billing/production_readiness_contracts.py",
    "docs/adr/ADR-009-billing-provider.md",
    "docs/billing/production_billing_provider_architecture_contract.md",
    "docs/billing/subscription_state_machine_contract.md",
    "docs/billing/webhook_security_idempotency_contract.md",
    "docs/billing/pricing_product_rules_contract.md",
    "docs/billing/billing_ux_audit_contract.md",
    "docs/backlog/production_readiness/09_billing_subscriptions_payments_and_monetization.md",
    "tests/unit/test_billing_monetization_production_readiness.py",
)

CONTENT_REQUIREMENTS = {
    "app/modules/billing/production_readiness_contracts.py": (
        "class BillingProvider",
        "class SubscriptionState",
        "class BillingPlan",
        "BillingProviderDecision",
        "PricingPolicy",
        "WebhookIdempotencyStore",
        "WebhookRetryPolicy",
        "BillingAuditEvent",
        "compute_webhook_signature",
        "verify_webhook_signature",
        "_parse_signature_header",
        "validate_subscription_transition",
        "DEFAULT_PROVIDER_DECISION",
        "DEFAULT_PRICING_POLICY",
        "default_billing_readiness_report",
        "application must not store raw card data",
    ),
    "docs/adr/ADR-009-billing-provider.md": (
        "Billing Provider Decision",
        "hosted-checkout billing provider integration pattern",
        "application must not store raw card data",
        "Webhook signature verification is mandatory",
        "Webhook idempotency is mandatory",
    ),
    "docs/billing/production_billing_provider_architecture_contract.md": (
        "Production Billing Provider Architecture Contract",
        "hosted checkout is required for paid card flows",
        "application must not store raw card data",
        "webhook signature verification is required",
        "webhook idempotency is required",
        "manual sponsorship flow is separated from paid subscription flow",
    ),
    "docs/billing/subscription_state_machine_contract.md": (
        "Subscription State Machine Contract",
        "trial",
        "active",
        "past_due",
        "paused",
        "canceled",
        "expired",
        "canceled is terminal",
        "expired is terminal",
        "sponsored learner plan must reference a sponsor account",
        "school plan must reference a school account",
    ),
    "docs/billing/webhook_security_idempotency_contract.md": (
        "Webhook Security and Idempotency Contract",
        "webhook signature verification",
        "webhook timestamp replay protection",
        "webhook idempotency by provider event ID",
        "duplicate event is idempotent",
        "out-of-order event is handled without corrupting subscription state",
        "dead-letter event records reason",
        "retry policy has bounded attempts",
    ),
    "docs/billing/pricing_product_rules_contract.md": (
        "Pricing and Product Rules Contract",
        "free tier is defined",
        "parent plan is defined",
        "school plan is defined",
        "sponsored learner plan is defined",
        "NGO/community plan is defined",
        "trial length is defined",
        "payment failure policy is defined",
        "cancellation policy is defined",
        "refund policy is defined",
        "data-access-after-cancellation policy is defined",
        "pricing admin config is required before launch",
    ),
    "docs/billing/billing_ux_audit_contract.md": (
        "Billing UX and Audit Contract",
        "parent billing page",
        "subscription status display",
        "invoice history",
        "cancel subscription flow",
        "payment failure state",
        "billing lifecycle tests",
        "billing audit tests",
        "billing metrics evidence",
        "churn metrics evidence",
    ),
    "docs/backlog/production_readiness/09_billing_subscriptions_payments_and_monetization.md": (
        "9.6 Repository-side implementation evidence",
        "docs/billing/production_billing_provider_architecture_contract.md",
        "scripts/check_billing_monetization_production_readiness.py",
        "make billing-monetization-production-readiness-check",
    ),
    "Makefile": (
        "billing-monetization-production-readiness-check:",
        "scripts/check_billing_monetization_production_readiness.py",
    ),
}


@dataclass(frozen=True)
class BillingReadinessResult:
    target: str
    ok: bool
    detail: str


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _load_contract_module():
    path = REPO_ROOT / "app/modules/billing/production_readiness_contracts.py"
    spec = importlib.util.spec_from_file_location("billing_contracts_for_check", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load billing contracts module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_checks() -> list[BillingReadinessResult]:
    results: list[BillingReadinessResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(
            BillingReadinessResult(
                rel_path,
                path.exists(),
                "file present" if path.exists() else "file missing",
            )
        )

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        text = _read(rel_path)
        for snippet in snippets:
            results.append(
                BillingReadinessResult(
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    try:
        module = _load_contract_module()
        report = module.default_billing_readiness_report()
        results.extend(
            [
                BillingReadinessResult(
                    "billing_contracts",
                    report["provider_decision_issues"] == [],
                    "provider decision validates",
                ),
                BillingReadinessResult(
                    "billing_contracts",
                    report["pricing_policy_issues"] == [],
                    "pricing policy validates",
                ),
                BillingReadinessResult(
                    "billing_contracts",
                    report["retry_policy_issues"] == [],
                    "retry policy validates",
                ),
                BillingReadinessResult(
                    "billing_contracts",
                    report["signature_verification_sample"] is True,
                    "webhook signature verification sample passes",
                ),
                BillingReadinessResult(
                    "billing_contracts",
                    report["state_transition_sample"] is True,
                    "subscription state transition sample passes",
                ),
                BillingReadinessResult(
                    "billing_contracts",
                    set(report["subscription_states"]) == {"trial", "active", "past_due", "paused", "canceled", "expired"},
                    "all canonical subscription states present",
                ),
            ]
        )
    except Exception as exc:  # pragma: no cover - deliberately defensive CLI output
        results.append(BillingReadinessResult("billing_contracts", False, f"contract import/check failed: {exc}"))

    return results


def main() -> int:
    results = run_checks()
    print("Billing monetization production readiness check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
