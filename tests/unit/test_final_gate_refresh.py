from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.final_gate_refresh import BETA_CRITICAL_IDS, build_refresh, write_refresh


ROOT = Path(__file__).resolve().parents[2]


def test_final_gate_refresh_builds_status():
    refresh = build_refresh()

    assert refresh.beta_decision in {"GO", "NO-GO"}
    assert refresh.refresh_results
    assert refresh.no_false_closure_rules


def test_final_gate_refresh_tracks_beta_critical_ids():
    assert {"CI-001", "LEGAL-001", "SEC-001", "CONTENT-001", "STAGING-001"}.issubset(BETA_CRITICAL_IDS)


def test_final_gate_refresh_no_go_when_non_ready_beta_findings_remain():
    refresh = build_refresh()

    if refresh.non_ready_beta_findings:
        assert refresh.beta_decision == "NO-GO"


def test_final_gate_refresh_writes_reports():
    refresh = write_refresh()

    assert (ROOT / "docs/release/final_beta_gate_refresh.json").exists()
    assert (ROOT / "docs/release/final_beta_gate_refresh.md").exists()
    assert refresh.current_commit


def test_final_gate_refresh_registry_patcher_runs_directly():
    result = subprocess.run(
        [sys.executable, "scripts/patch_final_gate_refresh_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_final_gate_refresh_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_final_gate_refresh.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_final_gate_refresh_release_mode_fails_when_no_go():
    refresh = build_refresh()
    if refresh.beta_decision == "GO":
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_final_gate_refresh.py", "--release"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode != 0
    assert "release mode requires final beta gate decision GO" in result.stdout


def test_makefile_contains_final_gate_refresh_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "final-gate-refresh:" in source
    assert "final-gate-refresh-check:" in source
    assert "backend-implementation-2271-2310-full-check:" in source
