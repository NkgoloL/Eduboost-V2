#!/usr/bin/env python3
from __future__ import annotations

import asyncio
from pathlib import Path

from app.services.backend_adapter_wiring_service import InMemoryAuditSink, record_all_safe_candidates
from app.services.backend_first_wiring_candidates import build_all_safe_candidate_payloads, safe_wiring_candidates, unsafe_wiring_candidates


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    Path("docs/release/backend_first_wiring_candidate_registry.md"),
    Path("docs/release/backend_adapter_wiring_service_contract.md"),
    Path("docs/release/backend_implementation_slice_391_400.md"),
    Path("docs/release/deep_readiness_route_implementation_gate.md"),
    Path("docs/release/schema_drift_real_db_execution_blocker.md"),
]


async def _check_recording() -> tuple[bool, str]:
    sink = InMemoryAuditSink()
    results = await record_all_safe_candidates(sink)
    if not results:
        return False, "no candidate recording results"
    if len(sink.events) != len(results):
        return False, "sink event count mismatch"
    if not all(result.recorded for result in results):
        return False, "some results not recorded"
    return True, f"recorded {len(results)} safe candidate(s)"


def main() -> int:
    failures: list[str] = []
    print("Backend first wiring candidate check")

    safe = safe_wiring_candidates()
    unsafe = unsafe_wiring_candidates()
    payloads = build_all_safe_candidate_payloads()

    if safe:
        print(f"- PASS safe wiring candidates: {len(safe)}")
    else:
        print("- FAIL no safe wiring candidates")
        failures.append("no safe candidates")

    if not unsafe:
        print("- PASS no unsafe wiring candidates in registry")
    else:
        print(f"- FAIL unsafe wiring candidates detected: {[candidate.id for candidate in unsafe]}")
        failures.append("unsafe candidates detected")

    if len(payloads) == len(safe):
        print(f"- PASS payloads generated for all safe candidates: {len(payloads)}")
    else:
        print("- FAIL payload count mismatch")
        failures.append("payload count mismatch")

    ok, message = asyncio.run(_check_recording())
    if ok:
        print(f"- PASS adapter recording: {message}")
    else:
        print(f"- FAIL adapter recording: {message}")
        failures.append(message)

    for doc in REQUIRED_DOCS:
        path = REPO_ROOT / doc
        if path.exists():
            print(f"- PASS [doc] {doc}: present")
        else:
            print(f"- FAIL [doc] {doc}: missing")
            failures.append(f"missing {doc}")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS backend first wiring candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
