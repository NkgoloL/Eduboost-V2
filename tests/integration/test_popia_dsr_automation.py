"""Integration test for POPIA DSR State Machine and Erasure Cascade (TSR-8)."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from uuid import uuid4
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.models import (
    Assessment,
    AssessmentAttempt,
    AuditLog,

    ConsentState,
    DiagnosticSession,
    ErasureRequest,
    Guardian,
    KnowledgeGap,
    Language,
    LearnerProfile,
    Lesson,
    ParentalConsent,
    PracticeQueue,
    PracticeSession,
    SecureToken,
    SpacedReviewSchedule,
    StudyPlan,
    SubjectMastery,
    TokenPurpose,
    TopicMastery,
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
        assessment_id = str(uuid4())

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
        assessment = Assessment(
            id=assessment_id,
            title="Test Baseline Assessment",
            grade=4,
            subject="Mathematics",
            assessment_type="baseline",
            term=1,

            total_marks=50,
            duration_minutes=45,
            pass_percentage=50.0,
        )
        attempt = AssessmentAttempt(
            id=str(uuid4()),
            learner_id=learner_id,
            assessment_id=assessment_id,
            score=0.80,
            marks_obtained=40,
            time_taken_seconds=1200,
            responses={"q1": "A"},
        )
        diag = DiagnosticSession(
            id=str(uuid4()),
            learner_id=learner_id,
            responses={"item_1": True},
            theta_before=0.0,
            theta_after=0.5,
            se_estimate=0.4,
            session_state="completed",
        )
        gap = KnowledgeGap(
            id=str(uuid4()),
            learner_id=learner_id,
            grade=4,
            subject="Mathematics",
            topic="Fractions",
            severity=0.6,
        )
        lesson = Lesson(
            id=str(uuid4()),
            learner_id=learner_id,
            knowledge_gap_id=gap.id,
            grade=4,
            subject="Mathematics",
            topic="Fractions",
            language=Language.ENGLISH,
            content="Lesson content on fractions",
        )
        mastery = TopicMastery(
            id=str(uuid4()),
            learner_id=learner_id,
            caps_ref="CAPS.MATH.G4.T1",
            mastery_score=0.75,
            mastery_label="proficient",
        )
        study_plan = StudyPlan(
            id=str(uuid4()),
            learner_id=learner_id,
            week_focus="Fractions Mastery",
            schedule={"mon": "lesson_1"},
        )
        token = SecureToken(
            user_id=learner_id,
            purpose=TokenPurpose.PASSWORD_RESET,
            token_hash="fake_hash_123",
            expires_at=datetime.now(timezone.utc),
        )

        session.add(guardian)
        await session.flush()
        session.add(learner)
        await session.flush()
        session.add(assessment)
        await session.flush()
        session.add_all([consent, attempt, diag, gap, lesson, mastery, study_plan, token])
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
        assert cascade_result["tables_cascaded"] >= 10
        assert cascade_result["records_purged"] >= 6

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

        # Operational, diagnostic, lesson, and assessment records are purged
        stmt_top = select(TopicMastery).where(TopicMastery.learner_id == learner_id)
        assert len((await session.execute(stmt_top)).scalars().all()) == 0

        stmt_diag = select(DiagnosticSession).where(DiagnosticSession.learner_id == learner_id)
        assert len((await session.execute(stmt_diag)).scalars().all()) == 0

        stmt_gap = select(KnowledgeGap).where(KnowledgeGap.learner_id == learner_id)
        assert len((await session.execute(stmt_gap)).scalars().all()) == 0

        stmt_lesson = select(Lesson).where(Lesson.learner_id == learner_id)
        assert len((await session.execute(stmt_lesson)).scalars().all()) == 0

        stmt_att = select(AssessmentAttempt).where(AssessmentAttempt.learner_id == learner_id)
        assert len((await session.execute(stmt_att)).scalars().all()) == 0

        stmt_plan = select(StudyPlan).where(StudyPlan.learner_id == learner_id)
        assert len((await session.execute(stmt_plan)).scalars().all()) == 0

        stmt_tok = select(SecureToken).where(SecureToken.user_id == learner_id)
        assert len((await session.execute(stmt_tok)).scalars().all()) == 0

        # Refreshed ErasureRequest record postflight_result is measured
        refreshed_req = await session.get(ErasureRequest, req.id)
        assert refreshed_req is not None
        assert refreshed_req.state == "executed"
        assert refreshed_req.postflight_result["status"] == "success"
        assert refreshed_req.postflight_result["tables_cascaded"] >= 10
        assert refreshed_req.postflight_result["records_purged"] >= 6

        # Audit log is appended and sanitized
        stmt_audit = select(AuditLog).where(AuditLog.event_type == "popia_erasure_completed")
        res_audit = await session.execute(stmt_audit)
        audit = res_audit.scalars().first()
        assert audit is not None
        assert audit.payload["action"] == "popia_erasure_cascade_completed"

    await engine.dispose()

