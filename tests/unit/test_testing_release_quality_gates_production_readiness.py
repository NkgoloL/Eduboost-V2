from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from app.modules.quality_gates.production_readiness_contracts import (
    DEFAULT_COVERAGE_THRESHOLDS,
    DEFAULT_DEFECT_TRIAGE,
    DEFAULT_QUALITY_GATES,
    DEFAULT_RELEASE_CHECKLISTS,
    DEFAULT_RELEASE_EVIDENCE,
    DEFAULT_TESTING_STRATEGY,
    DEFAULT_TEST_SUITES,
    EvidenceType,
    QualityGateStatus,
    ReleaseStage,
    compute_evidence_checksum,
    summarize_gate_status,
    validate_evidence_bundle,
)
from scripts.check_testing_release_quality_gates_production_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_testing_release_quality_gates_production_readiness_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_testing_release_quality_gates_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_testing_release_quality_gates_production_readiness.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Testing release quality gates production readiness check" in result.stdout


@pytest.mark.unit
def test_quality_gate_contracts_validate() -> None:
    assert DEFAULT_TESTING_STRATEGY.validate() == []
    assert [issue for suite in DEFAULT_TEST_SUITES for issue in suite.validate()] == []
    assert [issue for threshold in DEFAULT_COVERAGE_THRESHOLDS for issue in threshold.validate()] == []
    assert [issue for gate in DEFAULT_QUALITY_GATES for issue in gate.validate()] == []
    assert [issue for item in DEFAULT_RELEASE_EVIDENCE for issue in item.validate()] == []
    assert [issue for rule in DEFAULT_DEFECT_TRIAGE for issue in rule.validate()] == []
    assert [issue for checklist in DEFAULT_RELEASE_CHECKLISTS for issue in checklist.validate()] == []


@pytest.mark.unit
def test_release_evidence_bundle_validation() -> None:
    assert validate_evidence_bundle(DEFAULT_RELEASE_EVIDENCE, ReleaseStage.BETA) == []
    missing = tuple(item for item in DEFAULT_RELEASE_EVIDENCE if item.evidence_type != EvidenceType.SECURITY_SCAN)
    assert "missing security_scan for beta" in validate_evidence_bundle(missing, ReleaseStage.BETA)


@pytest.mark.unit
def test_gate_status_summary_priority() -> None:
    assert summarize_gate_status({"unit": QualityGateStatus.PASS}) == QualityGateStatus.PASS
    assert summarize_gate_status({"unit": QualityGateStatus.PASS, "security": QualityGateStatus.WAIVED}) == QualityGateStatus.WAIVED
    assert summarize_gate_status({"unit": QualityGateStatus.BLOCKED}) == QualityGateStatus.BLOCKED
    assert summarize_gate_status({"unit": QualityGateStatus.FAIL, "security": QualityGateStatus.BLOCKED}) == QualityGateStatus.FAIL


@pytest.mark.unit
def test_evidence_checksum_is_sha256_hex() -> None:
    checksum = compute_evidence_checksum("release-evidence")
    assert len(checksum) == 64
    assert checksum == compute_evidence_checksum("release-evidence")
    assert checksum != compute_evidence_checksum("other-evidence")


@pytest.mark.unit
def test_makefile_exposes_testing_release_quality_gates_target() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "testing-release-quality-gates-production-readiness-check:" in text
    assert "scripts/check_testing_release_quality_gates_production_readiness.py" in text


