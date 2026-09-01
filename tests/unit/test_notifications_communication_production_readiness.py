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


@pytest.mark.unit
def test_notifications_contracts_validation_error_branches() -> None:
    from datetime import time
    from app.modules.notifications.production_readiness_contracts import (
        CommunicationProviderDecision,
        DeliveryRetryPolicy,
        DeliveryStatus,
        NotificationAuditEvent,
        NotificationPolicy,
        NotificationPreference,
        NotificationTemplate,
        default_notifications_readiness_report,
    )

    # 1. CommunicationProviderDecision invalid branches
    bad_dec = CommunicationProviderDecision(
        email_provider="",
        sms_provider="",
        whatsapp_provider="",
        push_provider="",
        in_app_provider="",
        adr_path="invalid/path.md",
        architecture_doc_path="invalid/doc.md",
        provider_webhook_signature_required=False,
        provider_webhook_idempotency_required=False,
        bounce_handling_required=False,
    )
    assert len(bad_dec.validate()) == 10

    # 2. NotificationPreference delivery logic
    pref_sec = NotificationPreference(
        audience=NotificationAudience.PARENT,
        purpose=NotificationPurpose.SECURITY,
        channel=NotificationChannel.EMAIL,
        enabled=False,
        consent_required=False,
        quiet_hours_respected=False,
    )
    assert pref_sec.allows_delivery() is True

    pref_mkt_off = NotificationPreference(
        audience=NotificationAudience.PARENT,
        purpose=NotificationPurpose.MARKETING,
        channel=NotificationChannel.EMAIL,
        enabled=False,
        consent_required=True,
        quiet_hours_respected=True,
    )
    assert pref_mkt_off.allows_delivery() is False

    # 3. NotificationPolicy invalid branches
    bad_policy = NotificationPolicy(
        preferences=(),
        learner_direct_channels=(NotificationChannel.SMS, NotificationChannel.WHATSAPP),
        max_messages_per_user_per_day=-1,
        max_messages_per_user_per_hour=10,
        quiet_hours_start=time(20, 0),
        quiet_hours_end=time(7, 0),
        unsubscribe_required_for_marketing=False,
        audit_required=False,
        idempotency_required=False,
    )
    pol_issues = bad_policy.validate()
    assert "daily rate limit must be positive" in pol_issues
    assert "hourly rate limit cannot exceed daily rate limit" in pol_issues
    assert "marketing preference must be explicitly modeled" in pol_issues
    assert "marketing unsubscribe is required" in pol_issues
    assert "notification audit logging is required" in pol_issues
    assert "notification idempotency is required" in pol_issues
    assert "direct learner SMS is prohibited by default" in pol_issues
    assert "direct learner WhatsApp is prohibited by default" in pol_issues

    # 4. NotificationTemplate invalid branches
    bad_tmpl = NotificationTemplate(
        template_id="",
        version="",
        purpose=NotificationPurpose.BILLING,
        audience=NotificationAudience.LEARNER,
        channels=(),
        subject_template="",
        body_template="Hello {{unmodeled_var}}",
        locale="en-ZA",
        required_variables=(),
        allow_html=True,
        reviewed=False,
    )
    tmpl_issues = bad_tmpl.validate()
    assert "template_id is required" in tmpl_issues
    assert "template version is required" in tmpl_issues
    assert "at least one channel is required" in tmpl_issues
    assert "learner billing or marketing templates are prohibited" in tmpl_issues
    assert "template variable 'unmodeled_var' missing from required_variables" in tmpl_issues
    assert "template review is required" in tmpl_issues

    bad_sms_html = NotificationTemplate(
        template_id="sms-html",
        version="v1",
        purpose=NotificationPurpose.SUPPORT,
        audience=NotificationAudience.PARENT,
        channels=(NotificationChannel.SMS,),
        subject_template="",
        body_template="Text",
        locale="en-ZA",
        required_variables=(),
        allow_html=True,
        reviewed=True,
    )
    assert "SMS templates cannot allow HTML" in bad_sms_html.validate()

    # 5. DeliveryRetryPolicy invalid branches
    bad_retry = DeliveryRetryPolicy(max_attempts=0, backoff_seconds=(-1, 0))
    retry_issues = bad_retry.validate()
    assert "max_attempts must be at least 1" in retry_issues
    assert "backoff values must be positive" in retry_issues

    # 6. NotificationAuditEvent invalid branches
    naive_dt = datetime(2026, 1, 1, 0, 0)
    bad_evt = NotificationAuditEvent(
        event_id="",
        recipient_id="",
        audience=NotificationAudience.PARENT,
        purpose=NotificationPurpose.ACCOUNT,
        channel=NotificationChannel.EMAIL,
        delivery_status=DeliveryStatus.SENT,
        request_id="",
        idempotency_key="",
        occurred_at_utc=naive_dt,
        raw_payload_retained=True,
    )
    evt_issues = bad_evt.validate()
    assert "event_id is required" in evt_issues
    assert "recipient_id is required" in evt_issues
    assert "request_id is required" in evt_issues
    assert "idempotency_key is required" in evt_issues
    assert "occurred_at_utc must be timezone-aware" in evt_issues
    assert "raw provider payloads must not be retained without redaction" in evt_issues

    # 7. Outbox enqueue invalid & dead_letter
    outbox = NotificationOutbox()
    bad_req = NotificationRequest(
        recipient_id="",
        audience=NotificationAudience.PARENT,
        purpose=NotificationPurpose.ACCOUNT,
        channel=NotificationChannel.EMAIL,
        template_id="tmpl",
        template_version="v1",
        locale="en",
        variables={},
        request_id="r1",
        idempotency_key="k1",
    )
    with pytest.raises(ValueError, match="recipient_id is required"):
        outbox.enqueue(bad_req)

    outbox.mark_dead_letter("k1", "provider_error")
    assert len(outbox.dead_letter) == 1

    # 8. default_notifications_readiness_report
    report = default_notifications_readiness_report()
    assert report["provider_decision_issues"] == []
    assert report["first_enqueue"] == "queued"
    assert report["second_enqueue"] == "duplicate"
