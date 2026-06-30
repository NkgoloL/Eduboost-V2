#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from app.services.backend_runtime_wiring_cases import run_all_wiring_cases


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    Path("tests/fixtures/backend_consolidation/audit_runtime_wiring_cases.json"),
    Path("tests/fixtures/backend_consolidation/consent_runtime_wiring_cases.json"),
    Path("tests/fixtures/backend_consolidation/deep_readiness_route_wiring_cases.json"),
    Path("docs/release/backend_runtime_wiring_fixture_contract.md"),
    Path("docs/release/backend_runtime_wiring_test_pack.md"),
]


def main() -> int:
    failures: list[str] = []
    print("Backend runtime wiring fixture case check")

    for path in REQUIRED_FILES:
        full = REPO_ROOT / path
        if full.exists():
            print(f"- PASS [file] {path}: present")
        else:
            print(f"- FAIL [file] {path}: missing")
            failures.append(f"missing {path}")

    for result in run_all_wiring_cases():
        status = "PASS" if result.passed else "FAIL"
        print(f"- {status} [{result.case_name}] {result.message}: {result.details}")
        if not result.passed:
            failures.append(result.case_name)

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS backend runtime wiring fixture cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
