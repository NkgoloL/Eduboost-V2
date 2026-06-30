"""First non-destructive audit canonicalization implementation slice."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.repositories.audit_compat import AuditEventInput, AuditRepositoryCompatAdapter


@dataclass(frozen=True)
class CanonicalAuditCommand:
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


def build_learner_audit_command(
    *,
    action: str,
    actor_id: str | None,
    learner_id: str,
    metadata: dict[str, Any] | None = None,
) -> CanonicalAuditCommand:
    if not action:
        raise ValueError("audit action is required")
    if not learner_id:
        raise ValueError("learner_id is required")
    return CanonicalAuditCommand(
        action=action,
        actor_id=actor_id,
        resource_type="learner",
        resource_id=learner_id,
        learner_id=learner_id,
        metadata=dict(metadata or {}),
    )


async def record_learner_audit_event(
    repository: Any,
    *,
    action: str,
    actor_id: str | None,
    learner_id: str,
    metadata: dict[str, Any] | None = None,
) -> Any:
    """Record a learner-scoped audit event through the compatibility adapter.

    This is the first migration seam. Future call-site batches should route
    selected learner/audit-sensitive actions here before any legacy deletion.
    """
    command = build_learner_audit_command(
        action=action,
        actor_id=actor_id,
        learner_id=learner_id,
        metadata=metadata,
    )
    adapter = AuditRepositoryCompatAdapter(repository)
    return await adapter.record(command.to_event_input())


__all__ = [
    "CanonicalAuditCommand",
    "build_learner_audit_command",
    "record_learner_audit_event",
]
