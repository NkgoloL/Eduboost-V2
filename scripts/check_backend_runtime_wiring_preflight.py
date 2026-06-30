#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from app.services.backend_runtime_wiring_preflight import run_all_preflights


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    Path("docs/release/backend_runtime_wiring_preflight.md"),
    Path("docs/release/backend_implementation_decision_ledger.md"),
    Path("docs/release/backend_implementation_terminal_progress_packet.md"),
    Path("docs/release/schema_drift_execution_gate_hardening.md"),
]


def main() -> int:
    failures: list[str] = []
    print("Backend runtime wiring preflight check")

    for result in run_all_preflights():
        status = "PASS" if result.passed else "FAIL"
        print(f"- {status} [{result.area.value}] {result.message}: {result.details}")
        if not result.passed:
            failures.append(result.area.value)

    for doc in REQUIRED_DOCS:
        path = REPO_ROOT / doc
        if path.exists():
            print(f"- PASS [doc] {doc}: present")
        else:
            print(f"- FAIL [doc] {doc}: missing")
            failures.append(f"missing {doc}")

    ledger = REPO_ROOT / "docs/release/backend_implementation_decision_ledger.md"
    if ledger.exists():
        text = ledger.read_text(encoding="utf-8").lower()
        for needle in ["destructive decisions default to blocked", "alembic stamp head", "blocked"]:
            if needle in text:
                print(f"- PASS [ledger] contains {needle!r}")
            else:
                print(f"- FAIL [ledger] missing {needle!r}")
                failures.append(f"ledger missing {needle}")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS backend runtime wiring preflight")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
