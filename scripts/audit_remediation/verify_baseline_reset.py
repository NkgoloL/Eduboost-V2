#!/usr/bin/env python3
"""Verify technical-audit remediation baseline reset state.

This script is intentionally static and dependency-light so it can run from a
clean checkout before application dependencies are installed.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str) -> dict[str, Any]:
    return json.loads(read(path))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    control_path = "docs/roadmap/execution/atlas/phase_02r_start_gate_control.json"
    try:
        control = load_json(control_path)
    except FileNotFoundError:
        errors.append(f"missing {control_path}")
        control = {}

    if control.get("approved_gate") != "2R.8":
        errors.append("Phase 02R must be terminally approved at Gate 2R.8 before technical-audit reset")
    if control.get("authorised_next_gate") is not None:
        errors.append("Phase 02R authorised_next_gate must be null before technical-audit reset")
    if control.get("phase_status") not in {"closed", "complete"}:
        errors.append("Phase 02R phase_status must be closed or complete before technical-audit reset")

    plan = read("docs/roadmap/execution/atlas/phase_02r_execution_plan.md") if (ROOT / "docs/roadmap/execution/atlas/phase_02r_execution_plan.md").exists() else ""
    if "Phase 02R closed; no further Phase 02R gate authorised" not in plan:
        errors.append("execution plan must explicitly state terminal Phase 02R closure")
    if re.search(r"Execution authorisation:\*\* Gate 2R\.[0-8] only", plan):
        errors.append("execution plan contains stale Gate 2R.x execution authorisation")

    register_path = "docs/roadmap/execution/technical_audit_remediation/blocker_register.json"
    if not (ROOT / register_path).exists():
        errors.append(f"missing {register_path}")
    else:
        register = load_json(register_path)
        if register.get("stream") != "technical-audit-remediation":
            errors.append("blocker register stream must be technical-audit-remediation")
        if not register.get("remaining_release_blockers_after_reset"):
            errors.append("blocker register must preserve remaining release blockers")

    control_reset = ROOT / "docs/roadmap/execution/technical_audit_remediation/00_control_reset.md"
    if not control_reset.exists():
        errors.append("missing technical audit control-reset document")

    result = {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "checked": [
            control_path,
            "docs/roadmap/execution/atlas/phase_02r_execution_plan.md",
            register_path,
            "docs/roadmap/execution/technical_audit_remediation/00_control_reset.md",
        ],
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        if errors:
            print("TECHNICAL AUDIT BASELINE RESET FAILED")
            for error in errors:
                print(f"- {error}")
        else:
            print("TECHNICAL AUDIT BASELINE RESET PASSED")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
