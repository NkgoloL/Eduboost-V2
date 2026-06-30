from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.repositories.audit_compat import AuditEventInput, AuditRepositoryCompatAdapter
from app.services.audit_canonicalization_registry import MigrationStatus, migration_candidates


@dataclass(frozen=True)
class AuditMigrationEnvelope:
    candidate_name: str
    action: str
    actor_id: str | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    learner_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_event_input(self) -> AuditEventInput:
        return AuditEventInput(
            action=self.action,
            actor_id=self.actor_id,
            resource_type=self.resource_type,
            resource_id=self.resource_id,
            learner_id=self.learner_id,
            metadata=dict(self.metadata),
        )


def allowed_candidate_names() -> tuple[str, ...]:
    return tuple(
        candidate.name
        for candidate in migration_candidates()
        if candidate.status in {MigrationStatus.ADAPTER_READY, MigrationStatus.MIGRATION_READY}
        and not candidate.destructive
    )


def build_audit_migration_event(
    *,
    candidate_name: str,
    action: str,
    actor_id: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    learner_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    **extra: Any,
) -> AuditMigrationEnvelope:
    if candidate_name not in allowed_candidate_names():
        raise ValueError(f"audit migration candidate is not adapter-ready: {candidate_name}")
    if not action:
        raise ValueError("audit migration action is required")

    merged_metadata = dict(metadata or {})
    merged_metadata.update(extra)
    merged_metadata.setdefault("migration_candidate", candidate_name)

    return AuditMigrationEnvelope(
        candidate_name=candidate_name,
        action=action,
        actor_id=actor_id,
        resource_type=resource_type,
        resource_id=resource_id,
        learner_id=learner_id,
        metadata=merged_metadata,
    )


async def record_migrated_audit_event(repository: Any, envelope: AuditMigrationEnvelope) -> Any:
    adapter = AuditRepositoryCompatAdapter(repository)
    return await adapter.record(envelope.to_event_input())


__all__ = [
    "AuditMigrationEnvelope",
    "allowed_candidate_names",
    "build_audit_migration_event",
    "record_migrated_audit_event",
]
