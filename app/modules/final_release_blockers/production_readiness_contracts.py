"""Repository-verifiable final release-blocker checklist contracts.

These contracts do not approve a release, query GitHub, run CI, deploy workloads,
or inspect live infrastructure. They define deterministic repository-side evidence
for final release-blocker classification, ownership, closure, waiver boundaries,
manual/external dependencies, launch authority, and terminal go/no-go discipline.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
import hashlib
import re
from typing import Mapping


class ReleaseBlockerDomain(StrEnum):
    REPOSITORY = "repository"
    BACKEND_API = "backend_api"
    ARCHITECTURE = "architecture"
    AUTHORIZATION = "authorization"
    POPIA_CONSENT = "popia_consent"
    DATABASE = "database"
    AI_SAFETY = "ai_safety"
    FRONTEND_UX = "frontend_ux"
    BILLING = "billing"
    NOTIFICATIONS = "notifications"
    OBSERVABILITY = "observability"
    DEPLOYMENT = "deployment"
    BACKUP_DR = "backup_dr"
    TESTING_QUALITY = "testing_quality"
    SECURITY = "security"
    OPERATIONS_SUPPORT = "operations_support"
    DOCUMENTATION = "documentation"
    BETA_LAUNCH = "beta_launch"
    ROADMAP = "roadmap"
    EXTERNAL_MANUAL = "external_manual"


class BlockerSeverity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    RELEASE_BLOCKER = "release_blocker"


class BlockerStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"
    WAIVED = "waived"
    EXTERNAL_PENDING = "external_pending"
    NOT_APPLICABLE = "not_applicable"


class LaunchAuthority(StrEnum):
    ENGINEERING = "engineering"
    PRODUCT = "product"
    PRIVACY = "privacy"
    SECURITY = "security"
    SUPPORT = "support"
    RELEASE_OWNER = "release_owner"


class FinalDecision(StrEnum):
    GO = "go"
    NO_GO = "no_go"
    CONDITIONAL_GO = "conditional_go"
    DEFER = "defer"


@dataclass(frozen=True)
class FinalReleaseBlockerDecision:
    adr_path: str
    architecture_doc_path: str
    blocker_checklist_required: bool
    owner_assignment_required: bool
    closure_evidence_required: bool
    waiver_policy_required: bool
    external_dependency_boundary_required: bool
    launch_authority_required: bool
    final_go_no_go_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.adr_path.startswith("docs/adr/"):
            issues.append("final release-blocker decision must be documented in docs/adr/")
        if not self.architecture_doc_path.startswith("docs/release_blockers/"):
            issues.append("release-blocker architecture must be documented in docs/release_blockers/")
        for name, value in {
            "blocker_checklist_required": self.blocker_checklist_required,
            "owner_assignment_required": self.owner_assignment_required,
            "closure_evidence_required": self.closure_evidence_required,
            "waiver_policy_required": self.waiver_policy_required,
            "external_dependency_boundary_required": self.external_dependency_boundary_required,
            "launch_authority_required": self.launch_authority_required,
            "final_go_no_go_required": self.final_go_no_go_required,
        }.items():
            if not value:
                issues.append(f"{name} is required")
        return issues


@dataclass(frozen=True)
class ReleaseBlockerItem:
    blocker_id: str
    domain: ReleaseBlockerDomain
    title: str
    severity: BlockerSeverity
    status: BlockerStatus
    owner: str
    evidence_path: str
    closure_path: str | None
    waiver_path: str | None
    external_dependency: str | None
    blocks_launch: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not re.fullmatch(r"RB-\d{3}", self.blocker_id):
            issues.append("blocker_id must follow RB-### format")
        if not self.title:
            issues.append("release blocker title is required")
        if not self.owner:
            issues.append("release blocker owner is required")
        if not self.evidence_path.startswith(("docs/", "scripts/", "tests/", ".github/", "Makefile")):
            issues.append("release blocker evidence path must be controlled")
        if self.status == BlockerStatus.CLOSED and not self.closure_path:
            issues.append("closed blockers require closure evidence")
        if self.closure_path and not self.closure_path.startswith(("docs/", "scripts/", "tests/", ".github/", "Makefile")):
            issues.append("closure evidence path must be controlled")
        if self.status == BlockerStatus.WAIVED and not self.waiver_path:
            issues.append("waived blockers require waiver evidence")
        if self.waiver_path and not self.waiver_path.startswith("docs/release_blockers/"):
            issues.append("waiver evidence must live under docs/release_blockers/")
        if self.status == BlockerStatus.EXTERNAL_PENDING and not self.external_dependency:
            issues.append("external pending blockers require external dependency note")
        if self.severity in {BlockerSeverity.CRITICAL, BlockerSeverity.RELEASE_BLOCKER} and self.status == BlockerStatus.OPEN:
            issues.append("critical/release-blocker items cannot remain open")
        if self.severity == BlockerSeverity.RELEASE_BLOCKER and self.status == BlockerStatus.WAIVED:
            issues.append("release-blocker severity cannot be waived by default")
        if self.blocks_launch and self.status not in {BlockerStatus.CLOSED, BlockerStatus.NOT_APPLICABLE}:
            issues.append(f"{self.blocker_id} still blocks launch")
        return issues


@dataclass(frozen=True)
class ReleaseBlockerDomainSummary:
    domain: ReleaseBlockerDomain
    checklist_path: str
    check_command: str
    owner: str
    required_for_release: bool
    evidence_complete: bool
    manual_dependency: str | None = None

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.checklist_path.startswith("docs/"):
            issues.append("domain checklist path must live under docs/")
        if not self.check_command:
            issues.append("domain check command is required")
        if not self.owner:
            issues.append("domain summary owner is required")
        if self.required_for_release and not self.evidence_complete:
            issues.append(f"{self.domain.value} release evidence is incomplete")
        if self.domain == ReleaseBlockerDomain.EXTERNAL_MANUAL and not self.manual_dependency:
            issues.append("external/manual domain requires manual dependency")
        return issues


@dataclass(frozen=True)
class ReleaseWaiverRule:
    rule_id: str
    severity: BlockerSeverity
    waiver_allowed: bool
    required_approvers: tuple[LaunchAuthority, ...]
    expiry_days: int
    compensating_controls_required: bool
    evidence_path: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.rule_id:
            issues.append("waiver rule_id is required")
        if self.severity == BlockerSeverity.RELEASE_BLOCKER and self.waiver_allowed:
            issues.append("release-blocker severity cannot be waived")
        if self.waiver_allowed and not self.required_approvers:
            issues.append("waiver requires approvers")
        if self.waiver_allowed and not (0 < self.expiry_days <= 30):
            issues.append("waiver expiry must be between 1 and 30 days")
        if self.waiver_allowed and not self.compensating_controls_required:
            issues.append("waiver requires compensating controls")
        if not self.evidence_path.startswith("docs/release_blockers/"):
            issues.append("waiver rule evidence path must live under docs/release_blockers/")
        return issues


@dataclass(frozen=True)
class ExternalManualDependency:
    dependency_id: str
    description: str
    owner: str
    external_system: str
    verification_method: str
    required_before_launch: bool
    evidence_path: str
    status: BlockerStatus

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not re.fullmatch(r"EXT-\d{3}", self.dependency_id):
            issues.append("dependency_id must follow EXT-### format")
        if not self.description:
            issues.append("external dependency description is required")
        if not self.owner:
            issues.append("external dependency owner is required")
        if not self.external_system:
            issues.append("external system is required")
        if not self.verification_method:
            issues.append("verification method is required")
        if not self.evidence_path.startswith("docs/release_blockers/"):
            issues.append("external dependency evidence path must live under docs/release_blockers/")
        if self.required_before_launch and self.status != BlockerStatus.CLOSED:
            issues.append(f"{self.dependency_id} required external dependency is not closed")
        return issues


@dataclass(frozen=True)
class FinalGoNoGoChecklist:
    checklist_id: str
    decision: FinalDecision
    approvers: tuple[LaunchAuthority, ...]
    required_domains: tuple[ReleaseBlockerDomain, ...]
    blocker_register_path: str
    evidence_bundle_path: str
    known_issues_reviewed: bool
    rollback_reviewed: bool
    support_reviewed: bool
    privacy_security_reviewed: bool
    external_dependencies_reviewed: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.checklist_id:
            issues.append("final go/no-go checklist_id is required")
        if not self.approvers:
            issues.append("final go/no-go approvers are required")
        if LaunchAuthority.RELEASE_OWNER not in self.approvers:
            issues.append("release owner approval is required")
        if not self.required_domains:
            issues.append("required domains are required")
        if not self.blocker_register_path.startswith("docs/release_blockers/"):
            issues.append("blocker register path must live under docs/release_blockers/")
        if not self.evidence_bundle_path.startswith(("docs/", "artifacts/")):
            issues.append("evidence bundle path must be controlled")
        for name, value in {
            "known_issues_reviewed": self.known_issues_reviewed,
            "rollback_reviewed": self.rollback_reviewed,
            "support_reviewed": self.support_reviewed,
            "privacy_security_reviewed": self.privacy_security_reviewed,
            "external_dependencies_reviewed": self.external_dependencies_reviewed,
        }.items():
            if not value:
                issues.append(f"{name} must be reviewed")
        if self.decision == FinalDecision.GO and ReleaseBlockerDomain.EXTERNAL_MANUAL not in self.required_domains:
            issues.append("GO decision must include external/manual dependency review")
        return issues


@dataclass(frozen=True)
class ReleaseBlockerClosureRecord:
    closure_id: str
    blocker_id: str
    closed_on: date
    closed_by: str
    evidence_checksum: str
    evidence_path: str
    residual_risk: str
    follow_up_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not re.fullmatch(r"CLOSE-\d{3}", self.closure_id):
            issues.append("closure_id must follow CLOSE-### format")
        if not re.fullmatch(r"RB-\d{3}", self.blocker_id):
            issues.append("blocker_id must follow RB-### format")
        if not self.closed_by:
            issues.append("closed_by is required")
        if not re.fullmatch(r"[a-f0-9]{64}", self.evidence_checksum):
            issues.append("evidence_checksum must be 64 lowercase hex")
        if not self.evidence_path.startswith(("docs/", "scripts/", "tests/", ".github/", "Makefile")):
            issues.append("closure evidence path must be controlled")
        if not self.residual_risk:
            issues.append("residual risk summary is required")
        return issues


def compute_release_blocker_checksum(content: str) -> str:
    """Compute SHA-256 checksum for final release-blocker evidence."""

    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def summarize_blockers(blockers: tuple[ReleaseBlockerItem, ...]) -> dict[str, int]:
    """Summarize blocker statuses."""

    summary = {status.value: 0 for status in BlockerStatus}
    for blocker in blockers:
        summary[blocker.status.value] += 1
    return summary


def determine_final_decision(blockers: tuple[ReleaseBlockerItem, ...], external_dependencies: tuple[ExternalManualDependency, ...]) -> FinalDecision:
    """Determine final release decision from blockers and external dependencies."""

    for blocker in blockers:
        if blocker.blocks_launch and blocker.status not in {BlockerStatus.CLOSED, BlockerStatus.NOT_APPLICABLE}:
            return FinalDecision.NO_GO
        if blocker.severity in {BlockerSeverity.CRITICAL, BlockerSeverity.RELEASE_BLOCKER} and blocker.status != BlockerStatus.CLOSED:
            return FinalDecision.NO_GO
    for dependency in external_dependencies:
        if dependency.required_before_launch and dependency.status != BlockerStatus.CLOSED:
            return FinalDecision.DEFER
    if any(blocker.status == BlockerStatus.WAIVED for blocker in blockers):
        return FinalDecision.CONDITIONAL_GO
    return FinalDecision.GO


def validate_final_release_bundle(
    blockers: tuple[ReleaseBlockerItem, ...],
    external_dependencies: tuple[ExternalManualDependency, ...],
    checklist: FinalGoNoGoChecklist,
) -> list[str]:
    """Validate final release-blocker bundle."""

    issues: list[str] = []
    for blocker in blockers:
        issues.extend(blocker.validate())
    for dependency in external_dependencies:
        issues.extend(dependency.validate())
    issues.extend(checklist.validate())
    decision = determine_final_decision(blockers, external_dependencies)
    if checklist.decision == FinalDecision.GO and decision != FinalDecision.GO:
        issues.append(f"checklist GO conflicts with computed {decision.value}")
    return issues


_SAMPLE_DATE = date(2026, 1, 1)

DEFAULT_FINAL_BLOCKER_DECISION = FinalReleaseBlockerDecision(
    adr_path="docs/adr/ADR-020-final-release-blocker-checklist.md",
    architecture_doc_path="docs/release_blockers/final_release_blocker_architecture_contract.md",
    blocker_checklist_required=True,
    owner_assignment_required=True,
    closure_evidence_required=True,
    waiver_policy_required=True,
    external_dependency_boundary_required=True,
    launch_authority_required=True,
    final_go_no_go_required=True,
)

DEFAULT_DOMAIN_SUMMARIES = (
    ReleaseBlockerDomainSummary(ReleaseBlockerDomain.REPOSITORY, "docs/backlog/production_readiness/00_repository_state_and_canonical_source_of_truth.md", "python3 scripts/check_domain_01_repository_governance_ci_evidence.py", "release-owner", True, True),
    ReleaseBlockerDomainSummary(ReleaseBlockerDomain.BACKEND_API, "docs/backlog/production_readiness/01_pr-002r_replacement_#U2014_backend_runtime_and_api_contract_baseline.md", "python3 scripts/check_domain_02_backend_api_contract_evidence.py", "engineering", True, True),
    ReleaseBlockerDomainSummary(ReleaseBlockerDomain.SECURITY, "docs/backlog/production_readiness/15_security_posture_and_threat_modeling.md", "make security-posture-threat-modeling-production-readiness-check", "security-owner", True, True),
    ReleaseBlockerDomainSummary(ReleaseBlockerDomain.OPERATIONS_SUPPORT, "docs/backlog/production_readiness/16_incident_response_operations_and_support.md", "make incident-response-operations-support-production-readiness-check", "support-owner", True, True),
    ReleaseBlockerDomainSummary(ReleaseBlockerDomain.EXTERNAL_MANUAL, "docs/release_blockers/external_manual_dependency_register.md", "manual verification", "release-owner", True, True, "GitHub settings, legal approval, live provider setup"),
)

DEFAULT_RELEASE_BLOCKERS = (
    ReleaseBlockerItem("RB-001", ReleaseBlockerDomain.SECURITY, "Security posture evidence", BlockerSeverity.HIGH, BlockerStatus.CLOSED, "security-owner", "docs/security/security_posture_architecture_contract.md", "scripts/check_security_posture_threat_modeling_production_readiness.py", None, None, False),
    ReleaseBlockerItem("RB-002", ReleaseBlockerDomain.TESTING_QUALITY, "Testing release quality gate evidence", BlockerSeverity.HIGH, BlockerStatus.CLOSED, "engineering", "docs/testing/testing_release_evidence_architecture_contract.md", "scripts/check_testing_release_quality_gates_production_readiness.py", None, None, False),
    ReleaseBlockerItem("RB-003", ReleaseBlockerDomain.EXTERNAL_MANUAL, "External manual approvals", BlockerSeverity.MEDIUM, BlockerStatus.NOT_APPLICABLE, "release-owner", "docs/release_blockers/external_manual_dependency_register.md", "docs/release_blockers/final_go_no_go_checklist.md", None, "Tracked separately from repository-side launch evidence", False),
    ReleaseBlockerItem("RB-004", ReleaseBlockerDomain.BETA_LAUNCH, "Beta launch staging acceptance evidence", BlockerSeverity.HIGH, BlockerStatus.CLOSED, "release-owner", "docs/beta_launch/beta_launch_staging_acceptance_architecture_contract.md", "scripts/check_beta_launch_staging_acceptance_production_readiness.py", None, None, False),
)

DEFAULT_WAIVER_RULES = (
    ReleaseWaiverRule("WVR-001", BlockerSeverity.LOW, True, (LaunchAuthority.RELEASE_OWNER,), 30, True, "docs/release_blockers/release_blocker_waiver_policy.md"),
    ReleaseWaiverRule("WVR-002", BlockerSeverity.MEDIUM, True, (LaunchAuthority.RELEASE_OWNER, LaunchAuthority.ENGINEERING), 14, True, "docs/release_blockers/release_blocker_waiver_policy.md"),
    ReleaseWaiverRule("WVR-003", BlockerSeverity.HIGH, True, (LaunchAuthority.RELEASE_OWNER, LaunchAuthority.SECURITY), 7, True, "docs/release_blockers/release_blocker_waiver_policy.md"),
    ReleaseWaiverRule("WVR-004", BlockerSeverity.RELEASE_BLOCKER, False, (), 0, False, "docs/release_blockers/release_blocker_waiver_policy.md"),
)

DEFAULT_EXTERNAL_DEPENDENCIES = (
    ExternalManualDependency("EXT-001", "GitHub branch protection settings verified outside repository.", "release-owner", "GitHub repository settings", "human review screenshot or settings export", False, "docs/release_blockers/external_manual_dependency_register.md", BlockerStatus.NOT_APPLICABLE),
    ExternalManualDependency("EXT-002", "Legal/privacy launch approval completed outside repository.", "privacy-owner", "legal/privacy approval workflow", "signed approval record", False, "docs/release_blockers/external_manual_dependency_register.md", BlockerStatus.NOT_APPLICABLE),
)

DEFAULT_FINAL_CHECKLIST = FinalGoNoGoChecklist(
    checklist_id="final-release-blocker-checklist",
    decision=FinalDecision.GO,
    approvers=(LaunchAuthority.RELEASE_OWNER, LaunchAuthority.ENGINEERING, LaunchAuthority.SECURITY, LaunchAuthority.PRIVACY, LaunchAuthority.SUPPORT),
    required_domains=tuple(domain for domain in ReleaseBlockerDomain),
    blocker_register_path="docs/release_blockers/final_release_blocker_register.md",
    evidence_bundle_path="docs/release_blockers/final_release_blocker_evidence_bundle.md",
    known_issues_reviewed=True,
    rollback_reviewed=True,
    support_reviewed=True,
    privacy_security_reviewed=True,
    external_dependencies_reviewed=True,
)

DEFAULT_CLOSURE_RECORDS = (
    ReleaseBlockerClosureRecord("CLOSE-001", "RB-001", _SAMPLE_DATE, "security-owner", compute_release_blocker_checksum("security closure"), "scripts/check_security_posture_threat_modeling_production_readiness.py", "repository-side security evidence only; external approval remains separate", False),
    ReleaseBlockerClosureRecord("CLOSE-002", "RB-002", _SAMPLE_DATE, "engineering", compute_release_blocker_checksum("testing closure"), "scripts/check_testing_release_quality_gates_production_readiness.py", "repository-side quality evidence only; CI settings remain separate", False),
)


def default_final_release_blocker_readiness_report() -> dict[str, object]:
    """Return deterministic final release-blocker checklist readiness evidence."""

    return {
        "decision_issues": DEFAULT_FINAL_BLOCKER_DECISION.validate(),
        "domain_summary_issues": [issue for summary in DEFAULT_DOMAIN_SUMMARIES for issue in summary.validate()],
        "release_blocker_issues": [issue for blocker in DEFAULT_RELEASE_BLOCKERS for issue in blocker.validate()],
        "waiver_rule_issues": [issue for rule in DEFAULT_WAIVER_RULES for issue in rule.validate()],
        "external_dependency_issues": [issue for dependency in DEFAULT_EXTERNAL_DEPENDENCIES for issue in dependency.validate()],
        "final_checklist_issues": DEFAULT_FINAL_CHECKLIST.validate(),
        "closure_record_issues": [issue for closure in DEFAULT_CLOSURE_RECORDS for issue in closure.validate()],
        "final_bundle_issues": validate_final_release_bundle(DEFAULT_RELEASE_BLOCKERS, DEFAULT_EXTERNAL_DEPENDENCIES, DEFAULT_FINAL_CHECKLIST),
        "blocker_summary": summarize_blockers(DEFAULT_RELEASE_BLOCKERS),
        "computed_decision": determine_final_decision(DEFAULT_RELEASE_BLOCKERS, DEFAULT_EXTERNAL_DEPENDENCIES).value,
        "checksum_sample": compute_release_blocker_checksum("final-release-blocker-evidence"),
    }
