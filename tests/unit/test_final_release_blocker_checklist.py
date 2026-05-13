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
