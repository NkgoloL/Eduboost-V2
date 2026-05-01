"""V2 study-plan service using the modular-monolith service layer."""

from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import select

from app.api.core.database import AsyncSessionFactory
from app.api.models.db_models import StudyPlan, SubjectMastery
from app.domain.schemas import LearnerSummary
from app.repositories.learner_repository import LearnerRepository


class StudyPlanServiceV2:
    def __init__(self, learner_repository: LearnerRepository | None = None) -> None:
        self.learner_repository = learner_repository or LearnerRepository()

    async def generate_plan(self, learner_id: str, gap_ratio: float = 0.4) -> dict:
        learner = await self.learner_repository.get_by_id(learner_id)
        if learner is None:
            raise ValueError("Learner not found")

        async with AsyncSessionFactory() as session:
            mastery_result = await session.execute(
                select(SubjectMastery).where(SubjectMastery.learner_id == learner_id)
            )
            mastery_rows = mastery_result.scalars().all()

            focus_subjects = sorted(
                mastery_rows,
                key=lambda row: (row.grade_level, row.mastery_score),
            )
            schedule = {
                "monday": [],
                "tuesday": [],
                "wednesday": [],
                "thursday": [],
                "friday": [],
            }
            for idx, row in enumerate(focus_subjects[:5]):
                day = list(schedule.keys())[idx % len(schedule)]
                schedule[day].append(
                    {
                        "subject_code": row.subject_code,
                        "grade_level": row.grade_level,
                        "mastery_score": row.mastery_score,
                        "knowledge_gaps": row.knowledge_gaps or [],
                    }
                )

            plan = StudyPlan(
                plan_id=uuid.uuid4(),
                learner_id=uuid.UUID(learner_id),
                week_start=datetime.now(timezone.utc),
                schedule=schedule,
                gap_ratio=gap_ratio,
                week_focus="Prioritise lowest-grade foundational gaps first",
                generated_by="V2_ALGORITHM",
            )
            session.add(plan)
            await session.commit()
            await session.refresh(plan)

        return {
            "plan_id": str(plan.plan_id),
            "learner_id": learner_id,
            "schedule": plan.schedule,
            "gap_ratio": plan.gap_ratio,
            "week_focus": plan.week_focus,
            "generated_by": plan.generated_by,
        }
