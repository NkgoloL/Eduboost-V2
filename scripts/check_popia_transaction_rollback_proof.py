#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CRITICAL = [
    "app/services/popia_transactional_lifecycle.py",
    "tests/integration/test_popia_transaction_rollback_proof.py",
    "tests/unit/test_popia_transactional_lifecycle_contracts.py",
    "scripts/check_popia_transaction_rollback_proof.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    print("POPIA transaction rollback proof check")

    service_source = read("app/services/popia_transactional_lifecycle.py")
    for token in (
        "TransactionalPOPIAConsentLifecycleService",
        "async with _transaction_context(self.db)",
        "record_consent_lifecycle_event",
        "grant",
        "deny",
        "withdraw",
        "renew",
    ):
        if token in service_source:
            print(f"- PASS service contains {token}")
        else:
            failures.append(f"service missing {token}")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    if os.getenv("SKIP_PYTEST_RECURSION") != "1":
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        pytest_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-c",
                "pytest.ini",
                "tests/integration/test_popia_transaction_rollback_proof.py",
                "tests/unit/test_popia_transactional_lifecycle_contracts.py",
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
        print(pytest_result.stdout)
        if pytest_result.returncode == 0:
            print("- PASS POPIA transaction rollback proof tests")
        else:
            failures.append("POPIA transaction rollback proof tests failed")
    else:
        print("- INFO nested pytest execution skipped by SKIP_PYTEST_RECURSION")

    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *CRITICAL, "--select", "F821,F401,F811,E402"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff POPIA transaction rollback proof check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS POPIA transaction rollback proof check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
