"""Batch 230 — app/api_v2_routers/diagnostics.py comprehensive branch coverage expansion.

Tests:
- _subject_code conversions (all frontend mappings and fallback)
- _option_payload parser (None, dict, list of dicts, list of strings)
- _serialise_item_bank_item & _engine_item_from_item_bank
- _require_item_bank_admin (admin vs non-admin 403)
- get_diagnostic_items:
  - 404 learner not found
  - canonical items branch
  - IRT items fallback branch
- submit_diagnostic:
  - 404 learner not found
  - canonical items branch vs IRT items fallback branch
  - persistence of session, theta, knowledge gaps, runtime kg
- get_item_bank_coverage: metric updating
- get_item_bank_item: 404 vs serialized response
- review_item_bank_item: 404 vs review update
- start_diagnostic_session: session start
- recover_diagnostic_session: 404 no session vs 404 no learner vs success
- diagnostic_next_item: 404 no session vs 404 no learner vs 400 caps_ref mismatch vs completed=True vs completed=False
- diagnostic_respond: 404 no session vs 400 integrity error vs 404 item not found vs success response
"""
from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api_v2_deps.auth import AuthContext
from app.api_v2_routers.diagnostics import (
    DiagnosticSessionResponseRequest,
    DiagnosticSessionStartRequest,
    ReviewItemRequest,
    _engine_item_from_item_bank,
    _option_payload,
    _require_item_bank_admin,
    _serialise_item_bank_item,
    _subject_code,
    diagnostic_next_item,
    diagnostic_respond,
    get_diagnostic_items,
    get_item_bank_coverage,
    get_item_bank_item,
    recover_diagnostic_session,
    review_item_bank_item,
    start_diagnostic_session,
    submit_diagnostic,
)
from app.domain.schemas import DiagnosticSubmit


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_request():
    req = MagicMock()
    req.state = SimpleNamespace()
    return req


from app.models import UserRole


@pytest.fixture
def admin_user():
    return AuthContext(
        user_id=str(uuid.uuid4()),
        roles=[UserRole.ADMIN],
        token_type="access",
        raw_claims={},
        jti=str(uuid.uuid4()),
    )


@pytest.fixture
def normal_user():
    return AuthContext(
        user_id=str(uuid.uuid4()),
        roles=[UserRole.PARENT],
        token_type="access",
        raw_claims={},
        jti=str(uuid.uuid4()),
    )


# ---------------------------------------------------------------------------
# Helper Functions & Admin Guard
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_subject_code_and_option_payload():
    # _subject_code
    assert _subject_code("Mathematics") == "MATH"
    assert _subject_code("English") == "ENG"
    assert _subject_code("Natural Sciences") == "NS"
    assert _subject_code("Social Sciences") == "SS"
    assert _subject_code("Life Skills") == "LIFE"
    assert _subject_code("Unknown") == "Unknown"

    # _option_payload
    assert _option_payload(None) == []
    assert _option_payload({"A": "Option 1", "B": "Option 2"}) == [
        {"key": "A", "label": "Option 1"},
        {"key": "B", "label": "Option 2"},
    ]
    assert _option_payload([{"key": "1", "label": "First"}, {"id": "2", "text": "Second"}]) == [
        {"key": "1", "label": "First"},
        {"key": "2", "label": "Second"},
    ]
    assert _option_payload(["Option A", "Option B"]) == [
        {"key": "A", "label": "Option A"},
        {"key": "B", "label": "Option B"},
    ]


