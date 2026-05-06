"""Study plan persistence repository for EduBoost V2.

Owns all DB reads and writes for study plans, replacing direct
session access previously scattered across the service layer.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound

from app.core.database import AsyncSessionFactory
from sqlalchemy.orm import declarative_base

DummyBase = declarative_base()

class StudyPlan(DummyBase):
    __tablename__ = 'study_plan'
    plan_id = None
    learner_id = None
    week_start = None
    schedule = None
    gap_ratio = None
    week_focus = None
    generated_by = None

class SubjectMastery(DummyBase):
    __tablename__ = 'subject_mastery'
    learner_id = None
    subject_code = None
    grade_level = None
    mastery_score = None
    knowledge_gaps = None



class StudyPlanRepository:
    """Repository for study-plan CRUD operations."""

    async def create(
        self,
        learner_id: str,
        schedule: dict[str, Any],
        gap_ratio: float,
        week_focus: str,
        generated_by: str = "V2_ALGORITHM",
    ) -> dict:
        """Persist a new study plan and return a dict representation."""
        plan_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        async with AsyncSessionFactory() as session:
            plan = StudyPlan(
                plan_id=plan_id,
                learner_id=uuid.UUID(learner_id),
                week_start=now,
                schedule=schedule,
                gap_ratio=gap_ratio,
                week_focus=week_focus,
                generated_by=generated_by,
            )
            session.add(plan)
            await session.commit()
            await session.refresh(plan)
        return {
            "plan_id": str(plan.plan_id),
            "learner_id": learner_id,
            "week_start": plan.week_start.isoformat(),
            "schedule": plan.schedule,
            "gap_ratio": plan.gap_ratio,
            "week_focus": plan.week_focus,
            "generated_by": plan.generated_by,
        }

    async def get_by_id(self, plan_id: str) -> dict | None:
        """Fetch a single study plan by its UUID."""
        async with AsyncSessionFactory() as session:
            result = await session.execute(
                select(StudyPlan).where(StudyPlan.plan_id == uuid.UUID(plan_id))
            )
            plan = result.scalar_one_or_none()
            if plan is None:
                return None
        return {
            "plan_id": str(plan.plan_id),
            "learner_id": str(plan.learner_id),
            "week_start": plan.week_start.isoformat(),
            "schedule": plan.schedule,
            "gap_ratio": plan.gap_ratio,
            "week_focus": plan.week_focus,
            "generated_by": plan.generated_by,
        }

    async def list_for_learner(self, learner_id: str, limit: int = 10) -> list[dict]:
        """Return the N most recent study plans for a learner."""
        async with AsyncSessionFactory() as session:
            result = await session.execute(
                select(StudyPlan)
                .where(StudyPlan.learner_id == uuid.UUID(learner_id))
                .order_by(StudyPlan.week_start.desc())
                .limit(limit)
            )
            plans = result.scalars().all()
        return [
            {
                "plan_id": str(p.plan_id),
                "learner_id": str(p.learner_id),
                "week_start": p.week_start.isoformat(),
                "schedule": p.schedule,
                "gap_ratio": p.gap_ratio,
                "week_focus": p.week_focus,
                "generated_by": p.generated_by,
            }
            for p in plans
        ]

    async def get_subject_mastery(self, learner_id: str) -> list[dict]:
        """Return subject mastery rows for a learner (used by plan generation)."""
        async with AsyncSessionFactory() as session:
            result = await session.execute(
                select(SubjectMastery).where(SubjectMastery.learner_id == learner_id)
            )
            rows = result.scalars().all()
        return [
            {
                "subject_code": row.subject_code,
                "grade_level": row.grade_level,
                "mastery_score": row.mastery_score,
                "knowledge_gaps": row.knowledge_gaps or [],
            }
            for row in rows
        ]
