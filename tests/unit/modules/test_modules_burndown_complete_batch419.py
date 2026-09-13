"""Comprehensive unit test suite for Core Modules Burndown (Batch 419).

Covers:
- app/modules/practice/service.py
- app/modules/practice/router.py
- app/modules/progress/progress_timeline_service.py
- app/modules/learners/archetype_service.py
- app/modules/lessons/prompt_version_registry.py
- app/modules/lessons/lesson_metrics.py
- app/modules/diagnostics/irt_params.py
- app/modules/diagnostics/bias_review_router.py
- app/modules/study_plans/runtime_kg_planner.py
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

# ---------------------------------------------------------------------------
# 1. app/modules/practice/service.py & router.py
# ---------------------------------------------------------------------------
from app.modules.practice.router import (
    PracticeResponseRequest,
    PracticeSessionRequest,
    create_practice_session,
    get_practice_service,
    next_practice_item,
    respond_practice,
)
from app.modules.practice.service import PracticeService


@pytest.mark.asyncio
async def test_practice_service_workflow():
    session_repo = AsyncMock()
    item_repo = AsyncMock()

    # Setup dummy item
    dummy_item = SimpleNamespace(item_id="item-1", caps_ref="G4.Math.1")
    item_repo.list_by_caps_ref.return_value = [dummy_item]

    created_session = SimpleNamespace(
        id="session-123",
        items=["item-1"],
        responses=[],
        cursor=0,
        owner_subject="user-1",
        learner_id="learner-1",
    )
    session_repo.create.return_value = created_session
    session_repo.get_by_id.return_value = created_session

    service = PracticeService(session_repo=session_repo, item_repo=item_repo)

    # from_session factory
    mock_db = MagicMock()
    svc_from_session = PracticeService.from_session(mock_db)
    assert isinstance(svc_from_session, PracticeService)

    # create_session
    sid, count = await service.create_session(
        learner_id="learner-1",
        owner_subject="user-1",
        gap_topics=["G4.Math.1"],
        theta=0.5,
    )
    assert sid == "session-123"
    assert count == 1

    # get_session
    sess = await service.get_session("session-123")
    assert sess is not None
    assert sess.id == "session-123"

    # record_response: non-completing
    multi_session = SimpleNamespace(
        id="session-123",
        items=["item-1", "item-2"],
        responses=[],
        cursor=0,
    )
    res_adv = await service.record_response(multi_session, {"answer": "A"}, correct=True)
    assert res_adv["accepted"] is True
    assert "next_review_at" in res_adv
    assert res_adv["interval_days"] >= 1

    # record_response: completing
    res_comp = await service.record_response(created_session, {"answer": "B"}, correct=False)
    assert res_comp["completed"] is True
    session_repo.mark_completed.assert_awaited_once_with("session-123")


@pytest.mark.asyncio
async def test_practice_router_endpoints():
    db = AsyncMock()
    service = AsyncMock()
    current_user = {"sub": "user-1", "role": "learner"}
    learner_uuid = uuid4()

    # get_practice_service dependency
    svc = get_practice_service(db)
    assert isinstance(svc, PracticeService)

    with patch("app.modules.practice.router.require_learner_write_for_current_user"), patch(
        "app.modules.practice.router.require_active_consent_for_current_user", new_callable=AsyncMock
    ), patch("app.modules.practice.router.actor_id_from_current_user", return_value="user-1"):
        # 1. create_practice_session
        service.create_session.return_value = ("sess-abc", 3)
        req = PracticeSessionRequest(learner_id=learner_uuid, gap_topics=["topic-1"], theta=0.2)
        resp_create = await create_practice_session(req, current_user=current_user, db=db, service=service)
        assert resp_create["session_id"] == "sess-abc"
        assert resp_create["item_count"] == 3

        # 2. next_practice_item: 404 not found
        service.get_session.return_value = None
        with pytest.raises(HTTPException) as exc_404:
            await next_practice_item("missing-id", current_user=current_user, db=db, service=service)
        assert exc_404.value.status_code == 404

        # 3. next_practice_item: 403 forbidden owner mismatch
        service.get_session.return_value = SimpleNamespace(owner_subject="other-user", learner_id=str(learner_uuid))
        with pytest.raises(HTTPException) as exc_403:
            await next_practice_item("sess-abc", current_user=current_user, db=db, service=service)
        assert exc_403.value.status_code == 403

        # 4. next_practice_item: active item
        service.get_session.return_value = SimpleNamespace(
            owner_subject="user-1",
            learner_id=str(learner_uuid),
            items=["item-99"],
            cursor=0,
        )
        resp_next = await next_practice_item("sess-abc", current_user=current_user, db=db, service=service)
        assert resp_next["completed"] is False
        assert resp_next["item_id"] == "item-99"

        # 5. next_practice_item: completed
        service.get_session.return_value = SimpleNamespace(
            owner_subject="user-1",
            learner_id=str(learner_uuid),
            items=["item-99"],
            cursor=1,
        )
        resp_comp = await next_practice_item("sess-abc", current_user=current_user, db=db, service=service)
        assert resp_comp["completed"] is True

        # 6. respond_practice: 404 not found
        service.get_session.return_value = None
        resp_req = PracticeResponseRequest(item_id=uuid4(), correct=True, response="A")
        with pytest.raises(HTTPException) as exc_resp_404:
            await respond_practice("sess-abc", resp_req, current_user=current_user, db=db, service=service)
        assert exc_resp_404.value.status_code == 404

        # 7. respond_practice: 403 forbidden owner mismatch
        service.get_session.return_value = SimpleNamespace(owner_subject="other-user", learner_id=str(learner_uuid))
        with pytest.raises(HTTPException) as exc_resp_403:
            await respond_practice("sess-abc", resp_req, current_user=current_user, db=db, service=service)
        assert exc_resp_403.value.status_code == 403

        # 8. respond_practice: success
        service.get_session.return_value = SimpleNamespace(owner_subject="user-1", learner_id=str(learner_uuid))
        service.record_response.return_value = {"accepted": True}
        res_record = await respond_practice("sess-abc", resp_req, current_user=current_user, db=db, service=service)
        assert res_record["accepted"] is True


# ---------------------------------------------------------------------------
# 2. app/modules/progress/progress_timeline_service.py
# ---------------------------------------------------------------------------
from app.modules.progress.progress_timeline_service import ProgressTimelineService


@pytest.mark.asyncio
async def test_progress_timeline_service():
    repo = AsyncMock()
    service = ProgressTimelineService(mastery_repository=repo)

    now = datetime.now(timezone.utc)
    dummy_snapshot = SimpleNamespace(
        snapshot_at=now,
        mastery_score=0.85,
        mastery_label="proficient",
        trigger="quiz_completion",
    )
    repo.get_snapshots_for_learner_topic.return_value = [dummy_snapshot]

    timeline = await service.get_topic_progress_timeline("learner-1", "G4.Math.1")
    assert len(timeline) == 1
    assert timeline[0]["mastery_score"] == 0.85
    assert timeline[0]["snapshot_at"] == now.isoformat()

    # get_subject_mastery_summary
    row1 = SimpleNamespace(caps_ref="G4.Math.Fractions", mastery_score=0.8)
    row2 = SimpleNamespace(caps_ref="G4.Math.Decimals", mastery_score=0.6)
    row3 = SimpleNamespace(caps_ref="invalid_ref_without_dot", mastery_score=0.7)
    row4 = SimpleNamespace(caps_ref="G4.Science.Energy", mastery_score=0.9)
    repo.list_topic_mastery_by_learner.return_value = [row1, row2, row3, row4]

    summary = await service.get_subject_mastery_summary("learner-1", subject="Math")
    assert summary["learner_id"] == "learner-1"
    assert len(summary["subjects"]) == 1
    assert summary["subjects"][0]["subject_code"] == "Math"
    assert summary["subjects"][0]["average_mastery"] == 0.7


# ---------------------------------------------------------------------------
# 3. app/modules/learners/archetype_service.py
# ---------------------------------------------------------------------------
from app.domain.models import ArchetypeLabel
from app.modules.learners.archetype_service import ArchetypeService


def test_archetype_service():
    svc = ArchetypeService()

    questions = svc.get_onboarding_questions()
    assert len(questions) == 5

    answers = [
        {"question_id": 1, "answer": "A"},
        {"question_id": 2, "answer": "C"},
        {"question_id": 3, "answer": "D"},
        {"question_id": 4, "answer": "B"},
        {"question_id": 5, "answer": "A"},
    ]
    label, desc, scores = svc.classify_archetype(answers)
    assert isinstance(label, ArchetypeLabel)
    assert isinstance(desc, str)
    assert len(scores) == len(ArchetypeLabel)
    assert abs(sum(scores.values()) - 1.0) < 0.05

    # modify_prompt_for_archetype for all labels + None
    for arch in ArchetypeLabel:
        modified = svc.modify_prompt_for_archetype("Base prompt.", arch)
        assert "Tone modifier:" in modified

    assert svc.modify_prompt_for_archetype("Base prompt.", None) == "Base prompt."


# ---------------------------------------------------------------------------
# 4. app/modules/lessons/prompt_version_registry.py
# ---------------------------------------------------------------------------
from app.modules.lessons.prompt_version_registry import (
    PromptTemplateRegistry,
    validate_version_immutable,
)


def test_prompt_version_registry(tmp_path: Path):
    reg = PromptTemplateRegistry(prompts_dir=tmp_path)

    # Template version convention
    assert reg.get_template_version("lesson_v1") == "lesson_v1"

    # Missing template FileNotFoundError
    with pytest.raises(FileNotFoundError):
        reg.get_content_hash("missing_tpl")

    # Create template and hash
    tpl_file = tmp_path / "lesson_v1.jinja2"
    tpl_file.write_text("Hello {{ name }}!", encoding="utf-8")

    digest1 = reg.get_content_hash("lesson_v1")
    assert len(digest1) == 64

    # Render template
    rendered = reg.render("lesson_v1", name="Learner")
    assert rendered == "Hello Learner!"

    # Template changed on disk warning
    tpl_file.write_text("Hello {{ name }} updated!", encoding="utf-8")
    digest2 = reg.get_content_hash("lesson_v1")
    assert digest2 != digest1

    # list_templates
    (tmp_path / "_private.jinja2").write_text("private", encoding="utf-8")
    (tmp_path / "another_v2.jinja2").write_text("another", encoding="utf-8")
    templates = reg.list_templates()
    assert "lesson_v1" in templates
    assert "another_v2" in templates
    assert "_private" not in templates

    # validate_version_immutable
    validate_version_immutable(None, "v1", "lesson-1")
    validate_version_immutable("v1", "v1", "lesson-1")
    with pytest.raises(ValueError, match="Cannot overwrite"):
        validate_version_immutable("v1", "v2", "lesson-1")


# ---------------------------------------------------------------------------
# 5. app/modules/lessons/lesson_metrics.py
# ---------------------------------------------------------------------------
from app.modules.lessons.lesson_metrics import lesson_metrics


def test_lesson_metrics_records():
    lesson_metrics.record_validation(passed=True, caps_ref="G4.Math.1")
    lesson_metrics.record_validation(passed=False, caps_ref="G4.Math.1", failed_rule="rule_1")
    lesson_metrics.record_validation(passed=False, caps_ref="G4.Math.1", failed_rule="")

    lesson_metrics.record_answer_key_verification(verified=True, caps_ref="G4.Math.1")
    lesson_metrics.record_answer_key_verification(verified=False, caps_ref="G4.Math.1")

    lesson_metrics.set_review_queue_depth(5)
    lesson_metrics.record_provider_fallback(from_provider="groq", to_provider="anthropic")

    # Budget clamped between 0.0 and 1.0
    lesson_metrics.set_budget_utilization(ratio=0.5)
    lesson_metrics.set_budget_utilization(ratio=-0.2)
    lesson_metrics.set_budget_utilization(ratio=1.5)

    lesson_metrics.set_circuit_breaker_state(provider="groq", state="open")
    lesson_metrics.set_circuit_breaker_state(provider="anthropic", state="closed")
    lesson_metrics.set_circuit_breaker_state(provider="mock", state="half_open")

    lesson_metrics.record_generation_attempt(caps_ref="G4.Math.1", provider="groq", outcome="success")


# ---------------------------------------------------------------------------
# 6. app/modules/diagnostics/irt_params.py
# ---------------------------------------------------------------------------
from app.modules.diagnostics.irt_params import assign_irt_params


def test_assign_irt_params():
    # 1. MCQ item with missing params
    item_mcq = {"item_type": "mcq", "difficulty_band": "easy"}
    res_mcq = assign_irt_params(item_mcq)
    assert res_mcq["discrimination_a"] == 1.0
    assert res_mcq["guessing_c"] == 0.25
    assert res_mcq["difficulty_b"] == -1.5

    # MCQ item with already set guessing_c
    item_mcq_preset_c = {"item_type": "mcq", "guessing_c": 0.33, "difficulty_band": "easy"}
    res_mcq_preset_c = assign_irt_params(item_mcq_preset_c)
    assert res_mcq_preset_c["guessing_c"] == 0.33

    # 2. Non-MCQ item with explicit discrimination_a
    item_non_mcq = {"item_type": "short_answer", "discrimination_a": 1.4, "difficulty_band": "challenging"}
    res_non_mcq = assign_irt_params(item_non_mcq)
    assert res_non_mcq["discrimination_a"] == 1.4
    assert res_non_mcq["guessing_c"] == 0.0
    assert res_non_mcq["difficulty_b"] == 1.5

    # 3. Existing difficulty_b within band
    item_in_band = {"difficulty_band": "moderate", "difficulty_b": -0.7}
    res_in_band = assign_irt_params(item_in_band)
    assert res_in_band["difficulty_b"] == -0.7

    # 4. Existing difficulty_b out of band -> reset to midpoint
    item_out_band = {"difficulty_band": "moderate", "difficulty_b": 2.5}
    res_out_band = assign_irt_params(item_out_band)
    assert res_out_band["difficulty_b"] == -0.5

    # 5. Invalid float difficulty_b -> reset to midpoint
    item_bad_b = {"difficulty_band": "on_level", "difficulty_b": "not-a-number"}
    res_bad_b = assign_irt_params(item_bad_b)
    assert res_bad_b["difficulty_b"] == 0.5


def test_spaced_repetition_scheduler():
    from app.modules.practice.spaced_repetition_scheduler import SpacedRepetitionScheduler

    scheduler = SpacedRepetitionScheduler()

    # 1. Incorrect response resets interval to 1 and drops EF
    p_wrong = scheduler.update_schedule(correct=False, easiness_factor=2.5)
    assert p_wrong.interval_days == 1
    assert p_wrong.easiness_factor == 2.3

    # Incorrect clamped to 1.3
    p_wrong_clamped = scheduler.update_schedule(correct=False, easiness_factor=1.4)
    assert p_wrong_clamped.easiness_factor == 1.3

    # 2. Correct with interval <= 0
    p_first = scheduler.update_schedule(correct=True, interval_days=0, easiness_factor=2.5)
    assert p_first.interval_days == 1
    assert p_first.easiness_factor == 2.5

    # 3. Correct with interval == 1
    p_second = scheduler.update_schedule(correct=True, interval_days=1, easiness_factor=2.5)
    assert p_second.interval_days == 3
    assert p_second.easiness_factor == 2.6

    # 4. Correct with interval > 1
    p_multi = scheduler.update_schedule(correct=True, interval_days=3, easiness_factor=2.5)
    assert p_multi.interval_days >= 7
    assert p_multi.easiness_factor == 2.6


# ---------------------------------------------------------------------------
# 7. app/modules/diagnostics/bias_review_router.py
# ---------------------------------------------------------------------------
from app.modules.diagnostics.bias_review_router import (
    BiasReviewRequest,
    _require_admin,
    bias_review_queue,
    get_item_bank_service,
    record_bias_review,
)
from app.modules.diagnostics.item_bank_service import ItemBankService


@pytest.mark.asyncio
async def test_bias_review_router():
    db = AsyncMock()
    svc = get_item_bank_service(db)
    assert isinstance(svc, ItemBankService)

    # _require_admin
    _require_admin({"role": "admin"})
    with pytest.raises(HTTPException) as exc_admin:
        _require_admin({"role": "learner"})
    assert exc_admin.value.status_code == 403

    service = AsyncMock()
    admin_user = {"sub": str(uuid4()), "role": "admin"}

    # bias_review_queue: empty refs
    queue_empty = await bias_review_queue(caps_ref=None, limit=10, service=service, current_user=admin_user)
    assert queue_empty == []

    # bias_review_queue: flagged items
    item_flagged = SimpleNamespace(
        item_id=uuid4(),
        caps_ref="G4.Math.1",
        language="en",
        grade=4,
        quality_score=0.65,
        safety_passed=True,
    )
    item_safe = SimpleNamespace(
        item_id=uuid4(),
        caps_ref="G4.Math.1",
        language="en",
        grade=4,
        quality_score=0.9,
        safety_passed=True,
    )
    item_unsafe = SimpleNamespace(
        item_id=uuid4(),
        caps_ref="G4.Math.1",
        language="en",
        grade=4,
        quality_score=0.9,
        safety_passed=False,
    )
    service.repo.list_by_caps_ref.return_value = [item_flagged, item_safe, item_unsafe]

    queue_res = await bias_review_queue(caps_ref="G4.Math.1", limit=10, service=service, current_user=admin_user)
    assert len(queue_res) == 2

    # record_bias_review: item not found
    target_id = uuid4()
    service.mark_item_reviewed.return_value = None
    req_retire = BiasReviewRequest(outcome="retire", notes="Flagged bias")
    with pytest.raises(HTTPException) as exc_rev_404:
        await record_bias_review(target_id, req_retire, service=service, current_user=admin_user)
    assert exc_rev_404.value.status_code == 404

    # record_bias_review: success approve
    service.mark_item_reviewed.return_value = SimpleNamespace(item_id=target_id, review_status="human_reviewed")
    req_approve = BiasReviewRequest(outcome="approve", notes="Looks good")
    rev_res = await record_bias_review(target_id, req_approve, service=service, current_user=admin_user)
    assert rev_res["outcome"] == "approve"
    assert rev_res["review_status"] == "human_reviewed"


# ---------------------------------------------------------------------------
# 8. app/modules/study_plans/runtime_kg_planner.py
# ---------------------------------------------------------------------------
from app.modules.study_plans.runtime_kg_planner import build_runtime_kg_week_focus


def test_runtime_kg_planner():
    # 1. No focus items -> disabled
    with patch("app.modules.study_plans.runtime_kg_planner.runtime_kg_study_plan_focus", return_value=[]):
        res_disabled = build_runtime_kg_week_focus({})
        assert res_disabled["runtime_kg_enabled"] is False
        assert res_disabled["focus_items"] == []

    # 2. Focus items present -> enabled
    focus = [{"topic_id": "t1", "reason": "gap"}]
    with patch("app.modules.study_plans.runtime_kg_planner.runtime_kg_study_plan_focus", return_value=focus):
        res_enabled = build_runtime_kg_week_focus({"graph_version": "v1.0"})
        assert res_enabled["runtime_kg_enabled"] is True
        assert res_enabled["graph_version"] == "v1.0"
        assert res_enabled["focus_items"] == focus
