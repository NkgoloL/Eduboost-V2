#!/usr/bin/env python3
"""Verify backend fast-gate candidate evidence."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVIDENCE_DIR = ROOT / "docs/release-evidence/technical-audit/backend-fast-gate"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify(evidence_dir: Path = DEFAULT_EVIDENCE_DIR) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []
    raw = evidence_dir / "raw"

    required = [
        "phase02r_terminal_gate_control.json",
        "baseline_reset_check.json",
        "openapi_route_contract.json",
        "backend_fast_preflight.json",
        "compileall.txt",
        "backend_fast_gate.txt",
        "backend_fast_gate_result.json",
        "backend_fast_failure_classification.json",
        "SHA256SUMS.txt",
    ]
    for name in required:
        path = raw / name
        if not path.exists():
            errors.append(f"missing raw evidence artifact: raw/{name}")
        else:
            checked.append(str(path.relative_to(evidence_dir)))

    json_validity_files = [
        "phase02r_terminal_gate_control.json",
        "baseline_reset_check.json",
        "openapi_route_contract.json",
        "backend_fast_preflight.json",
    ]
    for name in json_validity_files:
        path = raw / name
        if path.exists():
            payload = _load_json(path)
            if payload.get("valid") is not True:
                errors.append(f"raw/{name} must report valid=true")

    result_path = raw / "backend_fast_gate_result.json"
    if result_path.exists():
        result = _load_json(result_path)
        if result.get("valid") is not True or result.get("returncode") != 0:
            errors.append("backend fast gate result must be valid with returncode 0")

    classification_path = raw / "backend_fast_failure_classification.json"
    if classification_path.exists():
        classification = _load_json(classification_path)
        if classification.get("failure_count", 0) != 0:
            errors.append("backend fast failure classification must detect zero failures")
        if classification.get("category_names"):
            warnings.append("classifier matched diagnostic categories despite zero failures; inspect raw output")

    index_path = evidence_dir / "evidence_index.md"
    if not index_path.exists():
        errors.append("missing evidence_index.md")
    else:
        checked.append("evidence_index.md")
        index_text = index_path.read_text(encoding="utf-8")
        if "Status:** Candidate verification passed — human approval pending" not in index_text:
            errors.append("evidence index must record candidate verification passing and pending approval")
        if not re.search(r"Source commit:\*\*\s*[0-9a-f]{40}", index_text):
            errors.append("evidence index must include a 40-character source commit")

    return {"valid": not errors, "errors": errors, "warnings": warnings, "checked": checked}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    args = parser.parse_args()
    result = verify(args.evidence_dir.resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("BACKEND FAST EVIDENCE PASSED" if result["valid"] else "BACKEND FAST EVIDENCE FAILED")
        for error in result["errors"]:
            print(f"- {error}")
        for warning in result["warnings"]:
            print(f"warning: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
