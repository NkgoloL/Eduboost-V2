from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.services.deep_readiness_route_contracts import DEFAULT_DEEP_READINESS_CHECKS


REPO_ROOT = Path(__file__).resolve().parents[2]
FIRST_DEEP_READINESS_CANDIDATE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "backend_consolidation"
    / "first_deep_readiness_runtime_candidate.json"
)


@dataclass(frozen=True)
class FirstDeepReadinessRuntimeCandidate:
    id: str
    checks: tuple[str, ...]
    approved_for_runtime_pr: bool
    destructive: bool
    requires_route_change: bool
    requires_schema_change: bool
    requires_database_write_in_test: bool
    allows_public_mutation: bool


@dataclass(frozen=True)
class DeepReadinessRuntimePlan:
    candidate_id: str
    checks: tuple[str, ...]
    public_safe: bool
    mutates_state: bool


def load_first_deep_readiness_runtime_candidate(
    path: Path = FIRST_DEEP_READINESS_CANDIDATE_PATH,
) -> FirstDeepReadinessRuntimeCandidate:
    data = json.loads(path.read_text(encoding="utf-8"))["selected_candidate"]
    return FirstDeepReadinessRuntimeCandidate(
        id=data["id"],
        checks=tuple(data["checks"]),
        approved_for_runtime_pr=bool(data["approved_for_runtime_pr"]),
        destructive=bool(data["destructive"]),
        requires_route_change=bool(data["requires_route_change"]),
        requires_schema_change=bool(data["requires_schema_change"]),
        requires_database_write_in_test=bool(data["requires_database_write_in_test"]),
        allows_public_mutation=bool(data["allows_public_mutation"]),
    )


def assert_deep_readiness_candidate_is_safe(candidate: FirstDeepReadinessRuntimeCandidate) -> None:
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
    if candidate.allows_public_mutation:
        raise ValueError(f"public mutation is blocked in this PR: {candidate.id}")


def build_first_deep_readiness_runtime_plan(
    candidate: FirstDeepReadinessRuntimeCandidate | None = None,
) -> DeepReadinessRuntimePlan:
    selected = candidate or load_first_deep_readiness_runtime_candidate()
    assert_deep_readiness_candidate_is_safe(selected)

    catalogue = {check.name: check for check in DEFAULT_DEEP_READINESS_CHECKS}
    selected_checks = []
    for name in selected.checks:
        if name not in catalogue:
            raise ValueError(f"deep-readiness check missing from catalogue: {name}")
        check = catalogue[name]
        if not check.public_safe or check.mutates_state:
            raise ValueError(f"deep-readiness check is not public/read-only safe: {name}")
        selected_checks.append(name)

    return DeepReadinessRuntimePlan(
        candidate_id=selected.id,
        checks=tuple(selected_checks),
        public_safe=True,
        mutates_state=False,
    )


def validate_first_deep_readiness_runtime_plan(
    candidate: FirstDeepReadinessRuntimeCandidate | None = None,
) -> bool:
    plan = build_first_deep_readiness_runtime_plan(candidate)
    return bool(plan.checks) and plan.public_safe and not plan.mutates_state


__all__ = [
    "FIRST_DEEP_READINESS_CANDIDATE_PATH",
    "DeepReadinessRuntimePlan",
    "FirstDeepReadinessRuntimeCandidate",
    "assert_deep_readiness_candidate_is_safe",
    "build_first_deep_readiness_runtime_plan",
    "load_first_deep_readiness_runtime_candidate",
    "validate_first_deep_readiness_runtime_plan",
]
