from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MasterySnapshot, TopicMastery


class MasteryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def upsert_topic_mastery(self, learner_id: str | UUID, caps_ref: str, *, mastery_score: float, mastery_label: str, theta: float | None = None, theta_se: float | None = None) -> TopicMastery:
        existing = await self.get_topic_mastery(learner_id, caps_ref)
        if existing:
            existing.mastery_score = mastery_score
            existing.mastery_label = mastery_label
            existing.theta_estimate = theta
            existing.theta_se = theta_se
            existing.last_updated_at = datetime.now(UTC)
            row = existing
        else:
            row = TopicMastery(learner_id=str(learner_id), caps_ref=caps_ref, mastery_score=mastery_score, mastery_label=mastery_label, theta_estimate=theta, theta_se=theta_se)
            self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def get_topic_mastery(self, learner_id: str | UUID, caps_ref: str) -> TopicMastery | None:
        result = await self.db.execute(select(TopicMastery).where(TopicMastery.learner_id == str(learner_id), TopicMastery.caps_ref == caps_ref))
        return result.scalar_one_or_none()

    async def list_topic_mastery_by_learner(self, learner_id: str | UUID) -> list[TopicMastery]:
        result = await self.db.execute(select(TopicMastery).where(TopicMastery.learner_id == str(learner_id)).order_by(TopicMastery.caps_ref.asc()))
        return list(result.scalars().all())

    async def create_snapshot(self, learner_id: str | UUID, caps_ref: str, *, mastery_score: float, mastery_label: str, theta_estimate: float | None, theta_se: float | None, trigger: str, practice_accuracy: float | None = None) -> MasterySnapshot:
        row = MasterySnapshot(learner_id=str(learner_id), caps_ref=caps_ref, mastery_score=mastery_score, mastery_label=mastery_label, theta_estimate=theta_estimate, theta_se=theta_se, practice_accuracy=practice_accuracy, trigger=trigger)
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def get_snapshots_for_learner_topic(self, learner_id: str | UUID, caps_ref: str) -> list[MasterySnapshot]:
        result = await self.db.execute(select(MasterySnapshot).where(MasterySnapshot.learner_id == str(learner_id), MasterySnapshot.caps_ref == caps_ref).order_by(MasterySnapshot.snapshot_at.asc()))
        return list(result.scalars().all())
