from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.route_tx_slice_rollup import build_rollup, write_rollup

ROOT = Path(__file__).resolve().parents[2]


def test_route_tx_slice_rollup_builds_three_slices():
    rollup = build_rollup()
    assert len(rollup.slices) == 3
    assert {item.domain for item in rollup.slices} == {"auth", "popia", "diagnostics"}


def test_route_tx_slice_rollup_status_matches_gap_counts():
    rollup = build_rollup()
    if rollup.local_source_gap_count or rollup.live_db_gap_count or rollup.inventory_unproven_route_count:
        assert rollup.status == "blocked"
    else:
        assert rollup.status == "route-transaction-slices-release-ready"


def test_route_tx_slice_rollup_does_not_treat_source_scans_as_live_db_proof():
    rollup = build_rollup()
    for item in rollup.slices:
        if item.live_db_status != "live-db-proof-accepted":
            assert item.live_db_gap_count == 1
            assert item.release_ready is False


def test_route_tx_slice_rollup_writes_reports():
    rollup = write_rollup()
    assert (ROOT / "docs/release/route_transaction_slice_rollup.json").exists()
    assert (ROOT / "docs/release/route_transaction_slice_rollup.md").exists()
    assert rollup.no_false_closure_rules


def test_route_tx_slice_rollup_registry_patcher_runs_directly():
    result = subprocess.run(
        [sys.executable, "scripts/patch_route_tx_slice_rollup_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_route_tx_slice_rollup_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return
    result = subprocess.run(
        [sys.executable, "scripts/check_route_tx_slice_rollup.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_route_tx_slice_rollup_release_mode_fails_when_blocked():
    rollup = build_rollup()
    if rollup.status == "route-transaction-slices-release-ready":
        return
    result = subprocess.run(
        [sys.executable, "scripts/check_route_tx_slice_rollup.py", "--release"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode != 0
    assert "release mode requires route transaction slice rollup release-ready" in result.stdout


def test_makefile_contains_route_tx_slice_rollup_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "route-tx-slice-rollup:" in source
    assert "route-tx-slice-rollup-check:" in source
    assert "backend-implementation-2191-2230-full-check:" in source
