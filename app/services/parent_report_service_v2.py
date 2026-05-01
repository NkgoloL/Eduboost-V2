"""V2 parent reporting service with BackgroundTasks-friendly output."""

from __future__ import annotations

from sqlalchemy import select

from app.api.core.database import AsyncSessionFactory
from app.api.models.db_models import ParentLearnerLink, SubjectMastery
from app.repositories.learner_repository import LearnerRepository


class ParentReportServiceV2:
    def __init__(self, learner_repository: LearnerRepository | None = None) -> None:
        self.learner_repository = learner_repository or LearnerRepository()

    async def build_report(self, learner_id: str, guardian_id: str) -> dict:
        learner = await self.learner_repository.get_by_id(learner_id)
        if learner is None:
            raise ValueError("Learner not found")

        async with AsyncSessionFactory() as session:
            link_result = await session.execute(
                select(ParentLearnerLink).where(
                    ParentLearnerLink.learner_id == learner_id,
                    ParentLearnerLink.parent_id == guardian_id,
                )
            )
            if link_result.scalar_one_or_none() is None:
                raise ValueError("Guardian is not linked to learner")

            mastery_result = await session.execute(
                select(SubjectMastery).where(SubjectMastery.learner_id == learner_id)
            )
            subjects = [
                {
                    "subject_code": row.subject_code,
                    "mastery_score": row.mastery_score,
                    "knowledge_gaps": row.knowledge_gaps or [],
                }
                for row in mastery_result.scalars().all()
            ]

        return {
            "learner_id": learner.learner_id,
            "grade": learner.grade,
            "overall_mastery": learner.overall_mastery,
            "summary": "V2 parent report generated from modular-monolith service layer.",
            "subjects": subjects,
        }
