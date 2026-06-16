#!/usr/bin/env python3
"""Validate that programme tooling accepts Phase 02R identifiers."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _natural_phase_key(value: str) -> tuple[int, str]:
    normalized = value.lower().replace("phase", "").replace("-", "").replace("_", "")
    match = re.search(r"(\d+)(r?)", normalized)
    if not match:
        return (9999, normalized)
    number = int(match.group(1))
    suffix = match.group(2)
    return (number, suffix)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("identifiers", nargs="*", default=["02R", "phase-02r", "phase_02r"])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    required_paths = [
        ROOT / "docs/roadmap/execution/atlas/phase_02r_execution_plan.md",
        ROOT / "docs/roadmap/execution/atlas/phase_02r_gate_2r0_report.md",
        ROOT / "scripts/preflight_phase02r.sh",
        ROOT / "scripts/verify_phase02r.sh",
        ROOT / "scripts/collect_phase02r_evidence.sh",
    ]
    scanned_files = [
        ROOT / "docs/roadmap/execution/atlas/phase_02r_execution_plan.md",
        ROOT / "docs/roadmap/execution/atlas/phase_02r_gate_2r0_report.md",
        ROOT / "docs/roadmap/PHASE_STATUS_REGISTER.md",
        ROOT / "docs/roadmap/execution/phase_execution_plan_template.md",
        ROOT / "docs/roadmap/execution/phase_evidence_pack_template.md",
    ]

    errors: list[str] = []
    warnings: list[str] = []
    for path in required_paths:
        if not path.exists():
            errors.append(f"missing required 02R control path: {path.relative_to(ROOT)}")

    corpus = "\n".join(_read(path) for path in scanned_files)
    for identifier in args.identifiers:
        if identifier not in corpus and identifier != "02R":
            warnings.append(f"identifier {identifier!r} was not observed in scanned docs")
    if "02R" not in corpus:
        errors.append("identifier '02R' was not observed in scanned docs")

    ordered = sorted(["phase-01", "phase-02", "phase-02r", "phase-03"], key=_natural_phase_key)
    if ordered != ["phase-01", "phase-02", "phase-02r", "phase-03"]:
        errors.append(f"phase natural sort does not preserve 02R order: {ordered}")

    phase_control = ROOT / "scripts/validate_phase_control_sets.py"
    text = _read(phase_control)
    if "range(1, 8)" in text and "phase_02r" not in text:
        warnings.append("validate_phase_control_sets.py remains numeric Phase 1-7 specific; 02R is handled by this validator")

    result = {
        "passed": not errors,
        "identifiers": args.identifiers,
        "natural_sort": ordered,
        "errors": errors,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Phase 02R identifier compatibility")
        for warning in warnings:
            print(f"WARNING: {warning}")
        if errors:
            print("FAIL")
            for error in errors:
                print(f"- {error}")
        else:
            print("PASS")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
