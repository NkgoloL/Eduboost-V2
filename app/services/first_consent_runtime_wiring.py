from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.services.consent_runtime_orchestrator import build_consent_runtime_audit_payload


REPO_ROOT = Path(__file__).resolve().parents[2]
FIRST_CONSENT_WIRING_CANDIDATE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "backend_consolidation"
    / "first_consent_runtime_wiring_candidate.json"
)


@dataclass(frozen=True)
class FirstConsentRuntimeCandidate:
    id: str
    action: str
    actor_id: str
    learner_id: str
    expected_operation_type: str
    expected_resource_type: str
    approved_for_runtime_pr: bool
    destructive: bool
    requires_route_change: bool
    requires_schema_change: bool
    requires_database_write_in_test: bool
    requires_table_merge: bool


@dataclass(frozen=True)
class FirstConsentRuntimePayload:
    candidate_id: str
    payload: dict[str, Any]


def load_first_consent_runtime_candidate(
    path: Path = FIRST_CONSENT_WIRING_CANDIDATE_PATH,
) -> FirstConsentRuntimeCandidate:
    data = json.loads(path.read_text(encoding="utf-8"))["selected_candidate"]
    return FirstConsentRuntimeCandidate(
        id=data["id"],
        action=data["action"],
        actor_id=data["actor_id"],
        learner_id=data["learner_id"],
        expected_operation_type=data["expected_operation_type"],
        expected_resource_type=data["expected_resource_type"],
        approved_for_runtime_pr=bool(data["approved_for_runtime_pr"]),
        destructive=bool(data["destructive"]),
        requires_route_change=bool(data["requires_route_change"]),
        requires_schema_change=bool(data["requires_schema_change"]),
        requires_database_write_in_test=bool(data["requires_database_write_in_test"]),
        requires_table_merge=bool(data["requires_table_merge"]),
    )


def assert_consent_candidate_is_safe(candidate: FirstConsentRuntimeCandidate) -> None:
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
    if candidate.requires_table_merge:
        raise ValueError(f"consent table merge is blocked in this PR: {candidate.id}")


def build_first_consent_runtime_payload(
    candidate: FirstConsentRuntimeCandidate | None = None,
) -> FirstConsentRuntimePayload:
    selected = candidate or load_first_consent_runtime_candidate()
    assert_consent_candidate_is_safe(selected)

    payload = build_consent_runtime_audit_payload(
        action=selected.action,
        actor_id=selected.actor_id,
        learner_id=selected.learner_id,
        metadata={
            "runtime_wiring_candidate_id": selected.id,
            "first_consent_runtime_wiring_pr": True,
        },
    )
    payload["metadata"].setdefault("runtime_wiring_candidate_id", selected.id)
    payload["metadata"].setdefault("first_consent_runtime_wiring_pr", True)

    return FirstConsentRuntimePayload(candidate_id=selected.id, payload=payload)


def validate_first_consent_runtime_payload(
    candidate: FirstConsentRuntimeCandidate | None = None,
) -> bool:
    selected = candidate or load_first_consent_runtime_candidate()
    payload = build_first_consent_runtime_payload(selected).payload
    return (
        payload["resource_id"] == selected.learner_id
        and payload["resource_type"] == selected.expected_resource_type
        and payload["metadata"]["operation_type"] == selected.expected_operation_type
        and payload["metadata"]["runtime_wiring_candidate_id"] == selected.id
    )


__all__ = [
    "FIRST_CONSENT_WIRING_CANDIDATE_PATH",
    "FirstConsentRuntimeCandidate",
    "FirstConsentRuntimePayload",
    "assert_consent_candidate_is_safe",
    "build_first_consent_runtime_payload",
    "load_first_consent_runtime_candidate",
    "validate_first_consent_runtime_payload",
]
