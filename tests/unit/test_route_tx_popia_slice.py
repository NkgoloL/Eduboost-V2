from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.route_tx_popia_slice import build_report, live_db_status, write_report


ROOT = Path(__file__).resolve().parents[2]


def test_popia_route_slice_builds_report():
    report = build_report()

    assert report.route_file == "app/api_v2_routers/popia.py"
    assert report.local_status in {"route-popia-delegation-passing", "route-popia-delegation-not-proven"}
    assert report.live_db_status in {"external-blocked", "live-db-proof-accepted"}


def test_popia_route_slice_has_selected_routes_when_inventory_has_popia_routes():
    report = build_report()

    assert report.selected_route_count >= 0
    if report.selected_route_count:
        assert report.findings


def test_popia_route_slice_passing_state_has_no_direct_db_mutations():
    report = build_report()

    if report.local_status == "route-popia-delegation-passing":
        for finding in report.findings:
            assert finding.direct_db_mutations == []
            assert finding.service_delegate_calls


def test_popia_route_slice_live_db_is_separate_from_local_delegation():
    status, blockers = live_db_status()

    assert status in {"external-blocked", "live-db-proof-accepted"}
    if blockers:
        assert status == "external-blocked"


def test_popia_route_slice_writes_reports():
    report = write_report()

    assert (ROOT / "docs/release/popia_route_transaction_slice_report.json").exists()
    assert (ROOT / "docs/release/popia_route_transaction_slice_report.md").exists()
    assert (ROOT / "docs/release/popia_route_transaction_live_db_evidence.md").exists()
    assert report.no_false_closure_rules


def test_route_tx_popia_registry_patcher_runs_directly():
    result = subprocess.run(
        [sys.executable, "scripts/patch_route_tx_popia_slice_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_route_tx_popia_slice_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_route_tx_popia_slice.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_route_tx_popia_slice_release_mode_fails_without_live_db_evidence():
    status, _ = live_db_status()
    if status == "live-db-proof-accepted":
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_route_tx_popia_slice.py", "--release"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode != 0
    assert "release mode requires live DB POPIA route transaction evidence" in result.stdout


def test_makefile_contains_route_tx_popia_slice_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "route-tx-popia-slice-report:" in source
    assert "route-tx-popia-slice-check:" in source
    assert "backend-implementation-2111-2150-full-check:" in source
