#!/usr/bin/env python3
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"

sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.evidence_registry import load_registry, validate_registry  # noqa: E402


CRITICAL = [
    "scripts/evidence_registry.py",
    "scripts/check_evidence_status_registry.py",
    "scripts/record_pytest_skip_inventory.py",
    "tests/unit/test_evidence_status_registry.py",
]


def main() -> int:
    failures: list[str] = []
    print("Evidence status registry check")

    if REGISTRY.exists():
        print("- PASS registry exists")
    else:
        print("- FAIL registry missing")
        return 1

    findings = load_registry(REGISTRY)
    print(f"- INFO loaded findings: {len(findings)}")

    errors = validate_registry(findings, ROOT)
    if errors:
        print("- FAIL registry validation")
        for error in errors:
            print(f"  - {error}")
        failures.extend(errors)
    else:
        print("- PASS registry validation")

    status_by_id = {finding.id: finding.proof_status for finding in findings}
    if status_by_id.get("POPIA-001") == "not-proven":
        print("- PASS skipped POPIA proof is classified as not-proven")
    else:
        failures.append("POPIA-001 must remain not-proven while focused tests skip cases")

    for path in CRITICAL:
        ast.parse((ROOT / path).read_text(encoding="utf-8"))
        print(f"- PASS syntax {path}")

    pytest_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            "pytest.ini",
            "tests/unit/test_evidence_status_registry.py",
            "-q",
            "--no-cov",
            "--tb=short",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(pytest_result.stdout)
    if pytest_result.returncode == 0:
        print("- PASS evidence registry unit tests")
    else:
        failures.append("evidence registry unit tests failed")

    ruff = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            *CRITICAL,
            "--select",
            "F821,F401,F811,E402",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff evidence registry check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS evidence status registry check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
