#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.auth_lifecycle_semantic_proof import write_status  # noqa: E402

CRITICAL = [
    "scripts/auth_lifecycle_semantic_proof.py",
    "scripts/check_auth_lifecycle_semantic_proof.py",
    "scripts/patch_auth_lifecycle_semantic_proof_registry.py",
    "tests/unit/test_auth_lifecycle_semantic_proof.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    release_mode = "--release" in sys.argv
    failures: list[str] = []
    status = write_status()
    print("Auth lifecycle controlled semantic proof check")
    print(f"- INFO status: {status.status}")

    if status.status == "auth-lifecycle-controlled-semantic-proof-passing":
        print("- PASS controlled auth lifecycle semantic proof")
    else:
        failures.extend(status.blockers)

    if release_mode and status.status != "auth-lifecycle-controlled-semantic-proof-passing":
        failures.append("release mode requires controlled auth lifecycle semantic proof passing")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-c", "pytest.ini", "tests/unit/test_auth_lifecycle_semantic_proof.py", "-q", "--no-cov", "--tb=short"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )
        print(result.stdout)
        if result.returncode != 0:
            failures.append("auth lifecycle semantic proof tests failed")

    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *CRITICAL, "app/api_v2_routers/auth.py", "app/services/auth_application_service.py", "--select", "F821,F401,F811,E402"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff auth lifecycle semantic proof check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS auth lifecycle controlled semantic proof check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
