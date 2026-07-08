"""Route-level runtime KG integration helpers for PRD-2.4-2.6.

The helpers in this module are deliberately feature-flagged and rollback-safe:
when runtime KG is disabled, not loaded, or cannot project a learner state, the
caller keeps the legacy diagnostic / lesson / study-plan path.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.runtime_kg.feature_flags import RuntimeKGFeatureFlags
from app.services.runtime_kg.integration import diagnostic_evidence_to_runtime_kg
from app.services.runtime_kg.schemas import RuntimeKGProjection


@dataclass(frozen=True)
class RuntimeKGRouteResult:
    """Serializable route metadata for graph-backed behaviour."""

    runtime_kg_enabled: bool
    graph_version: str | None = None
    behaviour: str = "legacy"
    fallback_to_legacy: bool = True
    rollback_reason: str | None = None
    projection_recorded: bool = False
    open_gap_count: int = 0
    focus_items: tuple[dict[str, Any], ...] = field(default_factory=tuple)

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["focus_items"] = list(self.focus_items)
        return payload


def projection_to_route_result(projection: RuntimeKGProjection, *, projection_recorded: bool = True) -> RuntimeKGRouteResult:
    """Convert a projection into route-safe metadata."""

    return RuntimeKGRouteResult(
        runtime_kg_enabled=True,
        graph_version=projection.graph_version,
        behaviour="runtime_kg_projection",
        fallback_to_legacy=False,
        projection_recorded=projection_recorded,
        open_gap_count=len(projection.open_gaps),
        focus_items=tuple(projection.study_plan_focus(limit=5)),
    )


def legacy_runtime_kg_result(reason: str, *, graph_version: str | None = None) -> RuntimeKGRouteResult:
    """Return a normalized rollback/fallback result."""

    return RuntimeKGRouteResult(
        runtime_kg_enabled=False,
        graph_version=graph_version,
        behaviour="legacy",
        fallback_to_legacy=True,
        rollback_reason=reason,
    )


async def build_runtime_kg_diagnostic_projection(
    db: AsyncSession,
    *,
    learner_id: str,
    subject_code: str,
    correct_by_item_id: dict[str, bool],
    item_to_stable_code: dict[str, str],
    flags: RuntimeKGFeatureFlags | None = None,
) -> RuntimeKGRouteResult:
    """Project and persist diagnostic evidence when runtime KG is enabled.

    The legacy diagnostic result remains authoritative. Runtime KG only enriches
    learner state when an active graph exists and diagnostic items can be mapped
    to stable graph node codes.
    """

    resolved_flags = flags or RuntimeKGFeatureFlags.from_env()
    if not resolved_flags.enabled:
        return legacy_runtime_kg_result("runtime_kg_feature_flag_disabled", graph_version=resolved_flags.graph_version)

    evidence = diagnostic_evidence_to_runtime_kg(correct_by_item_id, item_to_stable_code)
    if not evidence:
        return legacy_runtime_kg_result("no_diagnostic_items_mapped_to_runtime_kg", graph_version=resolved_flags.graph_version)

    from app.services.runtime_kg.repository import RuntimeKGRepository

    repo = RuntimeKGRepository(db)
    projection = await repo.project_and_persist_evidence(
        learner_id=learner_id,
        subject_code=subject_code,
        evidence=evidence,
        graph_version=resolved_flags.graph_version,
    )
    if projection is None:
        await repo.record_rollback(
            learner_id=learner_id,
            graph_version=resolved_flags.graph_version,
            reason="active_runtime_kg_graph_missing",
        )
        return legacy_runtime_kg_result("active_runtime_kg_graph_missing", graph_version=resolved_flags.graph_version)
    return projection_to_route_result(projection)


async def build_runtime_kg_study_plan_payload(
    db: AsyncSession,
    *,
    learner_id: str,
    subject_code: str,
    flags: RuntimeKGFeatureFlags | None = None,
) -> dict[str, Any]:
    """Build optional graph-backed study-plan focus payload for jobs/routes."""

    resolved_flags = flags or RuntimeKGFeatureFlags.from_env()
    if not resolved_flags.enabled:
        return legacy_runtime_kg_result("runtime_kg_feature_flag_disabled", graph_version=resolved_flags.graph_version).to_payload()

    from app.services.runtime_kg.repository import RuntimeKGRepository

    repo = RuntimeKGRepository(db)
    focus_items = await repo.get_learner_gap_focus(
        learner_id=learner_id,
        subject_code=subject_code,
        graph_version=resolved_flags.graph_version,
        limit=5,
    )
    if not focus_items:
        return legacy_runtime_kg_result("no_runtime_kg_focus_items", graph_version=resolved_flags.graph_version).to_payload()
    return RuntimeKGRouteResult(
        runtime_kg_enabled=True,
        graph_version=resolved_flags.graph_version,
        behaviour="runtime_kg_study_plan_focus",
        fallback_to_legacy=False,
        projection_recorded=True,
        open_gap_count=len(focus_items),
        focus_items=tuple(focus_items),
    ).to_payload()
