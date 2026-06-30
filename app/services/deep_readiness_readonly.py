"""Read-only deep-readiness primitives for EduBoost backend consolidation.

This module does not wire routes. It provides a small, testable read-only
contract that future deep-health route work can call without introducing public
write probes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Iterable


class ReadinessSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ReadinessCheckSpec:
    name: str
    description: str
    severity: ReadinessSeverity = ReadinessSeverity.CRITICAL
    read_only: bool = True
    required: bool = True
    evidence_hint: str | None = None


@dataclass(frozen=True)
class ReadinessCheckResult:
    name: str
    passed: bool
    read_only: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)


DEFAULT_READINESS_SPECS: tuple[ReadinessCheckSpec, ...] = (
    ReadinessCheckSpec(
        name="database_connectivity",
        description="Read-only database connectivity ping.",
        evidence_hint="Use SELECT 1 or SQLAlchemy connection ping only.",
    ),
    ReadinessCheckSpec(
        name="alembic_revision",
        description="Read Alembic current/head information without stamping or upgrading.",
        evidence_hint="Read alembic_version/current revision only.",
    ),
    ReadinessCheckSpec(
        name="required_core_tables",
        description="Read-only presence check for required runtime tables.",
        evidence_hint="Use SQLAlchemy inspector table names only.",
    ),
    ReadinessCheckSpec(
        name="audit_persistence_readiness",
        description="Read-only audit repository capability/readiness check.",
        evidence_hint="Do not insert synthetic audit events on public health paths.",
    ),
    ReadinessCheckSpec(
        name="consent_persistence_readiness",
        description="Read-only consent repository/service readiness check.",
        evidence_hint="Do not mutate consent state.",
    ),
)

WRITE_MARKERS = (
    ".commit(",
    ".add(",
    ".delete(",
    "insert into",
    "update ",
    "delete from",
    "alembic stamp",
    "alembic upgrade",
    "alembic downgrade",
)


def assert_read_only_operation(operation_text: str) -> None:
    """Raise if operation text appears to contain write/migration behavior."""
    lowered = operation_text.lower()
    for marker in WRITE_MARKERS:
        if marker in lowered:
            raise ValueError(f"deep-readiness operation is not read-only: {marker}")


def summarize_specs(specs: Iterable[ReadinessCheckSpec] = DEFAULT_READINESS_SPECS) -> dict[str, Any]:
    materialized = list(specs)
    return {
        "total": len(materialized),
        "required": sum(1 for spec in materialized if spec.required),
        "read_only": all(spec.read_only for spec in materialized),
        "names": [spec.name for spec in materialized],
    }


def run_read_only_probe(name: str, probe: Callable[[], Any]) -> ReadinessCheckResult:
    """Run a supplied read-only probe and normalize the result.

    The probe function is caller-supplied so this module remains DB/framework
    agnostic. Mutating probes must not be passed here.
    """
    assert_read_only_operation(getattr(probe, "__name__", name))
    try:
        value = probe()
    except Exception as exc:  # pragma: no cover - exercised by consumers
        return ReadinessCheckResult(
            name=name,
            passed=False,
            read_only=True,
            message=f"{type(exc).__name__}: {exc}",
        )
    return ReadinessCheckResult(
        name=name,
        passed=bool(value) if value is not None else True,
        read_only=True,
        message="probe completed",
        details={"value": value},
    )


__all__ = [
    "DEFAULT_READINESS_SPECS",
    "ReadinessCheckResult",
    "ReadinessCheckSpec",
    "ReadinessSeverity",
    "assert_read_only_operation",
    "run_read_only_probe",
    "summarize_specs",
]
