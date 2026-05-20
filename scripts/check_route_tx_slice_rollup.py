#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.route_tx_slice_rollup import write_rollup  # noqa: E402

CRITICAL = [
    "scripts/route_tx_slice_rollup.py",
    "scripts/patch_route_tx_slice_rollup_registry.py",
    "scripts/check_route_tx_slice_rollup.py",
    "tests/unit/test_route_tx_slice_rollup.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    release_mode = "--release" in sys.argv
    failures: list[str] = []
    print("Route transaction slice rollup check")
    rollup = write_rollup()
    print(f"- INFO status: {rollup.status}")
    print(f"- INFO local gaps: {rollup.local_source_gap_count}")
    print(f"- INFO live DB gaps: {rollup.live_db_gap_count}")
    print(f"- INFO inventory unproven routes: {rollup.inventory_unproven_route_count}")

    if len(rollup.slices) == 3:
        print("- PASS auth/POPIA/diagnostics slices represented")
    else:
        failures.append("expected three route transaction slices in rollup")

    if rollup.status == "blocked":
        print("- PASS rollup remains blocked while gaps remain")
    elif rollup.status == "route-transaction-slices-release-ready":
        print("- PASS all route transaction slices are release-ready")
    else:
        failures.append(f"unexpected rollup status: {rollup.status}")

    if release_mode and rollup.status != "route-transaction-slices-release-ready":
        failures.append("release mode requires route transaction slice rollup release-ready")

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
                "tests/unit/test_route_tx_slice_rollup.py",
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
            print("- PASS route transaction slice rollup tests")
        else:
            failures.append("route transaction slice rollup tests failed")

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
        print("- PASS focused Ruff route transaction slice rollup check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS route transaction slice rollup check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
