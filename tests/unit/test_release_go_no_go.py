from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.release_go_no_go import build_status, write_status


ROOT = Path(__file__).resolve().parents[2]


def test_release_go_no_go_builds_decision_status():
    status = build_status()

    assert status.decision in {"GO", "NO-GO"}
    assert status.current_commit
    assert status.findings


def test_release_go_no_go_remains_no_go_when_external_or_ci_blockers_exist():
    status = build_status()
    blocker_ids = {blocker.split(":", 1)[0] for blocker in status.blockers}

    if {"CI-001", "LEGAL-001", "SEC-001", "CONTENT-001", "STAGING-001"}.intersection(blocker_ids):
        assert status.decision == "NO-GO"


def test_release_go_no_go_writes_reports_and_decision_log():
    status = write_status()

    assert (ROOT / "docs/release/release_go_no_go_status.json").exists()
    assert (ROOT / "docs/release/release_go_no_go_status.md").exists()
    assert (ROOT / "docs/release/release_decision_log.md").exists()
    assert status.required_next_actions


def test_release_go_no_go_checker_runs_in_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_release_go_no_go.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_release_go_no_go_release_mode_fails_when_no_go():
    status = build_status()
    if status.decision == "GO":
        return

    result = subprocess.run(
        [sys.executable, "scripts/check_release_go_no_go.py", "--release"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )

    assert result.returncode != 0
    assert "release mode requires generated decision GO" in result.stdout


def test_makefile_contains_release_go_no_go_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "release-go-no-go-status:" in source
    assert "release-go-no-go-local-check:" in source
    assert "backend-implementation-1831-1870-full-check:" in source
