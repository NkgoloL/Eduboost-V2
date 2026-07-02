"""IRT Item persistence repository for EduBoost V2."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import BaseRepository
from app.models import IRTItem, Language


class IRTRepository(BaseRepository[IRTItem]):
    model = IRTItem

    async def get_items_for_grade(
        self,
        db: AsyncSession,
        grade: int,
        language: Language = Language.ENGLISH,
        limit: int = 20,
    ) -> list[IRTItem]:
        """Fetch items for a specific grade and language."""
        stmt = (
            select(IRTItem)
            .where(IRTItem.grade == grade)
            .where(IRTItem.language == language)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_items_by_subject(
        self,
        db: AsyncSession,
        grade: int,
        subject: str,
        limit: int = 10,
    ) -> list[IRTItem]:
        """Fetch items for a specific grade and subject."""
        stmt = (
            select(IRTItem)
            .where(IRTItem.grade == grade)
            .where(IRTItem.subject == subject)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
