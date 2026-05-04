"""Parent report persistence repository for EduBoost V2.

Owns all DB reads for guardian–learner links, subject mastery summaries,
and stored parent reports, replacing direct session access in the service layer.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, text

from app.core.database import AsyncSessionFactory
from sqlalchemy.orm import declarative_base

DummyBase = declarative_base()

class ParentLearnerLink(DummyBase):
    __tablename__ = 'parent_learner_link'
    learner_id = None
    parent_id = None

class SubjectMastery(DummyBase):
    __tablename__ = 'subject_mastery'
    learner_id = None
    subject_code = None
    mastery_score = None
    grade_level = None
    knowledge_gaps = None



class ParentReportRepository:
    """Repository for parent-report data access."""

    async def verify_guardian_link(self, learner_id: str, guardian_id: str) -> bool:
        """Return True if the guardian is linked to the learner."""
        async with AsyncSessionFactory() as session:
            result = await session.execute(
                select(ParentLearnerLink).where(
                    ParentLearnerLink.learner_id == learner_id,
                    ParentLearnerLink.parent_id == guardian_id,
                )
            )
            return result.scalar_one_or_none() is not None

    async def get_subject_mastery(self, learner_id: str) -> list[dict]:
        """Return all subject mastery rows for a given learner."""
        async with AsyncSessionFactory() as session:
            result = await session.execute(
                select(SubjectMastery).where(SubjectMastery.learner_id == learner_id)
            )
            rows = result.scalars().all()
        return [
            {
                "subject_code": row.subject_code,
                "mastery_score": row.mastery_score,
                "grade_level": row.grade_level,
                "knowledge_gaps": row.knowledge_gaps or [],
            }
            for row in rows
        ]

    async def persist_report(
        self,
        learner_id: str,
        guardian_id: str,
        overall_mastery: float,
        summary: str,
        subjects: list[dict],
    ) -> str:
        """Persist a generated parent report to the reports table and return its ID."""
        report_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        async with AsyncSessionFactory() as session:
            await session.execute(
                text(
                    "INSERT INTO reports "
                    "(report_id, learner_id, guardian_id, report_type, content, generated_at) "
                    "VALUES (:report_id, :learner_id, :guardian_id, 'parent_report', :content, :generated_at)"
                ),
                {
                    "report_id": report_id,
                    "learner_id": learner_id,
                    "guardian_id": guardian_id,
                    "content": {
                        "overall_mastery": overall_mastery,
                        "summary": summary,
                        "subjects": subjects,
                    },
                    "generated_at": now,
                },
            )
            await session.commit()
        return report_id

    async def get_reports_for_learner(
        self, learner_id: str, guardian_id: str, limit: int = 10
    ) -> list[dict]:
        """Return stored parent reports for a learner, newest first."""
        async with AsyncSessionFactory() as session:
            result = await session.execute(
                text(
                    "SELECT report_id, generated_at, content "
                    "FROM reports "
                    "WHERE learner_id = :learner_id AND guardian_id = :guardian_id "
                    "ORDER BY generated_at DESC LIMIT :limit"
                ),
                {"learner_id": learner_id, "guardian_id": guardian_id, "limit": limit},
            )
            rows = result.mappings().all()
        return [dict(r) for r in rows]
