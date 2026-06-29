#!/usr/bin/env python3
"""Verify Phase 02M backend-fast HEAD-aligned finalization assets."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "tests/unit/audit_remediation/test_backend_fast_gate.py",
    "scripts/audit_remediation/verify_backend_fast_phase02k.py",
    "scripts/audit_remediation/verify_backend_fast_phase02l.py",
    "docs/pr/PR-002R_BACKEND_RUNTIME_API_CONTRACT.md",
    "docs/pr/combined_runtime_wiring_pr_checklist.md",
    "docs/pr/first_audit_runtime_wiring_pr_checklist.md",
    "docs/pr/backend_runtime_wiring_pr_template.md",
    "docs/pr/runtime_integration_pr_template.md",
    "docs/operations/project_assistance_status.md",
    "docs/roadmap/execution/technical_audit_remediation/02m_backend_fast_head_aligned_finalization.md",
]


TERMINAL_STATUSES = {
    "phase_12_technical_audit_remediation_closed",
}


def _register_mode(data: dict[str, object]) -> str:
    if data.get("status") in TERMINAL_STATUSES or data.get("active_slice") == "technical-audit-remediation-closed":
        return "archival"
    return "phase-local"


def verify(root: Path = ROOT) -> dict[str, object]:
    errors: list[str] = []
    checked: list[str] = []
    for rel in REQUIRED:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required asset: {rel}")
        else:
            checked.append(rel)

    gate_test = root / "tests/unit/audit_remediation/test_backend_fast_gate.py"
    if gate_test.exists():
        text = gate_test.read_text(encoding="utf-8")
        for term in [
            "popia_route_contract.json",
            "frontend_env_contract.json",
            "dependency_scan_workflow.json",
            "backend_fast_runner_stdout.json",
            "does not claim full product release readiness",
            '"command": "make test-fast"',
        ]:
            if term not in text:
                errors.append(f"backend fast evidence test fixture missing hardened contract term: {term}")

    for rel in [
        "scripts/audit_remediation/verify_backend_fast_phase02k.py",
        "scripts/audit_remediation/verify_backend_fast_phase02l.py",
    ]:
        path = root / rel
        if path.exists():
            text = path.read_text(encoding="utf-8")
            if "must be 02k-backend-fast-evidence-authority" in text or "must be 02l-backend-fast-xfailed-evidence-verifier" in text:
                errors.append(f"{rel} still has an exact active_slice assertion")
            if "backend-fast 02-series remediation stream" not in text:
                errors.append(f"{rel} must allow later 02-series slices while preserving stream discipline")

    pr002r = root / "docs/pr/PR-002R_BACKEND_RUNTIME_API_CONTRACT.md"
    if pr002r.exists():
        text = pr002r.read_text(encoding="utf-8")
        for term in ["app.api_v2:app", "master", "Merge pull request #52", "Explicit Non-Scope"]:
            if term not in text:
                errors.append(f"PR-002R contract missing required term: {term}")

    status_doc = root / "docs/operations/project_assistance_status.md"
    if status_doc.exists():
        text = status_doc.read_text(encoding="utf-8")
        if "# Project Assistance Status" not in text or "Current Gate Snapshot" not in text:
            errors.append("project assistance status document is not in generated format")

    register = root / "docs/roadmap/execution/technical_audit_remediation/blocker_register.json"
    if register.exists():
        data = json.loads(register.read_text(encoding="utf-8"))
        mode = _register_mode(data)
        if mode == "phase-local" and data.get("active_slice") != "02m-backend-fast-head-aligned-finalization":
            errors.append("blocker register active_slice must be 02m-backend-fast-head-aligned-finalization")
        policy = data.get("backend_fast_failure", {}).get("phase_02m_slice", {}).get("policy", "")
        if mode == "phase-local" and "HEAD-aligned" not in policy:
            errors.append("blocker register must record HEAD-aligned evidence policy")
        if mode == "archival":
            blockers = data.get("remaining_release_blockers_after_reset", [])
            backend = next((item for item in blockers if isinstance(item, dict) and item.get("id") == "TA-BACKEND-FAST-001"), None)
            if not isinstance(backend, dict) or backend.get("status") != "evidence_recorded":
                errors.append("terminal register must archive TA-BACKEND-FAST-001 as evidence_recorded")
    else:
        errors.append("missing blocker register")

    return {"phase": "02M", "valid": not errors, "errors": errors, "checked": checked}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify(ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PHASE 02M VERIFIED" if result["valid"] else "PHASE 02M FAILED")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
