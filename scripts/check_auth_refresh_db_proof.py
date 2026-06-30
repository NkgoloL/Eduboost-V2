#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.auth_refresh_db_proof import write_status  # noqa: E402

CRITICAL = [
    "scripts/auth_refresh_db_proof.py",
    "scripts/check_auth_refresh_db_proof.py",
    "scripts/patch_auth_refresh_db_proof_registry.py",
    "tests/unit/test_auth_refresh_db_proof.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    release_mode = "--release" in sys.argv
    run_db = "--run-db" in sys.argv or release_mode
    failures: list[str] = []
    status = write_status(run_pytest=run_db)
    print("Auth refresh DB proof check")
    print(f"- INFO status: {status.status}")

    if release_mode and status.status != "auth-refresh-db-proof-accepted":
        failures.append("release mode requires accepted auth refresh DB proof")
    elif not release_mode:
        print("- PASS local DB proof harness/status generated")

    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")

    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        venv_py = str((ROOT / ".venv" / "bin" / "python")) if (ROOT / ".venv" / "bin" / "python").exists() else sys.executable
        result = subprocess.run(
            [venv_py, "-m", "pytest", "-c", "pytest.ini", "tests/unit/test_auth_refresh_db_proof.py", "-q", "--no-cov", "--tb=short"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )
        print(result.stdout)
        if result.returncode != 0:
            failures.append("auth refresh DB proof unit tests failed")

    venv_py = str((ROOT / ".venv" / "bin" / "python")) if (ROOT / ".venv" / "bin" / "python").exists() else sys.executable
    ruff = subprocess.run(
        [venv_py, "-m", "ruff", "check", *CRITICAL, "--select", "F821,F401,F811,E402"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff auth refresh DB proof check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS auth refresh DB proof local check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
