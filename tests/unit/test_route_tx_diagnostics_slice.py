from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.route_tx_diagnostics_slice import build_gap_plan, build_report, live_db_status, write_gap_plan, write_report

ROOT = Path(__file__).resolve().parents[2]


def test_diagnostics_route_slice_builds_report():
    report = build_report()
    assert report.route_file == "app/api_v2_routers/diagnostics.py"
    assert report.local_status in {"route-diagnostics-delegation-passing", "route-diagnostics-delegation-not-proven"}
    assert report.live_db_status in {"external-blocked", "live-db-proof-accepted"}


def test_diagnostics_route_slice_passing_state_has_no_direct_db_mutations():
    report = build_report()
    if report.local_status == "route-diagnostics-delegation-passing":
        for finding in report.findings:
            assert finding.direct_db_mutations == []
            assert finding.service_delegate_calls


def test_diagnostics_gap_plan_blocks_when_source_not_proven():
    plan = build_gap_plan()
    assert plan.status in {"blocked", "local-source-clear-live-db-still-required"}
    if plan.source_local_status != "route-diagnostics-delegation-passing":
        assert plan.status == "blocked"


def test_diagnostics_gap_actions_are_not_closeable_by_current_report():
    plan = build_gap_plan()
    for action in plan.actions:
        assert action.can_be_closed_by_current_report is False
        assert action.implementation_action
        assert action.verification_action


def test_diagnostics_route_slice_live_db_is_separate_from_local_delegation():
    status, blockers = live_db_status()
    assert status in {"external-blocked", "live-db-proof-accepted"}
    if blockers:
        assert status == "external-blocked"


def test_diagnostics_route_slice_writes_reports():
    report = write_report()
    plan = write_gap_plan()
    assert (ROOT / "docs/release/diagnostics_route_transaction_slice_report.json").exists()
    assert (ROOT / "docs/release/diagnostics_route_transaction_slice_report.md").exists()
    assert (ROOT / "docs/release/diagnostics_route_transaction_gap_plan.json").exists()
    assert (ROOT / "docs/release/diagnostics_route_transaction_gap_plan.md").exists()
    assert (ROOT / "docs/release/diagnostics_route_transaction_live_db_evidence.md").exists()
    assert report.no_false_closure_rules
    assert plan.no_false_closure_rules


def test_route_tx_diagnostics_registry_patcher_runs_directly():
    result = subprocess.run([sys.executable, "scripts/patch_route_tx_diagnostics_slice_registry.py"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    assert result.returncode == 0, result.stdout


def test_route_tx_diagnostics_slice_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return
    result = subprocess.run([sys.executable, "scripts/check_route_tx_diagnostics_slice.py"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}, check=False)
    assert result.returncode == 0, result.stdout


def test_route_tx_diagnostics_slice_release_mode_fails_without_complete_proof():
    report = build_report()
    if report.local_status == "route-diagnostics-delegation-passing" and report.live_db_status == "live-db-proof-accepted":
        return
    result = subprocess.run([sys.executable, "scripts/check_route_tx_diagnostics_slice.py", "--release"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}, check=False)
    assert result.returncode != 0
    assert "release mode requires local diagnostics route source passing and live DB evidence" in result.stdout


def test_makefile_contains_route_tx_diagnostics_slice_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "route-tx-diagnostics-slice-report:" in source
    assert "route-tx-diagnostics-slice-check:" in source
    assert "backend-implementation-2151-2190-full-check:" in source
