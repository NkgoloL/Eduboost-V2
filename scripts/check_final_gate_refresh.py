#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.final_gate_refresh import write_refresh  # noqa: E402


CRITICAL = [
    "scripts/final_gate_refresh.py",
    "scripts/patch_final_gate_refresh_registry.py",
    "scripts/check_final_gate_refresh.py",
    "tests/unit/test_final_gate_refresh.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    release_mode = "--release" in sys.argv
    failures: list[str] = []
    print("Final gate refresh check")

    refresh = write_refresh()
    print(f"- INFO beta decision: {refresh.beta_decision}")
    print(f"- INFO beta blockers: {refresh.beta_blocker_count}")

    if refresh.refresh_results:
        print("- PASS status surfaces refreshed")
    else:
        failures.append("no status surfaces refreshed")

    if refresh.beta_decision == "NO-GO":
        print("- PASS refresh honestly reports NO-GO while blockers remain")
    elif refresh.beta_decision == "GO":
        print("- PASS refresh reports GO")
    else:
        failures.append(f"unexpected beta decision: {refresh.beta_decision}")

    if release_mode and refresh.beta_decision != "GO":
        failures.append("release mode requires final beta gate decision GO")

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
                "tests/unit/test_final_gate_refresh.py",
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
            print("- PASS final gate refresh tests")
        else:
            failures.append("final gate refresh tests failed")

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
        print("- PASS focused Ruff final gate refresh check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS final gate refresh check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
