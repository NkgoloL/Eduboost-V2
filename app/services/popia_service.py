"""
EduBoost V2 — POPIA Service
Handles Data Subject Rights: Export and Erasure orchestration.
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.repositories.learner_repository import LearnerRepository
from app.repositories.lesson_repository import LessonRepository
from app.repositories.knowledge_gap_repository import KnowledgeGapRepository
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class POPIAService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.learner_repo = LearnerRepository(db)
        self.lesson_repo = LessonRepository(db)
        self.gap_repo = KnowledgeGapRepository(db)
        self.audit = AuditService(db)

    async def export_learner_data(self, learner_id: str, guardian_id: str) -> dict[str, Any]:
        """
        Gathers all personal and performance data for a learner for POPIA export.
        """
        learner = await self.learner_repo.get_by_id(learner_id)
        if not learner or str(learner.guardian_id) != guardian_id:
            raise NotFoundError("Learner not found or access denied")

        lessons = await self.lesson_repo.get_recent(learner_id, limit=1000)
        gaps = await self.gap_repo.get_active_gaps(learner_id)

        export_data = {
            "metadata": {
                "exported_at": datetime.now(UTC).isoformat(),
                "version": "V2",
            },
            "profile": {
                "id": learner.id,
                "display_name": learner.display_name,
                "grade": learner.grade,
                "language": str(learner.language),
                "created_at": learner.created_at.isoformat(),
                "xp": learner.xp,
                "theta": learner.theta,
            },
            "lessons": [
                {
                    "id": l.id,
                    "subject": l.subject,
                    "topic": l.topic,
                    "created_at": l.created_at.isoformat(),
                    "completed_at": l.completed_at.isoformat() if l.completed_at else None,
                    "score": l.feedback_score,
                }
                for l in lessons
            ],
            "knowledge_gaps": [
                {
                    "subject": g.subject,
                    "topic": g.topic,
                    "severity": g.severity,
                    "created_at": g.created_at.isoformat(),
                }
                for g in gaps
            ],
        }

        await self.audit.auth_event(
            "DATA_EXPORT_REQUESTED",
            guardian_id,
            {"learner_id": learner_id, "scope": "FULL_LEARNER_RECORD"}
        )

        return export_data

    async def request_erasure(self, learner_id: str, guardian_id: str) -> None:
        """
        Initiates the soft-delete/anonymization process for a learner.
        """
        learner = await self.learner_repo.get_by_id(learner_id)
        if not learner or str(learner.guardian_id) != guardian_id:
            raise NotFoundError("Learner not found or access denied")

        await self.learner_repo.soft_delete(learner_id)
        
        await self.audit.auth_event(
            "DATA_ERASURE_REQUESTED",
            guardian_id,
            {"learner_id": learner_id, "status": "SOFT_DELETED_PENDING_PURGE"}
        )
