#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.repositories.audit_compat import normalize_audit_kwargs
from app.services.consent_compat import classify_consent_action, normalize_consent_audit_event


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "backend_consolidation"

AUDIT_FIXTURE = FIXTURE_DIR / "audit_canonical_events.json"
CONSENT_FIXTURE = FIXTURE_DIR / "consent_runtime_events.json"
READINESS_FIXTURE = FIXTURE_DIR / "deep_readiness_expected_checks.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_audit_fixtures() -> list[str]:
    failures: list[str] = []
    payload = _load_json(AUDIT_FIXTURE)
    events = payload.get("events", [])
    if not events:
        return ["audit fixture has no events"]

    print(f"Audit fixture probe: {len(events)} event(s)")
    for event in events:
        normalized = normalize_audit_kwargs(**event["input"]).to_canonical_payload()
        expected = event["expected"]
        if normalized["action"] != expected["action"]:
            failures.append(f"{event['name']} action mismatch")
        if normalized["resource_id"] != expected["resource_id"]:
            failures.append(f"{event['name']} resource_id mismatch")
        for key in expected.get("payload_contains", []):
            if key not in normalized["payload"]:
                failures.append(f"{event['name']} payload missing {key}")
        print(f"- PASS [audit] {event['name']}: normalized")
    return failures


def check_consent_fixtures() -> list[str]:
    failures: list[str] = []
    payload = _load_json(CONSENT_FIXTURE)
    events = payload.get("events", [])
    if not events:
        return ["consent fixture has no events"]

    print(f"Consent fixture probe: {len(events)} event(s)")
    for event in events:
        normalized = normalize_consent_audit_event(**event["input"])
        audit_kwargs = normalized.to_audit_kwargs()
        classification = classify_consent_action(event["input"]["action"])
        if classification != event["expected_classification"]:
            failures.append(f"{event['name']} classification mismatch")
        if audit_kwargs["resource_type"] != event["expected_resource_type"]:
            failures.append(f"{event['name']} resource_type mismatch")
        if "learner_id" not in audit_kwargs["metadata"]:
            failures.append(f"{event['name']} missing learner_id metadata")
        print(f"- PASS [consent] {event['name']}: classified={classification}")
    return failures


def check_readiness_fixtures() -> list[str]:
    failures: list[str] = []
    payload = _load_json(READINESS_FIXTURE)
    checks = payload.get("checks", [])
    names = {check.get("name") for check in checks}
    required = {
        "database_connectivity",
        "alembic_current_revision",
        "required_core_tables",
        "audit_persistence_available",
        "consent_persistence_available",
    }
    missing = sorted(required - names)
    if missing:
        failures.append("readiness fixture missing required checks: " + ", ".join(missing))

    for check in checks:
        if check.get("name") == "audit_write_probe" and check.get("mode") != "internal_only_disabled_by_default":
            failures.append("audit_write_probe must be internal_only_disabled_by_default")
        if check.get("mode") not in {"read_only", "ping_only", "internal_only_disabled_by_default"}:
            failures.append(f"{check.get('name')} has unsafe/unknown mode {check.get('mode')}")

    print(f"Deep-readiness fixture probe: {len(checks)} check(s)")
    for check in checks:
        print(f"- PASS [readiness] {check['name']}: mode={check['mode']}")
    return failures


def main() -> int:
    failures: list[str] = []
    print("Backend runtime probe fixture check")
    for path in [AUDIT_FIXTURE, CONSENT_FIXTURE, READINESS_FIXTURE]:
        if path.exists():
            print(f"- PASS [file] {path.relative_to(REPO_ROOT)}: present")
        else:
            print(f"- FAIL [file] {path.relative_to(REPO_ROOT)}: missing")
            failures.append(f"missing {path}")

    if not failures:
        failures.extend(check_audit_fixtures())
        failures.extend(check_consent_fixtures())
        failures.extend(check_readiness_fixtures())

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("- PASS backend runtime probe fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
