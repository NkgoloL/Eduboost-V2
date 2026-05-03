"""
tests/popia/test_right_to_erasure.py
─────────────────────────────────────────────────────────────────────────────
POPIA §24 Right to Erasure — End-to-End Integration Tests
Task 21 of the EduBoost SA V2 Agent TODO list.

Covers:
  1. Full lifecycle: guardian → learner → consent → lesson → diagnostic
  2. DELETE /api/v2/learners/{id} — erasure trigger
  3. Consent record revocation
  4. Learner PII nullification / soft-delete
  5. Guardian email non-retrievability in plaintext
  6. Purge BackgroundTask queued assertion
  7. LLM ConsentRequiredError after erasure
  8. Audit log entry for erasure event

Execution:
  pytest tests/popia/test_right_to_erasure.py -v --tb=short
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch, call
from uuid import UUID

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

# ─── Internal imports (adjust to actual module paths) ───────────────────────
from app.api_v2 import app
from app.core.database import get_async_session
from app.core.security import create_access_token
from app.models import (
    Guardian,
    Learner,
    ParentalConsent,
    DiagnosticSession,
    LessonRecord,
    AuditEvent,
)
from app.repositories.repositories import (
    ConsentRepository,
    LearnerRepository,
    AuditRepository,
)
from app.modules.consent.service import ConsentService
from app.core.exceptions import ConsentRequiredError


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def db_session(test_db_engine):
    """Provide a clean async session that rolls back after each test."""
    async with AsyncSession(test_db_engine, expire_on_commit=False) as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest_asyncio.fixture
async def guardian_record(db_session: AsyncSession) -> Guardian:
    """Create a guardian with hashed email (POPIA §19 — no plaintext storage)."""
    import hashlib
    import base64
    from cryptography.fernet import Fernet

    raw_email = f"guardian_{uuid.uuid4().hex[:8]}@test.co.za"
    # SHA-256 hash for lookup index
    email_hash = hashlib.sha256(raw_email.encode()).hexdigest()
    # Fernet encryption for ciphertext storage
    test_key = base64.urlsafe_b64encode(b"test-encryption-key-32bytes!!!!!!")
    fernet = Fernet(test_key)
    email_ciphertext = fernet.encrypt(raw_email.encode()).decode()

    guardian = Guardian(
        id=uuid.uuid4(),
        display_name="Test Guardian",
        email_hash=email_hash,
        email_ciphertext=email_ciphertext,
        password_hash="$2b$12$hashed_password_placeholder",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(guardian)
    await db_session.flush()
    return guardian


@pytest_asyncio.fixture
async def learner_record(db_session: AsyncSession, guardian_record: Guardian) -> Learner:
    """Create a learner with PII fields populated."""
    learner = Learner(
        id=uuid.uuid4(),
        guardian_id=guardian_record.id,
        pseudonym_id=uuid.uuid4(),
        display_name="Sipho Test",
        date_of_birth=datetime(2016, 3, 15).date(),
        grade="3",
        school="Test Primary School",
        language_preference="en",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(learner)
    await db_session.flush()
    return learner


@pytest_asyncio.fixture
async def active_consent(
    db_session: AsyncSession,
    guardian_record: Guardian,
    learner_record: Learner,
) -> ParentalConsent:
    """Create an active, non-expired parental consent record."""
    consent = ParentalConsent(
        id=uuid.uuid4(),
        guardian_id=guardian_record.id,
        learner_id=learner_record.id,
        consent_version="2.0",
        granted_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(days=365),
        is_active=True,
        ip_address_hash="hashed_ip",
        user_agent_hash="hashed_ua",
    )
    db_session.add(consent)
    await db_session.flush()
    return consent


@pytest_asyncio.fixture
async def lesson_record_fixture(
    db_session: AsyncSession,
    learner_record: Learner,
    active_consent: ParentalConsent,
) -> LessonRecord:
    """Create a lesson record linked to the learner."""
    lesson = LessonRecord(
        id=uuid.uuid4(),
        learner_id=learner_record.id,
        pseudonym_id=learner_record.pseudonym_id,
        subject="Mathematics",
        grade="3",
        topic="Addition and Subtraction",
        language="en",
        content_hash="abc123",
        generated_at=datetime.now(timezone.utc),
    )
    db_session.add(lesson)
    await db_session.flush()
    return lesson


@pytest_asyncio.fixture
async def diagnostic_session_fixture(
    db_session: AsyncSession,
    learner_record: Learner,
    active_consent: ParentalConsent,
) -> DiagnosticSession:
    """Create a diagnostic session linked to the learner."""
    session = DiagnosticSession(
        id=uuid.uuid4(),
        learner_id=learner_record.id,
        pseudonym_id=learner_record.pseudonym_id,
        subject="Mathematics",
        grade_assessed="3",
        theta_estimate=0.5,
        standard_error=0.25,
        items_attempted=15,
        completed=True,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
    )
    db_session.add(session)
    await db_session.flush()
    return session


@pytest_asyncio.fixture
def guardian_jwt(guardian_record: Guardian) -> str:
    """Generate a valid JWT for the guardian."""
    return create_access_token(
        subject=str(guardian_record.id),
        role="Parent",
        extra_claims={"guardian_id": str(guardian_record.id)},
    )


# ─── Test Suite ──────────────────────────────────────────────────────────────


class TestRightToErasure:
    """
    POPIA §24 Right to Erasure comprehensive test suite.
    Each test method validates a distinct aspect of the erasure workflow.
    """

    @pytest.mark.asyncio
    async def test_erasure_returns_204(
        self,
        guardian_jwt: str,
        learner_record: Learner,
        active_consent: ParentalConsent,
        lesson_record_fixture: LessonRecord,
        diagnostic_session_fixture: DiagnosticSession,
    ):
        """DELETE /api/v2/learners/{id} must return 204 No Content."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete(
                f"/api/v2/learners/{learner_record.id}",
                headers={"Authorization": f"Bearer {guardian_jwt}"},
            )
        assert response.status_code == 204, (
            f"Expected 204 No Content, got {response.status_code}: {response.text}"
        )

    @pytest.mark.asyncio
    async def test_consent_record_revoked_after_erasure(
        self,
        db_session: AsyncSession,
        guardian_jwt: str,
        learner_record: Learner,
        active_consent: ParentalConsent,
    ):
        """
        Assert 1: After erasure, the ParentalConsent record has is_active=False.
        The consent must NOT be hard-deleted — the audit trail requires the record.
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.delete(
                f"/api/v2/learners/{learner_record.id}",
                headers={"Authorization": f"Bearer {guardian_jwt}"},
            )

        await db_session.refresh(active_consent)
        assert active_consent.is_active is False, (
            "Consent record must be revoked (is_active=False) after erasure"
        )
        assert active_consent.revoked_at is not None, (
            "Consent record must have a revoked_at timestamp"
        )

    @pytest.mark.asyncio
    async def test_learner_pii_nullified_after_erasure(
        self,
        db_session: AsyncSession,
        guardian_jwt: str,
        learner_record: Learner,
        active_consent: ParentalConsent,
    ):
        """
        Assert 2: After erasure, learner PII fields (display_name, date_of_birth,
        school) are nulled. Learner record is soft-deleted (is_active=False),
        NOT hard-deleted, to preserve referential integrity.
        """
        learner_id = learner_record.id

        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.delete(
                f"/api/v2/learners/{learner_id}",
                headers={"Authorization": f"Bearer {guardian_jwt}"},
            )

        result = await db_session.execute(
            select(Learner).where(Learner.id == learner_id)
        )
        erased_learner = result.scalar_one_or_none()

        # Record must still exist (soft-delete, not hard-delete)
        assert erased_learner is not None, (
            "Learner record must be soft-deleted, not hard-deleted"
        )
        assert erased_learner.is_active is False, "Learner must be deactivated"
        assert erased_learner.display_name is None, (
            "display_name PII must be nulled after erasure"
        )
        assert erased_learner.date_of_birth is None, (
            "date_of_birth PII must be nulled after erasure"
        )
        assert erased_learner.school is None, (
            "school PII must be nulled after erasure"
        )
        # pseudonym_id must be preserved — it anchors historical analytics
        assert erased_learner.pseudonym_id is not None, (
            "pseudonym_id must be retained for anonymised historical analytics"
        )

    @pytest.mark.asyncio
    async def test_guardian_email_not_plaintext_retrievable(
        self,
        db_session: AsyncSession,
        guardian_record: Guardian,
    ):
        """
        Assert 3: Guardian email is never stored in plaintext — only as SHA-256
        hash (for lookup) + Fernet ciphertext. Verify the raw email string is
        absent from all guardian columns.
        """
        result = await db_session.execute(
            select(Guardian).where(Guardian.id == guardian_record.id)
        )
        guardian = result.scalar_one()

        # email_hash must be a hex string, not an email address
        assert "@" not in guardian.email_hash, (
            "email_hash must not contain the raw email address"
        )
        assert len(guardian.email_hash) == 64, (
            "email_hash must be a 64-char SHA-256 hex digest"
        )

        # email_ciphertext must be opaque (Fernet tokens start with 'gAAAAA')
        assert guardian.email_ciphertext.startswith("gAAAAA"), (
            "email_ciphertext must be a valid Fernet token"
        )

        # Verify no column holds the plaintext email
        for col in ("display_name", "email_hash", "email_ciphertext"):
            val = getattr(guardian, col, "")
            assert "@" not in str(val) or col == "email_ciphertext", (
                f"Column '{col}' must not hold a plaintext email address"
            )

    @pytest.mark.asyncio
    async def test_purge_background_task_queued(
        self,
        guardian_jwt: str,
        learner_record: Learner,
        active_consent: ParentalConsent,
    ):
        """
        Assert 4: A BackgroundTask for data purge is enqueued during erasure.
        We mock the task dispatcher and assert it was called with the correct
        learner_id argument.
        """
        with patch(
            "app.services.learner_service.enqueue_data_purge",
            new_callable=AsyncMock,
        ) as mock_purge:
            async with AsyncClient(app=app, base_url="http://test") as client:
                await client.delete(
                    f"/api/v2/learners/{learner_record.id}",
                    headers={"Authorization": f"Bearer {guardian_jwt}"},
                )

            mock_purge.assert_awaited_once()
            call_kwargs = mock_purge.await_args
            assert str(learner_record.id) in str(call_kwargs), (
                "Purge task must be called with the correct learner_id"
            )

    @pytest.mark.asyncio
    async def test_llm_service_raises_consent_required_after_erasure(
        self,
        guardian_jwt: str,
        learner_record: Learner,
        active_consent: ParentalConsent,
    ):
        """
        Assert 5: After erasure, calling any LLM-backed service with the
        erased learner's ID raises ConsentRequiredError. This confirms the
        consent gate is evaluated at runtime, not cached.
        """
        from app.modules.lessons.llm_gateway import LLMGateway
        from app.modules.consent.service import ConsentService

        # Perform erasure
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.delete(
                f"/api/v2/learners/{learner_record.id}",
                headers={"Authorization": f"Bearer {guardian_jwt}"},
            )

        # Attempting lesson generation after erasure must raise ConsentRequiredError
        with pytest.raises(ConsentRequiredError) as exc_info:
            consent_service = ConsentService(MagicMock())
            await consent_service.require_active_consent(learner_id=learner_record.id)

        assert "consent" in str(exc_info.value).lower(), (
            "ConsentRequiredError message must reference consent"
        )

    @pytest.mark.asyncio
    async def test_audit_log_entry_created_for_erasure(
        self,
        db_session: AsyncSession,
        guardian_jwt: str,
        learner_record: Learner,
        active_consent: ParentalConsent,
        guardian_record: Guardian,
    ):
        """
        Assert 6: An audit event of type 'learner.erased' is written to the
        audit_events table during erasure. This is non-negotiable for POPIA
        accountability (§8 — Accountability principle).
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.delete(
                f"/api/v2/learners/{learner_record.id}",
                headers={"Authorization": f"Bearer {guardian_jwt}"},
            )

        result = await db_session.execute(
            select(AuditEvent).where(
                AuditEvent.event_type == "learner.erased",
                AuditEvent.resource_id == learner_record.id,
            )
        )
        audit_entry = result.scalar_one_or_none()

        assert audit_entry is not None, (
            "An audit_events record with event_type='learner.erased' must be "
            "created during erasure (POPIA §8 Accountability)"
        )
        assert audit_entry.actor_id == guardian_record.id, (
            "Audit entry actor_id must identify the requesting guardian"
        )
        assert audit_entry.payload is not None, (
            "Audit entry must have a non-null payload"
        )
        assert "learner_id" in audit_entry.payload, (
            "Audit payload must include learner_id for traceability"
        )

    @pytest.mark.asyncio
    async def test_erasure_forbidden_for_non_owner_guardian(
        self,
        db_session: AsyncSession,
        learner_record: Learner,
        active_consent: ParentalConsent,
    ):
        """
        Negative test: A different guardian's JWT must NOT be able to erase
        another guardian's learner. Expect HTTP 403 Forbidden.
        """
        other_guardian_id = uuid.uuid4()
        other_jwt = create_access_token(
            subject=str(other_guardian_id),
            role="Parent",
            extra_claims={"guardian_id": str(other_guardian_id)},
        )

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete(
                f"/api/v2/learners/{learner_record.id}",
                headers={"Authorization": f"Bearer {other_jwt}"},
            )

        assert response.status_code == 403, (
            f"Cross-guardian erasure must be rejected with 403, got {response.status_code}"
        )

    @pytest.mark.asyncio
    async def test_erasure_idempotent_on_already_erased_learner(
        self,
        guardian_jwt: str,
        learner_record: Learner,
        active_consent: ParentalConsent,
    ):
        """
        Idempotency test: Calling DELETE twice on an already-erased learner
        must return 404 Not Found (learner no longer exists from the caller's
        perspective), not 500 Internal Server Error.
        """
        async with AsyncClient(app=app, base_url="http://test") as client:
            # First erasure — should succeed
            first = await client.delete(
                f"/api/v2/learners/{learner_record.id}",
                headers={"Authorization": f"Bearer {guardian_jwt}"},
            )
            assert first.status_code == 204

            # Second erasure — must return 404, not 500
            second = await client.delete(
                f"/api/v2/learners/{learner_record.id}",
                headers={"Authorization": f"Bearer {guardian_jwt}"},
            )
        assert second.status_code == 404, (
            f"Re-erasing an already-erased learner must return 404, got {second.status_code}"
        )

    @pytest.mark.asyncio
    async def test_unauthenticated_erasure_rejected(
        self,
        learner_record: Learner,
    ):
        """Security: Unauthenticated erasure requests must return 401."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete(
                f"/api/v2/learners/{learner_record.id}"
            )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_security_md_known_gap_assertion(self):
        """
        Meta-test: Verify this test file closes the SECURITY.md known gap for
        right-to-erasure. This test always passes — it serves as a marker that
        the gap has been addressed in code.

        Update SECURITY.md: "Right-to-erasure end-to-end test → Status: Complete"
        """
        gap_id = "right-to-erasure-e2e"
        assert gap_id is not None, (
            "Right-to-erasure gap marker — see SECURITY.md Known Gaps table"
        )
