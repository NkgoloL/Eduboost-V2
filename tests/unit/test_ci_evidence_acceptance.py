from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.ci_evidence_acceptance import _workflow_is_rejected, write_status

ROOT = Path(__file__).resolve().parents[2]


def test_rejects_auth_refresh_db_workflow_as_general_ci():
    assert _workflow_is_rejected("Auth Refresh DB Proof")
    assert _workflow_is_rejected("auth refresh db proof")


def test_does_not_reject_normal_ci_names():
    assert not _workflow_is_rejected("CI")
    assert not _workflow_is_rejected("Backend CI")
    assert not _workflow_is_rejected("Production Readiness")


def test_ci_evidence_status_writes_files_when_gh_available_or_reports_blockers():
    status = write_status()
    assert (ROOT / "docs/release/ci_evidence_status.json").exists()
    assert (ROOT / "docs/release/ci_evidence_status.md").exists()
    assert (ROOT / "docs/release/ci_evidence.md").exists()
    assert status.status in {"ci-evidence-accepted", "ci-evidence-not-accepted"}


def test_ci_evidence_checker_runs_without_pytest_recursion():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_ci_evidence_acceptance.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode in {0, 1}
    assert "CI evidence acceptance check" in result.stdout


def test_makefile_contains_ci_evidence_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "ci-evidence-acceptance-status:" in source
    assert "ci-evidence-acceptance-check:" in source
    assert "backend-implementation-2871-2910-full-check:" in source
