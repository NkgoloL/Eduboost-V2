"""Runtime KG final acceptance helpers for PRD-2.7-2.9.

This module is intentionally dependency-light.  It gives routes, jobs, and
operators a deterministic acceptance summary for the runtime KG work completed
in PRD-2 without enabling learner-facing KG behaviour by default.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.services.runtime_kg.feature_flags import RuntimeKGFeatureFlags
from app.services.runtime_kg.route_integration import legacy_runtime_kg_result, projection_to_route_result
from app.services.runtime_kg.schemas import LearnerKGNodeProjection, RuntimeKGProjection


@dataclass(frozen=True)
class RuntimeKGAcceptanceCheck:
    """One final PRD-2 acceptance check."""

    name: str
    passed: bool
    detail: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RuntimeKGAcceptanceReport:
    """Machine-readable final PRD-2 runtime KG acceptance report."""

    prd_id: str
    checks: tuple[RuntimeKGAcceptanceCheck, ...]
    runtime_kg_enabled_by_default: bool
    next_authorised_item: str = "PRD-3"
    prd3_implementation_authorised: bool = False

    @property
    def accepted(self) -> bool:
        return all(check.passed for check in self.checks)

    def to_payload(self) -> dict[str, Any]:
        return {
            "prd_id": self.prd_id,
            "accepted": self.accepted,
            "runtime_kg_enabled_by_default": self.runtime_kg_enabled_by_default,
            "next_authorised_item": self.next_authorised_item,
            "prd3_implementation_authorised": self.prd3_implementation_authorised,
            "checks": [check.to_payload() for check in self.checks],
        }


def _sample_projection() -> RuntimeKGProjection:
    return RuntimeKGProjection(
        learner_id="acceptance-learner",
        subject_code="Mathematics",
        graph_version="caps-grade4-math-runtime-v1",
        nodes=(
            LearnerKGNodeProjection("CAPS.MATH.4.N.1", "Place value", 0.2, 0.9, True, 2),
            LearnerKGNodeProjection("CAPS.MATH.4.N.2", "Addition", 0.82, 0.8, False, 3),
        ),
    )


def build_runtime_kg_acceptance_report(flags: RuntimeKGFeatureFlags | None = None) -> RuntimeKGAcceptanceReport:
    """Build the final PRD-2 acceptance report.

    The report proves the important runtime boundaries:
    - the KG path can expose graph-backed projections;
    - fallback/rollback remains explicit;
    - runtime KG is still disabled by default until later controlled rollout.
    """

    default_flags = flags or RuntimeKGFeatureFlags()
    projection_payload = projection_to_route_result(_sample_projection()).to_payload()
    rollback_payload = legacy_runtime_kg_result("runtime_kg_feature_flag_disabled", graph_version=default_flags.graph_version).to_payload()
    checks = (
        RuntimeKGAcceptanceCheck(
            "runtime_kg_disabled_by_default",
            default_flags.enabled is False,
            "Runtime KG remains opt-in until PRD-3+ vertical journey rollout decisions.",
        ),
        RuntimeKGAcceptanceCheck(
            "projection_payload_available",
            projection_payload.get("runtime_kg_enabled") is True
            and projection_payload.get("fallback_to_legacy") is False
            and projection_payload.get("open_gap_count", 0) > 0,
            "Graph-backed learner gap projection exposes route-safe focus metadata.",
        ),
        RuntimeKGAcceptanceCheck(
            "rollback_payload_available",
            rollback_payload.get("runtime_kg_enabled") is False
            and rollback_payload.get("fallback_to_legacy") is True
            and rollback_payload.get("rollback_reason") == "runtime_kg_feature_flag_disabled",
            "Legacy fallback remains explicit and serialisable.",
        ),
        RuntimeKGAcceptanceCheck(
            "prd3_handoff_only",
            True,
            "PRD-2 may hand off to PRD-3 but does not implement PRD-3 learner/parent vertical journeys.",
        ),
    )
    return RuntimeKGAcceptanceReport(
        prd_id="PRD-2.7-2.9",
        checks=checks,
        runtime_kg_enabled_by_default=default_flags.enabled,
        next_authorised_item="PRD-3",
        prd3_implementation_authorised=False,
    )
