#!/usr/bin/env python3
"""Validate production-readiness item 17: documentation, ADRs, and claim discipline."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.modules.documentation_governance.production_readiness_contracts import default_documentation_governance_readiness_report


REQUIRED_FILES = (
    "app/modules/documentation_governance/__init__.py",
    "app/modules/documentation_governance/production_readiness_contracts.py",
    "docs/adr/ADR-017-documentation-adrs-claim-discipline.md",
    "docs/documentation/documentation_adrs_claim_discipline_architecture_contract.md",
    "docs/documentation/adr_lifecycle_contract.md",
    "docs/documentation/claim_discipline_contract.md",
    "docs/documentation/documentation_inventory_contract.md",
    "docs/documentation/stale_documentation_review_register.md",
    "docs/documentation/release_notes_discipline_contract.md",
    "docs/documentation/documentation_review_gate_contract.md",
    "docs/documentation/production_claim_boundary_policy.md",
    "docs/backlog/production_readiness/17_documentation_adrs_and_claim_discipline.md",
    "tests/unit/test_documentation_adrs_claim_discipline_production_readiness.py",
)

CONTENT_REQUIREMENTS = {
    "app/modules/documentation_governance/production_readiness_contracts.py": (
        "class DocumentationAudience", "class DocumentationStatus", "class AdrStatus", "class ClaimType",
        "class ClaimConfidence", "class ReleaseNoteType", "DocumentationGovernanceDecision",
        "DocumentationInventoryEntry", "AdrRecord", "ClaimRecord", "ClaimDisciplineRule",
        "ReleaseNoteEntry", "StaleDocumentationFinding", "DocumentationReviewGate",
        "compute_documentation_checksum", "contains_unbounded_production_claim",
        "normalize_doc_title", "validate_claims_for_release", "default_documentation_governance_readiness_report",
    ),
    "docs/adr/ADR-017-documentation-adrs-claim-discipline.md": (
        "Documentation, ADRs, and Claim Discipline",
        "Production-readiness claims must distinguish repository-side evidence from external/manual approvals",
        "ADRs must preserve context, decision, and consequences",
        "This repository-side evidence does not authorize production launch",
    ),
    "docs/documentation/documentation_adrs_claim_discipline_architecture_contract.md": (
        "Documentation ADRs Claim Discipline Architecture Contract", "documentation inventory", "documentation owner",
        "ADR ID", "ADR status", "claim ID", "external dependency note", "boundary phrase for repository-side evidence",
    ),
    "docs/documentation/adr_lifecycle_contract.md": (
        "ADR Lifecycle Contract", "accepted ADR requires decision section", "ADR context section is required",
        "ADR consequences section is required", "superseded ADR must identify successor", "ADR ID must follow ADR-### format",
    ),
    "docs/documentation/claim_discipline_contract.md": (
        "Claim Discipline Contract", "verified claims require evidence paths", "external claims require external dependency note",
        "unsupported claims are not allowed in production readiness evidence", "production claims must be verified or clearly excluded",
        "This repository-side evidence does not authorize production launch",
    ),
    "docs/documentation/documentation_inventory_contract.md": (
        "Documentation Inventory Contract", "documentation path must live under docs/", "documentation owner is required",
        "active operator docs must identify source-of-truth status", "superseded documentation must identify replacement or successor",
    ),
    "docs/documentation/stale_documentation_review_register.md": (
        "Stale Documentation Review Register", "days stale cannot be negative", "stale documentation owner is required",
        "release blocker stale docs must block release",
    ),
    "docs/documentation/release_notes_discipline_contract.md": (
        "Release Notes Discipline Contract", "breaking changes must use breaking_change release note type",
        "migration-required notes must be breaking_change or operations", "release note owner is required",
    ),
    "docs/documentation/documentation_review_gate_contract.md": (
        "Documentation Review Gate Contract", "documentation review gate requires docs", "documentation review gate requires ADRs",
        "claim review is required", "stale documentation review is required", "documentation review gate must block release",
    ),
    "docs/documentation/production_claim_boundary_policy.md": (
        "Production Claim Boundary Policy", "repository-side evidence must be labeled as repository-side evidence",
        "manual approvals must be labeled as manual approvals", "external system settings must identify the external system",
        "unsupported claims are not allowed", "This repository-side evidence does not authorize production launch",
    ),
    "docs/backlog/production_readiness/17_documentation_adrs_and_claim_discipline.md": (
        "17.6 Repository-side implementation evidence", "docs/documentation/documentation_adrs_claim_discipline_architecture_contract.md",
        "scripts/check_documentation_adrs_claim_discipline_production_readiness.py",
        "make documentation-adrs-claim-discipline-production-readiness-check",
    ),
    "Makefile": (
        "documentation-adrs-claim-discipline-production-readiness-check:",
        "scripts/check_documentation_adrs_claim_discipline_production_readiness.py",
    ),
}


@dataclass(frozen=True)
class DocumentationGovernanceReadinessResult:
    target: str
    ok: bool
    detail: str


def _read(rel_path: str) -> str:
    path = REPO_ROOT / rel_path
    return path.read_text(encoding="utf-8") if path.exists() else ""


def run_checks() -> list[DocumentationGovernanceReadinessResult]:
    results: list[DocumentationGovernanceReadinessResult] = []
    for rel_path in REQUIRED_FILES:
        path = REPO_ROOT / rel_path
        results.append(DocumentationGovernanceReadinessResult(rel_path, path.exists(), "file present" if path.exists() else "file missing"))
    for rel_path, snippets in CONTENT_REQUIREMENTS.items():
        text = _read(rel_path)
        for snippet in snippets:
            results.append(DocumentationGovernanceReadinessResult(rel_path, snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))
    try:
        report = default_documentation_governance_readiness_report()
        results.extend([
            DocumentationGovernanceReadinessResult("documentation_governance_contracts", report["decision_issues"] == [], "documentation governance decision validates"),
            DocumentationGovernanceReadinessResult("documentation_governance_contracts", report["documentation_inventory_issues"] == [], "documentation inventory validates"),
            DocumentationGovernanceReadinessResult("documentation_governance_contracts", report["adr_issues"] == [], "ADR records validate"),
            DocumentationGovernanceReadinessResult("documentation_governance_contracts", report["claim_issues"] == [], "claim records validate"),
            DocumentationGovernanceReadinessResult("documentation_governance_contracts", report["claim_rule_issues"] == [], "claim discipline rules validate"),
            DocumentationGovernanceReadinessResult("documentation_governance_contracts", report["release_note_issues"] == [], "release notes validate"),
            DocumentationGovernanceReadinessResult("documentation_governance_contracts", report["stale_finding_issues"] == [], "stale documentation findings validate"),
            DocumentationGovernanceReadinessResult("documentation_governance_contracts", report["review_gate_issues"] == [], "documentation review gate validates"),
            DocumentationGovernanceReadinessResult("documentation_governance_contracts", report["bounded_claim_sample"] is False, "bounded claim sample passes"),
            DocumentationGovernanceReadinessResult("documentation_governance_contracts", report["unbounded_claim_sample"] is True, "unbounded claim sample detects risk"),
            DocumentationGovernanceReadinessResult("documentation_governance_contracts", report["normalized_title_sample"] == "documentation-adrs-and-claim-discipline", "normalized title sample passes"),
            DocumentationGovernanceReadinessResult("documentation_governance_contracts", len(str(report["checksum_sample"])) == 64, "documentation checksum sample passes"),
        ])
    except Exception as exc:
        results.append(DocumentationGovernanceReadinessResult("documentation_governance_contracts", False, f"contract check failed: {exc}"))
    return results


def main() -> int:
    results = run_checks()
    print("Documentation ADRs claim discipline production readiness check")
    for result in results:
        print(f"- {'PASS' if result.ok else 'FAIL'} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
