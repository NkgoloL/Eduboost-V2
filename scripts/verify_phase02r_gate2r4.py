#!/usr/bin/env python3
"""Static and focused behavioral verifier for Phase 02R Gate 2R.4."""
from __future__ import annotations

import argparse
import json
from scripts._subprocess import run
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REQUIRED_FILES = [
    "app/services/curriculum/graph.py",
    "app/models/curriculum_graph.py",
    "scripts/curriculum/validate_phase02r_gate2r4_graph.py",
    "scripts/curriculum/export_phase02r_curriculum_graph.py",
    "scripts/verify_phase02r_gate2r4.py",
    "scripts/verify_phase02r_gate2r4_postgres.sh",
    "scripts/collect_phase02r_gate2r4_evidence.sh",
    "tests/unit/phase02r/test_gate2r4_curriculum_graph.py",
    "alembic/versions/20260622_1200_phase02r_gate2r4_curriculum_graph.py",
]


def _run(command: list[str]) -> dict[str, object]:
    proc = run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return {"command": command, "exit_code": proc.returncode, "output": proc.stdout[-12000:]}


def _gate_control(expected_approved: str, expected_authorised: str) -> dict[str, object]:
    path = ROOT / "docs/roadmap/execution/atlas/phase_02r_start_gate_control.json"
    if not path.exists():
        return {"valid": False, "errors": [f"missing gate control file: {path}"]}
    data = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if data.get("approved_gate") != expected_approved:
        errors.append(f"expected approved_gate={expected_approved}, got {data.get('approved_gate')!r}")
    if data.get("authorised_next_gate") != expected_authorised:
        errors.append(f"expected authorised_next_gate={expected_authorised}, got {data.get('authorised_next_gate')!r}")
    if data.get("authorised_next_gate") in {"2R.5", "2R.6", "2R.7", "2R.8"}:
        errors.append("Gate 2R.5+ appears authorised; Gate 2R.4 verification refuses to proceed")
    return {"valid": not errors, "errors": errors, "control": data}


def _migration_contract() -> dict[str, object]:
    path = ROOT / "alembic/versions/20260622_1200_phase02r_gate2r4_curriculum_graph.py"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    required_tokens = [
        "curriculum_node_versions",
        "curriculum_edge_versions",
        "curriculum_source_mapping_versions",
        "curriculum_mapping_review_events",
        "curriculum_language_links",
        "phase02r_prevent_approved_node_version_mutation",
        "phase02r_prevent_mapping_review_event_mutation",
        "down_revision = \"20260618_1200_phase02r_grounding\"",
    ]
    missing = [token for token in required_tokens if token not in text]
    return {"valid": not missing, "missing_tokens": missing}


def verify(mode: str, *, skip_gate_control: bool = False) -> dict[str, object]:
    errors: list[str] = []
    checks: list[dict[str, object]] = []

    missing_files = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing_files:
        errors.extend(f"missing Gate 2R.4 file: {path}" for path in missing_files)

    compile_targets = [path for path in REQUIRED_FILES if path.endswith(".py") and (ROOT / path).is_file()]
    if compile_targets:
        compile_check = _run([sys.executable, "-m", "compileall", "-q", *compile_targets])
        checks.append(compile_check)
        if compile_check["exit_code"] != 0:
            errors.append("compileall failed for Gate 2R.4 Python modules")

    migration = _migration_contract()
    checks.append({"name": "migration_contract", **migration})
    if not migration["valid"]:
        errors.append(f"Gate 2R.4 migration contract missing tokens: {migration['missing_tokens']}")

    validation_cmd = [sys.executable, "scripts/curriculum/validate_phase02r_gate2r4_graph.py", "--json"]
    if skip_gate_control:
        validation_cmd.append("--skip-gate-control")
    validation_check = _run(validation_cmd)
    checks.append(validation_check)
    if validation_check["exit_code"] != 0:
        errors.append("Gate 2R.4 graph validation failed")

    export_check_1 = _run([sys.executable, "scripts/curriculum/export_phase02r_curriculum_graph.py", "--json"])
    export_check_2 = _run([sys.executable, "scripts/curriculum/export_phase02r_curriculum_graph.py", "--json"])
    checks.extend([export_check_1, export_check_2])
    if export_check_1["exit_code"] != 0 or export_check_2["exit_code"] != 0:
        errors.append("Gate 2R.4 graph export failed")
    elif export_check_1["output"] != export_check_2["output"]:
        errors.append("Gate 2R.4 graph export is not deterministic")

    pytest_path = ROOT / "tests/unit/phase02r/test_gate2r4_curriculum_graph.py"
    if pytest_path.exists():
        pytest_check = _run([sys.executable, "-m", "pytest", "-q", str(pytest_path), "--no-cov"])
        checks.append(pytest_check)
        if pytest_check["exit_code"] != 0:
            errors.append("Gate 2R.4 focused tests failed")

    migration_graph = _run([sys.executable, "scripts/verify_migration_graph.py"])
    checks.append(migration_graph)
    if migration_graph["exit_code"] != 0:
        errors.append("migration graph verifier failed")

    if not skip_gate_control:
        control = _gate_control("2R.3", "2R.4")
        checks.append({"name": "gate_control", **control})
        if not control["valid"]:
            errors.extend(control["errors"])

    if mode == "closure":
        evidence_root = ROOT / "docs/release-evidence/atlas/phase-02r/gate-2r4"
        required_evidence = [
            "raw/preflight.txt",
            "raw/verify_phase02r.txt",
            "raw/verify_phase02r_postgres.txt",
            "raw/curriculum_graph_validation.json",
            "raw/mapping_review_validation.json",
            "raw/tier1_support_validation.json",
            "raw/graph_export.json",
            "raw/SHA256SUMS.txt",
            "evidence_index.md",
        ]
        missing_evidence = [path for path in required_evidence if not (evidence_root / path).is_file()]
        if missing_evidence:
            errors.extend(f"missing Gate 2R.4 evidence artifact: {path}" for path in missing_evidence)

    return {"valid": not errors, "errors": errors, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["implementation", "closure"], default="implementation")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--skip-gate-control", action="store_true")
    args = parser.parse_args()
    result = verify(args.mode, skip_gate_control=args.skip_gate_control)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["valid"]:
        print(f"PHASE 02R GATE 2R.4 {args.mode.upper()} VERIFICATION PASSED")
    else:
        print(f"PHASE 02R GATE 2R.4 {args.mode.upper()} VERIFICATION FAILED", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
