#!/usr/bin/env python3
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CRITICAL = [
    "app/services/auth_db_lifecycle_proof.py",
    "tests/integration/test_auth_transactional_db_lifecycle_proof.py",
    "scripts/generate_auth_db_lifecycle_proof_report.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    print("Auth DB lifecycle proof check")
    proof_source = read("app/services/auth_db_lifecycle_proof.py")
    for token in (
        "CREATE TABLE IF NOT EXISTS users",
        "CREATE TABLE IF NOT EXISTS refresh_tokens",
        "def register",
        "def login",
        "def refresh",
        "guardian_learner_ids",
    ):
        if token in proof_source:
            print(f"- PASS proof source contains {token}")
        else:
            failures.append(f"proof source missing {token}")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    pytest_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            "pytest.ini",
            "tests/integration/test_auth_transactional_db_lifecycle_proof.py",
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
    if pytest_result.returncode != 0:
        failures.append("transactional auth DB lifecycle tests failed")
    else:
        print("- PASS transactional auth DB lifecycle tests")

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
    if ruff.returncode != 0:
        failures.append("focused ruff failed")
        print(ruff.stdout)
    else:
        print("- PASS focused ruff auth DB lifecycle proof check")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS auth DB lifecycle proof")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
