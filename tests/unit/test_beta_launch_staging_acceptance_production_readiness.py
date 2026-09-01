from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from app.modules.beta_launch.production_readiness_contracts import (
    DEFAULT_BETA_DECISION,
    DEFAULT_COHORT,
    DEFAULT_ENTRY_CRITERIA,
    DEFAULT_EXIT_CRITERIA,
    DEFAULT_FEEDBACK_RULES,
    DEFAULT_KNOWN_ISSUES,
    DEFAULT_PRODUCT_SCOPE,
    DEFAULT_REVIEW,
    DEFAULT_STAGING_ACCEPTANCE,
    AcceptanceStatus,
    StagingAcceptanceCriterion,
    compute_beta_launch_checksum,
    summarize_acceptance_status,
    validate_beta_launch_bundle,
)
from scripts.check_beta_launch_staging_acceptance_production_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_beta_launch_staging_acceptance_production_readiness_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_beta_launch_staging_acceptance_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_beta_launch_staging_acceptance_production_readiness.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Beta launch staging acceptance production readiness check" in result.stdout


@pytest.mark.unit
def test_beta_launch_contracts_validate() -> None:
    assert DEFAULT_BETA_DECISION.validate() == []
    assert [issue for item in DEFAULT_PRODUCT_SCOPE for issue in item.validate()] == []
    assert [issue for criterion in DEFAULT_STAGING_ACCEPTANCE for issue in criterion.validate()] == []
    assert [issue for criterion in DEFAULT_ENTRY_CRITERIA for issue in criterion.validate()] == []
    assert [issue for criterion in DEFAULT_EXIT_CRITERIA for issue in criterion.validate()] == []
    assert DEFAULT_COHORT.validate() == []
    assert [issue for rule in DEFAULT_FEEDBACK_RULES for issue in rule.validate()] == []
    assert [issue for issue in DEFAULT_KNOWN_ISSUES for issue in issue.validate()] == []
    assert DEFAULT_REVIEW.validate() == []
    assert validate_beta_launch_bundle(DEFAULT_ENTRY_CRITERIA, DEFAULT_KNOWN_ISSUES, DEFAULT_REVIEW) == []


@pytest.mark.unit
def test_acceptance_status_summary_priority() -> None:
    pass_criterion = StagingAcceptanceCriterion("A", "pass", AcceptanceStatus.PASS, "docs/a.md", "owner", True)
    waived_criterion = StagingAcceptanceCriterion("B", "waived", AcceptanceStatus.WAIVED, "docs/b.md", "owner", True, "docs/waiver.md")
    fail_criterion = StagingAcceptanceCriterion("C", "fail", AcceptanceStatus.FAIL, "docs/c.md", "owner", False)

    assert summarize_acceptance_status((pass_criterion,)) == AcceptanceStatus.PASS
    assert summarize_acceptance_status((pass_criterion, waived_criterion)) == AcceptanceStatus.WAIVED
    assert summarize_acceptance_status((pass_criterion, fail_criterion)) == AcceptanceStatus.FAIL


@pytest.mark.unit
def test_beta_launch_checksum_is_sha256_hex() -> None:
    checksum = compute_beta_launch_checksum("beta-launch-evidence")
    assert len(checksum) == 64
    assert checksum == compute_beta_launch_checksum("beta-launch-evidence")
    assert checksum != compute_beta_launch_checksum("other-beta-launch-evidence")


@pytest.mark.unit
def test_makefile_exposes_beta_launch_target() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "beta-launch-staging-acceptance-production-readiness-check:" in text
    assert "scripts/check_beta_launch_staging_acceptance_production_readiness.py" in text


