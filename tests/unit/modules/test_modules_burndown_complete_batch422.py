"""Unit tests for modules burndown - Batch 422.

Targets:
1. app/modules/auth/service.py (40 stmts -> 100.0%)
2. app/modules/diagnostics/quality_scorer.py (128 stmts -> 100.0%)
3. app/modules/diagnostics/service.py (44 stmts -> 100.0%)
4. app/modules/progress/learning_velocity_service.py (36 stmts -> 100.0%)
5. app/modules/lessons/lesson_review_service.py (23 stmts -> 100.0%)
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4
import pytest
from fastapi import Request

from app.core.exceptions import (
    AuthenticationError,
    AuthorisationError,
    ConsentRequiredError,
    DuplicateError,
    NotFoundError,
)
from app.models import Guardian, ParentalConsent
from app.modules.auth.service import AuthService
from app.modules.diagnostics import quality_scorer
from app.modules.diagnostics.quality_scorer import (
    QualityScorer,
    _caps_alignment_score,
    _correctness_score,
    _readability_score,
    _sa_context_score,
    _topic_lookup,
)
from app.modules.diagnostics.service import ConsentService, _get_ip, _get_ua
from app.modules.lessons.lesson_review_service import (
    LessonReviewService,
    get_lesson_review_service,
)
from app.modules.progress.learning_velocity_service import LearningVelocityService


# ==============================================================================
# 1. AUTH SERVICE TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_auth_service_register_guardian_success():
    service = AuthService()
    mock_db = AsyncMock()

    with patch("app.modules.auth.service._guardian_repo") as mock_repo, \
         patch("app.modules.auth.service.write_audit_event", new=AsyncMock()) as mock_audit:
        mock_repo.get_by_email_hash = AsyncMock(return_value=None)
        dummy_guardian = SimpleNamespace(
            id=uuid4(),
            email_hash="hash",
            email_encrypted="enc",
            password_hash="pw_hash",
            full_name_encrypted="name_enc",
            is_active=True,
            is_verified=False,
        )
        mock_repo.create = AsyncMock(return_value=dummy_guardian)

        guardian = await service.register_guardian(
            mock_db,
            email="thabo@example.com",
            password="secretpassword123",
            full_name="Thabo Mokoena",
            phone="+27821234567",
        )
        assert guardian.id == dummy_guardian.id
        assert getattr(guardian, "is_verified", False) is False
        mock_repo.create.assert_awaited_once()
        mock_audit.assert_awaited_once()


@pytest.mark.asyncio
async def test_auth_service_register_guardian_duplicate():
    service = AuthService()
    mock_db = AsyncMock()

    with patch("app.modules.auth.service._guardian_repo") as mock_repo:
        mock_repo.get_by_email_hash = AsyncMock(return_value=SimpleNamespace(id=uuid4()))

        with pytest.raises(DuplicateError):
            await service.register_guardian(
                mock_db,
                email="exists@example.com",
                password="password",
                full_name="Existing User",
            )


@pytest.mark.asyncio
async def test_auth_service_authenticate_success():
    service = AuthService()
    mock_db = AsyncMock()

    with patch("app.modules.auth.service._guardian_repo") as mock_repo, \
         patch("app.modules.auth.service.verify_password", return_value=True), \
         patch("app.modules.auth.service.create_access_token", return_value="access_token_xyz"), \
         patch("app.modules.auth.service.create_refresh_token", return_value="refresh_token_abc"), \
         patch("app.modules.auth.service.write_audit_event", new=AsyncMock()):

        dummy_guardian = SimpleNamespace(
            id=uuid4(),
            password_hash="hashed_pw",
            is_active=True,
            is_verified=True,
        )
        mock_repo.get_by_email_hash = AsyncMock(return_value=dummy_guardian)
        mock_repo.update = AsyncMock(return_value=dummy_guardian)

        access, refresh = await service.authenticate(
            mock_db,
            email="thabo@example.com",
            password="secretpassword123",
            ip_address="127.0.0.1",
        )
        assert access == "access_token_xyz"
        assert refresh == "refresh_token_abc"
        mock_repo.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_auth_service_authenticate_invalid_or_deactivated():
    service = AuthService()
    mock_db = AsyncMock()

    with patch("app.modules.auth.service._guardian_repo") as mock_repo, \
         patch("app.modules.auth.service.write_audit_event", new=AsyncMock()):

        # 1. User not found
        mock_repo.get_by_email_hash = AsyncMock(return_value=None)
        with pytest.raises(AuthenticationError, match="Invalid email or password"):
            await service.authenticate(mock_db, email="unknown@test.com", password="pwd")

        # 2. Wrong password
        dummy_guardian = SimpleNamespace(id=uuid4(), password_hash="hash", is_active=True)
        mock_repo.get_by_email_hash = AsyncMock(return_value=dummy_guardian)
        with patch("app.modules.auth.service.verify_password", return_value=False):
            with pytest.raises(AuthenticationError, match="Invalid email or password"):
                await service.authenticate(mock_db, email="user@test.com", password="bad")

        # 3. Deactivated account
        deactivated = SimpleNamespace(id=uuid4(), password_hash="hash", is_active=False)
        mock_repo.get_by_email_hash = AsyncMock(return_value=deactivated)
        with patch("app.modules.auth.service.verify_password", return_value=True):
            with pytest.raises(AuthenticationError, match="Account is deactivated"):
                await service.authenticate(mock_db, email="user@test.com", password="pwd")


@pytest.mark.asyncio
async def test_auth_service_verify_email_and_get_profile():
    service = AuthService()
    mock_db = AsyncMock()

    with patch("app.modules.auth.service._guardian_repo") as mock_repo, \
         patch("app.modules.auth.service.decrypt_pii", side_effect=lambda x: f"decrypted_{x}"):

        # verify_email NotFoundError
        mock_repo.get_by_verification_token = AsyncMock(return_value=None)
        with pytest.raises(NotFoundError):
            await service.verify_email("bad_token", mock_db)

        # verify_email success
        dummy = SimpleNamespace(id=uuid4(), is_verified=False)
        mock_repo.get_by_verification_token = AsyncMock(return_value=dummy)
        mock_repo.update = AsyncMock(return_value=dummy)
        res = await service.verify_email("good_token", mock_db)
        assert res == dummy

        # get_guardian_profile
        g_id = uuid4()
        now = datetime.now(timezone.utc)
        guardian_record = SimpleNamespace(
            id=g_id,
            email_encrypted="enc_email",
            full_name_encrypted="enc_name",
            is_verified=True,
            created_at=now,
        )
        mock_repo.get_or_404 = AsyncMock(return_value=guardian_record)
        profile = await service.get_guardian_profile(g_id, mock_db)
        assert profile["id"] == str(g_id)
        assert profile["email"] == "decrypted_enc_email"
        assert profile["full_name"] == "decrypted_enc_name"
        assert profile["is_verified"] is True
        assert profile["created_at"] == now.isoformat()


# ==============================================================================
# 2. QUALITY SCORER TESTS
# ==============================================================================

def test_quality_scorer_topic_lookup():
    # Direct dictionary format
    direct = {"topics": {"MATH.4.1.1": {"topic": "Numbers"}}}
    assert _topic_lookup(direct) == {"MATH.4.1.1": {"topic": "Numbers"}}

    # Nested terms structure format
    nested = {
        "grade": 4,
        "subject": "Mathematics",
        "terms": [
            {
                "term": 1,
                "topics": [
                    {
                        "caps_ref": "MATH.4.1.1",
                        "topic": "Whole Numbers",
                        "subtopics": [
                            {
                                "caps_ref": "MATH.4.1.1.1",
                                "subtopic": "Place value",
                                "assessment_standards": ["Identify place value"],
                                "common_misconceptions": ["Confusion between units and tens"],
                            }
                        ],
                    }
                ],
            }
        ],
    }
    lookup = _topic_lookup(nested)
    assert "MATH.4.1.1" in lookup
    assert "MATH.4.1.1.1" in lookup
    assert lookup["MATH.4.1.1"]["grade"] == 4
    assert lookup["MATH.4.1.1.1"]["subtopic"] == "Place value"


def test_quality_scorer_caps_alignment_score():
    nested = {
        "grade": 4,
        "subject": "Mathematics",
        "terms": [
            {
                "term": 1,
                "topics": [
                    {
                        "caps_ref": "MATH.4.1.1",
                        "topic": "Whole Numbers",
                        "subtopics": [
                            {
                                "caps_ref": "MATH.4.1.1.1",
                                "subtopic": "Place value",
                                "assessment_standards": [],
                                "common_misconceptions": [],
                            }
                        ],
                    }
                ],
            }
        ],
    }
    # caps_ref missing from topic map
    assert _caps_alignment_score({"caps_ref": "UNKNOWN"}, nested) == 0.3

    # Matching item
    item_perfect = {
        "caps_ref": "MATH.4.1.1.1",
        "topic": "Whole Numbers",
        "subtopic": "Place value",
        "skill": "Place value",
        "grade": 4,
        "term": 1,
    }
    score_perfect = _caps_alignment_score(item_perfect, nested)
    assert score_perfect == 1.0

    # Topic-level reference (len(caps_ref.split('.')) == 4)
    item_topic_level = {
        "caps_ref": "MATH.4.1.1",
        "topic": "Whole Numbers",
        "grade": 4,
        "term": 1,
    }
    # Topic without caps_ref and subtopic without caps_ref
    no_caps_nested = {
        "grade": 4,
        "subject": "Mathematics",
        "terms": [
            {
                "term": 1,
                "topics": [
                    {
                        "topic": "No caps topic",
                        "subtopics": [
                            {"subtopic": "No caps subtopic"}
                        ],
                    }
                ],
            }
        ],
    }
    lookup_no_caps = _topic_lookup(no_caps_nested)
    assert len(lookup_no_caps) == 0


def test_quality_scorer_correctness_score():
    # Empty item
    assert _correctness_score({}) == 0.15  # empty options are distinct

    # High quality item with >= 20 word explanation
    explanation_20_words = " ".join([f"word{i}" for i in range(25)])
    item_good = {
        "answer_key": "B",
        "explanation": explanation_20_words,
        "options": [
            {"label": "A", "text": "10"},
            {"label": "B", "text": "100"},
            {"label": "C", "text": "1000"},
        ],
        "distractor_rationale": {
            "A": "User multiplied by 1 instead of 10",
            "C": "User multiplied by 100",
        },
        "misconception_tags": ["place_value_magnitude"],
    }
    score = _correctness_score(item_good)
    assert score >= 0.8

    # Duplicate option texts and short explanation
    item_dups = {
        "answer_key": "A",
        "explanation": "Short note",
        "options": [
            {"label": "A", "text": "Same"},
            {"label": "B", "text": "same"},
        ],
        "distractor_rationale": {"B": "Duplicate text"},
    }
    score_dups = _correctness_score(item_dups)
    assert score_dups < 0.6


def test_quality_scorer_readability_score():
    assert _readability_score({}) == 0.0
    assert _readability_score({"stem": "   "}) == 0.0

    with patch("app.modules.diagnostics.quality_scorer.flesch_kincaid_grade") as mock_fk:
        mock_fk.return_value = 3.5
        assert _readability_score({"stem": "easy stem"}) == 1.0
        mock_fk.return_value = 4.5
        assert _readability_score({"stem": "easy stem"}) == 0.8
        mock_fk.return_value = 5.5
        assert _readability_score({"stem": "medium stem"}) == 0.6
        mock_fk.return_value = 7.5
        assert _readability_score({"stem": "hard stem"}) == 0.3
        mock_fk.return_value = 9.5
        assert _readability_score({"stem": "complex stem"}) == 0.0


def test_quality_scorer_sa_context_score():
    # No SA context
    assert _sa_context_score({"stem": "What is 2 + 2?"}) == 0.0

    # Currency match only (e.g. 'rand' or 'R5')
    assert _sa_context_score({"stem": "It costs 50 rand to enter."}) > 0.0
    assert _sa_context_score({"stem": "It costs R5."}) > 0.0

    # Metric units match only (km)
    assert _sa_context_score({"stem": "The runner finished 5 km."}) > 0.0

    # With currency and names and metric units
    item_sa = {
        "stem": "Sipho buys pap for R5 and walks 2 km to the taxi rank.",
        "options": [{"text": "R5"}, {"text": "R2"}],
    }
    score = _sa_context_score(item_sa)
    assert score >= 0.8


def test_quality_scorer_class_and_report(capsys):
    topic_map = {"topics": {"CAPS-1": {"topic": "Math"}}}
    scorer = QualityScorer(topic_map)

    item = {
        "item_id": "item-12345",
        "caps_ref": "CAPS-1",
        "topic": "Math",
        "stem": "Nomsa has R50 to buy pap.",
        "answer_key": "A",
        "explanation": "Option A is correct because Nomsa has R50 which covers the cost.",
        "options": [
            {"label": "A", "text": "R50"},
            {"label": "B", "text": "R100"},
        ],
        "distractor_rationale": {"B": "Too much"},
        "misconception_tags": ["budget"],
    }

    scored_item = scorer.score(item)
    assert "quality_score" in scored_item
    assert "component_scores" in scored_item

    batch = scorer.score_batch([item])
    assert len(batch) == 1
    assert batch[0]["quality_score"] == scored_item["quality_score"]

    # Report with empty list
    scorer.report([])
    captured = capsys.readouterr()
    assert "No scored items to report." in captured.out

    # Report with scored items
    scorer.report(batch)
    captured2 = capsys.readouterr()
    assert "Quality Score Report" in captured2.out
    assert "CAPS-1" in captured2.out


# ==============================================================================
# 3. DIAGNOSTICS CONSENT SERVICE TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_diagnostics_consent_service_grant_consent():
    service = ConsentService()
    mock_db = AsyncMock()
    learner_id = uuid4()
    guardian_id = uuid4()

    with patch("app.modules.diagnostics.service._learner_repo") as mock_learner_repo, \
         patch("app.modules.diagnostics.service._consent_repo") as mock_consent_repo, \
         patch("app.modules.diagnostics.service.write_audit_event", new=AsyncMock()) as mock_audit, \
         patch("app.modules.diagnostics.service.consent_events_total"):

        # 1. Guardian mismatch -> AuthorisationError
        learner_other_guardian = SimpleNamespace(id=learner_id, guardian_id=uuid4())
        mock_learner_repo.get_or_404 = AsyncMock(return_value=learner_other_guardian)

        with pytest.raises(AuthorisationError, match="You are not the guardian"):
            await service.grant_consent(learner_id, guardian_id, mock_db)

        # 2. Successful grant
        learner_correct_guardian = SimpleNamespace(id=learner_id, guardian_id=guardian_id)
        mock_learner_repo.get_or_404 = AsyncMock(return_value=learner_correct_guardian)
        dummy_consent = SimpleNamespace(id=uuid4(), is_active=True)
        mock_consent_repo.grant = AsyncMock(return_value=dummy_consent)

        # Create mock request with headers
        req = MagicMock(spec=Request)
        req.headers = {"X-Forwarded-For": "10.0.0.1, 10.0.0.2", "User-Agent": "TestBrowser/1.0"}
        req.client = SimpleNamespace(host="10.0.0.1")

        consent = await service.grant_consent(
            learner_id, guardian_id, mock_db, request=req, consent_version="2.0"
        )
        assert consent.id == dummy_consent.id
        mock_audit.assert_awaited_once()


@pytest.mark.asyncio
async def test_diagnostics_consent_service_revoke_consent():
    service = ConsentService()
    mock_db = AsyncMock()
    learner_id = uuid4()
    guardian_id = uuid4()

    with patch("app.modules.diagnostics.service._learner_repo") as mock_learner_repo, \
         patch("app.modules.diagnostics.service._consent_repo") as mock_consent_repo, \
         patch("app.modules.diagnostics.service.write_audit_event", new=AsyncMock()), \
         patch("app.modules.diagnostics.service.consent_events_total"):

        # Mismatch
        mock_learner_repo.get_or_404 = AsyncMock(return_value=SimpleNamespace(guardian_id=uuid4()))
        with pytest.raises(AuthorisationError):
            await service.revoke_consent(learner_id, guardian_id, mock_db)

        # Success
        mock_learner_repo.get_or_404 = AsyncMock(return_value=SimpleNamespace(guardian_id=guardian_id))
        mock_consent_repo.revoke = AsyncMock(return_value=1)

        revoked_count = await service.revoke_consent(learner_id, guardian_id, mock_db, reason="manual_test")
        assert revoked_count == 1


@pytest.mark.asyncio
async def test_diagnostics_consent_service_require_and_expiring():
    service = ConsentService()
    mock_db = AsyncMock()
    learner_id = uuid4()

    with patch("app.modules.diagnostics.service._consent_repo") as mock_consent_repo:
        # ConsentRequiredError
        mock_consent_repo.get_active = AsyncMock(return_value=None)
        with pytest.raises(ConsentRequiredError):
            await service.require_active_consent(learner_id, mock_db)

        # Active consent
        active = SimpleNamespace(id=uuid4(), is_active=True)
        mock_consent_repo.get_active = AsyncMock(return_value=active)
        assert await service.require_active_consent(learner_id, mock_db) == active

        # Expiring consents
        mock_consent_repo.get_expiring_soon = AsyncMock(return_value=[active])
        expiring = await service.get_expiring_consents(mock_db, days=15)
        assert len(expiring) == 1


def test_diagnostics_consent_service_helpers():
    assert _get_ip(None) is None
    assert _get_ua(None) is None

    # Forwarded header
    req_fwd = cast(Any, SimpleNamespace(
        headers={"X-Forwarded-For": "1.2.3.4, 5.6.7.8", "User-Agent": "Bot/1.0"},
        client=SimpleNamespace(host="127.0.0.1"),
    ))
    assert _get_ip(req_fwd) == "1.2.3.4"
    assert _get_ua(req_fwd) == "Bot/1.0"

    # Direct client host
    req_host = cast(Any, SimpleNamespace(
        headers={},
        client=SimpleNamespace(host="192.168.1.1"),
    ))
    assert _get_ip(req_host) == "192.168.1.1"

    # Client is None
    req_no_client = cast(Any, SimpleNamespace(
        headers={},
        client=None,
    ))
    assert _get_ip(req_no_client) is None


# ==============================================================================
# 4. LEARNING VELOCITY SERVICE TESTS
# ==============================================================================

def test_learning_velocity_service_complete():
    service = LearningVelocityService()

    # <2 snapshots
    assert service.compute_velocity([]) == 0.0
    assert service.compute_velocity([SimpleNamespace(mastery_score=0.5)]) == 0.0

    # >=2 snapshots
    now = datetime(2026, 1, 15, 0, 0, tzinfo=timezone.utc)
    earlier = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    s1 = SimpleNamespace(snapshot_at=earlier, mastery_score=0.40)
    s2 = SimpleNamespace(snapshot_at=now, mastery_score=0.80)
    vel = service.compute_velocity([s2, s1])  # out of order test
    assert vel > 0.0

    # compute_risk_signal branches
    assert service.compute_risk_signal(0.35, 5, 0.1) == "urgent"
    assert service.compute_risk_signal(0.80, 35, 0.1) == "urgent"
    assert service.compute_risk_signal(0.80, 5, -0.10) == "urgent"

    assert service.compute_risk_signal(0.55, 5, 0.1) == "at_risk"
    assert service.compute_risk_signal(0.80, 20, 0.1) == "at_risk"
    assert service.compute_risk_signal(0.80, 5, -0.02) == "at_risk"

    assert service.compute_risk_signal(0.85, 2, 0.1) == "on_track"

    # next_best_activities branches
    rows = [
        SimpleNamespace(caps_ref="A", mastery_score=0.30),
        SimpleNamespace(caps_ref="B", mastery_score=0.50),
        SimpleNamespace(caps_ref="C", mastery_score=0.70),
        SimpleNamespace(caps_ref="D", mastery_score=0.90),
    ]
    activities = service.next_best_activities(rows)
    assert len(activities) == 4
    assert activities[0]["activity"] == "targeted_lesson"
    assert activities[1]["activity"] == "practice_drill"
    assert activities[2]["activity"] == "spaced_review"
    assert activities[3]["activity"] == "extension_challenge"


# ==============================================================================
# 5. LESSON REVIEW SERVICE TESTS
# ==============================================================================

@pytest.mark.asyncio
async def test_lesson_review_service_complete():
    mock_repo = AsyncMock()
    service = LessonReviewService(repository=mock_repo)

    # list_pending_review
    mock_repo.list_pending_review.return_value = ["lesson1"]
    res = await service.list_pending_review(grade=7, subject="Math", caps_ref="CAPS-1", limit=10, offset=0)
    assert res == ["lesson1"]
    mock_repo.list_pending_review.assert_awaited_once_with(
        grade=7, subject="Math", caps_ref="CAPS-1", limit=10, offset=0
    )

    # list_by_caps_ref
    mock_repo.list_by_caps_ref.return_value = ["lesson2"]
    res_caps = await service.list_by_caps_ref("CAPS-1", include_all_statuses=True)
    assert res_caps == ["lesson2"]
    mock_repo.list_by_caps_ref.assert_awaited_once_with("CAPS-1", include_all_statuses=True)

    # review_lesson
    l_id = uuid4()
    r_id = uuid4()
    mock_repo.update_review_status.return_value = {"status": "approved"}
    review_res = await service.review_lesson(l_id, "approved", r_id, reviewer_notes="Looks great")
    assert review_res == {"status": "approved"}
    mock_repo.update_review_status.assert_awaited_once_with(
        l_id, review_status="approved", reviewer_id=r_id, reviewer_notes="Looks great"
    )

    # Factory methods
    mock_session = AsyncMock()
    with patch("app.modules.lessons.lesson_review_service.LessonRepository"):
        svc_from_session = LessonReviewService.from_session(mock_session)
        assert isinstance(svc_from_session, LessonReviewService)

        dep_svc = get_lesson_review_service(mock_session)
        assert isinstance(dep_svc, LessonReviewService)
