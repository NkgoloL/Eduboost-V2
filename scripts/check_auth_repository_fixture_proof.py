#!/usr/bin/env python3
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CRITICAL = [
    "app/services/auth_application_service.py",
    "app/services/auth_runtime_boundary.py",
    "scripts/repair_auth_repository_fixture_proof.py",
    "scripts/check_auth_repository_fixture_proof.py",
    "tests/integration/test_auth_repository_fixture_proof.py",
    "tests/unit/test_auth_repository_fixture_proof_contracts.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    print("Auth repository fixture proof check")

    app_service = read("app/services/auth_application_service.py")
    runtime = read("app/services/auth_runtime_boundary.py")

    for source_name, source in (
        ("auth_application_service.py", app_service),
        ("auth_runtime_boundary.py", runtime),
    ):
        for canonical, legacy in (
            ("app.repositories.repositories.LearnerRepository", "app.repositories.learner_repository.LearnerRepository"),
            ("app.repositories.repositories.ConsentRepository", "app.repositories.consent_repository.ConsentRepository"),
        ):
            if canonical in source and legacy in source and source.index(canonical) < source.index(legacy):
                print(f"- PASS {source_name} prefers {canonical}")
            else:
                failures.append(f"{source_name} does not prefer {canonical}")

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
            "tests/integration/test_auth_repository_fixture_proof.py",
            "tests/unit/test_auth_repository_fixture_proof_contracts.py",
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
        print("- PASS auth repository fixture proof tests")
    else:
        failures.append("auth repository fixture proof tests failed")

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
        print("- PASS focused Ruff auth repository fixture proof check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS auth repository fixture proof check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
