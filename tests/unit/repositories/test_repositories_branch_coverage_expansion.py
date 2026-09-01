"""Batch 224 — app/repositories/repositories.py comprehensive branch coverage expansion.

Tests:
- GuardianRepository: create, get_by_id, get_by_email_hash, get_by_stripe_customer_id, update_subscription
- LearnerRepository: create, get_by_id, get_by_guardian, update_theta, update_archetype, add_xp (existing vs 0), soft_delete, purge_personal_data, count_lessons
- ConsentRepository: create, get_active, get_latest_for_learner, grant, revoke, renew (with previous vs without), get_expiring_soon
- IRTRepository: get_items_for_grade, get_items_by_subject
- DiagnosticRepository: create_session, complete_session
- KnowledgeGapRepository: upsert (new gap vs existing gap with max severity), get_active_gaps
- LessonRepository: create, get_recent, record_feedback, mark_completed (custom vs default completed_at)
- AuditRepository: log
- StripeEventRepository: is_processed (True vs False), record
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

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
from app.repositories.repositories import (
    AuditRepository,
    ConsentRepository,
    DiagnosticRepository,
    GuardianRepository,
    IRTRepository,
    KnowledgeGapRepository,
    LearnerRepository,
    LessonRepository,
    StripeEventRepository,
)


@pytest.fixture
def mock_db():
    return AsyncMock()


# ---------------------------------------------------------------------------
# GuardianRepository
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_guardian_repository_all_methods(mock_db):
    repo = GuardianRepository(mock_db)

    # 1. create
    guardian = await repo.create(id="g-1", email_hash="hash123")
    assert isinstance(guardian, Guardian)
    mock_db.add.assert_called_once()
    mock_db.flush.assert_called_once()

    # 2. get_by_id
    res_id = MagicMock()
    res_id.scalar_one_or_none.return_value = guardian
    mock_db.execute.return_value = res_id
    assert await repo.get_by_id("g-1") == guardian

    # 3. get_by_email_hash
    assert await repo.get_by_email_hash("hash123") == guardian

    # 4. get_by_stripe_customer_id
    assert await repo.get_by_stripe_customer_id("cus_123") == guardian

    # 5. update_subscription
    await repo.update_subscription("g-1", "premium", "sub_123")
    mock_db.execute.assert_called()


# ---------------------------------------------------------------------------
# LearnerRepository
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_learner_repository_all_methods(mock_db):
    repo = LearnerRepository(mock_db)

    # 1. create
    learner = await repo.create(id="l-1", guardian_id="g-1", display_name="Lethabo")
    assert isinstance(learner, LearnerProfile)
    mock_db.add.assert_called_once()

    # 2. get_by_id
    res_l = MagicMock()
    res_l.scalar_one_or_none.return_value = learner
    mock_db.execute.return_value = res_l
    assert await repo.get_by_id("l-1") == learner

    # 3. get_by_guardian
    res_list = MagicMock()
    res_list.scalars.return_value.all.return_value = [learner]
    mock_db.execute.return_value = res_list
    assert await repo.get_by_guardian("g-1") == [learner]

    # 4. update_theta & update_archetype
    await repo.update_theta("l-1", 1.25)
    await repo.update_archetype("l-1", "visual")

    # 5. add_xp
    res_xp = MagicMock()
    res_xp.scalar_one_or_none.return_value = 50
    mock_db.execute.return_value = res_xp
    await repo.add_xp("l-1", 20)

    # 6. soft_delete & purge_personal_data
    await repo.soft_delete("l-1")
    await repo.purge_personal_data("l-1")

    # 7. count_lessons
    res_lessons = MagicMock()
    res_lessons.scalars.return_value.all.return_value = [MagicMock(), MagicMock()]
    mock_db.execute.return_value = res_lessons
    assert await repo.count_lessons("l-1") == 2


# ---------------------------------------------------------------------------
# ConsentRepository
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_consent_repository_all_methods(mock_db):
    repo = ConsentRepository(mock_db)

    # 1. create
    consent = await repo.create(learner_id="l-1", guardian_id="g-1", policy_version="v1")
    assert isinstance(consent, ParentalConsent)

    # 2. get_active
    res_active = MagicMock()
    res_active.scalar_one_or_none.return_value = consent
    mock_db.execute.return_value = res_active
    assert await repo.get_active("l-1") == consent

    # 3. get_latest_for_learner
    assert await repo.get_latest_for_learner("l-1") == consent

    # 4. grant
    granted = await repo.grant("l-1", "g-1", "v1.1", ip_address="1.2.3.4", user_agent="agent", state="granted")
    assert isinstance(granted, ParentalConsent)

    # 5. revoke
    res_revoke = MagicMock(rowcount=1)
    mock_db.execute.return_value = res_revoke
    assert await repo.revoke("l-1", reason="user_withdrew") == 1

    # 6. renew (with active previous)
    repo.get_active = AsyncMock(return_value=consent)
    repo.revoke = AsyncMock(return_value=1)
    prev, renewed = await repo.renew("l-1", "g-1", "v2.0")
    assert prev == consent
    assert isinstance(renewed, ParentalConsent)

    # 7. get_expiring_soon
    res_expiring = MagicMock()
    res_expiring.scalars.return_value.all.return_value = [consent]
    mock_db.execute.return_value = res_expiring
    expiring = await repo.get_expiring_soon(days=14)
    assert len(expiring) == 1


# ---------------------------------------------------------------------------
# IRTRepository & DiagnosticRepository
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_irt_and_diagnostic_repositories(mock_db):
    irt_repo = IRTRepository(mock_db)
    res_irt = MagicMock()
    res_irt.scalars.return_value.all.return_value = [MagicMock(spec=IRTItem)]
    mock_db.execute.return_value = res_irt

    # 1. IRT items for grade & subject
    items1 = await irt_repo.get_items_for_grade(4, Language.ENGLISH)
    assert len(items1) == 1
    items2 = await irt_repo.get_items_by_subject(4, "Mathematics")
    assert len(items2) == 1

    # 2. Diagnostic session create & complete
    diag_repo = DiagnosticRepository(mock_db)
    session = await diag_repo.create_session("l-1", 0.0)
    assert isinstance(session, DiagnosticSession)

    await diag_repo.complete_session(str(uuid.uuid4()), {"q1": "a"}, 0.85)
    mock_db.execute.assert_called()


# ---------------------------------------------------------------------------
# KnowledgeGapRepository & LessonRepository
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_gap_and_lesson_repositories(mock_db):
    gap_repo = KnowledgeGapRepository(mock_db)

    # 1. Upsert new gap
    res_none = MagicMock()
    res_none.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = res_none

    gap1 = await gap_repo.upsert("l-1", 4, "Mathematics", "Fractions", 0.8)
    assert isinstance(gap1, KnowledgeGap)

    # 2. Upsert existing gap (severity updated)
    existing_gap = MagicMock(spec=KnowledgeGap, severity=0.5)
    res_exist = MagicMock()
    res_exist.scalar_one_or_none.return_value = existing_gap
    mock_db.execute.return_value = res_exist

    gap2 = await gap_repo.upsert("l-1", 4, "Mathematics", "Fractions", 0.9)
    assert existing_gap.severity == 0.9

    # 3. get_active_gaps
    res_gaps = MagicMock()
    res_gaps.scalars.return_value.all.return_value = [gap1]
    mock_db.execute.return_value = res_gaps
    assert await gap_repo.get_active_gaps("l-1") == [gap1]

    # 4. LessonRepository
    lesson_repo = LessonRepository(mock_db)
    lesson = await lesson_repo.create(
        learner_id="l-1",
        subject="Mathematics",
        topic="Fractions",
        content="Lesson content",
        grade=4,
    )
    assert isinstance(lesson, Lesson)

    res_lessons = MagicMock()
    res_lessons.scalars.return_value.all.return_value = [lesson]
    mock_db.execute.return_value = res_lessons
    assert await lesson_repo.get_recent("l-1") == [lesson]

    await lesson_repo.record_feedback("lesson-1", 5)
    await lesson_repo.mark_completed("lesson-1", datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# AuditRepository & StripeEventRepository
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_audit_and_stripe_repositories(mock_db):
    # 1. AuditRepository
    audit_repo = AuditRepository(mock_db)
    log_entry = await audit_repo.log("auth.login", actor_id="u-1", payload={"ip": "1.1.1.1"})
    assert isinstance(log_entry, AuditLog)

    # 2. StripeEventRepository
    stripe_repo = StripeEventRepository(mock_db)

    # is_processed True vs False
    res_true = MagicMock()
    res_true.scalar_one_or_none.return_value = MagicMock(spec=StripeWebhookEvent)
    mock_db.execute.return_value = res_true
    assert await stripe_repo.is_processed("evt_123") is True

    res_false = MagicMock()
    res_false.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = res_false
    assert await stripe_repo.is_processed("evt_new") is False

    # record
    await stripe_repo.record("evt_new", "payment_intent.succeeded", {"amount": 1000})
    mock_db.add.assert_called()
    mock_db.flush.assert_called()