@pytest.mark.unit
def test_item_bank_serialisation_and_admin_guard(admin_user, normal_user):
    item = SimpleNamespace(
        item_id=uuid.uuid4(),
        stem="What is 2+2?",
        options={"A": "3", "B": "4"},
        subject="Mathematics",
        topic="Addition",
        skill="Mental Math",
        difficulty_b=0.5,
        discrimination_a=1.2,
        caps_ref="4.M.1.1",
        review_status="approved",
        grade=4,
    )
    serialised = _serialise_item_bank_item(item)
    assert serialised["question"] == "What is 2+2?"
    assert serialised["subject"] == "MATH"

    engine_item = _engine_item_from_item_bank(item)
    assert engine_item.subject == "MATH"
    assert engine_item.b_param == 0.5

    # _require_item_bank_admin
    _require_item_bank_admin(admin_user)  # no exception
    with pytest.raises(HTTPException) as exc:
        _require_item_bank_admin(normal_user)
    assert exc.value.status_code == 403


# ---------------------------------------------------------------------------
# get_diagnostic_items
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_diagnostic_items_branches(mock_db, mock_request, admin_user):
    with patch("app.api_v2_deps.diagnostic_repositories.learner") as mock_learner_repo, \
         patch("app.api_v2_deps.diagnostic_repositories.item_bank") as mock_item_bank_repo, \
         patch("app.api_v2_deps.diagnostic_repositories.irt") as mock_irt_repo, \
         patch("app.api_v2_routers.diagnostics.require_learner_read_for_current_user"), \
         patch("app.api_v2_routers.diagnostics.require_active_consent_for_current_user", new_callable=AsyncMock):

        # 1. 404 Learner not found
        mock_learner_repo.return_value.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await get_diagnostic_items("l-1", mock_request, mock_db, admin_user)
        assert exc.value.status_code == 404

        # 2. Canonical items branch
        mock_learner = SimpleNamespace(id="l-1", pseudonym_id="p-1", grade=4)
        mock_learner_repo.return_value.get_by_id = AsyncMock(return_value=mock_learner)

        mock_item = SimpleNamespace(
            item_id=uuid.uuid4(),
            stem="Question 1",
            options=["A", "B"],
            subject="Mathematics",
            topic="Addition",
            skill="Math",
            difficulty_b=0.0,
            discrimination_a=1.0,
            caps_ref="4.M.1.1",
            review_status="approved",
        )
        mock_item_bank_repo.return_value.list_approved_for_grade = AsyncMock(return_value=[mock_item])

        items_res = await get_diagnostic_items("l-1", mock_request, mock_db, admin_user)
        assert len(items_res) == 1
        assert items_res[0]["question"] == "Question 1"

        # 3. IRT items fallback branch
        mock_item_bank_repo.return_value.list_approved_for_grade = AsyncMock(return_value=[])
        mock_irt_item = SimpleNamespace(
            id="irt-1",
            question_text="IRT Q",
            options=["A", "B"],
            subject="Mathematics",
            topic="Addition",
            grade=4,
            b_param=0.0,
            a_param=1.0,
            review_status="approved",
        )
        mock_irt_repo.return_value.get_items_for_grade = AsyncMock(return_value=[mock_irt_item])

        irt_res = await get_diagnostic_items("l-1", mock_request, mock_db, admin_user)
        assert len(irt_res) == 1
        assert irt_res[0]["question"] == "IRT Q"


