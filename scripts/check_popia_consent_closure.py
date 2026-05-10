#!/usr/bin/env python3
"""Run the full Cluster C POPIA consent/audit closure suite."""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

COMMANDS = (
    ("generate consent inventory", [sys.executable, "scripts/generate_consent_gate_inventory.py"]),
    ("generate consent boundary matrix", [sys.executable, "scripts/generate_popia_consent_boundary_matrix.py"]),
    ("consent gate inventory", ["make", "popia-consent-gate-check"]),
    ("audit event contract", ["make", "audit-contract-check"]),
    ("consent/audit evidence", ["make", "popia-consent-audit-check"]),
    ("consent boundary matrix", ["make", "popia-consent-boundary-check"]),
    ("consent route order", ["make", "popia-consent-order-check"]),
    ("consent route sources", ["make", "popia-consent-source-check"]),
    ("consent rejection audit", ["make", "popia-consent-rejection-audit-check"]),
)


@dataclass(frozen=True)
class ClosureResult:
    name: str
    ok: bool
    returncode: int
    output: str


def run_command(name: str, command: list[str]) -> ClosureResult:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return ClosureResult(
        name=name,
        ok=result.returncode == 0,
        returncode=result.returncode,
        output=(result.stdout + result.stderr).strip(),
    )


def run_checks() -> list[ClosureResult]:
    return [run_command(name, command) for name, command in COMMANDS]


def main() -> int:
    results = run_checks()
    print("POPIA consent closure check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.name}: exit {result.returncode}")
        if not result.ok and result.output:
            print(result.output)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
