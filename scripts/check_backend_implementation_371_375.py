#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from app.services.audit_migration_orchestrator import allowed_candidate_names, build_audit_migration_event
from app.services.consent_runtime_orchestrator import build_consent_runtime_audit_payload, summarize_consent_runtime_surfaces
from app.services.deep_readiness_route_contracts import public_deep_readiness_checks, release_required_checks, unsafe_public_checks


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    Path("docs/release/backend_implementation_slice_371_375.md"),
    Path("docs/release/audit_callsite_migration_slice_002.md"),
    Path("docs/release/consent_runtime_repair_slice_002.md"),
    Path("docs/release/deep_readiness_route_contract_slice_002.md"),
    Path("docs/release/schema_drift_execution_state.md"),
]


def main() -> int:
    failures: list[str] = []
    print("Backend implementation 371-375 check")

    candidates = allowed_candidate_names()
    if candidates:
        print(f"- PASS audit migration allowed candidates: {candidates}")
    else:
        print("- FAIL no allowed audit migration candidates")
        failures.append("no audit candidates")

    event = build_audit_migration_event(
        candidate_name=candidates[0],
        action="audit.migration.slice.test",
        actor_id="checker",
        learner_id="learner-check",
    )
    payload = event.to_event_input().to_canonical_payload()
    if payload["resource_id"] == "learner-check":
        print("- PASS audit migration event maps learner to resource")
    else:
        print("- FAIL audit migration event did not map learner")
        failures.append("audit event mapping")

    consent_payload = build_consent_runtime_audit_payload(
        action="consent.granted",
        actor_id="checker",
        learner_id="learner-check",
    )
    if consent_payload["metadata"]["operation_type"] == "write":
        print("- PASS consent runtime payload classifies write")
    else:
        print("- FAIL consent runtime payload did not classify write")
        failures.append("consent payload classification")

    summary = summarize_consent_runtime_surfaces()
    print(f"- PASS consent probe summary: importable={summary.importable_surfaces}, missing={summary.missing_surfaces}, required_params={summary.required_parameter_total}")

    if unsafe_public_checks():
        print("- FAIL unsafe public deep-readiness checks detected")
        failures.append("unsafe public readiness")
    else:
        print("- PASS no unsafe public deep-readiness checks")

    if release_required_checks() and public_deep_readiness_checks():
        print("- PASS deep-readiness required/public check catalogue present")
    else:
        print("- FAIL deep-readiness catalogue incomplete")
        failures.append("deep readiness catalogue")

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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
