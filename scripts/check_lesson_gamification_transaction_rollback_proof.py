#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CRITICAL = [
    "app/services/lesson_transactional_completion.py",
    "scripts/check_lesson_gamification_transaction_rollback_proof.py",
    "tests/integration/test_lesson_gamification_transaction_rollback_proof.py",
    "tests/unit/test_lesson_transactional_completion_contracts.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    print("Lesson gamification transaction rollback proof check")

    service_source = read("app/services/lesson_transactional_completion.py")
    for token in [
        "async with self.session.begin()",
        "fail_after_lesson",
        "fail_after_xp",
        "fail_after_audit",
        "LessonCompletionNotFoundError",
    ]:
        if token in service_source:
            print(f"- PASS service contains {token}")
        else:
            failures.append(f"service missing {token}")

    test_source = read("tests/integration/test_lesson_gamification_transaction_rollback_proof.py")
    for token in [
        "test_lesson_completion_success_commits_lesson_xp_and_audit",
        "test_lesson_completion_failure_rolls_back_all_rows",
        "test_lesson_completion_failure_does_not_damage_prior_committed_rows",
        "test_missing_profile_rolls_back_lesson_completion",
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
                "tests/integration/test_lesson_gamification_transaction_rollback_proof.py",
                "tests/unit/test_lesson_transactional_completion_contracts.py",
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
            print("- PASS lesson gamification transaction rollback proof tests")
        else:
            failures.append("lesson gamification transaction rollback proof tests failed")

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
        print("- PASS focused Ruff lesson gamification transaction rollback proof check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS lesson gamification transaction rollback proof check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
