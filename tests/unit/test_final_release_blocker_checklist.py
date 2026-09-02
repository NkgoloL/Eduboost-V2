from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from app.modules.final_release_blockers.production_readiness_contracts import (
    DEFAULT_CLOSURE_RECORDS,
    DEFAULT_DOMAIN_SUMMARIES,
    DEFAULT_EXTERNAL_DEPENDENCIES,
    DEFAULT_FINAL_BLOCKER_DECISION,
    DEFAULT_FINAL_CHECKLIST,
    DEFAULT_RELEASE_BLOCKERS,
    DEFAULT_WAIVER_RULES,
    FinalDecision,
    compute_release_blocker_checksum,
    determine_final_decision,
    summarize_blockers,
    validate_final_release_bundle,
)
from scripts.check_final_release_blocker_checklist import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_final_release_blocker_checklist_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_final_release_blocker_checklist_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_final_release_blocker_checklist.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Final release blocker checklist check" in result.stdout


@pytest.mark.unit
def test_final_release_blocker_contracts_validate() -> None:
    assert DEFAULT_FINAL_BLOCKER_DECISION.validate() == []
    assert [issue for summary in DEFAULT_DOMAIN_SUMMARIES for issue in summary.validate()] == []
    assert [issue for blocker in DEFAULT_RELEASE_BLOCKERS for issue in blocker.validate()] == []
    assert [issue for rule in DEFAULT_WAIVER_RULES for issue in rule.validate()] == []
    assert [issue for dependency in DEFAULT_EXTERNAL_DEPENDENCIES for issue in dependency.validate()] == []
    assert DEFAULT_FINAL_CHECKLIST.validate() == []
    assert [issue for closure in DEFAULT_CLOSURE_RECORDS for issue in closure.validate()] == []
    assert validate_final_release_bundle(DEFAULT_RELEASE_BLOCKERS, DEFAULT_EXTERNAL_DEPENDENCIES, DEFAULT_FINAL_CHECKLIST) == []


@pytest.mark.unit
def test_final_decision_and_summary() -> None:
    assert determine_final_decision(DEFAULT_RELEASE_BLOCKERS, DEFAULT_EXTERNAL_DEPENDENCIES) == FinalDecision.GO
    summary = summarize_blockers(DEFAULT_RELEASE_BLOCKERS)
    assert summary["closed"] == 3
    assert summary["not_applicable"] == 1
    assert summary["open"] == 0


@pytest.mark.unit
def test_release_blocker_checksum_is_sha256_hex() -> None:
    checksum = compute_release_blocker_checksum("final-release-blocker-evidence")
    assert len(checksum) == 64
    assert checksum == compute_release_blocker_checksum("final-release-blocker-evidence")
    assert checksum != compute_release_blocker_checksum("other-final-release-blocker-evidence")


@pytest.mark.unit
def test_makefile_exposes_final_release_blocker_target() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "final-release-blocker-checklist-check:" in text
    assert "scripts/check_final_release_blocker_checklist.py" in text


