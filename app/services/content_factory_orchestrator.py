"""Deterministic Content Factory orchestrator skeleton."""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.content_coverage import ContentLayer
from app.services.content_generation_runs import ContentGenerationRunService

PIPELINE_STATES = [
    "normalize_load_caps_map",
    "build_coverage_targets",
    "generate_diagnostic_candidates",
    "validate_diagnostic_candidates",
    "route_diagnostics_to_review",
    "generate_lesson_candidates",
    "validate_lesson_candidates",
    "route_lessons_to_review",
    "generate_assessment_blueprints",
    "generate_study_plan_templates",
    "dry_run_seed",
    "seed_staging",
    "verify_coverage",
    "promote_production",
]


@dataclass(frozen=True)
class OrchestratorPlan:
    run_id: uuid.UUID
    generation_enabled: bool
    dry_run: bool
    planned_states: list[str]
    task_count: int


class ContentFactoryOrchestrator:
    def __init__(self, run_service: ContentGenerationRunService | None = None) -> None:
        self.run_service = run_service or ContentGenerationRunService()

    @property
    def generation_enabled(self) -> bool:
        return os.environ.get("CONTENT_FACTORY_GENERATION_ENABLED", "false").lower() in {"1", "true", "yes"}

    async def create_dry_run_plan(self, session: AsyncSession, *, scope_id: str, layers: list[ContentLayer], requested_by: str) -> OrchestratorPlan:
        run = await self.run_service.create_run(
            session,
            scope_id=scope_id,
            layers=layers,
            requested_by=requested_by,
            dry_run=not self.generation_enabled,
        )
        tasks = await self.run_service.create_tasks_for_run(session, run.run_id)
        return OrchestratorPlan(
            run_id=run.run_id,
            generation_enabled=self.generation_enabled,
            dry_run=not self.generation_enabled,
            planned_states=PIPELINE_STATES,
            task_count=len(tasks),
        )

    async def execute_noop(self, session: AsyncSession, run_id: uuid.UUID) -> OrchestratorPlan:
        run = await self.run_service.get_run(session, run_id)
        tasks = await self.run_service.get_run_tasks(session, run_id)
        return OrchestratorPlan(
            run_id=run.run_id,
            generation_enabled=False,
            dry_run=True,
            planned_states=PIPELINE_STATES,
            task_count=len(tasks),
        )
