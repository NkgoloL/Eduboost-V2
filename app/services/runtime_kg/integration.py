"""Runtime KG integration hooks for diagnostics, lessons, and study plans."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.runtime_kg.feature_flags import RuntimeKGFeatureFlags
from app.services.runtime_kg.schemas import LearnerEvidence, RuntimeKGNodeInput
from app.services.runtime_kg.service import RuntimeKGProjectionService

FallbackContextBuilder = Callable[[str, str], Awaitable[dict[str, Any]]]


async def _active_nodes(db: AsyncSession, flags: RuntimeKGFeatureFlags) -> tuple[str, list[RuntimeKGNodeInput]] | None:
    if not flags.enabled:
        return None
    from app.models.runtime_kg import RuntimeKGGraphLoad, RuntimeKGNode

    graph = await db.scalar(
        select(RuntimeKGGraphLoad).where(
            RuntimeKGGraphLoad.graph_version == flags.graph_version,
            RuntimeKGGraphLoad.status == "active",
        )
    )
    if graph is None:
        return None
    result = await db.execute(select(RuntimeKGNode).where(RuntimeKGNode.graph_load_id == graph.id))
    nodes = [
        RuntimeKGNodeInput(
            stable_code=node.stable_code,
            label=node.label,
            node_type=node.node_type,
            curriculum_code=node.curriculum_code,
            grade=node.grade,
            subject_code=node.subject_code,
            strand=node.strand,
            topic=node.topic,
            mastery_weight=node.mastery_weight,
            properties=node.properties_json,
        )
        for node in result.scalars().all()
    ]
    return graph.graph_version, nodes


async def build_lesson_context_with_runtime_kg(
    db: AsyncSession,
    learner_id: str,
    subject: str,
    *,
    fallback_builder: FallbackContextBuilder,
    flags: RuntimeKGFeatureFlags | None = None,
) -> dict[str, Any]:
    """Build lesson context from runtime KG when enabled, otherwise legacy gaps."""

    resolved_flags = flags or RuntimeKGFeatureFlags.from_env()
    active = await _active_nodes(db, resolved_flags)
    if active is None:
        return await fallback_builder(learner_id, subject)
    graph_version, nodes = active
    projection = RuntimeKGProjectionService().project_from_evidence(
        learner_id=learner_id,
        subject_code=subject,
        graph_version=graph_version,
        nodes=[node for node in nodes if node.subject_code == subject],
        evidence=[],
    )
    legacy_context = await fallback_builder(learner_id, subject)
    kg_context = projection.lesson_context(limit=3)
    return {**legacy_context, **kg_context, "legacy_context_preserved": True}


def diagnostic_evidence_to_runtime_kg(
    responses: dict[str, bool],
    item_to_stable_code: dict[str, str],
    *,
    evidence_source: str = "diagnostic",
) -> list[LearnerEvidence]:
    """Convert diagnostic responses into runtime KG evidence rows."""

    evidence: list[LearnerEvidence] = []
    for item_id, correct in responses.items():
        stable_code = item_to_stable_code.get(str(item_id))
        if stable_code:
            evidence.append(LearnerEvidence(stable_code=stable_code, correct=bool(correct), evidence_source=evidence_source))
    return evidence


def runtime_kg_study_plan_focus(context: dict[str, Any], *, limit: int = 5) -> list[dict[str, Any]]:
    """Return study-plan focus items from a runtime KG lesson context."""

    if not context.get("runtime_kg_enabled"):
        return []
    return [
        {
            "stable_code": gap.get("stable_code"),
            "focus": gap.get("topic"),
            "recommended_minutes": 20,
            "reason": "runtime_kg_gap",
        }
        for gap in context.get("knowledge_gaps", [])[:limit]
    ]
