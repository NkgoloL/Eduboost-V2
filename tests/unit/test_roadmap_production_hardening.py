from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)

def test_reconciliation_outputs_exist():
    result = run([sys.executable, "scripts/reconcile_agent_roadmap.py"])
    assert result.returncode == 0, result.stdout
    assert (ROOT / "docs/roadmap/agent_roadmap_reconciliation.md").exists()
    assert (ROOT / "docs/roadmap/agent_roadmap_reconciliation.json").exists()

def test_docker_hardening_checker_runs():
    result = run([sys.executable, "scripts/check_docker_production_hardening.py"])
    assert result.returncode == 0, result.stdout

def test_auth_hardening_status_probe_runs():
    result = run([sys.executable, "scripts/check_auth_hardening_status.py"])
    assert result.returncode == 0, result.stdout
    assert (ROOT / "docs/security/auth_hardening_status.md").exists()

def test_beta_content_schema_check_runs_after_threshold_probe_even_if_blocked():
    run([sys.executable, "scripts/check_beta_content_threshold.py"])
    result = run([sys.executable, "scripts/check_beta_content_threshold_schema.py"])
    assert result.returncode == 0, result.stdout

def test_makefile_contains_531_560_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "roadmap-reconciliation-check:" in text
    assert "docker-production-hardening-check:" in text
    assert "backend-implementation-531-560-full-check:" in text
