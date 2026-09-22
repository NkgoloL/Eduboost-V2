"""Educational Validation Repository (LEV-WS03).

Provides append-only persistence and query capabilities for interaction events,
mastery transitions, and validation runs.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.educational_validation import (
    LEVInteractionEvent,
    LEVMasteryStateTransition,
    LEVValidationRun,
)


class EducationalValidationRepository:
    """Repository for managing educational validation events, transitions, and run logs."""

    async def record_interaction_event(
        self, db: AsyncSession, event: LEVInteractionEvent
    ) -> LEVInteractionEvent:
        db.add(event)
        await db.flush()
        return event

    async def record_interaction_events_batch(
        self, db: AsyncSession, events: List[LEVInteractionEvent]
    ) -> List[LEVInteractionEvent]:
        db.add_all(events)
        await db.flush()
        return events

    async def record_mastery_transition(
        self, db: AsyncSession, transition: LEVMasteryStateTransition
    ) -> LEVMasteryStateTransition:
        db.add(transition)
        await db.flush()
        return transition

    async def get_learner_events(
        self,
        db: AsyncSession,
        learner_pseudonym: str,
        concept_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[LEVInteractionEvent]:
        stmt = (
            select(LEVInteractionEvent)
            .where(LEVInteractionEvent.learner_pseudonym == learner_pseudonym)
        )
        if concept_id:
            stmt = stmt.where(LEVInteractionEvent.concept_id == concept_id)
        stmt = stmt.order_by(desc(LEVInteractionEvent.occurred_at)).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_learner_transitions(
        self,
        db: AsyncSession,
        learner_pseudonym: str,
        concept_id: Optional[str] = None,
    ) -> List[LEVMasteryStateTransition]:
        stmt = (
            select(LEVMasteryStateTransition)
            .where(LEVMasteryStateTransition.learner_pseudonym == learner_pseudonym)
        )
        if concept_id:
            stmt = stmt.where(LEVMasteryStateTransition.concept_id == concept_id)
        stmt = stmt.order_by(desc(LEVMasteryStateTransition.occurred_at))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def record_validation_run(
        self, db: AsyncSession, run: LEVValidationRun
    ) -> LEVValidationRun:
        db.add(run)
        await db.flush()
        return run

    async def get_latest_validation_run(
        self, db: AsyncSession, run_type: str
    ) -> Optional[LEVValidationRun]:
        stmt = (
            select(LEVValidationRun)
            .where(LEVValidationRun.run_type == run_type)
            .order_by(desc(LEVValidationRun.executed_at))
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalars().first()
