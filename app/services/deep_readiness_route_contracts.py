from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ReadinessCheckMode(str, Enum):
    LIGHTWEIGHT = "lightweight"
    DEEP_READONLY = "deep_readonly"
    INTERNAL_MUTATING = "internal_mutating"


@dataclass(frozen=True)
class DeepReadinessRouteCheck:
    name: str
    mode: ReadinessCheckMode
    dependency: str
    public_safe: bool
    mutates_state: bool
    required_for_release: bool


DEFAULT_DEEP_READINESS_CHECKS = (
    DeepReadinessRouteCheck(
        name="database_connectivity",
        mode=ReadinessCheckMode.DEEP_READONLY,
        dependency="database",
        public_safe=True,
        mutates_state=False,
        required_for_release=True,
    ),
    DeepReadinessRouteCheck(
        name="alembic_revision",
        mode=ReadinessCheckMode.DEEP_READONLY,
        dependency="database_schema",
        public_safe=True,
        mutates_state=False,
        required_for_release=True,
    ),
    DeepReadinessRouteCheck(
        name="required_table_presence",
        mode=ReadinessCheckMode.DEEP_READONLY,
        dependency="database_schema",
        public_safe=True,
        mutates_state=False,
        required_for_release=True,
    ),
    DeepReadinessRouteCheck(
        name="audit_persistence_capability",
        mode=ReadinessCheckMode.DEEP_READONLY,
        dependency="audit",
        public_safe=True,
        mutates_state=False,
        required_for_release=True,
    ),
    DeepReadinessRouteCheck(
        name="consent_persistence_capability",
        mode=ReadinessCheckMode.DEEP_READONLY,
        dependency="consent",
        public_safe=True,
        mutates_state=False,
        required_for_release=True,
    ),
    DeepReadinessRouteCheck(
        name="mutating_audit_probe",
        mode=ReadinessCheckMode.INTERNAL_MUTATING,
        dependency="audit",
        public_safe=False,
        mutates_state=True,
        required_for_release=False,
    ),
)


def public_deep_readiness_checks() -> tuple[DeepReadinessRouteCheck, ...]:
    return tuple(
        check
        for check in DEFAULT_DEEP_READINESS_CHECKS
        if check.public_safe and not check.mutates_state
    )


def unsafe_public_checks() -> tuple[DeepReadinessRouteCheck, ...]:
    return tuple(
        check
        for check in DEFAULT_DEEP_READINESS_CHECKS
        if check.public_safe and check.mutates_state
    )


def release_required_checks() -> tuple[DeepReadinessRouteCheck, ...]:
    return tuple(check for check in DEFAULT_DEEP_READINESS_CHECKS if check.required_for_release)


__all__ = [
    "DEFAULT_DEEP_READINESS_CHECKS",
    "DeepReadinessRouteCheck",
    "ReadinessCheckMode",
    "public_deep_readiness_checks",
    "release_required_checks",
    "unsafe_public_checks",
]
