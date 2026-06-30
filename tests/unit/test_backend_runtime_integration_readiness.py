from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from app.services.backend_runtime_integration_readiness import (
    blocked_changes,
    runtime_integration_ready_for_pr_planning,
    run_runtime_integration_dry_runs_sync,
    safe_dry_run_targets,
)


ROOT = Path(__file__).resolve().parents[2]


def test_runtime_integration_dry_runs_pass():
    results = run_runtime_integration_dry_runs_sync()
    assert results
    assert all(result.passed for result in results)
    assert runtime_integration_ready_for_pr_planning() is True


def test_runtime_integration_targets_are_safe_for_dry_run_only():
    targets = safe_dry_run_targets()
    assert len(targets) >= 3
    assert all(not target.runtime_wiring_allowed for target in targets)
    assert all(not target.requires_route_registration for target in targets)
    assert all(not target.requires_schema_change for target in targets)
    assert all(not target.destructive for target in targets)


def test_runtime_integration_blocked_changes_cover_danger_zones():
    blocked = blocked_changes()
    assert "route registration" in blocked
    assert "schema migration" in blocked
    assert "production DB mutation" in blocked
    assert "alembic stamp head" in blocked


def test_runtime_integration_scripts_run():
    for command in [
        [sys.executable, "scripts/check_backend_runtime_integration_readiness.py"],
        [sys.executable, "scripts/check_backend_runtime_integration_blocklists.py"],
        [sys.executable, "scripts/generate_backend_runtime_integration_readiness_report.py"],
    ]:
        result = subprocess.run(
            command,
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        assert result.returncode == 0, result.stdout


def test_makefile_contains_runtime_integration_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "backend-runtime-integration-readiness-check:" in text
    assert "backend-runtime-integration-readiness-report:" in text
    assert "backend-runtime-integration-readiness-full-check:" in text