@pytest.mark.unit
def test_quality_gates_contracts_validation_error_branches() -> None:
    from app.modules.quality_gates.production_readiness_contracts import (
        CoverageThreshold,
        DefectSeverity,
        DefectTriageRule,
        EvidenceType,
        QualityGate,
        ReleaseChecklist,
        ReleaseEvidenceItem,
        ReleaseStage,
        TestingStrategyDecision,
        TestLayer,
        TestSuiteContract,
        default_quality_gate_readiness_report,
    )

    # 1. TestingStrategyDecision invalid branches
    bad_dec = TestingStrategyDecision(
        adr_path="invalid/path.md",
        architecture_doc_path="invalid/doc.md",
        pytest_required=False,
        frontend_test_required=False,
        contract_test_required=False,
        e2e_test_required=False,
        security_test_required=False,
        accessibility_test_required=False,
        performance_test_required=False,
        release_evidence_required=False,
    )
    assert len(bad_dec.validate()) == 10

    # 2. TestSuiteContract invalid branches
    bad_suite = TestSuiteContract(
        layer=TestLayer.SECURITY,
        command="",
        owner="",
        required_for_pr=True,
        required_for_staging=False,
        required_for_production=True,
        deterministic=False,
        artifact_path="invalid/path.json",
    )
    suite_issues = bad_suite.validate()
    assert "security test command is required" in suite_issues
    assert "security test owner is required" in suite_issues
    assert "security production tests must also gate staging" in suite_issues
    assert "security PR tests must be deterministic" in suite_issues
    assert "security artifact path must be controlled" in suite_issues

    bad_e2e = TestSuiteContract(
        layer=TestLayer.E2E,
        command="make e2e",
        owner="owner",
        required_for_pr=False,
        required_for_staging=True,
        required_for_production=True,
        deterministic=True,
        artifact_path=None,
    )
    assert "e2e tests require evidence artifact path" in bad_e2e.validate()

    # 3. CoverageThreshold invalid branches
    bad_cov = CoverageThreshold(
        layer=TestLayer.UNIT,
        minimum_line_coverage=50.0,
        minimum_branch_coverage=105.0,
        measured_path="",
        ratchet_required=False,
        waiver_allowed=True,
    )
    cov_issues = bad_cov.validate()
    assert "minimum branch coverage must be between 0 and 100" in cov_issues
    assert "production line coverage threshold must be at least 70 percent" in cov_issues
    assert "coverage measured path is required" in cov_issues
    assert "coverage ratchet is required" in cov_issues
    assert "unit coverage waiver is not allowed by default" in cov_issues

    bad_line_cov = CoverageThreshold(
        layer=TestLayer.INTEGRATION, minimum_line_coverage=-5.0, minimum_branch_coverage=50.0, measured_path="p", ratchet_required=True, waiver_allowed=False
    )
    assert "minimum line coverage must be between 0 and 100" in bad_line_cov.validate()

    # 4. QualityGate invalid branches
    bad_gate = QualityGate(
        name="",
        release_stage=ReleaseStage.PRODUCTION,
        required_layers=(),
        required_evidence=(),
        manual_approval_required=False,
        waiver_policy_path="invalid/path.md",
        blocks_release=False,
        owner="",
    )
    gate_issues = bad_gate.validate()
    assert "quality gate name is required" in gate_issues
    assert "quality gate requires at least one test layer" in gate_issues
    assert "quality gate requires evidence" in gate_issues
    assert "production quality gate requires manual approval" in gate_issues
    assert "quality gate waiver policy must live under docs/testing/" in gate_issues
    assert "beta and production quality gates must block release" in gate_issues
    assert "quality gate owner is required" in gate_issues

    # 5. ReleaseEvidenceItem invalid branches
    bad_item = ReleaseEvidenceItem(
        evidence_id="",
        evidence_type=EvidenceType.TEST_REPORT,
        path="invalid/path.xml",
        generated_by="",
        git_sha="INVALID_SHA",
        checksum_sha256="INVALID_CHECKSUM",
        required_for_stage=ReleaseStage.PRODUCTION,
        retained=False,
    )
    item_issues = bad_item.validate()
    assert "evidence_id is required" in item_issues
    assert "evidence path must be controlled" in item_issues
    assert "generated_by is required" in item_issues
    assert "git_sha must be lowercase hex" in item_issues
    assert "checksum_sha256 must be 64 lowercase hex characters" in item_issues
    assert "beta and production evidence must be retained" in item_issues

    # 6. DefectTriageRule invalid branches
    bad_defect = DefectTriageRule(
        severity=DefectSeverity.RELEASE_BLOCKER,
        blocks_release=False,
        requires_owner=False,
        requires_fix_or_waiver=False,
        max_open_allowed_for_production=5,
        sla_hours=0,
    )
    defect_issues = bad_defect.validate()
    assert "release_blocker defects must block release" in defect_issues
    assert "release_blocker defects require owner" in defect_issues
    assert "release_blocker defects require fix or waiver" in defect_issues
    assert "release blockers allowed for production must be zero" in defect_issues
    assert "defect SLA must be positive" in defect_issues

    # 7. ReleaseChecklist invalid branches
    bad_chk = ReleaseChecklist(
        release_stage=ReleaseStage.PRODUCTION,
        checklist_path="invalid/path.md",
        required_approvers=(),
        evidence_bundle_required=False,
        known_issues_review_required=False,
        rollback_review_required=False,
        smoke_test_required=False,
        signoff_required=False,
    )
    assert len(bad_chk.validate()) == 7

    # 8. default_quality_gate_readiness_report
    report = default_quality_gate_readiness_report()
    assert report["strategy_issues"] == []
    assert report["gate_status_sample"] == "pass"
