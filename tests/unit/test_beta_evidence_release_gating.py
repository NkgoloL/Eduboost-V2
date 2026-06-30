from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(command: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, env=merged)


def test_ci_evidence_pending_without_run_url():
    result = run([sys.executable, "scripts/capture_remote_ci_evidence.py"], env={"GITHUB_ACTIONS_RUN_URL": "", "CI_RESULT": ""})
    assert result.returncode == 2, result.stdout
    data = json.loads((ROOT / "docs/release/ci_evidence.json").read_text(encoding="utf-8"))
    assert data["status"] == "pending_remote_ci_evidence"


def test_branch_protection_evidence_pending_without_required_checks():
    result = run([sys.executable, "scripts/capture_branch_protection_evidence.py"], env={"BRANCH_REQUIRED_CHECKS": ""})
    assert result.returncode == 2, result.stdout
    data = json.loads((ROOT / "docs/release/branch_protection_evidence.json").read_text(encoding="utf-8"))
    assert data["status"] == "pending_branch_protection_evidence"


def test_content_gate_schema_exists_even_when_blocked():
    run([sys.executable, "scripts/enforce_beta_content_gate.py"])
    result = run([sys.executable, "scripts/check_evidence_json_schema.py", "docs/beta/beta_content_hard_gate.json"])
    assert result.returncode == 0, result.stdout


def test_staging_smoke_finalization_schema_exists_even_when_pending():
    run([sys.executable, "scripts/finalize_staging_smoke_evidence.py"])
    result = run([sys.executable, "scripts/check_evidence_json_schema.py", "docs/release/staging_smoke_final_evidence.json"])
    assert result.returncode == 0, result.stdout


def test_operational_drill_wrapper_creates_schema():
    result = run([sys.executable, "scripts/capture_operational_drill_evidence.py"], env={"OPERATIONAL_DRILL": "backup", "OPERATIONAL_DRILL_RESULT": ""})
    assert result.returncode == 2, result.stdout
    result = run([sys.executable, "scripts/check_evidence_json_schema.py", "docs/release/backup_drill_evidence.json"])
    assert result.returncode == 0, result.stdout


def test_beta_readiness_and_go_no_go_reports_generate():
    run([sys.executable, "scripts/generate_beta_readiness_status.py"])
    result = run([sys.executable, "scripts/generate_release_owner_beta_go_no_go.py"])
    assert result.returncode == 0, result.stdout
    assert (ROOT / "docs/release/release_owner_beta_go_no_go_memo.md").exists()


def test_makefile_contains_561_580_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "remote-ci-evidence-capture:" in text
    assert "beta-readiness-status:" in text
    assert "backend-implementation-561-580-full-check:" in text