@pytest.mark.unit
def test_final_release_blocker_contracts_validation_error_branches() -> None:
    from datetime import date
    from app.modules.final_release_blockers.production_readiness_contracts import (
        BlockerSeverity,
        BlockerStatus,
        ExternalManualDependency,
        FinalGoNoGoChecklist,
        FinalReleaseBlockerDecision,
        LaunchAuthority,
        ReleaseBlockerClosureRecord,
        ReleaseBlockerDomain,
        ReleaseBlockerDomainSummary,
        ReleaseBlockerItem,
        ReleaseWaiverRule,
        default_final_release_blocker_readiness_report,
    )

    # 1. FinalReleaseBlockerDecision invalid branches
    bad_dec = FinalReleaseBlockerDecision(
        adr_path="invalid/path.md",
        architecture_doc_path="invalid/doc.md",
        blocker_checklist_required=False,
        owner_assignment_required=False,
        closure_evidence_required=False,
        waiver_policy_required=False,
        external_dependency_boundary_required=False,
        launch_authority_required=False,
        final_go_no_go_required=False,
    )
    assert len(bad_dec.validate()) == 9

    # 2. ReleaseBlockerItem invalid branches
    bad_item = ReleaseBlockerItem(
        blocker_id="INVALID",
        domain=ReleaseBlockerDomain.SECURITY,
        title="",
        severity=BlockerSeverity.RELEASE_BLOCKER,
        status=BlockerStatus.OPEN,
        owner="",
        evidence_path="invalid/path.md",
        closure_path=None,
        waiver_path=None,
        external_dependency=None,
        blocks_launch=True,
    )
    item_issues = bad_item.validate()
    assert "blocker_id must follow RB-### format" in item_issues
    assert "release blocker title is required" in item_issues
    assert "release blocker owner is required" in item_issues
    assert "release blocker evidence path must be controlled" in item_issues
    assert "critical/release-blocker items cannot remain open" in item_issues
    assert any("still blocks launch" in issue for issue in item_issues)

    waived_item = ReleaseBlockerItem(
        blocker_id="RB-001",
        domain=ReleaseBlockerDomain.SECURITY,
        title="Title",
        severity=BlockerSeverity.RELEASE_BLOCKER,
        status=BlockerStatus.WAIVED,
        owner="owner",
        evidence_path="docs/path.md",
        closure_path=None,
        waiver_path=None,
        external_dependency=None,
        blocks_launch=False,
    )
    w_issues = waived_item.validate()
    assert "waived blockers require waiver evidence" in w_issues
    assert "release-blocker severity cannot be waived by default" in w_issues

    ext_item = ReleaseBlockerItem(
        blocker_id="RB-002",
        domain=ReleaseBlockerDomain.EXTERNAL_MANUAL,
        title="Title",
        severity=BlockerSeverity.LOW,
        status=BlockerStatus.EXTERNAL_PENDING,
        owner="owner",
        evidence_path="docs/path.md",
        closure_path=None,
        waiver_path=None,
        external_dependency=None,
        blocks_launch=False,
    )
    assert "external pending blockers require external dependency note" in ext_item.validate()

    # 3. ReleaseBlockerDomainSummary invalid branches
    bad_summary = ReleaseBlockerDomainSummary(
        domain=ReleaseBlockerDomain.EXTERNAL_MANUAL,
        checklist_path="invalid/path.md",
        check_command="",
        owner="",
        required_for_release=True,
        evidence_complete=False,
        manual_dependency=None,
    )
    sum_issues = bad_summary.validate()
    assert "domain checklist path must live under docs/" in sum_issues
    assert "domain check command is required" in sum_issues
    assert "domain summary owner is required" in sum_issues
    assert any("release evidence is incomplete" in issue for issue in sum_issues)
    assert "external/manual domain requires manual dependency" in sum_issues

    # 4. ReleaseWaiverRule invalid branches
    bad_rule = ReleaseWaiverRule(
        rule_id="",
        severity=BlockerSeverity.RELEASE_BLOCKER,
        waiver_allowed=True,
        required_approvers=(),
        expiry_days=40,
        compensating_controls_required=False,
        evidence_path="invalid/path.md",
    )
    rule_issues = bad_rule.validate()
    assert "waiver rule_id is required" in rule_issues
    assert "release-blocker severity cannot be waived" in rule_issues
    assert "waiver requires approvers" in rule_issues
    assert "waiver expiry must be between 1 and 30 days" in rule_issues
    assert "waiver requires compensating controls" in rule_issues
    assert "waiver rule evidence path must live under docs/release_blockers/" in rule_issues

    # 5. ExternalManualDependency invalid branches
    bad_ext = ExternalManualDependency(
        dependency_id="INVALID",
        description="",
        owner="",
        external_system="",
        verification_method="",
        required_before_launch=True,
        evidence_path="invalid/path.md",
        status=BlockerStatus.OPEN,
    )
    ext_issues = bad_ext.validate()
    assert "dependency_id must follow EXT-### format" in ext_issues
    assert "external dependency description is required" in ext_issues
    assert "external dependency owner is required" in ext_issues
    assert "external system is required" in ext_issues
    assert "verification method is required" in ext_issues
    assert "external dependency evidence path must live under docs/release_blockers/" in ext_issues
    assert any("required external dependency is not closed" in issue for issue in ext_issues)

    # 6. FinalGoNoGoChecklist invalid branches
    bad_chk = FinalGoNoGoChecklist(
        checklist_id="",
        decision=FinalDecision.GO,
        approvers=(LaunchAuthority.ENGINEERING,),
        required_domains=(),
        blocker_register_path="invalid/path.md",
        evidence_bundle_path="invalid/path.md",
        known_issues_reviewed=False,
        rollback_reviewed=False,
        support_reviewed=False,
        privacy_security_reviewed=False,
        external_dependencies_reviewed=False,
    )
    chk_issues = bad_chk.validate()
    assert "final go/no-go checklist_id is required" in chk_issues
    assert "release owner approval is required" in chk_issues
    assert "required domains are required" in chk_issues
    assert "blocker register path must live under docs/release_blockers/" in chk_issues
    assert "evidence bundle path must be controlled" in chk_issues
    assert "known_issues_reviewed must be reviewed" in chk_issues
    assert "GO decision must include external/manual dependency review" in chk_issues

    # 7. ReleaseBlockerClosureRecord invalid branches
    bad_close = ReleaseBlockerClosureRecord(
        closure_id="INVALID",
        blocker_id="INVALID",
        closed_on=date(2026, 1, 1),
        closed_by="",
        evidence_checksum="INVALID",
        evidence_path="invalid/path.md",
        residual_risk="",
        follow_up_required=False,
    )
    close_issues = bad_close.validate()
    assert "closure_id must follow CLOSE-### format" in close_issues
    assert "blocker_id must follow RB-### format" in close_issues
    assert "closed_by is required" in close_issues
    assert "evidence_checksum must be 64 lowercase hex" in close_issues
    assert "closure evidence path must be controlled" in close_issues
    assert "residual risk summary is required" in close_issues

    # 8. Decision branches: NO_GO, DEFER, CONDITIONAL_GO
    open_blocker = ReleaseBlockerItem("RB-100", ReleaseBlockerDomain.SECURITY, "Open blocker", BlockerSeverity.CRITICAL, BlockerStatus.OPEN, "owner", "docs/p.md", None, None, None, True)
    assert determine_final_decision((open_blocker,), ()) == FinalDecision.NO_GO

    waived_b = ReleaseBlockerItem("RB-101", ReleaseBlockerDomain.SECURITY, "Waived blocker", BlockerSeverity.LOW, BlockerStatus.WAIVED, "owner", "docs/p.md", None, "docs/release_blockers/w.md", None, False)
    assert determine_final_decision((waived_b,), ()) == FinalDecision.CONDITIONAL_GO

    defer_ext = ExternalManualDependency("EXT-100", "Ext dep", "owner", "ext", "verify", True, "docs/release_blockers/e.md", BlockerStatus.OPEN)
    assert determine_final_decision((), (defer_ext,)) == FinalDecision.DEFER

    # 9. default_final_release_blocker_readiness_report
    report = default_final_release_blocker_readiness_report()
    assert report["decision_issues"] == []
    assert report["computed_decision"] == "go"
