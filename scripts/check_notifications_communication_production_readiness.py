#!/usr/bin/env python3
"""Validate production-readiness item 10: notifications and communication."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.modules.notifications.production_readiness_contracts import default_notifications_readiness_report


REQUIRED_FILES = (
    "app/modules/notifications/__init__.py",
    "app/modules/notifications/production_readiness_contracts.py",
    "docs/adr/ADR-010-notifications-communication-provider.md",
    "docs/notifications/production_notifications_architecture_contract.md",
    "docs/notifications/communication_consent_preferences_contract.md",
    "docs/notifications/notification_template_governance_contract.md",
    "docs/notifications/notification_delivery_reliability_contract.md",
    "docs/notifications/notification_audit_observability_contract.md",
    "docs/backlog/production_readiness/10_notifications_and_communication.md",
    "tests/unit/test_notifications_communication_production_readiness.py",
)

CONTENT_REQUIREMENTS = {
    "app/modules/notifications/production_readiness_contracts.py": (
        "class NotificationChannel",
        "class NotificationAudience",
        "class NotificationPurpose",
        "class DeliveryStatus",
        "CommunicationProviderDecision",
        "NotificationPreference",
        "NotificationPolicy",
        "NotificationTemplate",
        "NotificationRequest",
        "NotificationOutbox",
        "DeliveryRetryPolicy",
        "NotificationAuditEvent",
        "redact_contact_details",
        "build_notification_idempotency_key",
        "default_notifications_readiness_report",
        "direct learner SMS is prohibited by default",
        "direct learner WhatsApp is prohibited by default",
    ),
    "docs/adr/ADR-010-notifications-communication-provider.md": (
        "Notifications and Communication Provider Decision",
        "provider-neutral notification adapters",
        "provider webhook signature verification is required",
        "provider webhook idempotency is required",
        "bounce and complaint handling is required",
        "unsubscribe and preference handling is required",
    ),
    "docs/notifications/production_notifications_architecture_contract.md": (
        "Production Notifications Architecture Contract",
        "provider-neutral notification adapter",
        "database outbox pattern",
        "request ID propagation",
        "idempotency key per notification request",
        "retry and dead-letter handling",
        "suppression list enforcement",
        "audit logging for lifecycle events",
    ),
    "docs/notifications/communication_consent_preferences_contract.md": (
        "Communication Consent and Preferences Contract",
        "per-channel preference tracking",
        "per-purpose preference tracking",
        "marketing unsubscribe requirement",
        "learner-safe communication defaults",
        "direct learner SMS is prohibited by default",
        "learner billing notifications are prohibited",
    ),
    "docs/notifications/notification_template_governance_contract.md": (
        "Notification Template Governance Contract",
        "template ID",
        "template version",
        "required variable list",
        "human review status",
        "learner-safety review",
        "PII leakage review",
        "SMS HTML is rejected",
    ),
    "docs/notifications/notification_delivery_reliability_contract.md": (
        "Notification Delivery Reliability Contract",
        "idempotent notification enqueue",
        "outbox processing",
        "bounded retry policy",
        "dead-letter queue",
        "duplicate delivery suppression",
        "delivery status reconciliation",
        "queued",
        "dead_lettered",
    ),
    "docs/notifications/notification_audit_observability_contract.md": (
        "Notification Audit and Observability Contract",
        "event ID",
        "recipient ID",
        "delivery status",
        "request ID",
        "idempotency key",
        "redacted metadata only",
        "delivery failure spike alert",
        "notification backlog alert",
    ),
    "docs/backlog/production_readiness/10_notifications_and_communication.md": (
        "10.6 Repository-side implementation evidence",
        "docs/notifications/production_notifications_architecture_contract.md",
        "scripts/check_notifications_communication_production_readiness.py",
        "make notifications-communication-production-readiness-check",
    ),
    "Makefile": (
        "notifications-communication-production-readiness-check:",
        "scripts/check_notifications_communication_production_readiness.py",
    ),
}


@dataclass(frozen=True)
class NotificationsReadinessResult:
    target: str
    ok: bool
    detail: str


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def run_checks() -> list[NotificationsReadinessResult]:
    results: list[NotificationsReadinessResult] = []

    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(
            NotificationsReadinessResult(
                rel_path,
                path.exists(),
                "file present" if path.exists() else "file missing",
            )
        )

    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        text = _read(rel_path)
        for snippet in snippets:
            results.append(
                NotificationsReadinessResult(
                    rel_path,
                    snippet in text,
                    f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )

    try:
        report = default_notifications_readiness_report()
        results.extend(
            [
                NotificationsReadinessResult(
                    "notifications_contracts",
                    report["provider_decision_issues"] == [],
                    "provider decision validates",
                ),
                NotificationsReadinessResult(
                    "notifications_contracts",
                    report["policy_issues"] == [],
                    "notification policy validates",
                ),
                NotificationsReadinessResult(
                    "notifications_contracts",
                    report["retry_policy_issues"] == [],
                    "retry policy validates",
                ),
                NotificationsReadinessResult(
                    "notifications_contracts",
                    report["template_issues"] == [],
                    "template governance validates",
                ),
                NotificationsReadinessResult(
                    "notifications_contracts",
                    report["request_issues"] == [],
                    "sample notification request validates",
                ),
                NotificationsReadinessResult(
                    "notifications_contracts",
                    report["first_enqueue"] == "queued" and report["second_enqueue"] == "duplicate",
                    "outbox idempotency sample passes",
                ),
                NotificationsReadinessResult(
                    "notifications_contracts",
                    "[redacted-email]" in str(report["redaction_sample"]) and "[redacted-phone]" in str(report["redaction_sample"]),
                    "contact detail redaction sample passes",
                ),
                NotificationsReadinessResult(
                    "notifications_contracts",
                    {"email", "sms", "whatsapp", "push", "in_app"}.issubset(set(report["channels"])),
                    "all canonical channels present",
                ),
            ]
        )
    except Exception as exc:  # pragma: no cover - defensive CLI output
        results.append(NotificationsReadinessResult("notifications_contracts", False, f"contract check failed: {exc}"))

    return results


def main() -> int:
    results = run_checks()
    print("Notifications communication production readiness check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
