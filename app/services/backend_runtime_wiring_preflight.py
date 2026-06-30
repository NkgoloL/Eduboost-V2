from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.services.audit_migration_orchestrator import allowed_candidate_names, build_audit_migration_event
from app.services.consent_runtime_orchestrator import build_consent_runtime_audit_payload, summarize_consent_runtime_surfaces
from app.services.deep_readiness_route_contracts import public_deep_readiness_checks, unsafe_public_checks


class PreflightArea(str, Enum):
    AUDIT = "audit"
    CONSENT = "consent"
    DEEP_READINESS = "deep_readiness"
    SCHEMA_DRIFT = "schema_drift"


@dataclass(frozen=True)
class RuntimeWiringPreflightResult:
    area: PreflightArea
    passed: bool
    message: str
    details: dict[str, Any]


def check_audit_wiring_preflight() -> RuntimeWiringPreflightResult:
    candidates = allowed_candidate_names()
    if not candidates:
        return RuntimeWiringPreflightResult(
            area=PreflightArea.AUDIT,
            passed=False,
            message="no adapter-ready audit candidates",
            details={},
        )

    envelope = build_audit_migration_event(
        candidate_name=candidates[0],
        action="audit.preflight",
        actor_id="preflight",
        learner_id="learner-preflight",
    )
    payload = envelope.to_event_input().to_canonical_payload()
    passed = payload["resource_id"] == "learner-preflight" and payload["payload"]["migration_candidate"] == candidates[0]
    return RuntimeWiringPreflightResult(
        area=PreflightArea.AUDIT,
        passed=passed,
        message="audit adapter-ready candidate produces canonical payload",
        details={"candidate": candidates[0], "payload_keys": sorted(payload)},
    )


def check_consent_wiring_preflight() -> RuntimeWiringPreflightResult:
    summary = summarize_consent_runtime_surfaces()
    payload = build_consent_runtime_audit_payload(
        action="consent.granted",
        actor_id="preflight",
        learner_id="learner-preflight",
    )
    passed = (
        summary.write_operation_supported
        and summary.read_operation_supported
        and payload["resource_id"] == "learner-preflight"
        and payload["metadata"]["operation_type"] == "write"
    )
    return RuntimeWiringPreflightResult(
        area=PreflightArea.CONSENT,
        passed=passed,
        message="consent runtime normalization and constructor probes are stable",
        details={
            "importable_surfaces": summary.importable_surfaces,
            "missing_surfaces": summary.missing_surfaces,
            "required_parameter_total": summary.required_parameter_total,
        },
    )


def check_deep_readiness_wiring_preflight() -> RuntimeWiringPreflightResult:
    public_checks = public_deep_readiness_checks()
    unsafe = unsafe_public_checks()
    passed = bool(public_checks) and not unsafe
    return RuntimeWiringPreflightResult(
        area=PreflightArea.DEEP_READINESS,
        passed=passed,
        message="deep-readiness catalogue separates public read-only checks from unsafe probes",
        details={
            "public_check_count": len(public_checks),
            "unsafe_public_check_count": len(unsafe),
            "public_checks": [check.name for check in public_checks],
        },
    )


def check_schema_drift_wiring_preflight() -> RuntimeWiringPreflightResult:
    # This is a non-DB preflight. Real DB execution remains under
    # run_disposable_schema_drift_proof.py and make schema-drift-disposable-proof.
    return RuntimeWiringPreflightResult(
        area=PreflightArea.SCHEMA_DRIFT,
        passed=True,
        message="schema-drift runtime wiring is gated by disposable DB proof commands",
        details={
            "requires_real_disposable_db": True,
            "forbidden_repairs": ["alembic stamp head", "production DB mutation"],
        },
    )


def run_all_preflights() -> tuple[RuntimeWiringPreflightResult, ...]:
    return (
        check_audit_wiring_preflight(),
        check_consent_wiring_preflight(),
        check_deep_readiness_wiring_preflight(),
        check_schema_drift_wiring_preflight(),
    )


def all_preflights_pass() -> bool:
    return all(result.passed for result in run_all_preflights())


__all__ = [
    "PreflightArea",
    "RuntimeWiringPreflightResult",
    "all_preflights_pass",
    "check_audit_wiring_preflight",
    "check_consent_wiring_preflight",
    "check_deep_readiness_wiring_preflight",
    "check_schema_drift_wiring_preflight",
    "run_all_preflights",
]
