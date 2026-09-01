from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from app.modules.documentation_governance.production_readiness_contracts import (
    DEFAULT_ADRS,
    DEFAULT_CLAIM_RULES,
    DEFAULT_CLAIMS,
    DEFAULT_DOCUMENTATION_DECISION,
    DEFAULT_DOC_INVENTORY,
    DEFAULT_RELEASE_NOTES,
    DEFAULT_REVIEW_GATE,
    DEFAULT_STALE_FINDINGS,
    _SAMPLE_DATE,
    compute_documentation_checksum,
    contains_unbounded_production_claim,
    normalize_doc_title,
    validate_claims_for_release,
)
from scripts.check_documentation_adrs_claim_discipline_production_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_documentation_adrs_claim_discipline_production_readiness_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_documentation_adrs_claim_discipline_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_documentation_adrs_claim_discipline_production_readiness.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Documentation ADRs claim discipline production readiness check" in result.stdout


@pytest.mark.unit
def test_documentation_governance_contracts_validate() -> None:
    assert DEFAULT_DOCUMENTATION_DECISION.validate() == []
    assert [issue for entry in DEFAULT_DOC_INVENTORY for issue in entry.validate(_SAMPLE_DATE)] == []
    assert [issue for adr in DEFAULT_ADRS for issue in adr.validate()] == []
    assert validate_claims_for_release(DEFAULT_CLAIMS) == []
    assert [issue for rule in DEFAULT_CLAIM_RULES for issue in rule.validate()] == []
    assert [issue for note in DEFAULT_RELEASE_NOTES for issue in note.validate()] == []
    assert [issue for finding in DEFAULT_STALE_FINDINGS for issue in finding.validate()] == []
    assert DEFAULT_REVIEW_GATE.validate() == []


@pytest.mark.unit
def test_unbounded_production_claim_detection() -> None:
    assert contains_unbounded_production_claim("The platform is production ready.")
    assert not contains_unbounded_production_claim("Repository-side production readiness evidence is present; this does not authorize production launch.")


@pytest.mark.unit
def test_documentation_title_normalization() -> None:
    assert normalize_doc_title("Documentation, ADRs, and Claim Discipline") == "documentation-adrs-and-claim-discipline"


@pytest.mark.unit
def test_documentation_checksum_is_sha256_hex() -> None:
    checksum = compute_documentation_checksum("documentation-governance-evidence")
    assert len(checksum) == 64
    assert checksum == compute_documentation_checksum("documentation-governance-evidence")
    assert checksum != compute_documentation_checksum("other-documentation-evidence")


@pytest.mark.unit
def test_makefile_exposes_documentation_adrs_claim_discipline_target() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "documentation-adrs-claim-discipline-production-readiness-check:" in text
    assert "scripts/check_documentation_adrs_claim_discipline_production_readiness.py" in text


