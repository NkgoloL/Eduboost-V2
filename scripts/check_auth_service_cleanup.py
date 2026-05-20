#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.auth_service_cleanup import write_status  # noqa: E402

CRITICAL = [
    "scripts/auth_service_cleanup.py",
    "scripts/repair_auth_service_cleanup.py",
    "scripts/check_auth_service_cleanup.py",
    "scripts/patch_auth_service_cleanup_registry.py",
    "tests/unit/test_auth_service_cleanup.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    release_mode = "--release" in sys.argv
    failures: list[str] = []
    status = write_status()
    print("Auth service cleanup check")
    print(f"- INFO status: {status.status}")

    if status.status in {"auth-service-monkeypatch-cleaned-route-delegation-pending", "auth-service-cleanup-passing"}:
        print("- PASS no hard auth service cleanup blockers")
    else:
        failures.extend(status.blockers)

    if release_mode and status.status != "auth-service-cleanup-passing":
        failures.append("release mode requires logout/revoke route delegation")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-c", "pytest.ini", "tests/unit/test_auth_service_cleanup.py", "-q", "--no-cov", "--tb=short"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )
        print(result.stdout)
        if result.returncode != 0:
            failures.append("auth service cleanup tests failed")

    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *CRITICAL, "app/services/auth_application_service.py", "--select", "F821,F401,F811,E402"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff auth service cleanup check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS auth service cleanup check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
