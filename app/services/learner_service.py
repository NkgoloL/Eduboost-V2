"""Learner-facing V2 service layer."""

from __future__ import annotations

from app.domain.schemas import LearnerSummary
from app.repositories.learner_repository import LearnerRepository


class LearnerService:
    def __init__(self, repository: LearnerRepository | None = None) -> None:
        self.repository = repository or LearnerRepository()

    async def get_learner_summary(self, learner_id: str) -> LearnerSummary | None:
        learner = await self.repository.get_by_id(learner_id)
        if learner is None:
            return None
        return LearnerSummary(
            learner_id=learner.learner_id,
            grade=learner.grade,
            home_language=learner.home_language,
            overall_mastery=learner.overall_mastery,
        )
