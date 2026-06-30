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
