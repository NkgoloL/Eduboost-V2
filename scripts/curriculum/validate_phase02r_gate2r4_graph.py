#!/usr/bin/env python3
"""Validate Phase 02R Gate 2R.4 graph, mapping review, and Tier 1 support controls."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.curriculum.graph import validate_gate2r4_reference_graph  # noqa: E402


def _read_control() -> dict[str, object]:
    path = ROOT / "docs/roadmap/execution/atlas/phase_02r_start_gate_control.json"
    if not path.exists():
        return {"valid": False, "errors": [f"missing gate control file: {path}"]}
    data = json.loads(path.read_text(encoding="utf-8"))
    approved = data.get("approved_gate")
    authorised = data.get("authorised_next_gate")
    errors: list[str] = []
    if approved != "2R.3":
        errors.append(f"expected approved_gate=2R.3 before Gate 2R.4 execution, got {approved!r}")
    if authorised != "2R.4":
        errors.append(f"expected authorised_next_gate=2R.4 before Gate 2R.4 execution, got {authorised!r}")
    if authorised in {"2R.5", "2R.6", "2R.7", "2R.8"}:
        errors.append("Gate 2R.5+ is already authorised; Gate 2R.4 implementation must not proceed")
    return {
        "valid": not errors,
        "approved_gate": approved,
        "authorised_next_gate": authorised,
        "start_approved": data.get("start_approved"),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--section", choices=["all", "graph", "mapping-review", "tier1", "language"], default="all")
    parser.add_argument("--skip-gate-control", action="store_true", help="skip local gate-state check; intended only for isolated unit fixtures")
    args = parser.parse_args()

    report = validate_gate2r4_reference_graph()
    control = {"valid": True, "errors": []} if args.skip_gate_control else _read_control()
    report["gate_control_validation"] = control
    report["valid"] = bool(report["valid"] and control["valid"])

    if args.section == "graph":
        payload = report["curriculum_graph_validation"]
    elif args.section == "mapping-review":
        payload = report["mapping_review_validation"]
    elif args.section == "tier1":
        payload = report["tier1_support_validation"]
    elif args.section == "language":
        payload = report["language_authority_validation"]
    else:
        payload = report

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("valid"):
        print(f"Gate 2R.4 {args.section} validation passed")
    else:
        print(f"Gate 2R.4 {args.section} validation failed", file=sys.stderr)
        for error in payload.get("errors", []) or report.get("gate_control_validation", {}).get("errors", []):
            print(f"- {error}", file=sys.stderr)
    return 0 if payload.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
