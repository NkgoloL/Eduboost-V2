#!/usr/bin/env python3
"""Single-process Gate 2R.1 verifier for deterministic local/CI execution."""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from phase02r_gate_control import validate_state  # noqa: E402
from validate_phase02r_authority_schema import validate as validate_authority_schema  # noqa: E402

REQUIRED_FILES = (
    "app/models/curriculum_authority.py",
    "app/services/curriculum/rights_policy.py",
    "alembic/versions/20260616_1200_phase02r_authority_controls.py",
    "data/curriculum/registries/grade4_mathematics_caps_source_completeness.json",
    "scripts/curriculum/load_phase02r_authority_records.py",
    "scripts/validate_phase02r_authority_schema.py",
    "scripts/curriculum/validate_source_completeness_register.py",
    "scripts/verify_phase02r_postgres.sh",
    "tests/phase02r/test_phase02r_postgres_integration.py",
    "tests/unit/phase02r/test_authority_schema.py",
    "tests/unit/phase02r/test_rights_policy.py",
    "tests/unit/phase02r/test_source_completeness_register.py",
    "tests/unit/phase02r/test_gate_control.py",
)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _capture_main(name: str, func: Callable[[], int]) -> dict[str, Any]:
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        rc = func()
    return {"name": name, "passed": rc == 0, "exit_code": rc, "output": output.getvalue().strip()}


def verify(*, closure: bool) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    checks.append({
        "name": "implementation_manifest",
        "passed": not missing,
        "missing": missing,
    })

    def run_focused_tests() -> int:
        import pytest

        return int(pytest.main(["-q", "tests/unit/phase02r", "--no-cov"]))

    checks.append(_capture_main("focused_unit_tests", run_focused_tests))

    # Load control to see what the current expected authorised gate is
    from phase02r_gate_control import CONTROL_PATH, _load
    try:
        control_data = _load(CONTROL_PATH)
        current_authorised = control_data.get("authorised_next_gate", "2R.1")
    except Exception:
        current_authorised = "2R.1"
    if current_authorised not in ("2R.1", "2R.2"):
        current_authorised = "2R.1"

    gate_errors = validate_state(expected_authorised_gate=current_authorised)
    checks.append({"name": "gate_control", "passed": not gate_errors, "errors": gate_errors})

    authority_errors = validate_authority_schema()
    checks.append({"name": "authority_schema", "passed": not authority_errors, "errors": authority_errors})

    inventory_module = _load_module(
        "phase02r_inventory_validator",
        SCRIPTS / "curriculum/validate_source_completeness_register.py",
    )
    inventory = json.loads(inventory_module.DEFAULT_REGISTER.read_text(encoding="utf-8"))
    inventory_errors = inventory_module.validate(inventory, require_frozen=closure)
    checks.append({
        "name": "source_completeness_register",
        "passed": not inventory_errors,
        "status": inventory.get("status"),
        "require_frozen": closure,
        "manifest_sha256": inventory.get("manifest_sha256"),
        "errors": inventory_errors,
    })

    migration_module = _load_module("phase02r_migration_graph", SCRIPTS / "verify_migration_graph.py")
    checks.append(_capture_main("migration_graph", migration_module.main))

    schema_module = _load_module("phase02r_schema_integrity", SCRIPTS / "validate_schema_integrity.py")
    checks.append(_capture_main("schema_integrity", schema_module.main))

    controls_module = _load_module("phase02r_control_sets", SCRIPTS / "validate_phase_control_sets.py")
    checks.append(_capture_main("phase_control_sets", controls_module.main))

    passed = all(check.get("passed") is True for check in checks)
    return {
        "phase": "02R",
        "gate": "2R.1",
        "mode": "candidate_closure" if closure else "implementation",
        "passed": passed,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("implementation", "closure"), default="implementation")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify(closure=args.mode == "closure")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for check in result["checks"]:
            print(f"{'PASS' if check['passed'] else 'FAIL'} {check['name']}")
            if not check["passed"]:
                for error in check.get("errors", check.get("missing", [])):
                    print(f"- {error}")
                if check.get("output"):
                    print(check["output"])
        print(
            "PHASE 02R GATE 2R.1 "
            + ("VERIFICATION PASSED" if result["passed"] else "VERIFICATION FAILED")
        )
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
