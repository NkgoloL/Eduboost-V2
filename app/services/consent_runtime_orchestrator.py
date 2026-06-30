from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.services.consent_runtime_compatibility import (
    ConsentRuntimeOperation,
    normalize_consent_runtime_operation,
    probe_known_consent_surfaces,
)


@dataclass(frozen=True)
class ConsentRuntimeCompatibilitySummary:
    importable_surfaces: int
    missing_surfaces: int
    required_parameter_total: int
    write_operation_supported: bool
    read_operation_supported: bool


def summarize_consent_runtime_surfaces() -> ConsentRuntimeCompatibilitySummary:
    probes = probe_known_consent_surfaces()
    importable = [probe for probe in probes if probe.importable and probe.class_found]
    missing = [probe for probe in probes if not (probe.importable and probe.class_found)]
    required_parameter_total = sum(len(probe.required_parameters) for probe in probes)

    write = normalize_consent_runtime_operation(
        action="consent.granted",
        actor_id="compat-check",
        learner_id="learner-probe",
    )
    read = normalize_consent_runtime_operation(
        action="consent.status.read",
        actor_id="compat-check",
        learner_id="learner-probe",
    )

    return ConsentRuntimeCompatibilitySummary(
        importable_surfaces=len(importable),
        missing_surfaces=len(missing),
        required_parameter_total=required_parameter_total,
        write_operation_supported=write.operation_type == "write",
        read_operation_supported=read.operation_type == "read",
    )


def build_consent_runtime_audit_payload(
    *,
    action: str,
    actor_id: str,
    learner_id: str,
    operation_type: str | None = None,
    metadata: dict[str, Any] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    operation: ConsentRuntimeOperation = normalize_consent_runtime_operation(
        action=action,
        actor_id=actor_id,
        learner_id=learner_id,
        operation_type=operation_type,
        metadata=metadata,
        **extra,
    )
    payload = operation.to_audit_event()
    payload["metadata"].setdefault("consent_runtime_orchestrated", True)
    return payload


__all__ = [
    "ConsentRuntimeCompatibilitySummary",
    "build_consent_runtime_audit_payload",
    "summarize_consent_runtime_surfaces",
]
