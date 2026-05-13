"""Repository-verifiable beta launch, staging acceptance, and product-scope contracts.

These contracts do not enroll beta users, deploy staging, collect production
telemetry, or approve launch. They model deterministic evidence for beta scope,
staging acceptance, entry/exit criteria, launch cohorts, controlled rollout,
feedback intake, known issues, no-go decisions, and post-beta review.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
import hashlib
import re
from typing import Mapping


class BetaStage(StrEnum):
    INTERNAL_ALPHA = "internal_alpha"
    PRIVATE_BETA = "private_beta"
    CONTROLLED_BETA = "controlled_beta"
    PUBLIC_BETA = "public_beta"
    GENERAL_AVAILABILITY = "general_availability"


class LaunchDecision(StrEnum):
    GO = "go"
    NO_GO = "no_go"
    CONDITIONAL_GO = "conditional_go"
    DEFER = "defer"


class ProductScopeArea(StrEnum):
    LEARNER_ONBOARDING = "learner_onboarding"
    DIAGNOSTICS = "diagnostics"
    LESSON_GENERATION = "lesson_generation"
    STUDY_PLAN = "study_plan"
    PARENT_DASHBOARD = "parent_dashboard"
    POPIA_RIGHTS = "popia_rights"
    NOTIFICATIONS = "notifications"
    BILLING_DISABLED = "billing_disabled"
    SUPPORT = "support"


class AcceptanceStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"
    WAIVED = "waived"


class FeedbackSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class BetaLaunchDecision:
    adr_path: str
    architecture_doc_path: str
    beta_scope_required: bool
    staging_acceptance_required: bool
    entry_exit_criteria_required: bool
    cohort_controls_required: bool
    feedback_intake_required: bool
    known_issues_required: bool
    no_go_authority_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.adr_path.startswith("docs/adr/"):
            issues.append("beta launch decision must be documented in docs/adr/")
        if not self.architecture_doc_path.startswith("docs/beta_launch/"):
            issues.append("beta launch architecture must be documented in docs/beta_launch/")
        for name, value in {
            "beta_scope_required": self.beta_scope_required,
            "staging_acceptance_required": self.staging_acceptance_required,
            "entry_exit_criteria_required": self.entry_exit_criteria_required,
            "cohort_controls_required": self.cohort_controls_required,
            "feedback_intake_required": self.feedback_intake_required,
            "known_issues_required": self.known_issues_required,
            "no_go_authority_required": self.no_go_authority_required,
        }.items():
            if not value:
                issues.append(f"{name} is required")
        return issues


@dataclass(frozen=True)
class ProductScopeItem:
    scope_id: str
    area: ProductScopeArea
    description: str
    included_in_beta: bool
    explicit_exclusion: bool
    owner: str
    evidence_path: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.scope_id:
            issues.append("scope_id is required")
        if not self.description:
            issues.append("product scope description is required")
        if not self.owner:
            issues.append("product scope owner is required")
        if not self.evidence_path.startswith("docs/beta_launch/"):
            issues.append("product scope evidence path must live under docs/beta_launch/")
        if self.area == ProductScopeArea.BILLING_DISABLED and not self.explicit_exclusion:
            issues.append("billing must be explicitly excluded or disabled for beta unless approved")
        if not self.included_in_beta and not self.explicit_exclusion:
            issues.append("excluded beta scope must be explicitly marked as exclusion")
        return issues


@dataclass(frozen=True)
class StagingAcceptanceCriterion:
    criterion_id: str
    name: str
    status: AcceptanceStatus
    evidence_path: str
    owner: str
    blocks_beta: bool
    waiver_path: str | None = None

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.criterion_id:
            issues.append("criterion_id is required")
        if not self.name:
            issues.append("acceptance criterion name is required")
        if not self.evidence_path.startswith(("docs/", "scripts/", "tests/", "artifacts/")):
            issues.append("staging acceptance evidence path must be controlled")
        if not self.owner:
            issues.append("staging acceptance owner is required")
        if self.status in {AcceptanceStatus.FAIL, AcceptanceStatus.BLOCKED} and self.blocks_beta:
            issues.append(f"{self.criterion_id} blocks beta launch")
        if self.status == AcceptanceStatus.WAIVED and not self.waiver_path:
            issues.append("waived staging acceptance criterion requires waiver path")
        return issues


@dataclass(frozen=True)
class BetaEntryCriterion:
    criterion_id: str
    description: str
    met: bool
    evidence_path: str
    owner: str
    required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.criterion_id:
            issues.append("entry criterion_id is required")
        if not self.description:
            issues.append("entry criterion description is required")
        if not self.evidence_path.startswith(("docs/", "scripts/", "tests/", "artifacts/")):
            issues.append("entry criterion evidence path must be controlled")
        if not self.owner:
            issues.append("entry criterion owner is required")
        if self.required and not self.met:
            issues.append(f"{self.criterion_id} required entry criterion is not met")
        return issues


@dataclass(frozen=True)
class BetaExitCriterion:
    criterion_id: str
    description: str
    met: bool
    metric_name: str
    threshold: str
    owner: str
    evidence_path: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.criterion_id:
            issues.append("exit criterion_id is required")
        if not self.description:
            issues.append("exit criterion description is required")
        if not self.metric_name:
            issues.append("exit criterion metric name is required")
        if not self.threshold:
            issues.append("exit criterion threshold is required")
        if not self.owner:
            issues.append("exit criterion owner is required")
        if not self.evidence_path.startswith(("docs/", "artifacts/")):
            issues.append("exit criterion evidence path must be controlled")
        return issues


@dataclass(frozen=True)
class BetaCohortPlan:
    cohort_id: str
    stage: BetaStage
    max_learners: int
    max_guardians: int
    allowed_grades: tuple[int, ...]
    allowed_subjects: tuple[str, ...]
    consent_required: bool
    support_channel_ready: bool
    rollback_supported: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.cohort_id:
            issues.append("cohort_id is required")
        if self.max_learners <= 0:
            issues.append("max_learners must be positive")
        if self.max_guardians <= 0:
            issues.append("max_guardians must be positive")
        if not self.allowed_grades:
            issues.append("allowed grades are required")
        if any(grade < 1 or grade > 12 for grade in self.allowed_grades):
            issues.append("allowed grades must be South African school grades 1-12")
        if not self.allowed_subjects:
            issues.append("allowed subjects are required")
        if not self.consent_required:
            issues.append("beta cohort requires consent")
        if not self.support_channel_ready:
            issues.append("beta cohort requires support channel readiness")
        if not self.rollback_supported:
            issues.append("beta cohort requires rollback support")
        return issues


@dataclass(frozen=True)
class FeedbackIntakeRule:
    channel: str
    severity: FeedbackSeverity
    triage_sla_hours: int
    owner: str
    escalation_required: bool
    evidence_path: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.channel:
            issues.append("feedback channel is required")
        if self.triage_sla_hours <= 0:
            issues.append("feedback triage SLA must be positive")
        if self.severity in {FeedbackSeverity.HIGH, FeedbackSeverity.CRITICAL} and not self.escalation_required:
            issues.append(f"{self.severity.value} feedback requires escalation")
        if not self.owner:
            issues.append("feedback owner is required")
        if not self.evidence_path.startswith("docs/beta_launch/"):
            issues.append("feedback evidence path must live under docs/beta_launch/")
        return issues


@dataclass(frozen=True)
class KnownIssue:
    issue_id: str
    severity: FeedbackSeverity
    summary: str
    owner: str
    workaround: str | None
    blocks_beta: bool
    accepted_for_beta: bool
    evidence_path: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.issue_id:
            issues.append("known issue_id is required")
        if not self.summary:
            issues.append("known issue summary is required")
        if not self.owner:
            issues.append("known issue owner is required")
        if self.severity in {FeedbackSeverity.HIGH, FeedbackSeverity.CRITICAL} and not self.blocks_beta and not self.accepted_for_beta:
            issues.append("high/critical known issues must block beta or be explicitly accepted")
        if self.accepted_for_beta and not self.workaround:
            issues.append("accepted beta known issue requires workaround")
        if not self.evidence_path.startswith("docs/beta_launch/"):
            issues.append("known issue evidence path must live under docs/beta_launch/")
        return issues


@dataclass(frozen=True)
class LaunchReadinessReview:
    review_id: str
    stage: BetaStage
    decision: LaunchDecision
    approvers: tuple[str, ...]
    reviewed_scope: bool
    reviewed_staging_acceptance: bool
    reviewed_known_issues: bool
    reviewed_support: bool
    reviewed_rollback: bool
    evidence_path: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.review_id:
            issues.append("launch readiness review_id is required")
        if not self.approvers:
            issues.append("launch readiness review requires approvers")
        for name, value in {
            "reviewed_scope": self.reviewed_scope,
            "reviewed_staging_acceptance": self.reviewed_staging_acceptance,
            "reviewed_known_issues": self.reviewed_known_issues,
            "reviewed_support": self.reviewed_support,
            "reviewed_rollback": self.reviewed_rollback,
        }.items():
            if not value:
                issues.append(f"{name} must be reviewed")
        if self.decision == LaunchDecision.GO and self.stage == BetaStage.GENERAL_AVAILABILITY:
            issues.append("general availability requires separate production launch approval")
        if not self.evidence_path.startswith("docs/beta_launch/"):
            issues.append("launch readiness evidence path must live under docs/beta_launch/")
        return issues


def compute_beta_launch_checksum(content: str) -> str:
    """Compute SHA-256 checksum for beta launch evidence."""

    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def summarize_acceptance_status(criteria: tuple[StagingAcceptanceCriterion, ...]) -> AcceptanceStatus:
    """Summarize staging acceptance criteria."""

    statuses = {criterion.status for criterion in criteria}
    if AcceptanceStatus.FAIL in statuses:
        return AcceptanceStatus.FAIL
    if AcceptanceStatus.BLOCKED in statuses:
        return AcceptanceStatus.BLOCKED
    if AcceptanceStatus.WAIVED in statuses:
        return AcceptanceStatus.WAIVED
    return AcceptanceStatus.PASS


def validate_beta_launch_bundle(
    entry_criteria: tuple[BetaEntryCriterion, ...],
    known_issues: tuple[KnownIssue, ...],
    review: LaunchReadinessReview,
) -> list[str]:
    """Validate beta launch bundle from entry criteria, issues, and review."""

    issues: list[str] = []
    for criterion in entry_criteria:
        issues.extend(criterion.validate())
    for issue in known_issues:
        issues.extend(issue.validate())
        if issue.blocks_beta:
            issues.append(f"{issue.issue_id} blocks beta launch")
    issues.extend(review.validate())
    return issues


DEFAULT_BETA_DECISION = BetaLaunchDecision(
    adr_path="docs/adr/ADR-018-beta-launch-staging-acceptance-product-scope.md",
    architecture_doc_path="docs/beta_launch/beta_launch_staging_acceptance_architecture_contract.md",
    beta_scope_required=True,
    staging_acceptance_required=True,
    entry_exit_criteria_required=True,
    cohort_controls_required=True,
    feedback_intake_required=True,
    known_issues_required=True,
    no_go_authority_required=True,
)

DEFAULT_PRODUCT_SCOPE = (
    ProductScopeItem("SCOPE-001", ProductScopeArea.LEARNER_ONBOARDING, "Learner onboarding flow included for controlled beta.", True, False, "product-owner", "docs/beta_launch/beta_product_scope_contract.md"),
    ProductScopeItem("SCOPE-002", ProductScopeArea.DIAGNOSTICS, "Diagnostics and mastery baseline included for controlled beta.", True, False, "product-owner", "docs/beta_launch/beta_product_scope_contract.md"),
    ProductScopeItem("SCOPE-003", ProductScopeArea.LESSON_GENERATION, "Lesson generation included with AI safety controls.", True, False, "ai-owner", "docs/beta_launch/beta_product_scope_contract.md"),
    ProductScopeItem("SCOPE-004", ProductScopeArea.BILLING_DISABLED, "Billing is explicitly disabled for beta launch.", False, True, "release-owner", "docs/beta_launch/beta_product_scope_contract.md"),
)

DEFAULT_STAGING_ACCEPTANCE = (
    StagingAcceptanceCriterion("ACC-001", "backend API smoke", AcceptanceStatus.PASS, "docs/operations/staging_smoke_evidence_manifest.md", "engineering", True),
    StagingAcceptanceCriterion("ACC-002", "frontend journey smoke", AcceptanceStatus.PASS, "docs/frontend/playwright_e2e_scaffold.md", "frontend-owner", True),
    StagingAcceptanceCriterion("ACC-003", "privacy and consent evidence", AcceptanceStatus.PASS, "docs/operations/beta_release_readiness_contract.md", "privacy-owner", True),
    StagingAcceptanceCriterion("ACC-004", "support handoff", AcceptanceStatus.PASS, "docs/operations_support/production_operations_handover_checklist.md", "support-owner", True),
)

DEFAULT_ENTRY_CRITERIA = (
    BetaEntryCriterion("ENTRY-001", "repository evidence checks pass", True, "scripts/check_beta_launch_staging_acceptance_production_readiness.py", "release-owner", True),
    BetaEntryCriterion("ENTRY-002", "known issues register reviewed", True, "docs/beta_launch/beta_known_issues_register.md", "release-owner", True),
    BetaEntryCriterion("ENTRY-003", "support channel ready", True, "docs/operations_support/support_sla_policy.md", "support-owner", True),
)

DEFAULT_EXIT_CRITERIA = (
    BetaExitCriterion("EXIT-001", "critical beta defects remain zero", False, "critical_defects", "0", "release-owner", "docs/beta_launch/beta_exit_criteria_contract.md"),
    BetaExitCriterion("EXIT-002", "support response SLA met", False, "support_sla_compliance", ">= 95%", "support-owner", "docs/beta_launch/beta_exit_criteria_contract.md"),
)

DEFAULT_COHORT = BetaCohortPlan(
    cohort_id="controlled-beta-001",
    stage=BetaStage.CONTROLLED_BETA,
    max_learners=100,
    max_guardians=100,
    allowed_grades=(8, 9),
    allowed_subjects=("Mathematics", "Natural Sciences"),
    consent_required=True,
    support_channel_ready=True,
    rollback_supported=True,
)

DEFAULT_FEEDBACK_RULES = (
    FeedbackIntakeRule("in-app feedback", FeedbackSeverity.LOW, 72, "support-owner", False, "docs/beta_launch/beta_feedback_intake_contract.md"),
    FeedbackIntakeRule("support email", FeedbackSeverity.MEDIUM, 48, "support-owner", False, "docs/beta_launch/beta_feedback_intake_contract.md"),
    FeedbackIntakeRule("incident escalation", FeedbackSeverity.HIGH, 24, "incident-commander", True, "docs/beta_launch/beta_feedback_intake_contract.md"),
    FeedbackIntakeRule("critical incident", FeedbackSeverity.CRITICAL, 4, "incident-commander", True, "docs/beta_launch/beta_feedback_intake_contract.md"),
)

DEFAULT_KNOWN_ISSUES = (
    KnownIssue("KI-001", FeedbackSeverity.LOW, "Cosmetic copy issue in beta checklist.", "product-owner", "manual copy review", False, True, "docs/beta_launch/beta_known_issues_register.md"),
)

DEFAULT_REVIEW = LaunchReadinessReview(
    review_id="BLR-001",
    stage=BetaStage.CONTROLLED_BETA,
    decision=LaunchDecision.CONDITIONAL_GO,
    approvers=("release-owner", "product-owner", "support-owner"),
    reviewed_scope=True,
    reviewed_staging_acceptance=True,
    reviewed_known_issues=True,
    reviewed_support=True,
    reviewed_rollback=True,
    evidence_path="docs/beta_launch/beta_launch_readiness_review.md",
)


def default_beta_launch_readiness_report() -> dict[str, object]:
    """Return deterministic beta launch/staging acceptance/product scope readiness evidence."""

    return {
        "decision_issues": DEFAULT_BETA_DECISION.validate(),
        "product_scope_issues": [issue for item in DEFAULT_PRODUCT_SCOPE for issue in item.validate()],
        "staging_acceptance_issues": [issue for criterion in DEFAULT_STAGING_ACCEPTANCE for issue in criterion.validate()],
        "entry_criteria_issues": [issue for criterion in DEFAULT_ENTRY_CRITERIA for issue in criterion.validate()],
        "exit_criteria_issues": [issue for criterion in DEFAULT_EXIT_CRITERIA for issue in criterion.validate()],
        "cohort_issues": DEFAULT_COHORT.validate(),
        "feedback_rule_issues": [issue for rule in DEFAULT_FEEDBACK_RULES for issue in rule.validate()],
        "known_issue_issues": [issue for issue in DEFAULT_KNOWN_ISSUES for issue in issue.validate()],
        "review_issues": DEFAULT_REVIEW.validate(),
        "launch_bundle_issues": validate_beta_launch_bundle(DEFAULT_ENTRY_CRITERIA, DEFAULT_KNOWN_ISSUES, DEFAULT_REVIEW),
        "acceptance_status_sample": summarize_acceptance_status(DEFAULT_STAGING_ACCEPTANCE).value,
        "checksum_sample": compute_beta_launch_checksum("beta-launch-evidence"),
    }
