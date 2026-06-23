from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def run_json(script: str) -> dict:
    completed = subprocess.run(
        [sys.executable, script, "--json"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    return json.loads(completed.stdout)


def test_phase02r_is_terminally_closed_before_audit_reset() -> None:
    result = run_json("scripts/audit_remediation/verify_baseline_reset.py")
    assert result["valid"] is True


def test_popia_frontend_backend_routes_are_canonical() -> None:
    result = run_json("scripts/audit_remediation/verify_popia_route_contract.py")
    assert result["valid"] is True


def test_frontend_production_api_fallback_is_removed() -> None:
    result = run_json("scripts/audit_remediation/verify_frontend_env_contract.py")
    assert result["valid"] is True


def test_dependency_scan_workflow_uses_pnpm_summary() -> None:
    result = run_json("scripts/audit_remediation/verify_dependency_scan_workflow.py")
    assert result["valid"] is True


def test_technical_audit_register_preserves_remaining_blockers() -> None:
    register = json.loads((ROOT / "docs/roadmap/execution/technical_audit_remediation/blocker_register.json").read_text())
    pending_ids = {item["id"] for item in register["remaining_release_blockers_after_reset"]}
    assert "TA-OPENAPI-001" in pending_ids
    assert "TA-BACKEND-FAST-001" in pending_ids
    assert "TA-FRONTEND-001" in pending_ids
