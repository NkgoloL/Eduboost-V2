#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from app.services.backend_candidate_execution_harness import run_all_candidate_execution_harnesses


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FIXTURE = REPO_ROOT / "tests/fixtures/backend_consolidation/runtime_enablement_required_artifacts.json"


def _load_required() -> dict:
    return json.loads(REQUIRED_FIXTURE.read_text(encoding="utf-8"))


async def _run_harnesses() -> tuple[bool, list[str]]:
    failures: list[str] = []
    results = await run_all_candidate_execution_harnesses()
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"- {status} [{result.name}] {result.details}")
        if not result.passed:
            failures.append(result.name)
    return not failures, failures


def main() -> int:
    failures: list[str] = []
    print("Backend runtime enablement guard")

    required = _load_required()
    for relative in required["required_artifacts"]:
        path = REPO_ROOT / relative
        if path.exists():
            print(f"- PASS [artifact] {relative}: present")
        else:
            print(f"- FAIL [artifact] {relative}: missing")
            failures.append(f"missing {relative}")

    ok, harness_failures = asyncio.run(_run_harnesses())
    if not ok:
        failures.extend(harness_failures)

    for action in required["blocked_actions"]:
        print(f"- PASS [blocked] {action}: remains blocked")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS backend runtime enablement guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
