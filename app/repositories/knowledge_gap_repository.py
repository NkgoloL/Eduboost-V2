"""Knowledge gap persistence repository for EduBoost V2."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import BaseRepository
from app.models import KnowledgeGap


class KnowledgeGapRepository(BaseRepository[KnowledgeGap]):
    model = KnowledgeGap

    async def get_active_for_learner(
        self,
        learner_id: str | UUID,
        db: AsyncSession,
    ) -> list[KnowledgeGap]:
        """Fetch all unresolved knowledge gaps for a learner."""
        stmt = (
            select(KnowledgeGap)
            .where(KnowledgeGap.learner_id == UUID(str(learner_id)))
            .where(KnowledgeGap.resolved == False)  # noqa: E712
            .order_by(KnowledgeGap.severity.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def upsert_gap(
        self,
        db: AsyncSession,
        learner_id: str | UUID,
        grade: int,
        subject: str,
        topic: str,
        severity: float,
    ) -> KnowledgeGap:
        """Create or update a knowledge gap."""
        stmt = (
            select(KnowledgeGap)
            .where(KnowledgeGap.learner_id == UUID(str(learner_id)))
            .where(KnowledgeGap.subject == subject)
            .where(KnowledgeGap.topic == topic)
            .where(KnowledgeGap.resolved == False)  # noqa: E712
        )
        result = await db.execute(stmt)
        gap = result.scalar_one_or_none()

        if gap:
            gap.severity = max(gap.severity, severity)
            db.add(gap)
        else:
            gap = await self.create(
                db,
                learner_id=UUID(str(learner_id)),
                grade=grade,
                subject=subject,
                topic=topic,
                severity=severity,
            )
        
        await db.flush()
        return gap
