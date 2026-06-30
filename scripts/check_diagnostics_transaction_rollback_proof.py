#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CRITICAL = [
    "app/services/diagnostic_transactional_response.py",
    "scripts/check_diagnostics_transaction_rollback_proof.py",
    "tests/integration/test_diagnostics_transaction_rollback_proof.py",
    "tests/unit/test_diagnostic_transactional_response_contracts.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    print("Diagnostic transaction rollback proof check")

    service_source = read("app/services/diagnostic_transactional_response.py")
    for token in [
        "async with self.session.begin()",
        "DiagnosticTransactionError",
        "fail_after_response",
        "fail_after_mastery",
        "fail_after_audit",
        "diagnostic.response_submitted",
    ]:
        if token in service_source:
            print(f"- PASS service contains {token}")
        else:
            failures.append(f"service missing {token}")

    test_source = read("tests/integration/test_diagnostics_transaction_rollback_proof.py")
    for token in [
        "test_diagnostic_response_success_commits_response_mastery_and_audit",
        "test_diagnostic_response_failure_rolls_back_all_rows",
        "test_diagnostic_response_later_failure_does_not_damage_prior_commit",
        "test_mastery_update_cannot_orphan_a_response",
        "sqlite+aiosqlite:///:memory:",
    ]:
        if token in test_source:
            print(f"- PASS test contains {token}")
        else:
            failures.append(f"test missing {token}")

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
                "tests/integration/test_diagnostics_transaction_rollback_proof.py",
                "tests/unit/test_diagnostic_transactional_response_contracts.py",
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
            print("- PASS diagnostic transaction rollback proof tests")
        else:
            failures.append("diagnostic transaction rollback proof tests failed")

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
        print("- PASS focused Ruff diagnostic transaction rollback proof check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS diagnostic transaction rollback proof check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
