"""Repository-verifiable incident response, operations, and support contracts.

These contracts do not page humans, create tickets, send notifications, or call
external support systems. They model deterministic production-readiness evidence
for incident classification, escalation, runbooks, on-call ownership, support SLAs,
status communication, post-incident review, and operational handover.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import re


class IncidentSeverity(str, Enum):
    SEV1 = "sev1"
    SEV2 = "sev2"
    SEV3 = "sev3"
    SEV4 = "sev4"


class IncidentStatus(str, Enum):
    DETECTED = "detected"
    TRIAGED = "triaged"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    REVIEWED = "reviewed"


class OperationalRole(str, Enum):
    INCIDENT_COMMANDER = "incident_commander"
    TECHNICAL_LEAD = "technical_lead"
    COMMUNICATIONS_LEAD = "communications_lead"
    PRIVACY_LEAD = "privacy_lead"
    SUPPORT_LEAD = "support_lead"
    RELEASE_OWNER = "release_owner"


class SupportPriority(str, Enum):
    P0 = "p0"
    P1 = "p1"
    P2 = "p2"
    P3 = "p3"


class SupportChannel(str, Enum):
    EMAIL = "email"
    IN_APP = "in_app"
    STATUS_PAGE = "status_page"
    ADMIN_CONSOLE = "admin_console"
    INTERNAL_CHAT = "internal_chat"


class CustomerImpact(str, Enum):
    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


@dataclass(frozen=True)
class OperationsSupportDecision:
    adr_path: str
    architecture_doc_path: str
    incident_response_required: bool
    on_call_required: bool
    support_sla_required: bool
    runbook_required: bool
    status_communication_required: bool
    post_incident_review_required: bool
    privacy_escalation_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.adr_path.startswith("docs/adr/"):
            issues.append("operations support decision must be documented in docs/adr/")
        if not self.architecture_doc_path.startswith("docs/operations_support/"):
            issues.append("operations support architecture must be documented in docs/operations_support/")
        for name, value in {
            "incident_response_required": self.incident_response_required,
            "on_call_required": self.on_call_required,
            "support_sla_required": self.support_sla_required,
            "runbook_required": self.runbook_required,
            "status_communication_required": self.status_communication_required,
            "post_incident_review_required": self.post_incident_review_required,
            "privacy_escalation_required": self.privacy_escalation_required,
        }.items():
            if not value:
                issues.append(f"{name} is required")
        return issues


@dataclass(frozen=True)
class IncidentClassificationRule:
    severity: IncidentSeverity
    customer_impact: CustomerImpact
    response_time_minutes: int
    update_interval_minutes: int
    requires_incident_commander: bool
    requires_status_update: bool
    requires_privacy_review: bool
    blocks_release: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if self.response_time_minutes <= 0:
            issues.append("incident response time must be positive")
        if self.update_interval_minutes <= 0:
            issues.append("incident update interval must be positive")
        if self.severity in {IncidentSeverity.SEV1, IncidentSeverity.SEV2} and not self.requires_incident_commander:
            issues.append(f"{self.severity.value} requires incident commander")
        if self.severity == IncidentSeverity.SEV1 and not self.requires_status_update:
            issues.append("sev1 requires status update")
        if self.customer_impact in {CustomerImpact.MAJOR, CustomerImpact.CRITICAL} and not self.blocks_release:
            issues.append("major or critical customer impact must block release")
        return issues


@dataclass(frozen=True)
class OnCallEscalationPolicy:
    policy_id: str
    primary_role: OperationalRole
    secondary_role: OperationalRole
    escalation_minutes: int
    coverage_hours: str
    backup_required: bool
    handoff_required: bool
    evidence_path: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.policy_id:
            issues.append("policy_id is required")
        if self.primary_role == self.secondary_role:
            issues.append("primary and secondary roles must differ")
        if self.escalation_minutes <= 0:
            issues.append("escalation minutes must be positive")
        if not self.coverage_hours:
            issues.append("coverage hours are required")
        if not self.backup_required:
            issues.append("backup on-call is required")
        if not self.handoff_required:
            issues.append("on-call handoff is required")
        if not self.evidence_path.startswith("docs/operations_support/"):
            issues.append("on-call evidence path must live under docs/operations_support/")
        return issues


@dataclass(frozen=True)
class OperationalRunbook:
    runbook_path: str
    scenario: str
    owner: OperationalRole
    detection_steps: tuple[str, ...]
    triage_steps: tuple[str, ...]
    mitigation_steps: tuple[str, ...]
    recovery_steps: tuple[str, ...]
    verification_steps: tuple[str, ...]
    rollback_criteria: tuple[str, ...]

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.runbook_path.startswith("docs/operations_support/runbooks/"):
            issues.append("operational runbook must live under docs/operations_support/runbooks/")
        if not self.scenario:
            issues.append("runbook scenario is required")
        if not self.detection_steps:
            issues.append("detection steps are required")
        if not self.triage_steps:
            issues.append("triage steps are required")
        if not self.mitigation_steps:
            issues.append("mitigation steps are required")
        if not self.recovery_steps:
            issues.append("recovery steps are required")
        if not self.verification_steps:
            issues.append("verification steps are required")
        if not self.rollback_criteria:
            issues.append("rollback criteria are required")
        return issues


@dataclass(frozen=True)
class SupportSla:
    priority: SupportPriority
    first_response_minutes: int
    target_resolution_hours: int
    escalation_required: bool
    owner: OperationalRole
    customer_visible: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if self.first_response_minutes <= 0:
            issues.append("first response minutes must be positive")
        if self.target_resolution_hours <= 0:
            issues.append("target resolution hours must be positive")
        if self.priority in {SupportPriority.P0, SupportPriority.P1} and not self.escalation_required:
            issues.append(f"{self.priority.value} support requires escalation")
        if self.priority == SupportPriority.P0 and self.first_response_minutes > 30:
            issues.append("p0 first response must be <= 30 minutes")
        if self.priority == SupportPriority.P1 and self.first_response_minutes > 120:
            issues.append("p1 first response must be <= 120 minutes")
        return issues


@dataclass(frozen=True)
class StatusCommunicationTemplate:
    template_id: str
    severity: IncidentSeverity
    channels: tuple[SupportChannel, ...]
    audience: str
    update_interval_minutes: int
    requires_privacy_review: bool
    required_fields: tuple[str, ...]

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.template_id:
            issues.append("template_id is required")
        if not self.channels:
            issues.append("status communication channels are required")
        if not self.audience:
            issues.append("status communication audience is required")
        if self.update_interval_minutes <= 0:
            issues.append("status update interval must be positive")
        if self.severity in {IncidentSeverity.SEV1, IncidentSeverity.SEV2} and SupportChannel.STATUS_PAGE not in self.channels:
            issues.append(f"{self.severity.value} status communication requires status page")
        for field in ("incident_id", "impact", "current_status", "next_update"):
            if field not in self.required_fields:
                issues.append(f"status communication missing required field {field}")
        return issues


@dataclass(frozen=True)
class IncidentRecord:
    incident_id: str
    severity: IncidentSeverity
    status: IncidentStatus
    detected_at_utc: datetime
    owner: OperationalRole
    customer_impact: CustomerImpact
    root_cause_summary: str | None
    evidence_path: str
    post_incident_review_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.incident_id:
            issues.append("incident_id is required")
        if self.detected_at_utc.tzinfo is None:
            issues.append("detected_at_utc must be timezone-aware")
        if self.status in {IncidentStatus.RESOLVED, IncidentStatus.REVIEWED} and not self.root_cause_summary:
            issues.append("resolved/reviewed incidents require root cause summary")
        if not self.evidence_path.startswith("docs/operations_support/incidents/"):
            issues.append("incident evidence must live under docs/operations_support/incidents/")
        if self.severity in {IncidentSeverity.SEV1, IncidentSeverity.SEV2} and not self.post_incident_review_required:
            issues.append("sev1/sev2 incidents require post-incident review")
        return issues


@dataclass(frozen=True)
class PostIncidentReview:
    review_id: str
    incident_id: str
    completed: bool
    root_cause_documented: bool
    timeline_documented: bool
    corrective_actions: tuple[str, ...]
    owner: OperationalRole
    evidence_path: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.review_id:
            issues.append("review_id is required")
        if not self.incident_id:
            issues.append("incident_id is required")
        if not self.completed:
            issues.append("post-incident review must be completed")
        if not self.root_cause_documented:
            issues.append("root cause must be documented")
        if not self.timeline_documented:
            issues.append("incident timeline must be documented")
        if not self.corrective_actions:
            issues.append("corrective actions are required")
        if not self.evidence_path.startswith("docs/operations_support/post_incident_reviews/"):
            issues.append("post-incident review evidence must live under docs/operations_support/post_incident_reviews/")
        return issues


@dataclass(frozen=True)
class OperationalHandoverChecklist:
    checklist_path: str
    release_owner: str
    support_owner: str
    runbooks_reviewed: bool
    dashboards_reviewed: bool
    alert_routes_reviewed: bool
    escalation_matrix_reviewed: bool
    known_issues_reviewed: bool
    support_channels_ready: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.checklist_path.startswith("docs/operations_support/"):
            issues.append("operational handover checklist must live under docs/operations_support/")
        if not self.release_owner:
            issues.append("release owner is required")
        if not self.support_owner:
            issues.append("support owner is required")
        for name, value in {
            "runbooks_reviewed": self.runbooks_reviewed,
            "dashboards_reviewed": self.dashboards_reviewed,
            "alert_routes_reviewed": self.alert_routes_reviewed,
            "escalation_matrix_reviewed": self.escalation_matrix_reviewed,
            "known_issues_reviewed": self.known_issues_reviewed,
            "support_channels_ready": self.support_channels_ready,
        }.items():
            if not value:
                issues.append(f"{name} must be true")
        return issues


def compute_operations_evidence_checksum(content: str) -> str:
    """Compute SHA-256 checksum for operations/support evidence."""

    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def redact_incident_note(note: str) -> str:
    """Redact obvious email and phone values from incident/support notes."""

    note = re.sub(r"\b[^@\s]+@[^@\s]+\.[^@\s]+\b", "[redacted-email]", note or "")
    note = re.sub(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)", "[redacted-phone]", note)
    return note


def classify_support_priority(customer_impact: CustomerImpact, security_or_privacy: bool) -> SupportPriority:
    """Classify support priority from customer impact and security/privacy signal."""

    if customer_impact == CustomerImpact.CRITICAL or security_or_privacy:
        return SupportPriority.P0
    if customer_impact == CustomerImpact.MAJOR:
        return SupportPriority.P1
    if customer_impact == CustomerImpact.MODERATE:
        return SupportPriority.P2
    return SupportPriority.P3


DEFAULT_OPERATIONS_DECISION = OperationsSupportDecision(
    adr_path="docs/adr/ADR-016-incident-response-operations-support.md",
    architecture_doc_path="docs/operations_support/incident_response_operations_support_architecture_contract.md",
    incident_response_required=True,
    on_call_required=True,
    support_sla_required=True,
    runbook_required=True,
    status_communication_required=True,
    post_incident_review_required=True,
    privacy_escalation_required=True,
)

DEFAULT_INCIDENT_CLASSIFICATION = (
    IncidentClassificationRule(IncidentSeverity.SEV1, CustomerImpact.CRITICAL, 15, 30, True, True, True, True),
    IncidentClassificationRule(IncidentSeverity.SEV2, CustomerImpact.MAJOR, 30, 60, True, True, True, True),
    IncidentClassificationRule(IncidentSeverity.SEV3, CustomerImpact.MODERATE, 120, 240, False, False, False, False),
    IncidentClassificationRule(IncidentSeverity.SEV4, CustomerImpact.MINOR, 480, 1440, False, False, False, False),
)

DEFAULT_ON_CALL_POLICIES = (
    OnCallEscalationPolicy("oncall-primary", OperationalRole.TECHNICAL_LEAD, OperationalRole.INCIDENT_COMMANDER, 15, "24x7 for sev1/sev2", True, True, "docs/operations_support/on_call_escalation_policy.md"),
    OnCallEscalationPolicy("privacy-escalation", OperationalRole.PRIVACY_LEAD, OperationalRole.INCIDENT_COMMANDER, 30, "business hours plus sev escalation", True, True, "docs/operations_support/on_call_escalation_policy.md"),
)

DEFAULT_RUNBOOKS = (
    OperationalRunbook(
        "docs/operations_support/runbooks/api_outage.md",
        "API outage or severe degradation",
        OperationalRole.TECHNICAL_LEAD,
        ("confirm alert", "check dashboard", "review recent deploy"),
        ("classify severity", "assign incident commander", "identify affected routes"),
        ("scale service", "rollback recent release", "disable failing dependency"),
        ("verify health checks", "run smoke tests"),
        ("confirm API availability", "confirm error rate normal"),
        ("error rate remains elevated", "smoke tests fail", "customer impact persists"),
    ),
    OperationalRunbook(
        "docs/operations_support/runbooks/privacy_incident.md",
        "Privacy or learner-data incident",
        OperationalRole.PRIVACY_LEAD,
        ("confirm privacy signal", "preserve evidence", "identify data class"),
        ("classify severity", "notify privacy owner", "identify affected users"),
        ("disable affected path", "restrict access", "stop data flow"),
        ("verify access controls", "confirm data subject rights path"),
        ("confirm no ongoing exposure", "record evidence"),
        ("uncertain containment", "continued exposure", "legal notification needed"),
    ),
)

DEFAULT_SUPPORT_SLAS = (
    SupportSla(SupportPriority.P0, 15, 4, True, OperationalRole.SUPPORT_LEAD, True),
    SupportSla(SupportPriority.P1, 60, 24, True, OperationalRole.SUPPORT_LEAD, True),
    SupportSla(SupportPriority.P2, 240, 72, False, OperationalRole.SUPPORT_LEAD, True),
    SupportSla(SupportPriority.P3, 1440, 168, False, OperationalRole.SUPPORT_LEAD, True),
)

DEFAULT_STATUS_TEMPLATES = (
    StatusCommunicationTemplate(
        "sev1-status-update",
        IncidentSeverity.SEV1,
        (SupportChannel.STATUS_PAGE, SupportChannel.EMAIL, SupportChannel.IN_APP),
        "affected users and internal stakeholders",
        30,
        True,
        ("incident_id", "impact", "current_status", "next_update"),
    ),
    StatusCommunicationTemplate(
        "sev2-status-update",
        IncidentSeverity.SEV2,
        (SupportChannel.STATUS_PAGE, SupportChannel.EMAIL),
        "affected users and support",
        60,
        True,
        ("incident_id", "impact", "current_status", "next_update"),
    ),
)

_SAMPLE_TIME = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)

DEFAULT_INCIDENT_RECORD = IncidentRecord(
    incident_id="INC-001",
    severity=IncidentSeverity.SEV2,
    status=IncidentStatus.RESOLVED,
    detected_at_utc=_SAMPLE_TIME,
    owner=OperationalRole.INCIDENT_COMMANDER,
    customer_impact=CustomerImpact.MAJOR,
    root_cause_summary="provider timeout caused degraded response path",
    evidence_path="docs/operations_support/incidents/INC-001.md",
    post_incident_review_required=True,
)

DEFAULT_POST_INCIDENT_REVIEW = PostIncidentReview(
    review_id="PIR-001",
    incident_id="INC-001",
    completed=True,
    root_cause_documented=True,
    timeline_documented=True,
    corrective_actions=("add provider timeout alert", "update runbook", "add regression check"),
    owner=OperationalRole.INCIDENT_COMMANDER,
    evidence_path="docs/operations_support/post_incident_reviews/PIR-001.md",
)

DEFAULT_HANDOVER = OperationalHandoverChecklist(
    checklist_path="docs/operations_support/production_operations_handover_checklist.md",
    release_owner="release-owner",
    support_owner="support-owner",
    runbooks_reviewed=True,
    dashboards_reviewed=True,
    alert_routes_reviewed=True,
    escalation_matrix_reviewed=True,
    known_issues_reviewed=True,
    support_channels_ready=True,
)


def default_operations_support_readiness_report() -> dict[str, object]:
    """Return deterministic incident response, operations, and support readiness evidence."""

    incident_note = "Contact user@example.com or +27 82 123 4567 for incident follow-up"
    return {
        "decision_issues": DEFAULT_OPERATIONS_DECISION.validate(),
        "classification_issues": [issue for rule in DEFAULT_INCIDENT_CLASSIFICATION for issue in rule.validate()],
        "on_call_issues": [issue for policy in DEFAULT_ON_CALL_POLICIES for issue in policy.validate()],
        "runbook_issues": [issue for runbook in DEFAULT_RUNBOOKS for issue in runbook.validate()],
        "support_sla_issues": [issue for sla in DEFAULT_SUPPORT_SLAS for issue in sla.validate()],
        "status_template_issues": [issue for template in DEFAULT_STATUS_TEMPLATES for issue in template.validate()],
        "incident_record_issues": DEFAULT_INCIDENT_RECORD.validate(),
        "post_incident_review_issues": DEFAULT_POST_INCIDENT_REVIEW.validate(),
        "handover_issues": DEFAULT_HANDOVER.validate(),
        "priority_sample": classify_support_priority(CustomerImpact.CRITICAL, False).value,
        "privacy_priority_sample": classify_support_priority(CustomerImpact.MINOR, True).value,
        "redaction_sample": redact_incident_note(incident_note),
        "checksum_sample": compute_operations_evidence_checksum("operations-support-evidence"),
    }
