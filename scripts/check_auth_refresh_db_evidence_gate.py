#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.auth_refresh_db_evidence_gate import write_status  # noqa: E402

CRITICAL = [
    "scripts/auth_refresh_db_evidence_gate.py",
    "scripts/attach_auth_refresh_db_evidence.py",
    "scripts/check_auth_refresh_db_evidence_gate.py",
    "scripts/patch_auth_refresh_db_evidence_registry.py",
    "tests/unit/test_auth_refresh_db_evidence_gate.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    release_mode = "--release" in sys.argv
    failures: list[str] = []
    status = write_status()
    print("Auth refresh DB evidence gate check")
    print(f"- INFO status: {status.status}")

    if release_mode and not status.accepted:
        failures.append("release mode requires accepted auth refresh DB evidence")
    elif not release_mode:
        print("- PASS local auth refresh DB evidence status generated")

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
                "tests/unit/test_auth_refresh_db_evidence_gate.py",
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
        if result.returncode != 0:
            failures.append("auth refresh DB evidence gate unit tests failed")

    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *CRITICAL, "--select", "F821,F401,F811,E402"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff auth refresh DB evidence gate check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS auth refresh DB evidence gate check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
