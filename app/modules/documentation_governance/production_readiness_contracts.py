"""Repository-verifiable documentation, ADR, and claim-discipline contracts."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
import hashlib
import re


class DocumentationAudience(str, Enum):
    DEVELOPER = "developer"
    OPERATOR = "operator"
    REVIEWER = "reviewer"
    SUPPORT = "support"
    PRIVACY = "privacy"
    SECURITY = "security"
    PRODUCT = "product"
    END_USER = "end_user"


class DocumentationStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class AdrStatus(str, Enum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"


class ClaimType(str, Enum):
    REPOSITORY_EVIDENCE = "repository_evidence"
    MANUAL_APPROVAL = "manual_approval"
    EXTERNAL_SYSTEM = "external_system"
    PRODUCTION_RUNTIME = "production_runtime"
    LEGAL_REVIEW = "legal_review"
    SECURITY_REVIEW = "security_review"


class ClaimConfidence(str, Enum):
    VERIFIED = "verified"
    VERIFY_PENDING = "verify_pending"
    MANUAL_ONLY = "manual_only"
    UNSUPPORTED = "unsupported"


class ReleaseNoteType(str, Enum):
    FEATURE = "feature"
    FIX = "fix"
    SECURITY = "security"
    BREAKING_CHANGE = "breaking_change"
    OPERATIONS = "operations"
    DOCS = "docs"


@dataclass(frozen=True)
class DocumentationGovernanceDecision:
    adr_path: str
    architecture_doc_path: str
    adr_lifecycle_required: bool
    claim_discipline_required: bool
    stale_doc_review_required: bool
    docs_owner_required: bool
    release_notes_required: bool
    external_claim_boundary_required: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.adr_path.startswith("docs/adr/"):
            issues.append("documentation governance decision must be documented in docs/adr/")
        if not self.architecture_doc_path.startswith("docs/documentation/"):
            issues.append("documentation architecture must be documented in docs/documentation/")
        for name, value in {
            "adr_lifecycle_required": self.adr_lifecycle_required,
            "claim_discipline_required": self.claim_discipline_required,
            "stale_doc_review_required": self.stale_doc_review_required,
            "docs_owner_required": self.docs_owner_required,
            "release_notes_required": self.release_notes_required,
            "external_claim_boundary_required": self.external_claim_boundary_required,
        }.items():
            if not value:
                issues.append(f"{name} is required")
        return issues


@dataclass(frozen=True)
class DocumentationInventoryEntry:
    path: str
    title: str
    audience: DocumentationAudience
    status: DocumentationStatus
    owner: str
    reviewed_on: date
    review_interval_days: int
    source_of_truth: bool
    supersedes: str | None = None

    def validate(self, today: date) -> list[str]:
        issues: list[str] = []
        if not self.path.startswith("docs/"):
            issues.append("documentation path must live under docs/")
        if not self.title:
            issues.append("documentation title is required")
        if not self.owner:
            issues.append("documentation owner is required")
        if self.review_interval_days <= 0:
            issues.append("review interval must be positive")
        if self.status == DocumentationStatus.ACTIVE and (today - self.reviewed_on).days > self.review_interval_days:
            issues.append(f"{self.path} is stale")
        if self.status == DocumentationStatus.SUPERSEDED and not self.supersedes:
            issues.append("superseded documentation must identify replacement or successor")
        if self.status == DocumentationStatus.ACTIVE and not self.source_of_truth and self.audience in {DocumentationAudience.OPERATOR, DocumentationAudience.SECURITY, DocumentationAudience.PRIVACY}:
            issues.append("active operator/security/privacy docs must identify source-of-truth status")
        return issues


@dataclass(frozen=True)
class AdrRecord:
    adr_id: str
    path: str
    title: str
    status: AdrStatus
    decision_date: date
    owner: str
    context_present: bool
    decision_present: bool
    consequences_present: bool
    superseded_by: str | None = None

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not re.fullmatch(r"ADR-\d{3}", self.adr_id):
            issues.append("ADR ID must follow ADR-### format")
        if not self.path.startswith("docs/adr/"):
            issues.append("ADR path must live under docs/adr/")
        if not self.title:
            issues.append("ADR title is required")
        if not self.owner:
            issues.append("ADR owner is required")
        if self.status == AdrStatus.ACCEPTED and not self.decision_present:
            issues.append("accepted ADR requires decision section")
        if not self.context_present:
            issues.append("ADR context section is required")
        if not self.consequences_present:
            issues.append("ADR consequences section is required")
        if self.status == AdrStatus.SUPERSEDED and not self.superseded_by:
            issues.append("superseded ADR must identify successor")
        return issues


@dataclass(frozen=True)
class ClaimRecord:
    claim_id: str
    claim_text: str
    claim_type: ClaimType
    confidence: ClaimConfidence
    evidence_paths: tuple[str, ...]
    owner: str
    external_dependency: str | None
    production_claim: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.claim_id:
            issues.append("claim_id is required")
        if not self.claim_text:
            issues.append("claim_text is required")
        if not self.owner:
            issues.append("claim owner is required")
        if self.confidence == ClaimConfidence.VERIFIED and not self.evidence_paths:
            issues.append("verified claims require evidence paths")
        for path in self.evidence_paths:
            if not path.startswith(("docs/", "scripts/", "tests/", ".github/", "Makefile")):
                issues.append("claim evidence path must be controlled")
        if self.claim_type in {ClaimType.EXTERNAL_SYSTEM, ClaimType.MANUAL_APPROVAL, ClaimType.LEGAL_REVIEW, ClaimType.SECURITY_REVIEW} and not self.external_dependency:
            issues.append("external/manual/legal/security claims require external dependency note")
        if self.production_claim and self.confidence != ClaimConfidence.VERIFIED:
            issues.append("production claims must be verified or clearly excluded")
        if self.confidence == ClaimConfidence.UNSUPPORTED:
            issues.append("unsupported claims are not allowed in production readiness evidence")
        return issues


@dataclass(frozen=True)
class ClaimDisciplineRule:
    rule_id: str
    description: str
    prohibited_phrases: tuple[str, ...]
    required_boundary_phrase: str
    applies_to_paths: tuple[str, ...]
    blocks_release: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.rule_id:
            issues.append("claim discipline rule_id is required")
        if not self.description:
            issues.append("claim discipline description is required")
        if not self.prohibited_phrases:
            issues.append("prohibited phrases are required")
        if not self.required_boundary_phrase:
            issues.append("required boundary phrase is required")
        if not self.applies_to_paths:
            issues.append("claim discipline path scope is required")
        if not self.blocks_release:
            issues.append("claim discipline violations must block release")
        return issues


@dataclass(frozen=True)
class ReleaseNoteEntry:
    entry_id: str
    release_note_type: ReleaseNoteType
    summary: str
    evidence_path: str
    breaking_change: bool
    migration_required: bool
    user_visible: bool
    owner: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.entry_id:
            issues.append("release note entry_id is required")
        if not self.summary:
            issues.append("release note summary is required")
        if not self.evidence_path.startswith(("docs/", "scripts/", "tests/", ".github/", "Makefile")):
            issues.append("release note evidence path must be controlled")
        if self.breaking_change and self.release_note_type != ReleaseNoteType.BREAKING_CHANGE:
            issues.append("breaking changes must use breaking_change release note type")
        if self.migration_required and self.release_note_type not in {ReleaseNoteType.BREAKING_CHANGE, ReleaseNoteType.OPERATIONS}:
            issues.append("migration-required notes must be breaking_change or operations")
        if not self.owner:
            issues.append("release note owner is required")
        return issues


@dataclass(frozen=True)
class StaleDocumentationFinding:
    finding_id: str
    path: str
    days_stale: int
    owner: str
    severity: str
    action_required: str
    blocks_release: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.finding_id:
            issues.append("stale documentation finding_id is required")
        if not self.path.startswith("docs/"):
            issues.append("stale documentation path must live under docs/")
        if self.days_stale < 0:
            issues.append("days_stale cannot be negative")
        if not self.owner:
            issues.append("stale documentation owner is required")
        if self.severity not in {"low", "medium", "high", "release_blocker"}:
            issues.append("stale documentation severity is invalid")
        if not self.action_required:
            issues.append("stale documentation action is required")
        if self.severity == "release_blocker" and not self.blocks_release:
            issues.append("release_blocker stale docs must block release")
        return issues


@dataclass(frozen=True)
class DocumentationReviewGate:
    gate_id: str
    release_stage: str
    required_docs: tuple[str, ...]
    required_adrs: tuple[str, ...]
    claim_review_required: bool
    stale_doc_review_required: bool
    release_notes_required: bool
    owner: str
    blocks_release: bool

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.gate_id:
            issues.append("documentation review gate_id is required")
        if not self.required_docs:
            issues.append("documentation review gate requires docs")
        if not self.required_adrs:
            issues.append("documentation review gate requires ADRs")
        for path in self.required_docs:
            if not path.startswith("docs/"):
                issues.append("required documentation must live under docs/")
        for path in self.required_adrs:
            if not path.startswith("docs/adr/"):
                issues.append("required ADRs must live under docs/adr/")
        if not self.claim_review_required:
            issues.append("claim review is required")
        if not self.stale_doc_review_required:
            issues.append("stale documentation review is required")
        if not self.release_notes_required:
            issues.append("release notes are required")
        if not self.owner:
            issues.append("documentation review gate owner is required")
        if not self.blocks_release:
            issues.append("documentation review gate must block release")
        return issues


def compute_documentation_checksum(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def contains_unbounded_production_claim(text: str) -> bool:
    lowered = (text or "").lower()
    broad_claim = any(phrase in lowered for phrase in ("production ready", "fully complete", "guaranteed", "launch approved"))
    boundary = any(phrase in lowered for phrase in ("repository-side", "manual approval", "does not authorize", "verification boundary"))
    return broad_claim and not boundary


def normalize_doc_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (title or "").strip().lower()).strip("-")


def validate_claims_for_release(claims: tuple[ClaimRecord, ...]) -> list[str]:
    issues: list[str] = []
    for claim in claims:
        issues.extend(claim.validate())
        if contains_unbounded_production_claim(claim.claim_text):
            issues.append(f"{claim.claim_id} contains unbounded production claim")
    return issues


_SAMPLE_DATE = date(2026, 1, 1)

DEFAULT_DOCUMENTATION_DECISION = DocumentationGovernanceDecision(
    "docs/adr/ADR-017-documentation-adrs-claim-discipline.md",
    "docs/documentation/documentation_adrs_claim_discipline_architecture_contract.md",
    True, True, True, True, True, True,
)

DEFAULT_DOC_INVENTORY = (
    DocumentationInventoryEntry("docs/documentation/documentation_adrs_claim_discipline_architecture_contract.md", "Documentation ADRs Claim Discipline Architecture Contract", DocumentationAudience.REVIEWER, DocumentationStatus.ACTIVE, "release-owner", _SAMPLE_DATE, 365, True),
    DocumentationInventoryEntry("docs/security/security_posture_architecture_contract.md", "Security Posture Architecture Contract", DocumentationAudience.SECURITY, DocumentationStatus.ACTIVE, "security-owner", _SAMPLE_DATE, 365, True),
    DocumentationInventoryEntry("docs/operations_support/production_operations_handover_checklist.md", "Production Operations Handover Checklist", DocumentationAudience.OPERATOR, DocumentationStatus.ACTIVE, "support-owner", _SAMPLE_DATE, 365, True),
)

DEFAULT_ADRS = (
    AdrRecord("ADR-017", "docs/adr/ADR-017-documentation-adrs-claim-discipline.md", "Documentation, ADRs, and Claim Discipline", AdrStatus.ACCEPTED, _SAMPLE_DATE, "release-owner", True, True, True),
    AdrRecord("ADR-015", "docs/adr/ADR-015-security-posture-threat-modeling.md", "Security Posture and Threat Modeling", AdrStatus.ACCEPTED, _SAMPLE_DATE, "security-owner", True, True, True),
)

DEFAULT_CLAIMS = (
    ClaimRecord("CLAIM-001", "Repository-side documentation governance evidence is present and verified by scripts/check_documentation_adrs_claim_discipline_production_readiness.py.", ClaimType.REPOSITORY_EVIDENCE, ClaimConfidence.VERIFIED, ("scripts/check_documentation_adrs_claim_discipline_production_readiness.py", "docs/documentation/documentation_adrs_claim_discipline_architecture_contract.md"), "release-owner", None, False),
    ClaimRecord("CLAIM-002", "Manual branch protection configuration requires external GitHub verification before production launch.", ClaimType.EXTERNAL_SYSTEM, ClaimConfidence.MANUAL_ONLY, (), "release-owner", "GitHub repository settings", False),
)

DEFAULT_CLAIM_RULES = (
    ClaimDisciplineRule("CD-001", "Prevent unbounded launch and production-readiness claims.", ("fully complete", "guaranteed", "launch approved", "production ready"), "This repository-side evidence does not authorize production launch.", ("docs/", "README.md", "PR_INTEGRATION_SUMMARY.md"), True),
)

DEFAULT_RELEASE_NOTES = (
    ReleaseNoteEntry("RN-001", ReleaseNoteType.DOCS, "Add documentation, ADR, and claim-discipline readiness evidence.", "docs/documentation/documentation_adrs_claim_discipline_architecture_contract.md", False, False, False, "release-owner"),
    ReleaseNoteEntry("RN-002", ReleaseNoteType.OPERATIONS, "Add production documentation review gate and release-note expectations.", "docs/documentation/documentation_review_gate_contract.md", False, True, False, "release-owner"),
)

DEFAULT_STALE_FINDINGS = (
    StaleDocumentationFinding("STALE-001", "docs/documentation/stale_documentation_review_register.md", 0, "release-owner", "low", "track current documentation review date", False),
)

DEFAULT_REVIEW_GATE = DocumentationReviewGate(
    "documentation-release-review",
    "production",
    ("docs/documentation/documentation_adrs_claim_discipline_architecture_contract.md", "docs/documentation/claim_discipline_contract.md", "docs/documentation/documentation_review_gate_contract.md"),
    ("docs/adr/ADR-017-documentation-adrs-claim-discipline.md",),
    True, True, True, "release-owner", True,
)


def default_documentation_governance_readiness_report() -> dict[str, object]:
    bounded_claim = "Repository-side production readiness evidence is present; this does not authorize production launch."
    unbounded_claim = "The platform is production ready."
    return {
        "decision_issues": DEFAULT_DOCUMENTATION_DECISION.validate(),
        "documentation_inventory_issues": [issue for entry in DEFAULT_DOC_INVENTORY for issue in entry.validate(_SAMPLE_DATE)],
        "adr_issues": [issue for adr in DEFAULT_ADRS for issue in adr.validate()],
        "claim_issues": validate_claims_for_release(DEFAULT_CLAIMS),
        "claim_rule_issues": [issue for rule in DEFAULT_CLAIM_RULES for issue in rule.validate()],
        "release_note_issues": [issue for note in DEFAULT_RELEASE_NOTES for issue in note.validate()],
        "stale_finding_issues": [issue for finding in DEFAULT_STALE_FINDINGS for issue in finding.validate()],
        "review_gate_issues": DEFAULT_REVIEW_GATE.validate(),
        "bounded_claim_sample": contains_unbounded_production_claim(bounded_claim),
        "unbounded_claim_sample": contains_unbounded_production_claim(unbounded_claim),
        "normalized_title_sample": normalize_doc_title("Documentation, ADRs, and Claim Discipline"),
        "checksum_sample": compute_documentation_checksum("documentation-governance-evidence"),
    }
