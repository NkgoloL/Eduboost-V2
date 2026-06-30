#!/usr/bin/env python3
from __future__ import annotations

import asyncio
from pathlib import Path

from app.services.first_audit_runtime_wiring import (
    InMemoryFirstAuditRuntimeSink,
    build_first_audit_runtime_payload,
    load_first_audit_runtime_candidate,
    record_first_audit_runtime_candidate,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DOCS = [
    Path("docs/release/first_audit_runtime_wiring_pr.md"),
    Path("docs/release/first_audit_runtime_wiring_evidence.md"),
    Path("docs/pr/first_audit_runtime_wiring_pr_checklist.md"),
]


async def _record_once() -> tuple[bool, str]:
    sink = InMemoryFirstAuditRuntimeSink()
    result = await record_first_audit_runtime_candidate(sink)
    if not result.recorded:
        return False, "result not recorded"
    if len(sink.events) != 1:
        return False, "sink event count mismatch"
    event = sink.events[0]
    if event["action"] != "consent.granted":
        return False, "unexpected action"
    if event["resource_id"] != "learner-runtime-pr":
        return False, "unexpected resource_id"
    if event["payload"]["runtime_wiring_candidate_id"] != "BCW-421-AUDIT-CONSENT-GRANTED":
        return False, "candidate payload missing"
    return True, "recorded selected candidate through adapter into non-DB sink"


def main() -> int:
    failures: list[str] = []
    print("First audit runtime wiring check")

    candidate = load_first_audit_runtime_candidate()
    if candidate.approved_for_runtime_pr and not candidate.destructive:
        print(f"- PASS selected candidate safe: {candidate.id}")
    else:
        print(f"- FAIL selected candidate unsafe: {candidate}")
        failures.append("unsafe candidate")

    if not any([candidate.requires_route_change, candidate.requires_schema_change, candidate.requires_database_write_in_test]):
        print("- PASS selected candidate requires no route/schema/DB-writing test change")
    else:
        print("- FAIL selected candidate crosses boundary")
        failures.append("candidate boundary")

    payload = build_first_audit_runtime_payload()
    if payload.payload["resource_id"] == "learner-runtime-pr":
        print("- PASS canonical payload maps learner to resource")
    else:
        print("- FAIL canonical payload does not map learner")
        failures.append("payload mapping")

    ok, message = asyncio.run(_record_once())
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

    print("- PASS first audit runtime wiring")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
