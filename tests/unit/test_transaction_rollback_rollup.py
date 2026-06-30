from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.transaction_rollback_rollup import REQUIRED_PROOFS, build_rollup, write_rollup


ROOT = Path(__file__).resolve().parents[2]


def test_transaction_rollback_rollup_requires_all_domain_proofs():
    assert {"TX-POPIA-001", "TX-AUTH-001", "TX-DIAG-001", "TX-LESSON-001"} == set(REQUIRED_PROOFS)


def test_transaction_rollback_rollup_builds_complete_or_actionable_status():
    rollup = build_rollup()

    assert rollup.status in {"isolated_rollback_coverage_complete", "rollback_coverage_incomplete"}
    assert len(rollup.proofs) == 4
    assert "live Postgres rollback proof not proven" in rollup.remaining_boundaries


def test_transaction_rollback_rollup_writes_reports():
    rollup = write_rollup()

    assert (ROOT / "docs/release/transaction_rollback_rollup_report.json").exists()
    assert (ROOT / "docs/release/transaction_rollback_rollup_report.md").exists()
    assert rollup.remaining_boundaries


def test_transaction_rollback_rollup_checker_runs():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_transaction_rollback_rollup.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_makefile_contains_transaction_rollback_rollup_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "transaction-rollback-rollup-check:" in source
    assert "transaction-rollback-rollup-test:" in source
    assert "backend-implementation-1591-1630-full-check:" in source
