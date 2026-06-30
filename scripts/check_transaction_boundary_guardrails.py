#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_JSON = ROOT / "docs/architecture/transaction_boundary_inventory.json"
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"

CRITICAL = [
    "scripts/transaction_boundary_inventory.py",
    "scripts/check_transaction_boundary_guardrails.py",
    "tests/unit/test_transaction_boundary_guardrails.py",
]

REQUIRED_TERMS = [
    "auth",
    "consent",
    "diagnostic",
    "lesson",
]


def main() -> int:
    failures: list[str] = []
    print("Transaction boundary guardrail check")

    result = subprocess.run(
        [sys.executable, "scripts/transaction_boundary_inventory.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print(result.stdout)
    if result.returncode != 0:
        failures.append("transaction boundary inventory generation failed")

    if INVENTORY_JSON.exists():
        payload = json.loads(INVENTORY_JSON.read_text(encoding="utf-8"))
        print("- PASS inventory JSON exists")
    else:
        print("- FAIL inventory JSON missing")
        return 1

    findings = payload.get("findings", [])
    if findings:
        print(f"- PASS inventory contains findings: {len(findings)}")
    else:
        failures.append("inventory contains no findings")

    blob = json.dumps(payload).lower()
    for term in REQUIRED_TERMS:
        if term in blob:
            print(f"- PASS inventory references {term}")
        else:
            failures.append(f"inventory missing expected term: {term}")

    if REGISTRY.exists() and "TX-001" in REGISTRY.read_text(encoding="utf-8"):
        print("- PASS evidence registry tracks TX-001")
    else:
        failures.append("evidence registry missing TX-001")

    for path in CRITICAL:
        ast.parse((ROOT / path).read_text(encoding="utf-8"))
        print(f"- PASS syntax {path}")

    if not os.environ.get("SKIP_PYTEST_RECURSION"):
        pytest_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-c",
                "pytest.ini",
                "tests/unit/test_transaction_boundary_guardrails.py",
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
            print("- PASS transaction boundary guardrail unit tests")
        else:
            failures.append("transaction boundary guardrail unit tests failed")
    else:
        print("- SKIP transaction boundary guardrail unit tests (recursion break)")

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
        print("- PASS focused Ruff transaction boundary guardrail check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS transaction boundary guardrail check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
