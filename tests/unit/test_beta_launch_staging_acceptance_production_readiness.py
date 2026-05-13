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
