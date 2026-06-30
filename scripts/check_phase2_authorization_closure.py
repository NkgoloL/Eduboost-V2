#!/usr/bin/env python3
"""Run the final Phase 2 authorization closure checks."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


COMMANDS: tuple[tuple[str, ...], ...] = (
    ("make", "runtime-check"),
    ("make", "openapi-check"),
    ("make", "route-inventory-check"),
    ("make", "pr002r-check"),
    ("make", "phase2-authz-check"),
    ("make", "learner-authz-check"),
    (
        sys.executable,
        "-m",
        "pytest",
        "-c",
        "pytest.ini",
        "tests/unit/test_phase2_authorization_evidence.py",
        "tests/unit/test_check_learner_authz_coverage.py",
        "tests/unit/test_phase2_router_import_smoke.py",
        "tests/unit/test_generate_phase2_authorization_closure_report.py",
        "tests/unit/test_learner_authz_ci_contract.py",
        "-q",
        "--no-cov",
    ),
)


def run_command(command: tuple[str, ...]) -> int:
    print(f"$ {' '.join(command)}", flush=True)
    result = subprocess.run(command, cwd=REPO_ROOT)
    return result.returncode


def main() -> int:
    failures: list[tuple[str, ...]] = []

    for command in COMMANDS:
        if run_command(command) != 0:
            failures.append(command)

    if failures:
        print("\nPhase 2 authorization closure check failed:")
        for command in failures:
            print(f"- {' '.join(command)}")
        return 1

    print("\nPhase 2 authorization closure check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