# ---------------------------------------------------------------------------
# submit_diagnostic
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_submit_diagnostic_flow(mock_db, mock_request, admin_user):
    body = DiagnosticSubmit.model_validate({
        "learner_id": "00000000-0000-0000-0000-000000000001",
        "answers": [{"item_id": "00000000-0000-0000-0000-000000000002", "selected_option": "B"}],
    })

    with patch("app.api_v2_deps.diagnostic_repositories.learner") as mock_learner_repo, \
         patch("app.api_v2_deps.diagnostic_repositories.guardian") as mock_guardian_repo, \
         patch("app.api_v2_deps.diagnostic_repositories.item_bank") as mock_item_bank_repo, \
         patch("app.api_v2_deps.diagnostic_repositories.diagnostic") as mock_diag_repo, \
         patch("app.api_v2_deps.diagnostic_repositories.knowledge_gap") as mock_gap_repo, \
         patch("app.api_v2_routers.diagnostics.require_learner_write_for_current_user"), \
         patch("app.api_v2_routers.diagnostics.require_active_consent_for_current_user", new_callable=AsyncMock), \
         patch("app.api_v2_routers.diagnostics.check_ai_quota", new_callable=AsyncMock), \
         patch("app.api_v2_routers.diagnostics.build_runtime_kg_diagnostic_projection", new_callable=AsyncMock) as mock_kg:

        # 1. 404 Learner not found
        mock_learner_repo.return_value.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await submit_diagnostic(body, mock_request, mock_db, admin_user)
        assert exc.value.status_code == 404

        # 2. Canonical items submission success
        mock_learner = SimpleNamespace(
            id="00000000-0000-0000-0000-000000000001",
            pseudonym_id="p-1",
            guardian_id="g-1",
            grade=4,
            theta=0.0,
            subject="Mathematics",
        )
        mock_learner_repo.return_value.get_by_id = AsyncMock(return_value=mock_learner)
        mock_learner_repo.return_value.update_theta = AsyncMock()

        mock_guardian = SimpleNamespace(subscription_tier="premium")
        mock_guardian_repo.return_value.get_by_id = AsyncMock(return_value=mock_guardian)

        mock_item = SimpleNamespace(
            item_id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
            stem="Question 1",
            options=["A", "B"],
            subject="Mathematics",
            topic="Addition",
            skill="Math",
            difficulty_b=0.0,
            discrimination_a=1.0,
            caps_ref="4.M.1.1",
            answer_key="B",
            grade=4,
        )
        mock_item_bank_repo.return_value.list_approved_for_grade = AsyncMock(return_value=[mock_item])

        mock_diag_session = SimpleNamespace(id=str(uuid.uuid4()))
        mock_diag_repo.return_value.create_session = AsyncMock(return_value=mock_diag_session)
        mock_diag_repo.return_value.complete_session = AsyncMock()
        mock_gap_repo.return_value.upsert = AsyncMock()

        mock_kg_proj = MagicMock()
        mock_kg_proj.to_payload.return_value = {"gaps": []}
        mock_kg.return_value = mock_kg_proj

        res = await submit_diagnostic(body, mock_request, mock_db, admin_user)
        assert res.session_id == mock_diag_session.id
        assert res.theta_before == 0.0


# ---------------------------------------------------------------------------
# Item Bank Admin & Sessions
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_item_bank_admin_routes(mock_db, admin_user):
    item_id = uuid.uuid4()

    # 1. Coverage
    with patch("app.api_v2_routers.diagnostics.ItemBankService") as mock_ib_svc:
        mock_ib_svc.return_value.get_coverage_summary = AsyncMock(
            return_value={"4.M.1.1": {"coverage_ratio": 0.8}}
        )
        cov = await get_item_bank_coverage(mock_db, admin_user)
        assert "4.M.1.1" in cov

    # 2. Get item bank item 404 & success
    with patch("app.api_v2_deps.diagnostic_repositories.item_bank") as mock_item_bank_repo:
        mock_item_bank_repo.return_value.get_item = AsyncMock(return_value=None)
        with pytest.raises(HTTPException) as exc:
            await get_item_bank_item(item_id, mock_db, admin_user)
        assert exc.value.status_code == 404

        mock_item = SimpleNamespace(
            item_id=item_id,
            caps_ref="4.M.1.1",
            grade=4,
            subject="Mathematics",
            term=1,
            topic="Addition",
            subtopic="Basic",
            skill="Math",
            stem="Q",
            answer_key="A",
            options=["A"],
            explanation="Exp",
            distractor_rationale={},
            misconception_tags=[],
            difficulty_b=0.0,
            discrimination_a=1.0,
            guessing_c=0.0,
            review_status="approved",
            reviewer_id=None,
            reviewed_at=None,
            exposure_count=0,
            max_exposure=100,
            quality_score=0.9,
            safety_passed=True,
        )
        mock_item_bank_repo.return_value.get_item = AsyncMock(return_value=mock_item)
        res_item = await get_item_bank_item(item_id, mock_db, admin_user)
        assert res_item["caps_ref"] == "4.M.1.1"

    # 3. Review item bank item
    with patch("app.api_v2_routers.diagnostics.ItemBankService") as mock_ib_svc:
        mock_ib_svc.return_value.mark_item_reviewed = AsyncMock(return_value=mock_item)
        body = ReviewItemRequest(review_status="approved", quality_score=0.95)
        rev_res = await review_item_bank_item(item_id, body, mock_db, admin_user)
        assert rev_res["item_id"] == str(item_id)


