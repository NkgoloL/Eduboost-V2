from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Awaitable, Protocol
from app.repositories.audit_compat import AuditRepositoryCompatAdapter
from app.services.audit_migration_orchestrator import build_audit_migration_event

class AuditRecordRepository(Protocol):
    def record(self, **kwargs: Any) -> Awaitable[Any]: ...

@dataclass(frozen=True)
class RuntimeAuditRecord:
    action: str
    resource_id: str | None
    metadata: dict[str, Any]

async def record_runtime_audit_event(repository: AuditRecordRepository, *, action: str, candidate_name: str,
                                     actor_id: str | None = None, learner_id: str | None = None,
                                     resource_type: str = "runtime_event",
                                     metadata: dict[str, Any] | None = None) -> RuntimeAuditRecord:
    envelope = build_audit_migration_event(
        candidate_name=candidate_name, action=action, actor_id=actor_id, learner_id=learner_id,
        resource_type=resource_type, metadata={"runtime_audit_facade": True, **(metadata or {})},
    )
    payload = envelope.to_event_input().to_canonical_payload()
    await AuditRepositoryCompatAdapter(repository).record(
        action=payload["action"], actor_id=payload.get("actor_id"),
        resource_type=payload.get("resource_type"), resource_id=payload.get("resource_id"),
        payload=payload.get("payload", {}),
    )
    return RuntimeAuditRecord(action=payload["action"], resource_id=payload.get("resource_id"), metadata=payload.get("payload", {}))
