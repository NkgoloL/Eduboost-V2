"""Repository-verifiable roadmap-after-production-readiness-baseline contracts.

These contracts do not create GitHub issues, modify a product roadmap tool, or
approve future scope. They model deterministic evidence for post-baseline
prioritization, deferred work, risk tracking, owner assignment, milestones, dependency
mapping, graduation criteria, and production-readiness baseline boundaries.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
import hashlib
import re


class RoadmapHorizon(str, Enum):
    NOW = "now"
    NEXT = "next"
    LATER = "later"
    PARKED = "parked"


class RoadmapCategory(str, Enum):
    PRODUCT = "product"
    ENGINEERING = "engineering"
    SECURITY = "security"
    PRIVACY = "privacy"
    AI_SAFETY = "ai_safety"
    INFRASTRUCTURE = "infrastructure"
    DATA = "data"
    OPERATIONS = "operations"
    COMMERCIAL = "commercial"
    RESEARCH = "research"


class RoadmapStatus(str, Enum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    DEFERRED = "deferred"
    BLOCKED = "blocked"
    DONE = "done"


class BaselineBoundary(str, Enum):
    INCLUDED = "included"
    DEFERRED = "deferred"
    EXCLUDED = "excluded"
    EXTERNAL_MANUAL = "external_manual"


class DependencyType(str, Enum):
    TECHNICAL = "technical"
    PRODUCT = "product"
    LEGAL = "legal"
    SECURITY = "security"
    OPERATIONAL = "operational"
    COMMERCIAL = "commercial"


class PriorityLevel(str, Enum):
    P0 = "p0"
    P1 = "p1"
    P2 = "p2"
    P3 = "p3"


@dataclass(frozen=True)
class RoadmapGovernanceDecision:
    adr_path: str
    architecture_doc_path: str
    roadmap_owner_required: bool
    deferred_scope_register_required: bool
    dependency_mapping_required: bool
    prioritization_required: bool
    graduation_criteria_required: bool
    baseline_boundary_required: bool
    review_cadence_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.adr_path.startswith("docs/adr/"):
            issues.append("roadmap governance decision must be documented in docs/adr/")
        if not self.architecture_doc_path.startswith("docs/roadmap/"):
            issues.append("roadmap architecture must be documented in docs/roadmap/")
        for name, value in {
            "roadmap_owner_required": self.roadmap_owner_required,
            "deferred_scope_register_required": self.deferred_scope_register_required,
            "dependency_mapping_required": self.dependency_mapping_required,
            "prioritization_required": self.prioritization_required,
            "graduation_criteria_required": self.graduation_criteria_required,
            "baseline_boundary_required": self.baseline_boundary_required,
            "review_cadence_required": self.review_cadence_required,
        }.items():
            if not value:
                issues.append(f"{name} is required")
        return issues


@dataclass(frozen=True)
class BaselineBoundaryItem:
    boundary_id: str
    area: RoadmapCategory
    title: str
    boundary: BaselineBoundary
    rationale: str
    evidence_path: str
    owner: str
    manual_dependency: str | None = None

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.boundary_id:
            issues.append("boundary_id is required")
        if not self.title:
            issues.append("baseline boundary title is required")
        if not self.rationale:
            issues.append("baseline boundary rationale is required")
        if not self.evidence_path.startswith(("docs/", "scripts/", "tests/", ".github/", "Makefile")):
            issues.append("baseline boundary evidence path must be controlled")
        if not self.owner:
            issues.append("baseline boundary owner is required")
        if self.boundary == BaselineBoundary.EXTERNAL_MANUAL and not self.manual_dependency:
            issues.append("external/manual boundary requires manual dependency")
        return issues


@dataclass(frozen=True)
class RoadmapItem:
    roadmap_id: str
    title: str
    category: RoadmapCategory
    horizon: RoadmapHorizon
    status: RoadmapStatus
    priority: PriorityLevel
    owner: str
    rationale: str
    expected_outcome: str
    evidence_path: str
    target_quarter: str | None = None

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not re.fullmatch(r"RM-\d{3}", self.roadmap_id):
            issues.append("roadmap_id must follow RM-### format")
        if not self.title:
            issues.append("roadmap item title is required")
        if not self.owner:
            issues.append("roadmap owner is required")
        if not self.rationale:
            issues.append("roadmap rationale is required")
        if not self.expected_outcome:
            issues.append("roadmap expected outcome is required")
        if self.priority in {PriorityLevel.P0, PriorityLevel.P1} and self.horizon == RoadmapHorizon.PARKED:
            issues.append("P0/P1 items cannot be parked")
        if self.status == RoadmapStatus.IN_PROGRESS and self.horizon not in {RoadmapHorizon.NOW, RoadmapHorizon.NEXT}:
            issues.append("in-progress items must be now or next")
        if not self.evidence_path.startswith("docs/roadmap/"):
            issues.append("roadmap evidence path must live under docs/roadmap/")
        if self.horizon in {RoadmapHorizon.NOW, RoadmapHorizon.NEXT} and not self.target_quarter:
            issues.append("now/next roadmap items require target quarter")
        return issues


@dataclass(frozen=True)
class DeferredScopeItem:
    deferred_id: str
    title: str
    category: RoadmapCategory
    reason_deferred: str
    unblock_condition: str
    owner: str
    risk_if_deferred: str
    evidence_path: str
    review_date: date

    def validate(self, today: date) -> list[str]:
        issues: list[str] = []
        if not re.fullmatch(r"DEF-\d{3}", self.deferred_id):
            issues.append("deferred_id must follow DEF-### format")
        if not self.title:
            issues.append("deferred title is required")
        if not self.reason_deferred:
            issues.append("deferred reason is required")
        if not self.unblock_condition:
            issues.append("unblock condition is required")
        if not self.owner:
            issues.append("deferred scope owner is required")
        if not self.risk_if_deferred:
            issues.append("risk if deferred is required")
        if not self.evidence_path.startswith("docs/roadmap/"):
            issues.append("deferred scope evidence path must live under docs/roadmap/")
        if self.review_date < today:
            issues.append("deferred scope review date is stale")
        return issues


@dataclass(frozen=True)
class RoadmapDependency:
    dependency_id: str
    source_roadmap_id: str
    dependency_type: DependencyType
    description: str
    owner: str
    external: bool
    mitigation: str
    evidence_path: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not re.fullmatch(r"DEP-\d{3}", self.dependency_id):
            issues.append("dependency_id must follow DEP-### format")
        if not re.fullmatch(r"RM-\d{3}", self.source_roadmap_id):
            issues.append("source_roadmap_id must follow RM-### format")
        if not self.description:
            issues.append("dependency description is required")
        if not self.owner:
            issues.append("dependency owner is required")
        if self.external and not self.mitigation:
            issues.append("external dependencies require mitigation")
        if not self.evidence_path.startswith("docs/roadmap/"):
            issues.append("roadmap dependency evidence path must live under docs/roadmap/")
        return issues


@dataclass(frozen=True)
class GraduationCriterion:
    criterion_id: str
    roadmap_id: str
    metric_name: str
    threshold: str
    evidence_path: str
    owner: str
    required_for_ga: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not re.fullmatch(r"GRAD-\d{3}", self.criterion_id):
            issues.append("criterion_id must follow GRAD-### format")
        if not re.fullmatch(r"RM-\d{3}", self.roadmap_id):
            issues.append("roadmap_id must follow RM-### format")
        if not self.metric_name:
            issues.append("graduation metric name is required")
        if not self.threshold:
            issues.append("graduation threshold is required")
        if not self.evidence_path.startswith(("docs/", "artifacts/")):
            issues.append("graduation evidence path must be controlled")
        if not self.owner:
            issues.append("graduation criterion owner is required")
        if self.required_for_ga and self.metric_name in {"", "undefined"}:
            issues.append("GA-required graduation criterion must define metric")
        return issues


@dataclass(frozen=True)
class RoadmapReviewCadence:
    cadence_id: str
    frequency_days: int
    owner: str
    required_inputs: tuple[str, ...]
    required_outputs: tuple[str, ...]
    evidence_path: str
    blocks_scope_expansion: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.cadence_id:
            issues.append("cadence_id is required")
        if self.frequency_days <= 0:
            issues.append("roadmap review frequency must be positive")
        if self.frequency_days > 90:
            issues.append("roadmap review cadence must be at least quarterly")
        if not self.owner:
            issues.append("roadmap review owner is required")
        if not self.required_inputs:
            issues.append("roadmap review requires inputs")
        if not self.required_outputs:
            issues.append("roadmap review requires outputs")
        if not self.evidence_path.startswith("docs/roadmap/"):
            issues.append("roadmap review evidence path must live under docs/roadmap/")
        if not self.blocks_scope_expansion:
            issues.append("roadmap review must block uncontrolled scope expansion")
        return issues


@dataclass(frozen=True)
class PostBaselineRisk:
    risk_id: str
    title: str
    category: RoadmapCategory
    impact: str
    likelihood: str
    owner: str
    mitigation: str
    evidence_path: str
    blocks_ga: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not re.fullmatch(r"RISK-\d{3}", self.risk_id):
            issues.append("risk_id must follow RISK-### format")
        if not self.title:
            issues.append("risk title is required")
        if self.impact not in {"low", "medium", "high", "critical"}:
            issues.append("risk impact is invalid")
        if self.likelihood not in {"low", "medium", "high"}:
            issues.append("risk likelihood is invalid")
        if not self.owner:
            issues.append("risk owner is required")
        if not self.mitigation:
            issues.append("risk mitigation is required")
        if not self.evidence_path.startswith("docs/roadmap/"):
            issues.append("risk evidence path must live under docs/roadmap/")
        if self.impact == "critical" and not self.blocks_ga:
            issues.append("critical post-baseline risk must block GA")
        return issues


def compute_roadmap_checksum(content: str) -> str:
    """Compute SHA-256 checksum for roadmap evidence."""

    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def summarize_roadmap_horizons(items: tuple[RoadmapItem, ...]) -> dict[str, int]:
    """Summarize roadmap items by planning horizon."""

    summary = {horizon.value: 0 for horizon in RoadmapHorizon}
    for item in items:
        summary[item.horizon.value] += 1
    return summary


def validate_roadmap_bundle(
    roadmap_items: tuple[RoadmapItem, ...],
    deferred_items: tuple[DeferredScopeItem, ...],
    dependencies: tuple[RoadmapDependency, ...],
    today: date,
) -> list[str]:
    """Validate the post-baseline roadmap bundle."""

    issues: list[str] = []
    roadmap_ids = {item.roadmap_id for item in roadmap_items}
    for item in roadmap_items:
        issues.extend(item.validate())
    for item in deferred_items:
        issues.extend(item.validate(today))
    for dependency in dependencies:
        issues.extend(dependency.validate())
        if dependency.source_roadmap_id not in roadmap_ids:
            issues.append(f"{dependency.dependency_id} references unknown roadmap item")
    return issues


_SAMPLE_DATE = date(2026, 1, 1)

DEFAULT_ROADMAP_DECISION = RoadmapGovernanceDecision(
    adr_path="docs/adr/ADR-019-roadmap-after-production-readiness-baseline.md",
    architecture_doc_path="docs/roadmap/post_baseline_roadmap_architecture_contract.md",
    roadmap_owner_required=True,
    deferred_scope_register_required=True,
    dependency_mapping_required=True,
    prioritization_required=True,
    graduation_criteria_required=True,
    baseline_boundary_required=True,
    review_cadence_required=True,
)

DEFAULT_BASELINE_BOUNDARIES = (
    BaselineBoundaryItem("BOUND-001", RoadmapCategory.ENGINEERING, "Repository evidence baseline", BaselineBoundary.INCLUDED, "Repo-side production-readiness evidence is included in baseline.", "docs/project_status.md", "release-owner"),
    BaselineBoundaryItem("BOUND-002", RoadmapCategory.COMMERCIAL, "Live billing launch", BaselineBoundary.DEFERRED, "Live billing requires provider setup and commercial approval.", "docs/billing/production_billing_provider_architecture_contract.md", "commercial-owner"),
    BaselineBoundaryItem("BOUND-003", RoadmapCategory.OPERATIONS, "External branch protection verification", BaselineBoundary.EXTERNAL_MANUAL, "GitHub settings require external verification.", "docs/documentation/production_claim_boundary_policy.md", "release-owner", "GitHub repository settings"),
)

DEFAULT_ROADMAP_ITEMS = (
    RoadmapItem("RM-001", "Live billing provider integration", RoadmapCategory.COMMERCIAL, RoadmapHorizon.NEXT, RoadmapStatus.ACCEPTED, PriorityLevel.P1, "commercial-owner", "Billing is disabled in beta and requires provider integration after baseline.", "Provider-backed subscriptions can be tested safely.", "docs/roadmap/post_baseline_roadmap_register.md", "2026-Q2"),
    RoadmapItem("RM-002", "Production telemetry dashboard implementation", RoadmapCategory.OPERATIONS, RoadmapHorizon.NEXT, RoadmapStatus.ACCEPTED, PriorityLevel.P1, "operations-owner", "Repository contracts exist; live dashboards require provider configuration.", "Operators can monitor production SLOs.", "docs/roadmap/post_baseline_roadmap_register.md", "2026-Q2"),
    RoadmapItem("RM-003", "Advanced mastery-model research", RoadmapCategory.RESEARCH, RoadmapHorizon.LATER, RoadmapStatus.PROPOSED, PriorityLevel.P2, "data-owner", "BKT/DKT require sufficient post-beta usage data.", "Learning science model roadmap is evidence-driven.", "docs/roadmap/post_baseline_roadmap_register.md"),
    RoadmapItem("RM-004", "Public beta expansion", RoadmapCategory.PRODUCT, RoadmapHorizon.LATER, RoadmapStatus.PROPOSED, PriorityLevel.P2, "product-owner", "Controlled beta outcomes should drive expansion.", "Expansion decision is based on beta exit criteria.", "docs/roadmap/post_baseline_roadmap_register.md"),
)

DEFAULT_DEFERRED_SCOPE = (
    DeferredScopeItem("DEF-001", "Live payment processing", RoadmapCategory.COMMERCIAL, "Payment provider credentials and approvals are external to repository evidence.", "Provider account, pricing approval, and legal/commercial signoff complete.", "commercial-owner", "Revenue flows remain disabled until integration.", "docs/roadmap/deferred_scope_register.md", date(2026, 6, 30)),
    DeferredScopeItem("DEF-002", "General availability launch", RoadmapCategory.PRODUCT, "GA requires beta outcome evidence and manual launch approval.", "Beta exit criteria met and production launch approval completed.", "release-owner", "Public launch remains blocked until beta evidence exists.", "docs/roadmap/deferred_scope_register.md", date(2026, 6, 30)),
)

DEFAULT_DEPENDENCIES = (
    RoadmapDependency("DEP-001", "RM-001", DependencyType.COMMERCIAL, "Billing provider account and pricing approval.", "commercial-owner", True, "Keep billing disabled until provider contract is active.", "docs/roadmap/roadmap_dependency_register.md"),
    RoadmapDependency("DEP-002", "RM-002", DependencyType.OPERATIONAL, "Telemetry provider credentials and dashboard workspace.", "operations-owner", True, "Use repository contracts and staging evidence until live configuration exists.", "docs/roadmap/roadmap_dependency_register.md"),
    RoadmapDependency("DEP-003", "RM-003", DependencyType.TECHNICAL, "Sufficient anonymized post-beta learning events.", "data-owner", False, "Use diagnostics baseline until sample size is enough.", "docs/roadmap/roadmap_dependency_register.md"),
)

DEFAULT_GRADUATION_CRITERIA = (
    GraduationCriterion("GRAD-001", "RM-001", "billing_webhook_success_rate", ">= 99%", "docs/roadmap/roadmap_graduation_criteria.md", "commercial-owner", True),
    GraduationCriterion("GRAD-002", "RM-002", "dashboard_alert_route_coverage", "100%", "docs/roadmap/roadmap_graduation_criteria.md", "operations-owner", True),
    GraduationCriterion("GRAD-003", "RM-004", "beta_exit_criteria_passed", "all required criteria pass", "docs/beta_launch/post_beta_review_contract.md", "product-owner", True),
)

DEFAULT_REVIEW_CADENCE = RoadmapReviewCadence(
    cadence_id="roadmap-quarterly-review",
    frequency_days=60,
    owner="release-owner",
    required_inputs=("beta feedback", "known issues", "security findings", "support metrics", "operations metrics"),
    required_outputs=("updated roadmap register", "deferred scope register", "risk register", "owner assignments"),
    evidence_path="docs/roadmap/roadmap_review_cadence_contract.md",
    blocks_scope_expansion=True,
)

DEFAULT_POST_BASELINE_RISKS = (
    PostBaselineRisk("RISK-001", "External approvals lag repository readiness", RoadmapCategory.OPERATIONS, "medium", "medium", "release-owner", "Track external/manual approval dependencies explicitly.", "docs/roadmap/post_baseline_risk_register.md", False),
    PostBaselineRisk("RISK-002", "Live billing complexity delays monetization", RoadmapCategory.COMMERCIAL, "high", "medium", "commercial-owner", "Keep beta billing disabled and stage provider integration separately.", "docs/roadmap/post_baseline_risk_register.md", False),
)


def default_post_baseline_roadmap_readiness_report() -> dict[str, object]:
    """Return deterministic post-baseline roadmap readiness evidence."""

    return {
        "decision_issues": DEFAULT_ROADMAP_DECISION.validate(),
        "baseline_boundary_issues": [issue for item in DEFAULT_BASELINE_BOUNDARIES for issue in item.validate()],
        "roadmap_item_issues": [issue for item in DEFAULT_ROADMAP_ITEMS for issue in item.validate()],
        "deferred_scope_issues": [issue for item in DEFAULT_DEFERRED_SCOPE for issue in item.validate(_SAMPLE_DATE)],
        "dependency_issues": [issue for dependency in DEFAULT_DEPENDENCIES for issue in dependency.validate()],
        "graduation_criteria_issues": [issue for criterion in DEFAULT_GRADUATION_CRITERIA for issue in criterion.validate()],
        "review_cadence_issues": DEFAULT_REVIEW_CADENCE.validate(),
        "post_baseline_risk_issues": [issue for risk in DEFAULT_POST_BASELINE_RISKS for issue in risk.validate()],
        "roadmap_bundle_issues": validate_roadmap_bundle(DEFAULT_ROADMAP_ITEMS, DEFAULT_DEFERRED_SCOPE, DEFAULT_DEPENDENCIES, _SAMPLE_DATE),
        "horizon_summary": summarize_roadmap_horizons(DEFAULT_ROADMAP_ITEMS),
        "checksum_sample": compute_roadmap_checksum("post-baseline-roadmap-evidence"),
    }
