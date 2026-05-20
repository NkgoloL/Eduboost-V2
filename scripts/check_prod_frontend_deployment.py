#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.prod_frontend_deployment import write_status  # noqa: E402


CRITICAL = [
    "scripts/prod_frontend_deployment.py",
    "scripts/repair_prod_frontend_deployment.py",
    "scripts/check_prod_frontend_deployment.py",
    "tests/unit/test_prod_frontend_deployment.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    release_mode = "--release" in sys.argv
    failures: list[str] = []
    print("Production frontend deployment check")

    status = write_status()
    print(f"- INFO status: {status.status}")

    if status.status == "production-frontend-configured":
        print("- PASS production frontend deployment config is present")
    else:
        failures.extend(status.blockers)

    if release_mode and status.status != "production-frontend-configured":
        failures.append("release mode requires production frontend deployment configuration")

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
                "tests/unit/test_prod_frontend_deployment.py",
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
            print("- PASS production frontend deployment tests")
        else:
            failures.append("production frontend deployment tests failed")

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
        print("- PASS focused Ruff production frontend deployment check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS production frontend deployment check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
