#!/usr/bin/env python3
"""Gate 2R.2 focused verifier: secure acquisition and immutable source versioning."""
from __future__ import annotations

import argparse
import hashlib
import json
from scripts._subprocess import run
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run(command: list[str]) -> dict[str, object]:
    proc = run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return {"command": command, "exit_code": proc.returncode, "output": proc.stdout[-4000:]}


def behavioral_checks() -> list[str]:
    errors: list[str] = []
    try:
        from app.services.curriculum.acquisition import AcquisitionRejectedError, ControlledAcquisitionService
        from app.services.curriculum.object_storage import LocalImmutableObjectStore

        rights = {"decision_status": "approved", "may_store_original": True}
        denied = {"decision_status": "approved", "may_store_original": False}

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source_root = root / "sources"
            source_root.mkdir()
            store_root = root / "objects"
            path = source_root / "caps.txt"
            path.write_text("Numbers, operations and relationships", encoding="utf-8")
            sha = hashlib.sha256(path.read_bytes()).hexdigest()

            service = ControlledAcquisitionService(object_store=LocalImmutableObjectStore(store_root))
            acquired = service.acquire_local_file(path, expected_sha256=sha, rights_decision=rights, allowed_root=source_root)
            if acquired.sha256 != sha or not acquired.object_uri.startswith("local://phase02r/sources/"):
                errors.append("successful acquisition contract failed")

            again = service.acquire_local_file(path, expected_sha256=sha, rights_decision=rights, allowed_root=source_root)
            if again.object_uri != acquired.object_uri:
                errors.append("same SHA acquisition is not idempotent")

            try:
                service.acquire_local_file(path, expected_sha256="0" * 64, rights_decision=rights, allowed_root=source_root)
                errors.append("checksum mismatch was not rejected")
            except AcquisitionRejectedError:
                pass

            try:
                service.acquire_local_file(path, expected_sha256=sha, rights_decision=denied, allowed_root=source_root)
                errors.append("denied may_store_original was not rejected")
            except AcquisitionRejectedError:
                pass

            try:
                service.acquire_local_file(path, expected_sha256=sha, rights_decision=None, allowed_root=source_root)
                errors.append("missing rights decision was not rejected")
            except AcquisitionRejectedError:
                pass

            outside = root / "outside.txt"
            outside.write_text("escape", encoding="utf-8")
            outside_sha = hashlib.sha256(outside.read_bytes()).hexdigest()
            try:
                service.acquire_local_file(outside, expected_sha256=outside_sha, rights_decision=rights, allowed_root=source_root)
                errors.append("path escape was not rejected")
            except AcquisitionRejectedError:
                pass
    except Exception as exc:  # pragma: no cover - verifier diagnostic
        errors.append(f"behavioral checks crashed: {exc}")
    return errors


def verify(*, include_real_source: bool) -> dict[str, object]:
    errors: list[str] = []
    checks: list[dict[str, object]] = []

    required = [
        "app/services/curriculum/object_storage.py",
        "app/services/curriculum/acquisition.py",
        "scripts/curriculum/acquire_phase02r_sources.py",
        "scripts/verify_phase02r_gate2r2.py",
        "tests/unit/phase02r/test_gate2r2_secure_acquisition.py",
    ]
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        errors.append(f"missing required files: {missing}")

    gate = run([
        sys.executable,
        "scripts/phase02r_gate_control.py",
        "--expected-approved-gate", "2R.1",
        "--expected-authorised-gate", "2R.2",
        "--require-approval-roles",
        "--require-evidence-index-sha",
        "--json",
    ])
    checks.append(gate)
    if gate["exit_code"] != 0:
        errors.append("gate control does not authorise 2R.2")

    compile_check = run([
        sys.executable,
        "-m",
        "compileall",
        "-q",
        "app/services/curriculum",
        "scripts/curriculum",
        "scripts/verify_phase02r_gate2r2.py",
        "tests/unit/phase02r",
    ])
    checks.append(compile_check)
    if compile_check["exit_code"] != 0:
        errors.append("compileall failed")

    tests = run([sys.executable, "-m", "pytest", "-q", "tests/unit/phase02r/test_gate2r2_secure_acquisition.py", "--no-cov"])
    checks.append(tests)
    if tests["exit_code"] != 0:
        errors.append("Gate 2R.2 focused unit tests failed")

    dry_run = run([sys.executable, "scripts/curriculum/acquire_phase02r_sources.py", "--dry-run", "--json"])
    checks.append(dry_run)
    if dry_run["exit_code"] != 0:
        errors.append("Gate 2R.2 acquisition dry-run failed")

    if include_real_source:
        acquire = run([sys.executable, "scripts/curriculum/acquire_phase02r_sources.py", "--json"])
        checks.append(acquire)
        if acquire["exit_code"] != 0:
            errors.append("Gate 2R.2 real source acquisition failed")

    errors.extend(behavioral_checks())
    return {"valid": not errors, "errors": errors, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--include-real-source", action="store_true")
    args = parser.parse_args()
    result = verify(include_real_source=args.include_real_source)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["valid"]:
        print("PHASE 02R GATE 2R.2 VERIFICATION PASSED")
    else:
        print("PHASE 02R GATE 2R.2 VERIFICATION FAILED", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
