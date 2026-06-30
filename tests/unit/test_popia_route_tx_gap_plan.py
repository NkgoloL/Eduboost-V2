from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.popia_route_tx_gap_plan import build_plan, write_plan


ROOT = Path(__file__).resolve().parents[2]


def test_popia_route_tx_gap_plan_builds_from_slice_report():
    plan = build_plan()

    assert plan.source_report == "docs/release/popia_route_transaction_slice_report.json"
    assert plan.status in {"blocked", "local-source-clear-live-db-still-required"}
    assert plan.no_false_closure_rules


def test_popia_route_tx_gap_plan_blocks_when_source_not_proven():
    plan = build_plan()

    if plan.source_local_status != "route-popia-delegation-passing":
        assert plan.status == "blocked"


def test_popia_route_tx_gap_actions_are_not_closeable_by_current_report():
    plan = build_plan()

    for action in plan.actions:
        assert action.can_be_closed_by_current_report is False
        assert action.implementation_action
        assert action.verification_action


def test_popia_route_tx_gap_plan_writes_reports():
    plan = write_plan()

    assert (ROOT / "docs/release/popia_route_transaction_gap_plan.json").exists()
    assert (ROOT / "docs/release/popia_route_transaction_gap_plan.md").exists()
    assert plan.current_commit


def test_popia_route_tx_no_false_closure_checker_runs():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    subprocess.run(
        [sys.executable, "scripts/patch_popia_route_tx_not_proven_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    result = subprocess.run(
        [sys.executable, "scripts/check_popia_route_tx_no_false_closure.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_makefile_contains_popia_route_tx_gap_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "popia-route-tx-gap-plan:" in source
    assert "popia-route-tx-no-false-closure-check:" in source
    assert "backend-implementation-2111-2150R-full-check:" in source
