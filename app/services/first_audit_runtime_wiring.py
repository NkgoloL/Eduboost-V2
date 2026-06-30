from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.repositories.audit_compat import AuditRepositoryCompatAdapter
from app.services.audit_migration_orchestrator import build_audit_migration_event


REPO_ROOT = Path(__file__).resolve().parents[2]
FIRST_AUDIT_WIRING_CANDIDATE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "backend_consolidation"
    / "first_audit_runtime_wiring_candidate.json"
)


@dataclass(frozen=True)
class FirstAuditRuntimeCandidate:
    id: str
    source_candidate: str
    action: str
    actor_id: str
    learner_id: str
    resource_type: str
    approved_for_runtime_pr: bool
    destructive: bool
    requires_route_change: bool
    requires_schema_change: bool
    requires_database_write_in_test: bool


@dataclass(frozen=True)
class FirstAuditRuntimePayload:
    candidate_id: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class FirstAuditRuntimeRecordResult:
    candidate_id: str
    recorded: bool
    response: Any


class InMemoryFirstAuditRuntimeSink:
    """Non-DB audit sink for the first runtime wiring PR.

    This sink proves adapter compatibility without writing to a real database.
    """

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    async def record(self, **kwargs: Any) -> dict[str, Any]:
        self.events.append(kwargs)
        return {
            "recorded": True,
            "event_count": len(self.events),
            "action": kwargs.get("action"),
            "resource_id": kwargs.get("resource_id"),
        }


def load_first_audit_runtime_candidate(
    path: Path = FIRST_AUDIT_WIRING_CANDIDATE_PATH,
) -> FirstAuditRuntimeCandidate:
    data = json.loads(path.read_text(encoding="utf-8"))["selected_candidate"]
    return FirstAuditRuntimeCandidate(
        id=data["id"],
        source_candidate=data["source_candidate"],
        action=data["action"],
        actor_id=data["actor_id"],
        learner_id=data["learner_id"],
        resource_type=data["resource_type"],
        approved_for_runtime_pr=bool(data["approved_for_runtime_pr"]),
        destructive=bool(data["destructive"]),
        requires_route_change=bool(data["requires_route_change"]),
        requires_schema_change=bool(data["requires_schema_change"]),
        requires_database_write_in_test=bool(data["requires_database_write_in_test"]),
    )


def assert_candidate_is_safe(candidate: FirstAuditRuntimeCandidate) -> None:
    if not candidate.approved_for_runtime_pr:
        raise ValueError(f"candidate is not approved for runtime PR: {candidate.id}")
    if candidate.destructive:
        raise ValueError(f"destructive candidate is blocked: {candidate.id}")
    if candidate.requires_route_change:
        raise ValueError(f"route-change candidate is blocked in this PR: {candidate.id}")
    if candidate.requires_schema_change:
        raise ValueError(f"schema-change candidate is blocked in this PR: {candidate.id}")
    if candidate.requires_database_write_in_test:
        raise ValueError(f"DB-writing test candidate is blocked in this PR: {candidate.id}")


def build_first_audit_runtime_payload(
    candidate: FirstAuditRuntimeCandidate | None = None,
) -> FirstAuditRuntimePayload:
    selected = candidate or load_first_audit_runtime_candidate()
    assert_candidate_is_safe(selected)

    envelope = build_audit_migration_event(
        candidate_name=selected.source_candidate,
        action=selected.action,
        actor_id=selected.actor_id,
        learner_id=selected.learner_id,
        resource_type=selected.resource_type,
        metadata={
            "runtime_wiring_candidate_id": selected.id,
            "first_runtime_wiring_pr": True,
        },
    )
    return FirstAuditRuntimePayload(
        candidate_id=selected.id,
        payload=envelope.to_event_input().to_canonical_payload(),
    )


async def record_first_audit_runtime_candidate(
    repository: Any,
    candidate: FirstAuditRuntimeCandidate | None = None,
) -> FirstAuditRuntimeRecordResult:
    runtime_payload = build_first_audit_runtime_payload(candidate)
    payload = runtime_payload.payload
    adapter = AuditRepositoryCompatAdapter(repository)

    response = await adapter.record(
        action=payload["action"],
        actor_id=payload.get("actor_id"),
        resource_type=payload.get("resource_type"),
        resource_id=payload.get("resource_id"),
        payload=payload.get("payload", {}),
    )

    return FirstAuditRuntimeRecordResult(
        candidate_id=runtime_payload.candidate_id,
        recorded=True,
        response=response,
    )


__all__ = [
    "FIRST_AUDIT_WIRING_CANDIDATE_PATH",
    "FirstAuditRuntimeCandidate",
    "FirstAuditRuntimePayload",
    "FirstAuditRuntimeRecordResult",
    "InMemoryFirstAuditRuntimeSink",
    "assert_candidate_is_safe",
    "build_first_audit_runtime_payload",
    "load_first_audit_runtime_candidate",
    "record_first_audit_runtime_candidate",
]
