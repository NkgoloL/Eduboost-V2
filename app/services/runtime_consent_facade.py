from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from app.services.consent_runtime_orchestrator import build_consent_runtime_audit_payload
from app.services.runtime_audit_facade import record_runtime_audit_event

@dataclass(frozen=True)
class ConsentRuntimeEmission:
    action: str
    learner_id: str
    operation_type: str
    audit_recorded: bool

async def emit_consent_runtime_event(*, action: str, learner_id: str, actor_id: str | None = None,
                                     audit_repository: Any | None = None,
                                     metadata: dict[str, Any] | None = None) -> ConsentRuntimeEmission:
    payload = build_consent_runtime_audit_payload(action=action, actor_id=actor_id, learner_id=learner_id,
                                                  metadata={"runtime_consent_facade": True, **(metadata or {})})
    recorded = False
    if audit_repository is not None:
        await record_runtime_audit_event(audit_repository, action=payload["action"], candidate_name="consent_audit_events",
                                         actor_id=actor_id, learner_id=learner_id, resource_type=payload["resource_type"],
                                         metadata=payload["metadata"])
        recorded = True
    return ConsentRuntimeEmission(payload["action"], payload["resource_id"], payload["metadata"]["operation_type"], recorded)
