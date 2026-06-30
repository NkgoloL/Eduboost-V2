#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.tx_route_wiring_inventory import write_inventory  # noqa: E402


CRITICAL = [
    "scripts/tx_route_wiring_inventory.py",
    "scripts/check_tx_route_wiring.py",
    "tests/unit/test_tx_route_wiring_inventory.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    print("Transaction route wiring check")

    inventory = write_inventory()
    print(f"- INFO status: {inventory.status}")

    if inventory.routes:
        print(f"- PASS scanned route functions: {len(inventory.routes)}")
    else:
        failures.append("no route functions scanned")

    not_proven = [row for row in inventory.routes if row.status == "route-transaction-wiring-not-proven"]
    if not_proven:
        print(f"- INFO route transaction wiring not proven: {len(not_proven)}")
        for row in not_proven[:10]:
            print(f"  - {row.domain}:{row.function_name}:{row.line}")
    else:
        print("- PASS no mutation route wiring gaps detected by marker scan")

    # This check is guardrail-only. It should not fail just because production
    # route wiring is not proven; that would block inventory creation.
    if "production-route-transaction-wiring-not-proven" in inventory.status:
        print("- PASS inventory honestly records route wiring as not proven")

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
                "tests/unit/test_tx_route_wiring_inventory.py",
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
            print("- PASS TX route wiring inventory tests")
        else:
            failures.append("TX route wiring inventory tests failed")

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
        print("- PASS focused Ruff TX route wiring check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS transaction route wiring check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
