"""
EduBoost V2 — Repository Layer
All PostgreSQL access lives here. Services call repositories — never raw SQLAlchemy.
"""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import (
    AuditLog,
    DiagnosticSession,
    Guardian,
    IRTItem,
    KnowledgeGap,
    Language,
    LearnerProfile,
    Lesson,
    ParentalConsent,
    StripeWebhookEvent,
)


class GuardianRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, **kwargs) -> Guardian:
        guardian = Guardian(**kwargs)
        self.db.add(guardian)
        await self.db.flush()
        return guardian

    async def get_by_id(self, guardian_id: str) -> Guardian | None:
        result = await self.db.execute(select(Guardian).where(Guardian.id == guardian_id))
        return result.scalar_one_or_none()

    async def get_by_email_hash(self, email_hash: str) -> Guardian | None:
        result = await self.db.execute(select(Guardian).where(Guardian.email_hash == email_hash))
        return result.scalar_one_or_none()

    async def get_by_stripe_customer_id(self, stripe_customer_id: str) -> Guardian | None:
        result = await self.db.execute(
            select(Guardian).where(Guardian.stripe_customer_id == stripe_customer_id)
        )
        return result.scalar_one_or_none()

    async def update_subscription(self, guardian_id: str, tier: str, stripe_sub_id: str | None = None) -> None:
        await self.db.execute(
            update(Guardian)
            .where(Guardian.id == guardian_id)
            .values(subscription_tier=tier, stripe_subscription_id=stripe_sub_id, updated_at=datetime.now(UTC))
        )


class LearnerRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, **kwargs) -> LearnerProfile:
        learner = LearnerProfile(**kwargs)
        self.db.add(learner)
        await self.db.flush()
        return learner

    async def get_by_id(self, learner_id: str) -> LearnerProfile | None:
        result = await self.db.execute(
            select(LearnerProfile).where(LearnerProfile.id == learner_id, LearnerProfile.is_deleted == False)  # noqa: E712
        )
        return result.scalar_one_or_none()

    async def get_by_guardian(self, guardian_id: str) -> list[LearnerProfile]:
        result = await self.db.execute(
            select(LearnerProfile).where(
                LearnerProfile.guardian_id == guardian_id, LearnerProfile.is_deleted == False  # noqa: E712
            )
        )
        return list(result.scalars().all())

    async def update_theta(self, learner_id: str, theta: float) -> None:
        await self.db.execute(
            update(LearnerProfile).where(LearnerProfile.id == learner_id).values(theta=theta, updated_at=datetime.now(UTC))
        )

    async def update_archetype(self, learner_id: str, archetype: str) -> None:
        await self.db.execute(
            update(LearnerProfile)
            .where(LearnerProfile.id == learner_id)
            .values(archetype=archetype, updated_at=datetime.now(UTC))
        )

    async def add_xp(self, learner_id: str, xp_delta: int) -> None:
        result = await self.db.execute(select(LearnerProfile.xp).where(LearnerProfile.id == learner_id))
        current = result.scalar_one_or_none() or 0
        await self.db.execute(
            update(LearnerProfile)
            .where(LearnerProfile.id == learner_id)
            .values(xp=current + xp_delta, updated_at=datetime.now(UTC))
        )

    async def soft_delete(self, learner_id: str) -> None:
        await self.db.execute(
            update(LearnerProfile)
            .where(LearnerProfile.id == learner_id)
            .values(
                display_name="[erased]",
                is_deleted=True,
                deletion_requested_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        )

    async def purge_personal_data(self, learner_id: str) -> None:
        """Physically purge learner-linked personal/product data after erasure approval."""
        await self.db.execute(delete(Lesson).where(Lesson.learner_id == learner_id))
        await self.db.execute(delete(KnowledgeGap).where(KnowledgeGap.learner_id == learner_id))
        await self.db.execute(delete(DiagnosticSession).where(DiagnosticSession.learner_id == learner_id))
        await self.db.execute(delete(ParentalConsent).where(ParentalConsent.learner_id == learner_id))
        await self.db.execute(delete(LearnerProfile).where(LearnerProfile.id == learner_id))

    async def count_lessons(self, learner_id: str) -> int:
        result = await self.db.execute(select(Lesson).where(Lesson.learner_id == learner_id))
        return len(result.scalars().all())


class ConsentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, **kwargs) -> ParentalConsent:
        consent = ParentalConsent(**kwargs)
        self.db.add(consent)
        await self.db.flush()
        return consent

    async def get_active(self, learner_id: str) -> ParentalConsent | None:
        result = await self.db.execute(
            select(ParentalConsent).where(
                ParentalConsent.learner_id == learner_id,
                ParentalConsent.revoked_at == None,  # noqa: E711
                ParentalConsent.expires_at > datetime.now(UTC),
            )
        )
        return result.scalar_one_or_none()

    async def revoke(self, consent_id: str) -> None:
        await self.db.execute(
            update(ParentalConsent).where(ParentalConsent.id == consent_id).values(revoked_at=datetime.now(UTC))
        )


class IRTRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_items_for_grade(self, grade: int, language: Language = Language.ENGLISH, limit: int = 20) -> list[IRTItem]:
        result = await self.db.execute(
            select(IRTItem).where(IRTItem.grade == grade, IRTItem.language == language).limit(limit)
        )
        return list(result.scalars().all())

    async def get_items_by_subject(self, grade: int, subject: str, limit: int = 10) -> list[IRTItem]:
        result = await self.db.execute(
            select(IRTItem).where(IRTItem.grade == grade, IRTItem.subject == subject).limit(limit)
        )
        return list(result.scalars().all())


class DiagnosticRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_session(self, learner_id: str, theta_before: float) -> DiagnosticSession:
        session = DiagnosticSession(learner_id=learner_id, theta_before=theta_before)
        self.db.add(session)
        await self.db.flush()
        return session

    async def complete_session(self, session_id: str, responses: dict, theta_after: float) -> None:
        await self.db.execute(
            update(DiagnosticSession)
            .where(DiagnosticSession.id == session_id)
            .values(responses=responses, theta_after=theta_after, completed_at=datetime.now(UTC))
        )


class KnowledgeGapRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def upsert(self, learner_id: str, grade: int, subject: str, topic: str, severity: float) -> KnowledgeGap:
        result = await self.db.execute(
            select(KnowledgeGap).where(
                KnowledgeGap.learner_id == learner_id,
                KnowledgeGap.subject == subject,
                KnowledgeGap.topic == topic,
                KnowledgeGap.resolved == False,  # noqa: E712
            )
        )
        gap = result.scalar_one_or_none()
        if gap:
            gap.severity = max(gap.severity, severity)
        else:
            gap = KnowledgeGap(learner_id=learner_id, grade=grade, subject=subject, topic=topic, severity=severity)
            self.db.add(gap)
        await self.db.flush()
        return gap

    async def get_active_gaps(self, learner_id: str) -> list[KnowledgeGap]:
        result = await self.db.execute(
            select(KnowledgeGap).where(
                KnowledgeGap.learner_id == learner_id, KnowledgeGap.resolved == False  # noqa: E712
            ).order_by(KnowledgeGap.severity.desc())
        )
        return list(result.scalars().all())


class LessonRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, **kwargs) -> Lesson:
        lesson = Lesson(**kwargs)
        self.db.add(lesson)
        await self.db.flush()
        return lesson

    async def get_recent(self, learner_id: str, limit: int = 5) -> list[Lesson]:
        result = await self.db.execute(
            select(Lesson).where(Lesson.learner_id == learner_id).order_by(Lesson.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def record_feedback(self, lesson_id: str, score: int) -> None:
        await self.db.execute(update(Lesson).where(Lesson.id == lesson_id).values(feedback_score=score))

    async def mark_completed(self, lesson_id: str, completed_at: datetime | None = None) -> None:
        await self.db.execute(
            update(Lesson)
            .where(Lesson.id == lesson_id)
            .values(completed_at=completed_at or datetime.now(UTC))
        )


class AuditRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def log(
        self,
        event_type: str,
        actor_id: str | None = None,
        learner_pseudonym: str | None = None,
        payload: dict | None = None,
        constitutional_outcome: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            event_type=event_type,
            actor_id=actor_id,
            learner_pseudonym=learner_pseudonym,
            payload=payload or {},
            constitutional_outcome=constitutional_outcome,
        )
        self.db.add(entry)
        await self.db.flush()
        return entry


class StripeEventRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def is_processed(self, stripe_event_id: str) -> bool:
        result = await self.db.execute(
            select(StripeWebhookEvent).where(StripeWebhookEvent.stripe_event_id == stripe_event_id)
        )
        return result.scalar_one_or_none() is not None

    async def record(self, stripe_event_id: str, event_type: str, payload: dict) -> None:
        event = StripeWebhookEvent(stripe_event_id=stripe_event_id, event_type=event_type, payload=payload)
        self.db.add(event)
        await self.db.flush()
