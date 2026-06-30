from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.repositories.audit_compat import AuditRepositoryCompatAdapter
from app.services.backend_first_wiring_candidates import WiringCandidatePayload, build_all_safe_candidate_payloads


@dataclass(frozen=True)
class AdapterWiringResult:
    candidate_id: str
    recorded: bool
    response: Any


class InMemoryAuditSink:
    """Test sink for adapter-backed wiring validation.

    This is not a production repository. It exists to prove payload compatibility
    without writing to a database.
    """

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    async def record(self, **kwargs: Any) -> dict[str, Any]:
        self.events.append(kwargs)
        return {"recorded": True, "event_count": len(self.events), "action": kwargs.get("action")}


async def record_candidate_payload(repository: Any, candidate_payload: WiringCandidatePayload) -> AdapterWiringResult:
    adapter = AuditRepositoryCompatAdapter(repository)
    payload = candidate_payload.payload

    response = await adapter.record(
        action=payload["action"],
        actor_id=payload.get("actor_id"),
        resource_type=payload.get("resource_type"),
        resource_id=payload.get("resource_id"),
        metadata=payload.get("payload") or payload.get("metadata") or {},
    )
    return AdapterWiringResult(
        candidate_id=candidate_payload.candidate_id,
        recorded=True,
        response=response,
    )


async def record_all_safe_candidates(repository: Any) -> tuple[AdapterWiringResult, ...]:
    results = []
    for payload in build_all_safe_candidate_payloads():
        results.append(await record_candidate_payload(repository, payload))
    return tuple(results)


__all__ = [
    "AdapterWiringResult",
    "InMemoryAuditSink",
    "record_all_safe_candidates",
    "record_candidate_payload",
]
