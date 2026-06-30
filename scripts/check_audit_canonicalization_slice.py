#!/usr/bin/env python3
from __future__ import annotations

from app.services.audit_canonicalization_slice import build_learner_audit_command


def main() -> int:
    print("Audit canonicalization slice check")
    command = build_learner_audit_command(
        action="learner.read",
        actor_id="guardian-1",
        learner_id="learner-1",
        metadata={"source": "slice-check"},
    )
    payload = command.to_event_input().to_canonical_payload()
    failures: list[str] = []
    if payload["action"] != "learner.read":
        failures.append("action mismatch")
    if payload["resource_type"] != "learner":
        failures.append("resource_type mismatch")
    if payload["resource_id"] != "learner-1":
        failures.append("resource_id mismatch")
    if payload["payload"].get("learner_id") != "learner-1":
        failures.append("learner_id missing from payload")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS audit canonicalization slice")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
