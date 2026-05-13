from __future__ import annotations

from datetime import datetime, timezone
import subprocess
import sys
from pathlib import Path

import pytest

from app.modules.notifications.production_readiness_contracts import (
    DEFAULT_COMMUNICATION_PROVIDER_DECISION,
    DEFAULT_NOTIFICATION_POLICY,
    DEFAULT_RETRY_POLICY,
    DEFAULT_TEMPLATES,
    NotificationAudience,
    NotificationChannel,
    NotificationOutbox,
    NotificationPurpose,
    NotificationRequest,
    build_notification_idempotency_key,
    redact_contact_details,
)
from scripts.check_notifications_communication_production_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_notifications_communication_production_readiness_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_notifications_communication_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_notifications_communication_production_readiness.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Notifications communication production readiness check" in result.stdout


@pytest.mark.unit
def test_provider_policy_retry_and_templates_validate() -> None:
    assert DEFAULT_COMMUNICATION_PROVIDER_DECISION.validate() == []
    assert DEFAULT_NOTIFICATION_POLICY.validate() == []
    assert DEFAULT_RETRY_POLICY.validate() == []
    assert [issue for template in DEFAULT_TEMPLATES for issue in template.validate()] == []


@pytest.mark.unit
def test_notification_outbox_is_idempotent() -> None:
    key = build_notification_idempotency_key(
        recipient_id="parent-001",
        purpose=NotificationPurpose.PROGRESS_SUMMARY,
        template_id="parent_weekly_progress",
        template_version="v1",
        scheduled_bucket="2026-W01",
    )
    request = NotificationRequest(
        recipient_id="parent-001",
        audience=NotificationAudience.PARENT,
        purpose=NotificationPurpose.PROGRESS_SUMMARY,
        channel=NotificationChannel.EMAIL,
        template_id="parent_weekly_progress",
        template_version="v1",
        locale="en-ZA",
        variables={"completed_lessons": "4"},
        request_id="req-001",
        idempotency_key=key,
        scheduled_at_utc=datetime.now(tz=timezone.utc),
    )
    outbox = NotificationOutbox()

    assert outbox.enqueue(request) == "queued"
    assert outbox.enqueue(request) == "duplicate"
    assert len(outbox.processed_keys) == 1


@pytest.mark.unit
def test_learner_billing_sms_and_whatsapp_are_rejected() -> None:
    key = build_notification_idempotency_key(
        recipient_id="learner-001",
        purpose=NotificationPurpose.BILLING,
        template_id="billing_notice",
        template_version="v1",
        scheduled_bucket="now",
    )
    request = NotificationRequest(
        recipient_id="learner-001",
        audience=NotificationAudience.LEARNER,
        purpose=NotificationPurpose.BILLING,
        channel=NotificationChannel.SMS,
        template_id="billing_notice",
        template_version="v1",
        locale="en-ZA",
        variables={},
        request_id="req-002",
        idempotency_key=key,
    )

    issues = request.validate()
    assert "learner billing and marketing notifications are prohibited" in issues
    assert "direct learner SMS or WhatsApp delivery is prohibited by default" in issues


@pytest.mark.unit
def test_contact_redaction_removes_email_and_phone() -> None:
    redacted = redact_contact_details("Reach me at user@example.com or +27 82 123 4567")
    assert "user@example.com" not in redacted
    assert "+27 82 123 4567" not in redacted
    assert "[redacted-email]" in redacted
    assert "[redacted-phone]" in redacted


@pytest.mark.unit
def test_makefile_exposes_notifications_target() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "notifications-communication-production-readiness-check:" in text
    assert "scripts/check_notifications_communication_production_readiness.py" in text