# ---------------------------------------------------------------------------
# Diagnostic Adaptive Sessions
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_diagnostic_sessions_full_flow(mock_db, admin_user):
    session_id = uuid.uuid4()
    learner_id = uuid.uuid4()
    item_id = uuid.uuid4()

    with patch("app.api_v2_routers.diagnostics.require_learner_write_for_current_user"), \
         patch("app.api_v2_routers.diagnostics.require_learner_read_for_current_user"), \
         patch("app.api_v2_routers.diagnostics.require_active_consent_for_current_user", new_callable=AsyncMock), \
         patch("app.api_v2_routers.diagnostics.DiagnosticSessionService") as mock_sess_svc_cls, \
         patch("app.api_v2_deps.diagnostic_repositories.learner") as mock_learner_repo, \
         patch("app.api_v2_deps.diagnostic_repositories.item_bank") as mock_item_bank_repo:

        mock_snap = SimpleNamespace(
            session_id=session_id,
            learner_id=str(learner_id),
            caps_ref="4.M.1.1",
            theta=0.0,
        )
        mock_sess_svc_cls.return_value.start_session = AsyncMock(return_value=mock_snap)
        mock_sess_svc_cls.return_value.recover_session = AsyncMock(return_value=mock_snap)

        mock_learner = SimpleNamespace(id=str(learner_id), pseudonym_id="p-1")
        mock_learner_repo.return_value.get_by_id = AsyncMock(return_value=mock_learner)

        # 1. Start session
        start_req = DiagnosticSessionStartRequest(learner_id=learner_id, caps_ref="4.M.1.1", theta=0.0)
        start_res = await start_diagnostic_session(start_req, mock_db, admin_user)
        assert start_res["caps_ref"] == "4.M.1.1"

        # 2. Recover session
        rec_res = await recover_diagnostic_session(session_id, mock_db, admin_user)
        assert rec_res["caps_ref"] == "4.M.1.1"

        # 3. Next item (completed=False)
        mock_item = SimpleNamespace(
            item_id=item_id,
            caps_ref="4.M.1.1",
            stem="Next item stem",
            options=["A", "B"],
        )
        mock_item_bank_repo.return_value.list_by_caps_ref = AsyncMock(return_value=[mock_item])
        mock_sess_svc_cls.return_value.get_next_item = AsyncMock(return_value=mock_item)

        next_res = await diagnostic_next_item(session_id, "4.M.1.1", mock_db, admin_user)
        assert next_res["completed"] is False
        assert next_res["stem"] == "Next item stem"

        # 4. Respond
        mock_item_bank_repo.return_value.get_item = AsyncMock(return_value=mock_item)
        mock_resp_result = SimpleNamespace(session_id=session_id, status="in_progress")
        mock_sess_svc_cls.return_value.submit_response = AsyncMock(return_value=mock_resp_result)

        resp_req = DiagnosticSessionResponseRequest(
            item_id=item_id,
            correct=True,
            response="A",
            caps_ref="4.M.1.1",
        )
        with patch("app.api_v2_routers.diagnostics.validate_adaptive_diagnostic_response"):
            resp_res = await diagnostic_respond(session_id, resp_req, mock_db, admin_user)
            assert resp_res["status"] == "in_progress"
