from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MigrationStatus(str, Enum):
    INVENTORIED = "inventoried"
    ADAPTER_READY = "adapter_ready"
    MIGRATION_READY = "migration_ready"
    MIGRATED = "migrated"
    DEFERRED = "deferred"


@dataclass(frozen=True)
class AuditMigrationCandidate:
    name: str
    source_area: str
    current_shape: str
    canonical_shape: str
    status: MigrationStatus
    destructive: bool = False
    notes: str = ""


DEFAULT_AUDIT_MIGRATION_CANDIDATES = (
    AuditMigrationCandidate(
        name="consent_audit_events",
        source_area="consent runtime",
        current_shape="consent event metadata keyed by learner/resource",
        canonical_shape="AuditEventInput -> AuditRepositoryCompatAdapter.record",
        status=MigrationStatus.MIGRATION_READY,
        notes="safe first migration slice; uses adapter and does not delete legacy paths",
    ),
    AuditMigrationCandidate(
        name="popia_data_rights_audit",
        source_area="POPIA data rights",
        current_shape="service-layer audit emission",
        canonical_shape="canonical action/resource/payload event",
        status=MigrationStatus.ADAPTER_READY,
        notes="requires review of POPIA service call sites before runtime wiring",
    ),
    AuditMigrationCandidate(
        name="legacy_audit_logs",
        source_area="legacy audit persistence",
        current_shape="legacy audit_logs/AuditLog references",
        canonical_shape="retained or migrated after ADR/data-retention approval",
        status=MigrationStatus.DEFERRED,
        destructive=False,
        notes="no deletion or migration until decision record is complete",
    ),
)


def migration_candidates() -> tuple[AuditMigrationCandidate, ...]:
    return DEFAULT_AUDIT_MIGRATION_CANDIDATES


def unsafe_candidates() -> tuple[AuditMigrationCandidate, ...]:
    return tuple(candidate for candidate in DEFAULT_AUDIT_MIGRATION_CANDIDATES if candidate.destructive)


def ready_candidates() -> tuple[AuditMigrationCandidate, ...]:
    return tuple(
        candidate
        for candidate in DEFAULT_AUDIT_MIGRATION_CANDIDATES
        if candidate.status in {MigrationStatus.ADAPTER_READY, MigrationStatus.MIGRATION_READY}
        and not candidate.destructive
    )


__all__ = [
    "AuditMigrationCandidate",
    "DEFAULT_AUDIT_MIGRATION_CANDIDATES",
    "MigrationStatus",
    "migration_candidates",
    "ready_candidates",
    "unsafe_candidates",
]
