from __future__ import annotations

from typing import Any


class LearnerService:
    def __init__(self, repository: Any) -> None:
        self.repository = repository

    async def get_learner_summary(self, learner_id: str):
        return await self.repository.get_by_id(learner_id)
