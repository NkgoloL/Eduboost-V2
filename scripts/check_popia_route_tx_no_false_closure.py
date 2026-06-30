#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.popia_route_tx_gap_plan import write_plan  # noqa: E402


CRITICAL = [
    "scripts/popia_route_tx_gap_plan.py",
    "scripts/check_popia_route_tx_no_false_closure.py",
    "tests/unit/test_popia_route_tx_gap_plan.py",
]


REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def registry_block(item_id: str) -> str:
    if not REGISTRY.exists():
        return ""
    text = REGISTRY.read_text(encoding="utf-8")
    marker = f"id: {item_id}"
    index = text.find(marker)
    if index < 0:
        return ""
    next_index = text.find("\n  - id:", index + 1)
    return text[index:] if next_index < 0 else text[index:next_index]


def registry_status(item_id: str) -> str | None:
    block = registry_block(item_id)
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("proof_status:"):
            return stripped.split(":", 1)[1].strip()
    return None


def main() -> int:
    failures: list[str] = []
    print("POPIA route transaction no-false-closure check")

    plan = write_plan()
    print(f"- INFO source local status: {plan.source_local_status}")
    print(f"- INFO gap plan status: {plan.status}")
    print(f"- INFO gap actions: {plan.action_count}")

    route_status = registry_status("ROUTE-TX-POPIA-001")
    if plan.source_local_status != "route-popia-delegation-passing":
        if route_status in {"runtime-passing", "integration-passing", "production-ready"}:
            failures.append(
                "ROUTE-TX-POPIA-001 cannot be proven while source local status is not passing"
            )
        else:
            print("- PASS ROUTE-TX-POPIA-001 is not falsely marked proven")
    else:
        print("- INFO local source status is passing; live DB proof remains separate")

    if plan.action_count and plan.status != "blocked":
        failures.append("gap plan with actions must remain blocked")
    else:
        print("- PASS gap plan status is consistent with action count")

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
                "tests/unit/test_popia_route_tx_gap_plan.py",
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
            print("- PASS POPIA route transaction gap-plan tests")
        else:
            failures.append("POPIA route transaction gap-plan tests failed")

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
        print("- PASS focused Ruff POPIA route transaction gap-plan check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS POPIA route transaction no-false-closure check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
