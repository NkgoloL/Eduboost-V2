"""Repository-verifiable notification and communication production-readiness contracts.

The contracts in this module are deterministic and provider-neutral. They do not send
email, SMS, WhatsApp, push, or in-app messages. They define the production boundaries
needed for channel routing, consent, templates, rate limits, audit logging,
idempotency, retries, quiet hours, and learner-safe communication handling.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timezone
from enum import StrEnum
import hashlib
import re
from typing import Mapping


class NotificationChannel(StrEnum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationAudience(StrEnum):
    LEARNER = "learner"
    PARENT = "parent"
    TEACHER = "teacher"
    ADMIN = "admin"
    SCHOOL = "school"


class NotificationPurpose(StrEnum):
    SECURITY = "security"
    ACCOUNT = "account"
    LEARNING_REMINDER = "learning_reminder"
    PROGRESS_SUMMARY = "progress_summary"
    BILLING = "billing"
    SUPPORT = "support"
    MARKETING = "marketing"
    INCIDENT = "incident"


class DeliveryStatus(StrEnum):
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    SUPPRESSED = "suppressed"
    DEAD_LETTERED = "dead_lettered"


NON_OPTIONAL_PURPOSES = {
    NotificationPurpose.SECURITY,
    NotificationPurpose.ACCOUNT,
    NotificationPurpose.INCIDENT,
}


LEARNER_PROHIBITED_PURPOSES = {
    NotificationPurpose.BILLING,
    NotificationPurpose.MARKETING,
}


@dataclass(frozen=True)
class CommunicationProviderDecision:
    email_provider: str
    sms_provider: str
    whatsapp_provider: str
    push_provider: str
    in_app_provider: str
    adr_path: str
    architecture_doc_path: str
    provider_webhook_signature_required: bool
    provider_webhook_idempotency_required: bool
    bounce_handling_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.adr_path.startswith("docs/adr/"):
            issues.append("communication provider decision must be documented in docs/adr/")
        if not self.architecture_doc_path.startswith("docs/notifications/"):
            issues.append("notification architecture must be documented in docs/notifications/")
        for name, provider in {
            "email_provider": self.email_provider,
            "sms_provider": self.sms_provider,
            "whatsapp_provider": self.whatsapp_provider,
            "push_provider": self.push_provider,
            "in_app_provider": self.in_app_provider,
        }.items():
            if not provider:
                issues.append(f"{name} is required")
        if not self.provider_webhook_signature_required:
            issues.append("provider webhook signature verification is required")
        if not self.provider_webhook_idempotency_required:
            issues.append("provider webhook idempotency is required")
        if not self.bounce_handling_required:
            issues.append("bounce and complaint handling is required")
        return issues


@dataclass(frozen=True)
class NotificationPreference:
    audience: NotificationAudience
    purpose: NotificationPurpose
    channel: NotificationChannel
    enabled: bool
    consent_required: bool
    quiet_hours_respected: bool

    def allows_delivery(self) -> bool:
        if self.purpose in NON_OPTIONAL_PURPOSES:
            return True
        return self.enabled


@dataclass(frozen=True)
class NotificationPolicy:
    preferences: tuple[NotificationPreference, ...]
    learner_direct_channels: tuple[NotificationChannel, ...]
    max_messages_per_user_per_day: int
    max_messages_per_user_per_hour: int
    quiet_hours_start: time
    quiet_hours_end: time
    unsubscribe_required_for_marketing: bool
    audit_required: bool
    idempotency_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if self.max_messages_per_user_per_day <= 0:
            issues.append("daily rate limit must be positive")
        if self.max_messages_per_user_per_hour <= 0:
            issues.append("hourly rate limit must be positive")
        if self.max_messages_per_user_per_hour > self.max_messages_per_user_per_day:
            issues.append("hourly rate limit cannot exceed daily rate limit")
        if NotificationPurpose.MARKETING not in {preference.purpose for preference in self.preferences}:
            issues.append("marketing preference must be explicitly modeled")
        if not self.unsubscribe_required_for_marketing:
            issues.append("marketing unsubscribe is required")
        if not self.audit_required:
            issues.append("notification audit logging is required")
        if not self.idempotency_required:
            issues.append("notification idempotency is required")
        if NotificationChannel.SMS in self.learner_direct_channels:
            issues.append("direct learner SMS is prohibited by default")
        if NotificationChannel.WHATSAPP in self.learner_direct_channels:
            issues.append("direct learner WhatsApp is prohibited by default")
        return issues


@dataclass(frozen=True)
class NotificationTemplate:
    template_id: str
    version: str
    purpose: NotificationPurpose
    audience: NotificationAudience
    channels: tuple[NotificationChannel, ...]
    subject_template: str
    body_template: str
    locale: str
    required_variables: tuple[str, ...]
    allow_html: bool = False
    reviewed: bool = False

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.template_id:
            issues.append("template_id is required")
        if not self.version:
            issues.append("template version is required")
        if not self.channels:
            issues.append("at least one channel is required")
        if self.audience == NotificationAudience.LEARNER and self.purpose in LEARNER_PROHIBITED_PURPOSES:
            issues.append("learner billing or marketing templates are prohibited")
        if "{{" in self.body_template and "}}" in self.body_template:
            for variable in re.findall(r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}", self.body_template):
                if variable not in self.required_variables:
                    issues.append(f"template variable {variable!r} missing from required_variables")
        if self.allow_html and NotificationChannel.SMS in self.channels:
            issues.append("SMS templates cannot allow HTML")
        if not self.reviewed:
            issues.append("template review is required")
        return issues


@dataclass(frozen=True)
class NotificationRequest:
    recipient_id: str
    audience: NotificationAudience
    purpose: NotificationPurpose
    channel: NotificationChannel
    template_id: str
    template_version: str
    locale: str
    variables: Mapping[str, str]
    request_id: str
    idempotency_key: str
    scheduled_at_utc: datetime | None = None

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.recipient_id:
            issues.append("recipient_id is required")
        if self.audience == NotificationAudience.LEARNER and self.purpose in LEARNER_PROHIBITED_PURPOSES:
            issues.append("learner billing and marketing notifications are prohibited")
        if self.channel in {NotificationChannel.SMS, NotificationChannel.WHATSAPP} and self.audience == NotificationAudience.LEARNER:
            issues.append("direct learner SMS or WhatsApp delivery is prohibited by default")
        if not self.template_id:
            issues.append("template_id is required")
        if not self.template_version:
            issues.append("template_version is required")
        if not self.request_id:
            issues.append("request_id is required")
        if not self.idempotency_key:
            issues.append("idempotency_key is required")
        if self.scheduled_at_utc and self.scheduled_at_utc.tzinfo is None:
            issues.append("scheduled_at_utc must be timezone-aware")
        return issues


EMAIL_PATTERN = re.compile(r"\b[^@\s]+@[^@\s]+\.[^@\s]+\b")
PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)")


def redact_contact_details(text: str) -> str:
    """Remove obvious contact details before storing notification audit metadata."""

    text = EMAIL_PATTERN.sub("[redacted-email]", text)
    text = PHONE_PATTERN.sub("[redacted-phone]", text)
    return text


def build_notification_idempotency_key(
    *,
    recipient_id: str,
    purpose: NotificationPurpose,
    template_id: str,
    template_version: str,
    scheduled_bucket: str,
) -> str:
    """Build deterministic idempotency key without exposing raw contact details."""

    raw = f"{recipient_id}:{purpose.value}:{template_id}:{template_version}:{scheduled_bucket}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass
class NotificationOutbox:
    processed_keys: set[str] = field(default_factory=set)
    audit_log: list[str] = field(default_factory=list)
    dead_letter: list[str] = field(default_factory=list)

    def enqueue(self, request: NotificationRequest) -> str:
        issues = request.validate()
        if issues:
            raise ValueError("; ".join(issues))
        if request.idempotency_key in self.processed_keys:
            self.audit_log.append(f"duplicate:{request.idempotency_key}:{request.purpose.value}")
            return "duplicate"
        self.processed_keys.add(request.idempotency_key)
        self.audit_log.append(f"queued:{request.idempotency_key}:{request.channel.value}:{request.purpose.value}")
        return "queued"

    def mark_dead_letter(self, idempotency_key: str, reason: str) -> None:
        self.dead_letter.append(f"{idempotency_key}:{reason}")


@dataclass(frozen=True)
class DeliveryRetryPolicy:
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
class NotificationAuditEvent:
    event_id: str
    recipient_id: str
    audience: NotificationAudience
    purpose: NotificationPurpose
    channel: NotificationChannel
    delivery_status: DeliveryStatus
    request_id: str
    idempotency_key: str
    occurred_at_utc: datetime
    provider_message_id: str | None = None
    raw_payload_retained: bool = False

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.event_id:
            issues.append("event_id is required")
        if not self.recipient_id:
            issues.append("recipient_id is required")
        if not self.request_id:
            issues.append("request_id is required")
        if not self.idempotency_key:
            issues.append("idempotency_key is required")
        if self.occurred_at_utc.tzinfo is None:
            issues.append("occurred_at_utc must be timezone-aware")
        if self.raw_payload_retained:
            issues.append("raw provider payloads must not be retained without redaction")
        return issues


DEFAULT_COMMUNICATION_PROVIDER_DECISION = CommunicationProviderDecision(
    email_provider="resend_or_sendgrid",
    sms_provider="twilio_or_local_aggregator",
    whatsapp_provider="twilio_whatsapp_or_meta_cloud_api",
    push_provider="web_push",
    in_app_provider="database_outbox",
    adr_path="docs/adr/ADR-010-notifications-communication-provider.md",
    architecture_doc_path="docs/notifications/production_notifications_architecture_contract.md",
    provider_webhook_signature_required=True,
    provider_webhook_idempotency_required=True,
    bounce_handling_required=True,
)

DEFAULT_NOTIFICATION_POLICY = NotificationPolicy(
    preferences=(
        NotificationPreference(NotificationAudience.PARENT, NotificationPurpose.PROGRESS_SUMMARY, NotificationChannel.EMAIL, True, True, True),
        NotificationPreference(NotificationAudience.PARENT, NotificationPurpose.LEARNING_REMINDER, NotificationChannel.EMAIL, True, True, True),
        NotificationPreference(NotificationAudience.PARENT, NotificationPurpose.MARKETING, NotificationChannel.EMAIL, False, True, True),
        NotificationPreference(NotificationAudience.LEARNER, NotificationPurpose.LEARNING_REMINDER, NotificationChannel.IN_APP, True, False, True),
        NotificationPreference(NotificationAudience.TEACHER, NotificationPurpose.PROGRESS_SUMMARY, NotificationChannel.EMAIL, True, True, True),
        NotificationPreference(NotificationAudience.ADMIN, NotificationPurpose.INCIDENT, NotificationChannel.EMAIL, True, False, False),
    ),
    learner_direct_channels=(NotificationChannel.IN_APP, NotificationChannel.PUSH),
    max_messages_per_user_per_day=8,
    max_messages_per_user_per_hour=3,
    quiet_hours_start=time(20, 0),
    quiet_hours_end=time(7, 0),
    unsubscribe_required_for_marketing=True,
    audit_required=True,
    idempotency_required=True,
)

DEFAULT_RETRY_POLICY = DeliveryRetryPolicy(max_attempts=5, backoff_seconds=(60, 300, 900, 3600, 10800))

DEFAULT_TEMPLATES = (
    NotificationTemplate(
        template_id="parent_weekly_progress",
        version="v1",
        purpose=NotificationPurpose.PROGRESS_SUMMARY,
        audience=NotificationAudience.PARENT,
        channels=(NotificationChannel.EMAIL,),
        subject_template="EduBoost weekly progress",
        body_template="Your learner has completed {{completed_lessons}} lessons this week.",
        locale="en-ZA",
        required_variables=("completed_lessons",),
        reviewed=True,
    ),
    NotificationTemplate(
        template_id="learner_study_reminder",
        version="v1",
        purpose=NotificationPurpose.LEARNING_REMINDER,
        audience=NotificationAudience.LEARNER,
        channels=(NotificationChannel.IN_APP, NotificationChannel.PUSH),
        subject_template="Study reminder",
        body_template="You have a recommended revision activity waiting.",
        locale="en-ZA",
        required_variables=(),
        reviewed=True,
    ),
    NotificationTemplate(
        template_id="admin_incident_alert",
        version="v1",
        purpose=NotificationPurpose.INCIDENT,
        audience=NotificationAudience.ADMIN,
        channels=(NotificationChannel.EMAIL,),
        subject_template="EduBoost incident alert",
        body_template="Incident {{incident_id}} requires review.",
        locale="en-ZA",
        required_variables=("incident_id",),
        reviewed=True,
    ),
)


def default_notifications_readiness_report() -> dict[str, object]:
    """Return deterministic notification readiness evidence."""

    sample_key = build_notification_idempotency_key(
        recipient_id="recipient-001",
        purpose=NotificationPurpose.PROGRESS_SUMMARY,
        template_id="parent_weekly_progress",
        template_version="v1",
        scheduled_bucket="2026-W01",
    )
    request = NotificationRequest(
        recipient_id="recipient-001",
        audience=NotificationAudience.PARENT,
        purpose=NotificationPurpose.PROGRESS_SUMMARY,
        channel=NotificationChannel.EMAIL,
        template_id="parent_weekly_progress",
        template_version="v1",
        locale="en-ZA",
        variables={"completed_lessons": "5"},
        request_id="req-001",
        idempotency_key=sample_key,
        scheduled_at_utc=datetime.now(tz=timezone.utc),
    )
    outbox = NotificationOutbox()
    first = outbox.enqueue(request)
    second = outbox.enqueue(request)

    return {
        "provider_decision_issues": DEFAULT_COMMUNICATION_PROVIDER_DECISION.validate(),
        "policy_issues": DEFAULT_NOTIFICATION_POLICY.validate(),
        "retry_policy_issues": DEFAULT_RETRY_POLICY.validate(),
        "template_issues": [issue for template in DEFAULT_TEMPLATES for issue in template.validate()],
        "request_issues": request.validate(),
        "first_enqueue": first,
        "second_enqueue": second,
        "redaction_sample": redact_contact_details("email test@example.com or call +27 82 123 4567"),
        "channels": [channel.value for channel in NotificationChannel],
        "purposes": [purpose.value for purpose in NotificationPurpose],
    }
