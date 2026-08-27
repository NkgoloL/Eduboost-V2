"""Application service for practice sessions."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from app.modules.practice.practice_generator import PracticeGenerator
from app.modules.practice.spaced_repetition_scheduler import SpacedRepetitionScheduler
from app.repositories.item_bank_repository import ItemBankRepository
from app.repositories.practice_session_repository import PracticeSessionRepository


class PracticeService:
    def __init__(self, session_repo: PracticeSessionRepository, item_repo: ItemBankRepository) -> None:
        self.session_repo = session_repo
        self.item_repo = item_repo
        self.generator = PracticeGenerator()
        self.scheduler = SpacedRepetitionScheduler()

    @classmethod
    def from_session(cls, session: Any) -> PracticeService:
        return cls(
            session_repo=PracticeSessionRepository(session),
            item_repo=ItemBankRepository(session),
        )

    async def create_session(
        self,
        *,
        learner_id: str,
        owner_subject: str,
        gap_topics: list[str],
        theta: float = 0.0,
    ) -> tuple[str, int]:
        items: list[Any] = []
        for caps_ref in gap_topics:
            items.extend(await self.item_repo.list_by_caps_ref(caps_ref, limit=100))
        selected = self.generator.select_items(items, gap_topics=gap_topics, theta=theta, per_gap=5)

        session = await self.session_repo.create(
            learner_id=learner_id,
            owner_subject=owner_subject,
            items=[str(getattr(i, "item_id", i)) for i in selected],
            gap_topics=gap_topics,
            theta=theta,
        )
        return session.id, len(selected)

    async def get_session(self, session_id: str) -> Any | None:
        return await self.session_repo.get_by_id(session_id)

    async def record_response(self, session: Any, response_data: dict, correct: bool) -> dict:
        new_responses = session.responses + [response_data]
        new_cursor = session.cursor + 1
        await self.session_repo.update_cursor_and_responses(session.id, new_cursor, new_responses)
        
        schedule = self.scheduler.update_schedule(correct=correct)
        if new_cursor >= len(session.items):
            await self.session_repo.mark_completed(session.id)
            return {
                "completed": True,
                "next_review_at": schedule.next_review_at.isoformat(),
                "interval_days": schedule.interval_days,
            }
        return {
            "accepted": True,
            "next_review_at": schedule.next_review_at.isoformat(),
            "interval_days": schedule.interval_days,
        }