@pytest.mark.unit
def test_beta_launch_contracts_validation_error_branches() -> None:
    from app.modules.beta_launch.production_readiness_contracts import (
        BetaCohortPlan,
        BetaEntryCriterion,
        BetaExitCriterion,
        BetaLaunchDecision,
        BetaStage,
        FeedbackIntakeRule,
        FeedbackSeverity,
        KnownIssue,
        LaunchDecision,
        LaunchReadinessReview,
        ProductScopeArea,
        ProductScopeItem,
        default_beta_launch_readiness_report,
    )

    # 1. BetaLaunchDecision invalid branches
    bad_dec = BetaLaunchDecision(
        adr_path="invalid/path.md",
        architecture_doc_path="invalid/doc.md",
        beta_scope_required=False,
        staging_acceptance_required=False,
        entry_exit_criteria_required=False,
        cohort_controls_required=False,
        feedback_intake_required=False,
        known_issues_required=False,
        no_go_authority_required=False,
    )
    assert len(bad_dec.validate()) == 9

    # 2. ProductScopeItem invalid branches
    bad_scope = ProductScopeItem(
        scope_id="",
        area=ProductScopeArea.BILLING_DISABLED,
        description="",
        included_in_beta=False,
        explicit_exclusion=False,
        owner="",
        evidence_path="invalid/path.md",
    )
    scope_issues = bad_scope.validate()
    assert "scope_id is required" in scope_issues
    assert "product scope description is required" in scope_issues
    assert "product scope owner is required" in scope_issues
    assert "product scope evidence path must live under docs/beta_launch/" in scope_issues
    assert "billing must be explicitly excluded or disabled for beta unless approved" in scope_issues
    assert "excluded beta scope must be explicitly marked as exclusion" in scope_issues

    # 3. StagingAcceptanceCriterion invalid branches
    bad_crit = StagingAcceptanceCriterion(
        criterion_id="",
        name="",
        status=AcceptanceStatus.BLOCKED,
        evidence_path="invalid/path.md",
        owner="",
        blocks_beta=True,
    )
    crit_issues = bad_crit.validate()
    assert "criterion_id is required" in crit_issues
    assert "acceptance criterion name is required" in crit_issues
    assert "staging acceptance evidence path must be controlled" in crit_issues
    assert "staging acceptance owner is required" in crit_issues
    assert any("blocks beta launch" in issue for issue in crit_issues)

    bad_waived = StagingAcceptanceCriterion(
        criterion_id="C1",
        name="waived",
        status=AcceptanceStatus.WAIVED,
        evidence_path="docs/path.md",
        owner="owner",
        blocks_beta=False,
        waiver_path=None,
    )
    assert "waived staging acceptance criterion requires waiver path" in bad_waived.validate()

    # 4. BetaEntryCriterion invalid branches
    bad_entry = BetaEntryCriterion(
        criterion_id="",
        description="",
        met=False,
        evidence_path="invalid/path.md",
        owner="",
        required=True,
    )
    entry_issues = bad_entry.validate()
    assert "entry criterion_id is required" in entry_issues
    assert "entry criterion description is required" in entry_issues
    assert "entry criterion evidence path must be controlled" in entry_issues
    assert "entry criterion owner is required" in entry_issues
    assert any("required entry criterion is not met" in issue for issue in entry_issues)

    # 5. BetaExitCriterion invalid branches
    bad_exit = BetaExitCriterion(
        criterion_id="",
        description="",
        met=False,
        metric_name="",
        threshold="",
        owner="",
        evidence_path="invalid/path.md",
    )
    assert len(bad_exit.validate()) == 6

    # 6. BetaCohortPlan invalid branches
    bad_cohort = BetaCohortPlan(
        cohort_id="",
        stage=BetaStage.CONTROLLED_BETA,
        max_learners=0,
        max_guardians=-1,
        allowed_grades=(0, 13),
        allowed_subjects=(),
        consent_required=False,
        support_channel_ready=False,
        rollback_supported=False,
    )
    assert len(bad_cohort.validate()) == 8

    # 7. FeedbackIntakeRule invalid branches
    bad_fb = FeedbackIntakeRule(
        channel="",
        severity=FeedbackSeverity.CRITICAL,
        triage_sla_hours=0,
        owner="",
        escalation_required=False,
        evidence_path="invalid/path.md",
    )
    fb_issues = bad_fb.validate()
    assert "feedback channel is required" in fb_issues
    assert "feedback triage SLA must be positive" in fb_issues
    assert "critical feedback requires escalation" in fb_issues
    assert "feedback owner is required" in fb_issues
    assert "feedback evidence path must live under docs/beta_launch/" in fb_issues

    # 8. KnownIssue invalid branches
    bad_ki = KnownIssue(
        issue_id="",
        severity=FeedbackSeverity.HIGH,
        summary="",
        owner="",
        workaround=None,
        blocks_beta=False,
        accepted_for_beta=True,
        evidence_path="invalid/path.md",
    )
    ki_issues = bad_ki.validate()
    assert "known issue_id is required" in ki_issues
    assert "known issue summary is required" in ki_issues
    assert "known issue owner is required" in ki_issues
    assert "accepted beta known issue requires workaround" in ki_issues
    assert "known issue evidence path must live under docs/beta_launch/" in ki_issues

    unaccepted_high = KnownIssue(
        issue_id="KI-2",
        severity=FeedbackSeverity.HIGH,
        summary="High issue",
        owner="owner",
        workaround=None,
        blocks_beta=False,
        accepted_for_beta=False,
        evidence_path="docs/beta_launch/path.md",
    )
    assert "high/critical known issues must block beta or be explicitly accepted" in unaccepted_high.validate()

    # 9. LaunchReadinessReview invalid branches
    bad_rev = LaunchReadinessReview(
        review_id="",
        stage=BetaStage.GENERAL_AVAILABILITY,
        decision=LaunchDecision.GO,
        approvers=(),
        reviewed_scope=False,
        reviewed_staging_acceptance=False,
        reviewed_known_issues=False,
        reviewed_support=False,
        reviewed_rollback=False,
        evidence_path="invalid/path.md",
    )
    rev_issues = bad_rev.validate()
    assert "launch readiness review_id is required" in rev_issues
    assert "launch readiness review requires approvers" in rev_issues
    assert "general availability requires separate production launch approval" in rev_issues
    assert "launch readiness evidence path must live under docs/beta_launch/" in rev_issues

    # 10. default_beta_launch_readiness_report
    report = default_beta_launch_readiness_report()
    assert report["decision_issues"] == []
    assert report["acceptance_status_sample"] == "pass"
