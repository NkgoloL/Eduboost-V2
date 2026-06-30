from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.beta_blocker_burndown import build_plan, write_plan

ROOT = Path(__file__).resolve().parents[2]


def test_beta_blocker_burndown_builds_plan_from_release_status():
    plan = build_plan()
    assert plan.source_decision in {"GO", "NO-GO", "UNKNOWN"}
    assert plan.burn_down_status in {"blocked", "clear"}
    assert plan.no_false_closure_rules


def test_beta_blocker_burndown_tracks_known_release_critical_items_when_present():
    plan = build_plan()
    action_ids = {action.id for action in plan.actions}
    if plan.source_decision == "NO-GO":
        assert action_ids
        assert {"CI-001", "LEGAL-001", "SEC-001", "CONTENT-001", "STAGING-001"}.intersection(action_ids)


def test_beta_blocker_burndown_local_closure_rules_are_conservative():
    plan = build_plan()
    for action in plan.actions:
        if action.id in {"CI-001", "LEGAL-001", "SEC-001", "CONTENT-001", "STAGING-001"}:
            assert not action.can_be_closed_locally


def test_beta_blocker_burndown_writes_reports():
    plan = write_plan()
    assert (ROOT / "docs/release/beta_blocker_burndown_plan.json").exists()
    assert (ROOT / "docs/release/beta_blocker_burndown_plan.md").exists()
    assert plan.current_commit


def test_beta_blocker_burndown_checker_runs_in_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return
    result = subprocess.run(
        [sys.executable, "scripts/check_beta_blocker_burndown.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_beta_blocker_burndown_release_mode_fails_when_blocked():
    plan = build_plan()
    if plan.release_mode_allowed:
        return
    result = subprocess.run(
        [sys.executable, "scripts/check_beta_blocker_burndown.py", "--release"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode != 0
    assert "release mode requires blocker burn-down status clear" in result.stdout


def test_makefile_contains_beta_blocker_burndown_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "beta-blocker-burndown-plan:" in source
    assert "beta-blocker-burndown-check:" in source
    assert "backend-implementation-1871-1910-full-check:" in source
