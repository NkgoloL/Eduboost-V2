#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from app.services.consent_runtime_compatibility import (
    normalize_consent_runtime_operation,
    probe_known_consent_surfaces,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    failures: list[str] = []
    print("Consent runtime compatibility slice check")

    event = normalize_consent_runtime_operation(
        action="consent.granted",
        actor_id="guardian-1",
        learner_id="learner-1",
        source="checker",
    )
    audit = event.to_audit_event()
    if audit["resource_id"] == "learner-1" and audit["metadata"]["operation_type"] == "write":
        print("- PASS consent operation normalizes to audit-compatible write event")
    else:
        print("- FAIL consent operation did not normalize correctly")
        failures.append("normalization failed")

    probes = probe_known_consent_surfaces()
    if probes:
        print(f"- PASS constructor probes returned {len(probes)} surface(s)")
    else:
        print("- FAIL no constructor probes returned")
        failures.append("no probes")

    for probe in probes:
        status = "PASS" if probe.importable else "WARN"
        print(f"- {status} probe {probe.target}: importable={probe.importable}, class_found={probe.class_found}, required={probe.required_parameters}, error={probe.error}")

    doc = REPO_ROOT / "docs/release/consent_runtime_compatibility_slice_001.md"
    if doc.exists() and "non-destructive implementation scaffold" in doc.read_text(encoding="utf-8"):
        print("- PASS consent compatibility slice doc present")
    else:
        print("- FAIL consent compatibility slice doc missing/incomplete")
        failures.append("doc missing")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
