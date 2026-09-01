"""Batch 234 — StudyPlanServiceV2 and StudyPlanRepository branch coverage expansion.

Tests:
- app/services/study_plan_service_v2.py:
  - Default _MissingLearnerRepository and _MemoryStudyPlanRepository
  - generate_plan: learner missing (ValueError), weak mastery vs no mastery, template vs fallback schedule
  - list_plans: learner missing (ValueError) vs success list
  - _weak_caps_refs parsing string and dict gaps
  - _build_template_schedule non-grade-4 fallback
  - _build_schedule gap subjects fallback
- app/repositories/study_plan_repository.py:
  - create: persistence and dict return
  - get_by_id: found vs None
  - list_for_learner: list mapping
  - get_subject_mastery: rows mapping
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models import StudyPlan, SubjectMastery
from app.repositories.study_plan_repository import StudyPlanRepository
from app.services.study_plan_service_v2 import (
    StudyPlanServiceV2,
    _build_schedule,
    _build_template_schedule,
    _MemoryStudyPlanRepository,
    _MissingLearnerRepository,
    _weak_caps_refs,
)


# ---------------------------------------------------------------------------
# Default Repositories & Helpers
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_default_memory_and_missing_repos():
    missing_learner = _MissingLearnerRepository()
    assert await missing_learner.get_by_id("l-1") is None

    mem_study_plan = _MemoryStudyPlanRepository()
    assert await mem_study_plan.get_subject_mastery("l-1") == []
    assert await mem_study_plan.list_for_learner("l-1") == []
    created = await mem_study_plan.create(gap_ratio=0.3)
    assert created["plan_id"] == "local-plan"
    assert created["gap_ratio"] == 0.3


@pytest.mark.unit
def test_weak_caps_refs_and_schedules():
    # String gaps with >=3 dots and dict gaps
    weak = [
        {"knowledge_gaps": ["4.M.1.1.1", "invalid_gap"]},
        {"knowledge_gaps": [{"caps_ref": "4.M.2.1"}, {"caps_reference": "4.M.3.1"}]},
    ]
    refs = _weak_caps_refs(weak)
    assert "4.M.1.1.1" in refs
    assert "4.M.2.1" in refs
    assert "4.M.3.1" in refs

    # Non-grade-4 returns None for template schedule
    assert _build_template_schedule(weak, learner_grade=7) is None

    # Fallback schedule with empty weak subjects for non-grade-4
    sched_fallback = _build_schedule([], learner_grade=7)
    assert "Mon" in sched_fallback
    assert "English" in sched_fallback["Mon"][0]["label"]


# ---------------------------------------------------------------------------
# StudyPlanServiceV2 generate_plan & list_plans
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_study_plan_service_generate_and_list():
    mock_learner_repo = AsyncMock()
    mock_study_repo = AsyncMock()
    svc = StudyPlanServiceV2(
        learner_repository=mock_learner_repo,
        study_plan_repository=mock_study_repo,
    )

    # 1. generate_plan learner missing -> ValueError
    mock_learner_repo.get_by_id.return_value = None
    with pytest.raises(ValueError, match="Learner not found"):
        await svc.generate_plan("l-1")

    # 2. generate_plan success with weak mastery
    mock_learner = SimpleNamespace(id="l-1", grade=4)
    mock_learner_repo.get_by_id.return_value = mock_learner

    mock_study_repo.get_subject_mastery.return_value = [
        {"subject_code": "MATHS", "mastery_score": 0.4, "knowledge_gaps": ["4.M.1.1.1"]},
        {"subject_code": "ENG", "mastery_score": 0.8, "knowledge_gaps": []},
    ]
    mock_study_repo.create.return_value = {
        "plan_id": "plan-123",
        "learner_id": "l-1",
        "week_focus": "Focus on MATHS, ENG",
        "gap_ratio": 0.4,
    }

    with patch("app.services.study_plan_service_v2.AuditService") as mock_audit:
        mock_audit.return_value.log_event = AsyncMock()
        plan_res = await svc.generate_plan("l-1", gap_ratio=0.4)
        assert plan_res["plan_id"] == "plan-123"
        assert "schedule" in plan_res
        mock_study_repo.create.assert_called_once()
        mock_audit.return_value.log_event.assert_called_once()

    # 3. list_plans learner missing vs success
    mock_learner_repo.get_by_id.return_value = None
    with pytest.raises(ValueError, match="Learner not found"):
        await svc.list_plans("l-1")

    mock_learner_repo.get_by_id.return_value = mock_learner
    mock_study_repo.list_for_learner.return_value = [{"plan_id": "plan-1"}]
    plans = await svc.list_plans("l-1")
    assert len(plans) == 1
    assert plans[0]["plan_id"] == "plan-1"


# ---------------------------------------------------------------------------
# StudyPlanRepository DB Operations
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_study_plan_repository_operations():
    repo = StudyPlanRepository()
    mock_session = AsyncMock()

    with patch("app.repositories.study_plan_repository.AsyncSessionFactory") as mock_session_factory:
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        # 1. create
        plan_created = await repo.create(
            learner_id="l-100",
            schedule={"Mon": []},
            gap_ratio=0.3,
            week_focus="Review",
        )
        assert plan_created["learner_id"] == "l-100"
        assert plan_created["gap_ratio"] == 0.3
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

        # 2. get_by_id None vs Found
        res_exec_none = MagicMock()
        res_exec_none.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = res_exec_none

        assert await repo.get_by_id("missing-id") is None

        mock_plan = SimpleNamespace(
            id="p-1",
            learner_id="l-100",
            week_start=datetime.now(timezone.utc),
            schedule={"Mon": []},
            gap_ratio=0.2,
            week_focus="Maths",
            generated_by="ALGO",
        )
        res_exec_found = MagicMock()
        res_exec_found.scalar_one_or_none.return_value = mock_plan
        mock_session.execute.return_value = res_exec_found

        plan_found = await repo.get_by_id("p-1")
        assert plan_found is not None
        assert plan_found["plan_id"] == "p-1"

        # 3. list_for_learner
        res_exec_list = MagicMock()
        res_exec_list.scalars.return_value.all.return_value = [mock_plan]
        mock_session.execute.return_value = res_exec_list

        list_plans = await repo.list_for_learner("l-100")
        assert len(list_plans) == 1
        assert list_plans[0]["plan_id"] == "p-1"

        # 4. get_subject_mastery
        mock_mastery = SimpleNamespace(
            subject_code="MATHS",
            grade_level=4,
            mastery_score=0.85,
            knowledge_gaps=["gap-1"],
        )
        res_exec_mastery = MagicMock()
        res_exec_mastery.scalars.return_value.all.return_value = [mock_mastery]
        mock_session.execute.return_value = res_exec_mastery

        mastery_list = await repo.get_subject_mastery("l-100")
        assert len(mastery_list) == 1
        assert mastery_list[0]["subject_code"] == "MATHS"
        assert mastery_list[0]["mastery_score"] == 0.85
