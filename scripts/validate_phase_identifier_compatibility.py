#!/usr/bin/env python3
"""Validate that programme tooling accepts Phase 02R identifiers."""
from __future__ import annotations

import argparse
import json
import re
import contextlib
import io
import tempfile
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


def _run_phase_control_validation() -> tuple[int, str]:
    """Run the control validator in-process to avoid subprocess drift/hangs."""
    from validate_phase_control_sets import main as validate_control_sets

    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        rc = validate_control_sets()
    return rc, output.getvalue().strip()


RESERVED_PHASE02R_FUTURE_ARTIFACTS = {
    "docs/roadmap/execution/atlas/phase_02r_implementation_report.md",
    "docs/release-evidence/atlas/phase-02r/phase_02r_evidence_index.md",
    "docs/release-evidence/atlas/phase-02r/phase_02r_audit_report.md",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("identifiers", nargs="*", default=["02R", "phase-02r", "phase_02r"])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Require closure-grade compatibility; warnings fail.")
    args = parser.parse_args()

    required_paths = [
        ROOT / "docs/roadmap/execution/atlas/phase_02r_execution_plan.md",
        ROOT / "docs/roadmap/execution/atlas/phase_02r_gate_2r0_initial_report.md",
        ROOT / "docs/roadmap/execution/atlas/phase_02r_gate_2r0_closure_report.md",
        ROOT / "docs/roadmap/execution/atlas/phase_02r_start_gate_control.json",
        ROOT / "scripts/preflight_phase02r.sh",
        ROOT / "scripts/verify_phase02r.sh",
        ROOT / "scripts/collect_phase02r_evidence.sh",
    ]
    scanned_files = [
        ROOT / "docs/roadmap/execution/atlas/phase_02r_execution_plan.md",
        ROOT / "docs/roadmap/execution/atlas/phase_02r_gate_2r0_initial_report.md",
        ROOT / "docs/roadmap/execution/atlas/phase_02r_gate_2r0_closure_report.md",
        ROOT / "docs/roadmap/PHASE_STATUS_REGISTER.md",
        ROOT / "docs/roadmap/execution/phase_execution_plan_template.md",
        ROOT / "docs/roadmap/execution/phase_evidence_pack_template.md",
        ROOT / ".github" / "workflows" / "phase-gates.yml",
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
    if "phase-02r" not in corpus:
        warnings.append("identifier 'phase-02r' was not observed in scanned docs")
    if "phase_02r" not in corpus:
        warnings.append("identifier 'phase_02r' was not observed in scanned docs")

    ordered = sorted(["phase-01", "phase-02", "phase-02r", "phase-03"], key=_natural_phase_key)
    if ordered != ["phase-01", "phase-02", "phase-02r", "phase-03"]:
        errors.append(f"phase natural sort does not preserve 02R order: {ordered}")

    phase_control = ROOT / "scripts/validate_phase_control_sets.py"
    text = _read(phase_control)
    if "phase_02r" not in text or "phase-02r" not in text:
        warnings.append("validate_phase_control_sets.py does not include Phase 02R canonical artifacts")
    if args.strict:
        rc, output = _run_phase_control_validation()
        if rc != 0:
            errors.append(f"Atlas control-set validation failed: {output}")
        with tempfile.TemporaryDirectory(prefix="phase-02r-evidence-") as tmp:
            probe = Path(tmp) / "docs" / "release-evidence" / "atlas" / "phase-02r" / "gate-2r0"
            probe.mkdir(parents=True)
            if probe.name != "gate-2r0":
                errors.append("evidence path creation failed for phase-02r/gate-2r0")
        template_requirements = {
            "docs/roadmap/execution/phase_execution_plan_template.md": ["phase-<NN>", "docs/release-evidence/<codename>/phase-<NN>/"],
            "docs/roadmap/execution/phase_evidence_pack_template.md": ["phase-<NN>", "docs/release-evidence/atlas/phase-<NN>/"],
        }
        for relative, snippets in template_requirements.items():
            body = _read(ROOT / relative)
            for snippet in snippets:
                if snippet not in body:
                    errors.append(f"{relative} missing template snippet {snippet!r}")
        execution_plan = _read(ROOT / "docs/roadmap/execution/atlas/phase_02r_execution_plan.md")
        for relative in re.findall(r"`(docs/[^`]+)`", execution_plan):
            if relative in RESERVED_PHASE02R_FUTURE_ARTIFACTS:
                continue
            if relative.startswith("docs/") and not (ROOT / relative).exists():
                errors.append(f"Phase 02R plan references missing report/evidence path: {relative}")
        workflows = list((ROOT / ".github" / "workflows").glob("*.yml")) + list((ROOT / ".github" / "workflows").glob("*.yaml"))
        if not workflows:
            errors.append("CI workflow directory has no YAML workflows to inspect")
        shell_scripts = [
            ROOT / "scripts/preflight_phase02r.sh",
            ROOT / "scripts/verify_phase02r.sh",
            ROOT / "scripts/collect_phase02r_evidence.sh",
            ROOT / "scripts/apply_phase02r_patch.sh",
        ]
        for path in shell_scripts:
            body = _read(path)
            if "2R.0" not in body and path.name != "apply_phase02r_patch.sh":
                errors.append(f"{path.relative_to(ROOT)} does not gate on 2R.0")
            if path.name == "apply_phase02r_patch.sh" and "Gate 2R.0 is read-only discovery" not in body:
                errors.append("apply_phase02r_patch.sh does not explicitly reject Gate 2R.0")
        for path in scanned_files:
            if path.exists() and not _read(path):
                warnings.append(f"strict scan target is empty: {path.relative_to(ROOT)}")
        if warnings:
            errors.extend(f"strict compatibility warning: {warning}" for warning in warnings)

    result = {
        "passed": not errors,
        "mode": "strict" if args.strict else "discovery",
        "local_identifier_smoke_passed": "02R" in corpus and ordered == ["phase-01", "phase-02", "phase-02r", "phase-03"],
        "full_programme_tool_compatibility": not errors if args.strict else False,
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
