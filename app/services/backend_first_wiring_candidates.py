from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from app.services.audit_migration_orchestrator import build_audit_migration_event
from app.services.consent_runtime_orchestrator import build_consent_runtime_audit_payload


REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "tests" / "fixtures" / "backend_consolidation" / "backend_wiring_candidate_registry.json"


class WiringArea(str, Enum):
    AUDIT = "audit"
    CONSENT = "consent"


@dataclass(frozen=True)
class WiringCandidate:
    id: str
    area: WiringArea
    name: str
    action: str
    actor_id: str
    learner_id: str
    approved_for_wiring: bool
    destructive: bool
    requires_route_change: bool
    candidate_name: str | None = None
    resource_type: str | None = None


@dataclass(frozen=True)
class WiringCandidatePayload:
    candidate_id: str
    area: WiringArea
    payload: dict[str, Any]


def _load_registry_payload(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_wiring_candidates(path: Path = REGISTRY_PATH) -> tuple[WiringCandidate, ...]:
    payload = _load_registry_payload(path)
    candidates = []
    for item in payload.get("candidates", []):
        candidates.append(
            WiringCandidate(
                id=item["id"],
                area=WiringArea(item["area"]),
                name=item["name"],
                action=item["action"],
                actor_id=item["actor_id"],
                learner_id=item["learner_id"],
                approved_for_wiring=bool(item["approved_for_wiring"]),
                destructive=bool(item["destructive"]),
                requires_route_change=bool(item["requires_route_change"]),
                candidate_name=item.get("candidate_name"),
                resource_type=item.get("resource_type"),
            )
        )
    return tuple(candidates)


def safe_wiring_candidates() -> tuple[WiringCandidate, ...]:
    return tuple(
        candidate
        for candidate in load_wiring_candidates()
        if candidate.approved_for_wiring
        and not candidate.destructive
        and not candidate.requires_route_change
    )


def build_candidate_payload(candidate: WiringCandidate) -> WiringCandidatePayload:
    if candidate.destructive:
        raise ValueError(f"destructive candidate is blocked: {candidate.id}")
    if candidate.requires_route_change:
        raise ValueError(f"route-change candidate is blocked in this pack: {candidate.id}")
    if not candidate.approved_for_wiring:
        raise ValueError(f"candidate not approved for wiring: {candidate.id}")

    if candidate.area is WiringArea.AUDIT:
        if not candidate.candidate_name:
            raise ValueError(f"audit candidate missing candidate_name: {candidate.id}")
        envelope = build_audit_migration_event(
            candidate_name=candidate.candidate_name,
            action=candidate.action,
            actor_id=candidate.actor_id,
            learner_id=candidate.learner_id,
            resource_type=candidate.resource_type,
        )
        return WiringCandidatePayload(
            candidate_id=candidate.id,
            area=candidate.area,
            payload=envelope.to_event_input().to_canonical_payload(),
        )

    if candidate.area is WiringArea.CONSENT:
        return WiringCandidatePayload(
            candidate_id=candidate.id,
            area=candidate.area,
            payload=build_consent_runtime_audit_payload(
                action=candidate.action,
                actor_id=candidate.actor_id,
                learner_id=candidate.learner_id,
            ),
        )

    raise ValueError(f"unknown wiring area: {candidate.area}")


def build_all_safe_candidate_payloads() -> tuple[WiringCandidatePayload, ...]:
    return tuple(build_candidate_payload(candidate) for candidate in safe_wiring_candidates())


def unsafe_wiring_candidates() -> tuple[WiringCandidate, ...]:
    return tuple(
        candidate
        for candidate in load_wiring_candidates()
        if candidate.destructive or candidate.requires_route_change or not candidate.approved_for_wiring
    )


__all__ = [
    "REGISTRY_PATH",
    "WiringArea",
    "WiringCandidate",
    "WiringCandidatePayload",
    "build_all_safe_candidate_payloads",
    "build_candidate_payload",
    "load_wiring_candidates",
    "safe_wiring_candidates",
    "unsafe_wiring_candidates",
]
