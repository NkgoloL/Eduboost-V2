#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from app.services.first_consent_runtime_wiring import (
    build_first_consent_runtime_payload,
    load_first_consent_runtime_candidate,
    validate_first_consent_runtime_payload,
)
from app.services.first_deep_readiness_runtime_wiring import (
    build_first_deep_readiness_runtime_plan,
    load_first_deep_readiness_runtime_candidate,
    validate_first_deep_readiness_runtime_plan,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DOCS = [
    Path("docs/release/first_consent_runtime_wiring_pr.md"),
    Path("docs/release/first_deep_readiness_runtime_wiring_pr.md"),
    Path("docs/release/schema_drift_operator_packet_refresh.md"),
    Path("docs/pr/combined_runtime_wiring_pr_checklist.md"),
    Path("docs/release/backend_implementation_slice_431_450.md"),
    Path("docs/release/backend_runtime_wiring_status_rollup.md"),
]


def main() -> int:
    failures: list[str] = []
    print("First consent and deep-readiness runtime wiring check")

    consent_candidate = load_first_consent_runtime_candidate()
    if consent_candidate.approved_for_runtime_pr and not consent_candidate.destructive:
        print(f"- PASS consent candidate safe: {consent_candidate.id}")
    else:
        print(f"- FAIL consent candidate unsafe: {consent_candidate}")
        failures.append("consent candidate unsafe")

    if validate_first_consent_runtime_payload(consent_candidate):
        payload = build_first_consent_runtime_payload(consent_candidate).payload
        print(f"- PASS consent payload valid: {payload}")
    else:
        print("- FAIL consent payload invalid")
        failures.append("consent payload invalid")

    deep_candidate = load_first_deep_readiness_runtime_candidate()
    if deep_candidate.approved_for_runtime_pr and not deep_candidate.destructive:
        print(f"- PASS deep-readiness candidate safe: {deep_candidate.id}")
    else:
        print(f"- FAIL deep-readiness candidate unsafe: {deep_candidate}")
        failures.append("deep-readiness candidate unsafe")

    if validate_first_deep_readiness_runtime_plan(deep_candidate):
        plan = build_first_deep_readiness_runtime_plan(deep_candidate)
        print(f"- PASS deep-readiness plan valid: {plan}")
    else:
        print("- FAIL deep-readiness plan invalid")
        failures.append("deep-readiness plan invalid")

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

    print("- PASS first consent/deep-readiness runtime wiring")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
