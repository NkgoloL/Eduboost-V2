#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.route_tx_impl_plan import write_plan  # noqa: E402


CRITICAL = [
    "scripts/route_tx_impl_plan.py",
    "scripts/patch_route_tx_impl_registry.py",
    "scripts/check_route_tx_impl_plan.py",
    "tests/unit/test_route_tx_impl_plan.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    release_mode = "--release" in sys.argv
    failures: list[str] = []
    print("Route transaction implementation plan check")

    plan = write_plan()
    print(f"- INFO plan status: {plan.plan_status}")
    print(f"- INFO action count: {plan.action_count}")

    if plan.source_status == "missing-inventory":
        failures.append("TX route inventory is missing")
    else:
        print("- PASS source TX route inventory loaded")

    if plan.actions:
        print("- PASS route transaction implementation actions generated")
        for action in plan.actions[:10]:
            print(f"  - {action.id}: {action.route_file}:{action.line}")
    else:
        print("- INFO no unproven mutation routes detected by inventory")

    if any(action.can_be_closed_by_static_marker for action in plan.actions):
        failures.append("route transaction actions must not be closable by static marker")
    else:
        print("- PASS no route action is closable by static marker")

    if release_mode and plan.action_count:
        failures.append("release mode requires route transaction implementation actions to be zero")

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
                "tests/unit/test_route_tx_impl_plan.py",
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
            print("- PASS route transaction implementation plan tests")
        else:
            failures.append("route transaction implementation plan tests failed")

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
        print("- PASS focused Ruff route transaction implementation plan check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS route transaction implementation plan check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
