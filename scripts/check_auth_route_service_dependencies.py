#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.auth_route_service_dependency_repair import write_status  # noqa: E402

CRITICAL = [
    "scripts/auth_route_service_dependency_repair.py",
    "scripts/repair_auth_route_service_dependencies.py",
    "scripts/check_auth_route_service_dependencies.py",
    "tests/unit/test_auth_route_service_dependency_repair.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    status = write_status()
    print("Auth route service dependency repair check")
    print(f"- INFO status: {status.status}")
    if status.status == "auth-route-service-dependencies-passing":
        print("- PASS every auth route using auth_service declares the dependency")
    else:
        failures.extend(status.blockers)

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-c", "pytest.ini", "tests/unit/test_auth_route_service_dependency_repair.py", "tests/unit/test_auth_route_logout_delegate.py", "-q", "--no-cov", "--tb=short"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )
        print(result.stdout)
        if result.returncode != 0:
            failures.append("auth route service dependency tests failed")

    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *CRITICAL, "app/api_v2_routers/auth.py", "--select", "F821,F401,F811,E402"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff auth route service dependency check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS auth route service dependency repair check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
