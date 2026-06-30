from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from scripts.ci_auth_refresh_db_proof_workflow import build_status, write_status

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/auth-refresh-db-proof.yml"


def test_auth_refresh_db_proof_workflow_exists_and_uses_postgres_service():
    source = WORKFLOW.read_text(encoding="utf-8")
    assert "postgres:16-alpine" in source
    assert "AUTH_REFRESH_DB_PROOF_DSN:" in source


def test_auth_refresh_db_proof_workflow_uses_concrete_github_runtime_values():
    source = WORKFLOW.read_text(encoding="utf-8")
    assert "actions/runs/${{ github.run_id }}" in source
    assert "AUTH_REFRESH_DB_COMMIT_SHA: ${{ github.sha }}" in source
    assert "REAL_RUN_ID" not in source
    assert "$REAL_" not in source


def test_auth_refresh_db_proof_workflow_runs_proof_and_evidence_gate():
    source = WORKFLOW.read_text(encoding="utf-8")
    assert "tests/integration/test_auth_refresh_db_proof.py" in source
    assert "make auth-refresh-db-evidence-attach" in source
    assert "make auth-refresh-db-evidence-release-check" in source
    assert "actions/upload-artifact@v4" in source


def test_ci_auth_refresh_db_proof_workflow_status_passing():
    status = build_status()
    assert status.status == "ci-auth-refresh-db-proof-workflow-configured"
    assert not status.blockers


def test_ci_auth_refresh_db_proof_workflow_status_writes_reports():
    status = write_status()
    assert (ROOT / "docs/release/ci_auth_refresh_db_proof_workflow_status.json").exists()
    assert (ROOT / "docs/release/ci_auth_refresh_db_proof_workflow_status.md").exists()
    assert status.status == "ci-auth-refresh-db-proof-workflow-configured"


def test_ci_auth_refresh_db_proof_workflow_checker_runs_local_mode():
    if os.getenv("SKIP_PYTEST_RECURSION"):
        return
    result = subprocess.run(
        [sys.executable, "scripts/check_ci_auth_refresh_db_proof_workflow.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"},
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_ci_auth_refresh_db_proof_workflow_registry_patcher_runs_directly():
    result = subprocess.run(
        [sys.executable, "scripts/patch_ci_auth_refresh_db_proof_workflow_registry.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_makefile_contains_ci_auth_refresh_db_proof_workflow_targets():
    source = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "ci-auth-refresh-db-proof-workflow-status:" in source
    assert "ci-auth-refresh-db-proof-workflow-check:" in source
    assert "backend-implementation-2751-2790-full-check:" in source
