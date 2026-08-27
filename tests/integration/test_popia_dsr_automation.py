"""Integration test for POPIA DSR State Machine and Erasure Cascade (TSR-8)."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from uuid import uuid4
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.core.database import Base
from app.models import (
    ConsentState,
    ErasureRequest,
    Guardian,
    LearnerProfile,
    ParentalConsent,
    SubjectMastery,
    TopicMastery,
    SpacedReviewSchedule,
    StudyPlan,
    SecureToken,
    TokenPurpose,
    AuditLog,
)
from app.services.popia_dsr_service import POPIADSRService

TEST_DB_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres")
if "postgresql://" in TEST_DB_URL and "+asyncpg" not in TEST_DB_URL:
    TEST_DB_URL = TEST_DB_URL.replace("postgresql://", "postgresql+asyncpg://")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_popia_erasure_cascade_executes_cleanly():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        # Seed test fixture: Guardian, Learner, Consent, Learning records, Token
        guardian_id = str(uuid4())
        learner_id = str(uuid4())

        guardian = Guardian(
            id=guardian_id,
            email_hash=f"hash_{guardian_id[:8]}",
            email_encrypted=f"enc_{guardian_id[:8]}",
            display_name="Test Guardian",
            password_hash="fake_pw_hash",
        )
        learner = LearnerProfile(
            id=learner_id,
            guardian_id=guardian_id,
            display_name="Test Learner Minor",
            grade=4,
        )
        consent = ParentalConsent(
            id=str(uuid4()),
            guardian_id=guardian_id,
            learner_id=learner_id,
            status=ConsentState.GRANTED,
        )
        mastery = TopicMastery(
            id=str(uuid4()),
            learner_id=learner_id,
            caps_ref="CAPS.MATH.G4.T1",
            mastery_score=0.75,
            mastery_label="proficient",
        )
        token = SecureToken(
            user_id=guardian_id,
            purpose=TokenPurpose.PASSWORD_RESET,
            token_hash="fake_hash_123",
            expires_at=datetime.now(timezone.utc),
        )

        session.add(guardian)
        await session.flush()
        session.add(learner)
        await session.flush()
        session.add_all([consent, mastery, token])
        await session.commit()

        # Execute DSR Erasure Service
        dsr_service = POPIADSRService(session)
        req = await dsr_service.initiate_erasure_request(
            learner_id=learner_id,
            requester_id=guardian_id,
            requester_role="guardian",
            reason="Parent requested total account deletion",
        )
        assert req.state == "requested"

        cascade_result = await dsr_service.execute_erasure_cascade(req.id)
        assert cascade_result["state"] == "executed"

        # Assertions: Primary Learner profile is soft-deleted and pseudonymized
        refreshed_learner = await session.get(LearnerProfile, learner_id)
        assert refreshed_learner is not None
        assert refreshed_learner.is_deleted is True
        assert "[ERASED_LEARNER_" in refreshed_learner.display_name

        # Consents are withdrawn
        stmt = select(ParentalConsent).where(ParentalConsent.learner_id == learner_id)
        res = await session.execute(stmt)
        consents = res.scalars().all()
        assert all(c.status == ConsentState.WITHDRAWN for c in consents)

        # Operational records are purged
        stmt = select(TopicMastery).where(TopicMastery.learner_id == learner_id)
        res = await session.execute(stmt)
        assert len(res.scalars().all()) == 0

        stmt = select(SecureToken).where(SecureToken.user_id == learner_id)
        res = await session.execute(stmt)
        assert len(res.scalars().all()) == 0

        # Audit log is appended and sanitized
        stmt = select(AuditLog).where(AuditLog.event_type == "popia_erasure_completed")
        res = await session.execute(stmt)
        audit = res.scalars().first()
        assert audit is not None
        assert audit.payload["action"] == "popia_erasure_cascade_completed"

    await engine.dispose()
