#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ci_auth_refresh_db_proof_workflow import write_status  # noqa: E402

CRITICAL = [
    "scripts/ci_auth_refresh_db_proof_workflow.py",
    "scripts/check_ci_auth_refresh_db_proof_workflow.py",
    "scripts/patch_ci_auth_refresh_db_proof_workflow_registry.py",
    "tests/unit/test_ci_auth_refresh_db_proof_workflow.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    status = write_status()
    print("CI auth refresh DB proof workflow check")
    print(f"- INFO status: {status.status}")

    if status.status == "ci-auth-refresh-db-proof-workflow-configured":
        print("- PASS CI auth refresh DB proof workflow configured")
    else:
        failures.extend(status.blockers)

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-c", "pytest.ini", "tests/unit/test_ci_auth_refresh_db_proof_workflow.py", "-q", "--no-cov", "--tb=short"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )
        print(result.stdout)
        if result.returncode != 0:
            failures.append("CI auth refresh DB proof workflow unit tests failed")

    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *CRITICAL, "--select", "F821,F401,F811,E402"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff CI auth refresh DB proof workflow check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS CI auth refresh DB proof workflow check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
