"""V2 study-plan service — fully repository-driven.

Delegates all persistence to StudyPlanRepository and LearnerRepository,
keeping this class focused purely on business/scheduling logic.
"""

from __future__ import annotations

from app.repositories.learner_repository import LearnerRepository
from app.repositories.study_plan_repository import StudyPlanRepository
from app.services.audit_service import AuditService


class StudyPlanServiceV2:
    """Generate and retrieve CAPS-aligned study plans for V2 learners."""

    def __init__(
        self,
        learner_repository: LearnerRepository | None = None,
        study_plan_repository: StudyPlanRepository | None = None,
    ) -> None:
        self.learner_repository = learner_repository or LearnerRepository()
        self.study_plan_repository = study_plan_repository or StudyPlanRepository()

    async def generate_plan(self, learner_id: str, gap_ratio: float = 0.4) -> dict:
        """Build a CAPS-aligned weekly schedule from the learner's mastery data."""
        learner = await self.learner_repository.get_by_id(learner_id)
        if learner is None:
            raise ValueError("Learner not found")

        mastery_rows = await self.study_plan_repository.get_subject_mastery(learner_id)

        # Sort by grade ascending, then mastery ascending → lowest-grade gaps first
        focus_subjects = sorted(
            mastery_rows,
            key=lambda row: (row["grade_level"], row["mastery_score"]),
        )

        days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        schedule: dict[str, list] = {d: [] for d in days}

        for idx, row in enumerate(focus_subjects[:10]):
            day = days[idx % len(days)]
            schedule[day].append(
                {
                    "subject_code": row["subject_code"],
                    "grade_level": row["grade_level"],
                    "mastery_score": row["mastery_score"],
                    "knowledge_gaps": row["knowledge_gaps"],
                    "priority": "remediation" if row["mastery_score"] < 0.5 else "grade-level",
                }
            )

        # Determine the week's focus narrative
        weakest = focus_subjects[0] if focus_subjects else None
        week_focus = (
            f"Prioritise Grade {weakest['grade_level']} {weakest['subject_code']} gaps "
            f"(current mastery: {weakest['mastery_score']:.0%})"
            if weakest
            else "Balanced weekly practice across all subjects"
        )

        plan = await self.study_plan_repository.create(
            learner_id=learner_id,
            schedule=schedule,
            gap_ratio=gap_ratio,
            week_focus=week_focus,
        )

        await AuditService().log_event(
            event_type="STUDY_PLAN_GENERATED",
            learner_id=learner_id,
            payload={"plan_id": plan["plan_id"], "gap_ratio": gap_ratio},
        )
        return plan

    async def get_plan(self, plan_id: str) -> dict | None:
        """Return a single study plan by ID."""
        return await self.study_plan_repository.get_by_id(plan_id)

    async def list_plans(self, learner_id: str, limit: int = 10) -> list[dict]:
        """Return recent study plans for a learner."""
        learner = await self.learner_repository.get_by_id(learner_id)
        if learner is None:
            raise ValueError("Learner not found")
        return await self.study_plan_repository.list_for_learner(learner_id, limit=limit)
