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
        schedule = _build_schedule(weak)
        plan = await self.study_plan_repository.create(
            learner_id=learner_id,
            schedule=schedule,
            gap_ratio=gap_ratio if weak else min(gap_ratio, 0.2),
            week_focus=week_focus,
        )
        await AuditService().log_event("STUDY_PLAN_CREATED", {"week_focus": week_focus}, learner_id)
        return {
            **plan,
            "schedule": schedule,
            "days": schedule,
            "week_focus": week_focus,
        }

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


def _build_schedule(weak: list[dict]) -> dict[str, list[dict]]:
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    gap_subjects = [item.get("subject_code", "General Review") for item in weak if item.get("subject_code")]
    if not gap_subjects:
        gap_subjects = ["English", "Mathematics"]

    weekday_topics = [
        {"label": f"{gap_subjects[0]} Review", "emoji": "📘", "type": "curriculum"},
        {"label": f"{gap_subjects[-1]} Practice", "emoji": "📝", "type": "gap-fill"},
        {"label": "Reading and Reflection", "emoji": "📖", "type": "curriculum"},
        {"label": "Problem Solving", "emoji": "🧠", "type": "gap-fill"},
        {"label": "Weekly Challenge", "emoji": "🏆", "type": "curriculum"},
    ]

    return {
        "Mon": [weekday_topics[0]],
        "Tue": [weekday_topics[1]],
        "Wed": [weekday_topics[2]],
        "Thu": [weekday_topics[3]],
        "Fri": [weekday_topics[4]],
        "Sat": [],
        "Sun": [],
    }
