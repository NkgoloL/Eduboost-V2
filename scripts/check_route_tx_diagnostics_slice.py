#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.route_tx_diagnostics_slice import write_gap_plan, write_report  # noqa: E402

CRITICAL = [
    "scripts/route_tx_diagnostics_slice.py",
    "scripts/patch_route_tx_diagnostics_slice_registry.py",
    "scripts/check_route_tx_diagnostics_slice.py",
    "tests/unit/test_route_tx_diagnostics_slice.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    release_mode = "--release" in sys.argv
    failures: list[str] = []
    print("Diagnostics route transaction slice check")
    report = write_report()
    gap_plan = write_gap_plan()
    print(f"- INFO local status: {report.local_status}")
    print(f"- INFO live DB status: {report.live_db_status}")
    print(f"- INFO selected routes: {report.selected_route_count}")
    print(f"- INFO gap actions: {gap_plan.action_count}")

    if report.local_status == "route-diagnostics-delegation-passing":
        print("- PASS diagnostics route delegation slice is locally proven")
    else:
        print("- PASS diagnostics route delegation slice is honestly not-proven")
    if gap_plan.action_count and gap_plan.status != "blocked":
        failures.append("gap plan with actions must remain blocked")
    else:
        print("- PASS diagnostics gap plan status is consistent")
    if report.live_db_status == "external-blocked":
        print("- PASS live DB proof remains blocked until evidence is attached")
    elif report.live_db_status == "live-db-proof-accepted":
        print("- PASS live DB proof metadata accepted")
    else:
        failures.append(f"unexpected live DB status: {report.live_db_status}")
    if release_mode and (report.local_status != "route-diagnostics-delegation-passing" or report.live_db_status != "live-db-proof-accepted"):
        failures.append("release mode requires local diagnostics route source passing and live DB evidence")
    for path in CRITICAL:
        ast.parse(read(path))
        print(f"- PASS syntax {path}")
    if not os.getenv("SKIP_PYTEST_RECURSION"):
        env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
        result = subprocess.run([sys.executable, "-m", "pytest", "-c", "pytest.ini", "tests/unit/test_route_tx_diagnostics_slice.py", "-q", "--no-cov", "--tb=short"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=False)
        print(result.stdout)
        if result.returncode == 0:
            print("- PASS diagnostics route transaction slice tests")
        else:
            failures.append("diagnostics route transaction slice tests failed")
    ruff = subprocess.run([sys.executable, "-m", "ruff", "check", *CRITICAL, "--select", "F821,F401,F811,E402"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if ruff.returncode == 0:
        print("- PASS focused Ruff diagnostics route transaction slice check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)
    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS diagnostics route transaction slice check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
