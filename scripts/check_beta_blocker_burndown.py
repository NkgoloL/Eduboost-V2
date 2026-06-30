#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.beta_blocker_burndown import write_plan  # noqa: E402

CRITICAL = [
    "scripts/beta_blocker_burndown.py",
    "scripts/patch_beta_blocker_burndown_registry.py",
    "scripts/check_beta_blocker_burndown.py",
    "tests/unit/test_beta_blocker_burndown.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    release_mode = "--release" in sys.argv
    print("Beta blocker burn-down check")
    plan = write_plan()
    print(f"- INFO burn-down status: {plan.burn_down_status}")
    print(f"- INFO blocker actions: {len(plan.actions)}")
    if plan.source_decision == "NO-GO" and not plan.actions:
        failures.append("NO-GO source decision must have blocker actions")
    else:
        print("- PASS blocker actions are consistent with source decision")
    if plan.actions and plan.release_mode_allowed:
        failures.append("release mode cannot be allowed while blocker actions exist")
    else:
        print("- PASS release mode is not allowed while blockers exist")
    if release_mode and not plan.release_mode_allowed:
        failures.append("release mode requires blocker burn-down status clear")
    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")
    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-c", "pytest.ini", "tests/unit/test_beta_blocker_burndown.py", "-q", "--no-cov", "--tb=short"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )
        print(result.stdout)
        if result.returncode == 0:
            print("- PASS beta blocker burn-down tests")
        else:
            failures.append("beta blocker burn-down tests failed")
    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *CRITICAL, "--select", "F821,F401,F811,E402"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if ruff.returncode == 0:
        print("- PASS focused Ruff beta blocker burn-down check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)
    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS beta blocker burn-down check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
