#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.transaction_rollback_rollup import REQUIRED_PROOFS, write_rollup  # noqa: E402


CRITICAL = [
    "scripts/transaction_rollback_rollup.py",
    "scripts/check_transaction_rollback_rollup.py",
    "tests/unit/test_transaction_rollback_rollup.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    print("Transaction rollback rollup check")

    rollup = write_rollup()
    print(f"- INFO status: {rollup.status}")

    if rollup.status == "isolated_rollback_coverage_complete":
        print("- PASS isolated rollback coverage is complete")
    else:
        failures.append("isolated rollback coverage incomplete")

    for proof in rollup.proofs:
        if proof.present_in_registry:
            print(f"- PASS {proof.id} present in registry")
        else:
            failures.append(f"{proof.id} missing from registry")
        if proof.integration_passing:
            print(f"- PASS {proof.id} is integration-passing")
        else:
            failures.append(f"{proof.id} is not integration-passing")
        if proof.evidence_exists:
            print(f"- PASS {proof.id} evidence file exists")
        else:
            failures.append(f"{proof.id} evidence file missing: {proof.evidence_file}")

    registry = read("docs/release/evidence_status_registry.yml")
    for proof_id in REQUIRED_PROOFS:
        if f"id: {proof_id}" not in registry:
            failures.append(f"registry missing {proof_id}")

    if "id: TX-001" in registry:
        tx001_block = registry.split("id: TX-001", 1)[1].split("  - id:", 1)[0]
        if "proof_status: production-ready" in tx001_block:
            failures.append("TX-001 must not be marked production-ready by this rollup")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-c",
                "pytest.ini",
                "tests/unit/test_transaction_rollback_rollup.py",
                "-q",
                "--no-cov",
                "--tb=short",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )
        print(result.stdout)
        if result.returncode == 0:
            print("- PASS transaction rollback rollup tests")
        else:
            failures.append("transaction rollback rollup tests failed")

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
        print("- PASS focused Ruff transaction rollback rollup check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS transaction rollback rollup check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
