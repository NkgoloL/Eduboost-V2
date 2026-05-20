#!/usr/bin/env python3
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.beta_no_go_handoff_packet import write_packet  # noqa: E402


CRITICAL = [
    "scripts/beta_no_go_handoff_packet.py",
    "scripts/check_beta_no_go_handoff_packet.py",
    "scripts/patch_beta_no_go_handoff_registry.py",
    "tests/unit/test_beta_no_go_handoff_packet.py",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    print("Beta NO-GO handoff packet check")

    packet = write_packet()
    print(f"- INFO handoff status: {packet.handoff_status}")
    print(f"- INFO beta decision: {packet.beta_decision}")
    print(f"- INFO blocker count: {packet.blocker_count}")

    if packet.beta_decision == "NO-GO":
        print("- PASS handoff preserves NO-GO state")
    else:
        print("- INFO beta decision is not NO-GO; verify release-mode checks separately")

    if len(packet.required_items) >= 8:
        print("- PASS required evidence items are represented")
    else:
        failures.append("required evidence items missing")

    if all(not item.local_close_allowed for item in packet.required_items):
        print("- PASS no required external/live evidence item is locally closeable")
    else:
        failures.append("some required evidence item is locally closeable")

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
                "tests/unit/test_beta_no_go_handoff_packet.py",
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
            print("- PASS beta NO-GO handoff packet tests")
        else:
            failures.append("beta NO-GO handoff packet tests failed")

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
        print("- PASS focused Ruff beta NO-GO handoff packet check")
    else:
        failures.append("focused Ruff failed")
        print(ruff.stdout)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS beta NO-GO handoff packet check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