@pytest.mark.unit
def test_documentation_governance_contracts_validation_error_branches() -> None:
    from datetime import date
    from app.modules.documentation_governance.production_readiness_contracts import (
        AdrRecord,
        AdrStatus,
        ClaimConfidence,
        ClaimDisciplineRule,
        ClaimRecord,
        ClaimType,
        DocumentationAudience,
        DocumentationGovernanceDecision,
        DocumentationInventoryEntry,
        DocumentationReviewGate,
        DocumentationStatus,
        ReleaseNoteEntry,
        ReleaseNoteType,
        StaleDocumentationFinding,
        default_documentation_governance_readiness_report,
    )

    # 1. DocumentationGovernanceDecision invalid branches
    bad_dec = DocumentationGovernanceDecision(
        adr_path="invalid/path.md",
        architecture_doc_path="invalid/doc.md",
        adr_lifecycle_required=False,
        claim_discipline_required=False,
        stale_doc_review_required=False,
        docs_owner_required=False,
        release_notes_required=False,
        external_claim_boundary_required=False,
    )
    assert len(bad_dec.validate()) == 8

    # 2. DocumentationInventoryEntry invalid branches
    today = date(2026, 6, 1)
    bad_inv = DocumentationInventoryEntry(
        path="invalid/path.md",
        title="",
        audience=DocumentationAudience.OPERATOR,
        status=DocumentationStatus.SUPERSEDED,
        owner="",
        reviewed_on=date(2025, 1, 1),
        review_interval_days=0,
        source_of_truth=False,
        supersedes=None,
    )
    inv_issues = bad_inv.validate(today)
    assert "documentation path must live under docs/" in inv_issues
    assert "documentation title is required" in inv_issues
    assert "documentation owner is required" in inv_issues
    assert "review interval must be positive" in inv_issues
    assert "superseded documentation must identify replacement or successor" in inv_issues

    # Stale & operator active source of truth
    stale_inv = DocumentationInventoryEntry(
        path="docs/stale.md",
        title="Stale Doc",
        audience=DocumentationAudience.OPERATOR,
        status=DocumentationStatus.ACTIVE,
        owner="owner",
        reviewed_on=date(2025, 1, 1),
        review_interval_days=30,
        source_of_truth=False,
    )
    stale_issues = stale_inv.validate(today)
    assert "docs/stale.md is stale" in stale_issues
    assert "active operator/security/privacy docs must identify source-of-truth status" in stale_issues

    # 3. AdrRecord invalid branches
    bad_adr = AdrRecord(
        adr_id="INVALID",
        path="invalid/path.md",
        title="",
        status=AdrStatus.ACCEPTED,
        decision_date=date(2026, 1, 1),
        owner="",
        context_present=False,
        decision_present=False,
        consequences_present=False,
    )
    adr_issues = bad_adr.validate()
    assert "ADR ID must follow ADR-### format" in adr_issues
    assert "ADR path must live under docs/adr/" in adr_issues
    assert "ADR title is required" in adr_issues
    assert "ADR owner is required" in adr_issues
    assert "accepted ADR requires decision section" in adr_issues
    assert "ADR context section is required" in adr_issues
    assert "ADR consequences section is required" in adr_issues

    bad_super_adr = AdrRecord(
        adr_id="ADR-001",
        path="docs/adr/ADR-001.md",
        title="Title",
        status=AdrStatus.SUPERSEDED,
        decision_date=date(2026, 1, 1),
        owner="owner",
        context_present=True,
        decision_present=True,
        consequences_present=True,
        superseded_by=None,
    )
    assert "superseded ADR must identify successor" in bad_super_adr.validate()

    # 4. ClaimRecord invalid branches
    bad_claim = ClaimRecord(
        claim_id="",
        claim_text="",
        claim_type=ClaimType.EXTERNAL_SYSTEM,
        confidence=ClaimConfidence.UNSUPPORTED,
        evidence_paths=("invalid/path.txt",),
        owner="",
        external_dependency=None,
        production_claim=True,
    )
    claim_issues = bad_claim.validate()
    assert "claim_id is required" in claim_issues
    assert "claim_text is required" in claim_issues
    assert "claim owner is required" in claim_issues
    assert "claim evidence path must be controlled" in claim_issues
    assert "external/manual/legal/security claims require external dependency note" in claim_issues
    assert "production claims must be verified or clearly excluded" in claim_issues
    assert "unsupported claims are not allowed in production readiness evidence" in claim_issues

    bad_verified_claim = ClaimRecord(
        claim_id="C-1",
        claim_text="Text",
        claim_type=ClaimType.REPOSITORY_EVIDENCE,
        confidence=ClaimConfidence.VERIFIED,
        evidence_paths=(),
        owner="owner",
        external_dependency=None,
        production_claim=False,
    )
    assert "verified claims require evidence paths" in bad_verified_claim.validate()

    # 5. ClaimDisciplineRule invalid branches
    bad_rule = ClaimDisciplineRule(
        rule_id="",
        description="",
        prohibited_phrases=(),
        required_boundary_phrase="",
        applies_to_paths=(),
        blocks_release=False,
    )
    assert len(bad_rule.validate()) == 6

    # 6. ReleaseNoteEntry invalid branches
    bad_rn = ReleaseNoteEntry(
        entry_id="",
        release_note_type=ReleaseNoteType.FEATURE,
        summary="",
        evidence_path="invalid/path.md",
        breaking_change=True,
        migration_required=True,
        user_visible=False,
        owner="",
    )
    rn_issues = bad_rn.validate()
    assert "release note entry_id is required" in rn_issues
    assert "release note summary is required" in rn_issues
    assert "release note evidence path must be controlled" in rn_issues
    assert "breaking changes must use breaking_change release note type" in rn_issues
    assert "migration-required notes must be breaking_change or operations" in rn_issues
    assert "release note owner is required" in rn_issues

    # 7. StaleDocumentationFinding invalid branches
    bad_finding = StaleDocumentationFinding(
        finding_id="",
        path="invalid/path.md",
        days_stale=-1,
        owner="",
        severity="invalid_sev",
        action_required="",
        blocks_release=False,
    )
    find_issues = bad_finding.validate()
    assert "stale documentation finding_id is required" in find_issues
    assert "stale documentation path must live under docs/" in find_issues
    assert "days_stale cannot be negative" in find_issues
    assert "stale documentation owner is required" in find_issues
    assert "stale documentation severity is invalid" in find_issues
    assert "stale documentation action is required" in find_issues

    blocker_finding = StaleDocumentationFinding(
        finding_id="F1",
        path="docs/f.md",
        days_stale=10,
        owner="owner",
        severity="release_blocker",
        action_required="fix",
        blocks_release=False,
    )
    assert "release_blocker stale docs must block release" in blocker_finding.validate()

    # 8. DocumentationReviewGate invalid branches
    bad_gate = DocumentationReviewGate(
        gate_id="",
        release_stage="prod",
        required_docs=("invalid/doc.md",),
        required_adrs=("invalid/adr.md",),
        claim_review_required=False,
        stale_doc_review_required=False,
        release_notes_required=False,
        owner="",
        blocks_release=False,
    )
    gate_issues = bad_gate.validate()
    assert "documentation review gate_id is required" in gate_issues
    assert "required documentation must live under docs/" in gate_issues
    assert "required ADRs must live under docs/adr/" in gate_issues
    assert "claim review is required" in gate_issues
    assert "stale documentation review is required" in gate_issues
    assert "release notes are required" in gate_issues
    assert "documentation review gate owner is required" in gate_issues
    assert "documentation review gate must block release" in gate_issues

    empty_gate = DocumentationReviewGate(
        gate_id="G1",
        release_stage="prod",
        required_docs=(),
        required_adrs=(),
        claim_review_required=True,
        stale_doc_review_required=True,
        release_notes_required=True,
        owner="owner",
        blocks_release=True,
    )
    assert "documentation review gate requires docs" in empty_gate.validate()
    assert "documentation review gate requires ADRs" in empty_gate.validate()

    # 9. default_documentation_governance_readiness_report
    report = default_documentation_governance_readiness_report()
    assert report["decision_issues"] == []
    assert report["bounded_claim_sample"] is False
    assert report["unbounded_claim_sample"] is True
