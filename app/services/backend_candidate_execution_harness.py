from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.services.backend_adapter_wiring_service import InMemoryAuditSink, record_all_safe_candidates
from app.services.backend_first_wiring_candidates import build_all_safe_candidate_payloads
from app.services.consent_runtime_orchestrator import build_consent_runtime_audit_payload
from app.services.deep_readiness_route_contracts import public_deep_readiness_checks, unsafe_public_checks


@dataclass(frozen=True)
class HarnessResult:
    name: str
    passed: bool
    details: dict[str, Any]


async def run_audit_candidate_execution_harness() -> HarnessResult:
    sink = InMemoryAuditSink()
    results = await record_all_safe_candidates(sink)
    payloads = build_all_safe_candidate_payloads()
    passed = bool(results) and len(results) == len(payloads) == len(sink.events)
    return HarnessResult(
        name="audit_candidate_execution_harness",
        passed=passed,
        details={
            "payload_count": len(payloads),
            "result_count": len(results),
            "sink_event_count": len(sink.events),
            "actions": [event.get("action") for event in sink.events],
        },
    )


def run_consent_candidate_execution_harness() -> HarnessResult:
    write_payload = build_consent_runtime_audit_payload(
        action="consent.granted",
        actor_id="guardian-harness",
        learner_id="learner-harness",
    )
    read_payload = build_consent_runtime_audit_payload(
        action="consent.status.read",
        actor_id="guardian-harness",
        learner_id="learner-harness",
    )
    passed = (
        write_payload["metadata"]["operation_type"] == "write"
        and read_payload["metadata"]["operation_type"] == "read"
        and write_payload["resource_id"] == "learner-harness"
        and read_payload["resource_id"] == "learner-harness"
    )
    return HarnessResult(
        name="consent_candidate_execution_harness",
        passed=passed,
        details={
            "write_operation_type": write_payload["metadata"]["operation_type"],
            "read_operation_type": read_payload["metadata"]["operation_type"],
            "resource_type": write_payload["resource_type"],
        },
    )


def run_deep_readiness_candidate_execution_harness() -> HarnessResult:
    public_checks = public_deep_readiness_checks()
    unsafe = unsafe_public_checks()
    passed = bool(public_checks) and not unsafe and all(not check.mutates_state for check in public_checks)
    return HarnessResult(
        name="deep_readiness_candidate_execution_harness",
        passed=passed,
        details={
            "public_checks": [check.name for check in public_checks],
            "unsafe_public_checks": [check.name for check in unsafe],
        },
    )


async def run_all_candidate_execution_harnesses() -> tuple[HarnessResult, ...]:
    return (
        await run_audit_candidate_execution_harness(),
        run_consent_candidate_execution_harness(),
        run_deep_readiness_candidate_execution_harness(),
    )


__all__ = [
    "HarnessResult",
    "run_all_candidate_execution_harnesses",
    "run_audit_candidate_execution_harness",
    "run_consent_candidate_execution_harness",
    "run_deep_readiness_candidate_execution_harness",
]
