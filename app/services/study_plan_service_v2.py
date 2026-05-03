from __future__ import annotations

from typing import Any

from app.services.audit_service import AuditService


class StudyPlanServiceV2:
    def __init__(self, learner_repository: Any | None = None, study_plan_repository: Any | None = None) -> None:
        self.learner_repository = learner_repository or _MissingLearnerRepository()
        self.study_plan_repository = study_plan_repository or _MemoryStudyPlanRepository()

    async def generate_plan(self, learner_id: str, gap_ratio: float = 0.4) -> dict:
        learner = await self.learner_repository.get_by_id(learner_id)
        if learner is None:
            raise ValueError("Learner not found")
        mastery = await self.study_plan_repository.get_subject_mastery(learner_id)
        weak = sorted(mastery, key=lambda m: m.get("mastery_score", 1.0))[:2]
        week_focus = "Balanced revision and grade-level progress"
        if weak:
            week_focus = "Focus on " + ", ".join(item.get("subject_code", "subject") for item in weak)
        plan = await self.study_plan_repository.create(
            learner_id=learner_id,
            schedule={"monday": week_focus},
            gap_ratio=gap_ratio if weak else min(gap_ratio, 0.2),
            week_focus=week_focus,
        )
        await AuditService().log_event("STUDY_PLAN_CREATED", {"week_focus": week_focus}, learner_id)
        return plan

    async def list_plans(self, learner_id: str) -> list[dict]:
        learner = await self.learner_repository.get_by_id(learner_id)
        if learner is None:
            raise ValueError("Learner not found")
        return await self.study_plan_repository.list_for_learner(learner_id)


class _MissingLearnerRepository:
    async def get_by_id(self, learner_id: str):
        return None


class _MemoryStudyPlanRepository:
    async def get_subject_mastery(self, learner_id: str):
        return []

    async def create(self, **kwargs):
        return {"plan_id": "local-plan", **kwargs}

    async def list_for_learner(self, learner_id: str):
        return []
