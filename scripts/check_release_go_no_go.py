#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.release_go_no_go import write_status  # noqa: E402


CRITICAL = [
    "scripts/release_go_no_go.py",
    "scripts/patch_release_go_no_go_registry.py",
    "scripts/check_release_go_no_go.py",
    "tests/unit/test_release_go_no_go.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    release_mode = "--release" in sys.argv
    failures: list[str] = []
    print("Release go/no-go check")

    status = write_status()
    print(f"- INFO decision: {status.decision}")
    print(f"- INFO beta blockers: {status.beta_blocker_count}")

    if status.decision == "NO-GO":
        print("- PASS generated decision is NO-GO while blockers remain")
    elif status.decision == "GO":
        print("- PASS generated decision is GO")
    else:
        failures.append(f"unexpected decision: {status.decision}")

    if release_mode and status.decision != "GO":
        failures.append("release mode requires generated decision GO")

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
                "tests/unit/test_release_go_no_go.py",
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
            print("- PASS release go/no-go unit tests")
        else:
            failures.append("release go/no-go unit tests failed")

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
        print("- PASS focused Ruff release go/no-go check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS release go/no-go check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
