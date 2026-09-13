import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.services.gamification_service_v2 import GamificationServiceV2
from app.services.study_plan_service_v2 import (
    StudyPlanServiceV2,
    _build_schedule,
    _build_template_schedule,
    _weak_caps_refs,
)


@pytest.mark.asyncio
async def test_gamification_service_v2_complete():
    mock_session = AsyncMock()

    # 1. from_session and session-based initialization (lines 17, 23)
    service_from_session = GamificationServiceV2.from_session(mock_session)
    assert service_from_session.session is mock_session

    # 2. award_xp with session is None (lines 49-50)
    service_no_session = GamificationServiceV2(repository=MagicMock())
    await service_no_session.award_xp("l1", 50, lesson_id="less-1")

    # 3. award_xp with active session and lesson_id (lines 51-54)
    with patch("app.services.gamification_service_v2.LearnerRepository") as mock_lr_cls, \
         patch("app.services.gamification_service_v2.LessonRepository") as mock_less_cls:
        mock_lr = AsyncMock()
        mock_less = AsyncMock()
        mock_lr_cls.return_value = mock_lr
        mock_less_cls.return_value = mock_less

        await service_from_session.award_xp("l1", 100, lesson_id="less-1")
        mock_lr.add_xp.assert_awaited_once_with("l1", 100)
        mock_less.mark_completed.assert_awaited_once_with("less-1")


@pytest.mark.asyncio
async def test_study_plan_service_v2_complete():
    # 1. Default fallback repositories (_MissingLearnerRepository, _MemoryStudyPlanRepository)
    default_service = StudyPlanServiceV2()
    with pytest.raises(ValueError, match="Learner not found"):
        await default_service.generate_plan("l-missing")

    with pytest.raises(ValueError, match="Learner not found"):
        await default_service.list_plans("l-missing")

    # Direct calls on _MemoryStudyPlanRepository
    mem_repo = default_service.study_plan_repository
    assert await mem_repo.get_subject_mastery("l1") == []
    created_local = await mem_repo.create(test="data")
    assert created_local["plan_id"] == "local-plan"
    assert await mem_repo.list_for_learner("l1") == []

    # 2. _weak_caps_refs with string and dict gaps (lines 78-86)
    weak_rows = [
        {"knowledge_gaps": ["CAPS.MATH.G4.T1", "invalid_short_gap"]},
        {"knowledge_gaps": [{"caps_ref": "CAPS.MATH.G4.T2"}, {"caps_reference": "CAPS.MATH.G4.T3"}]},
        {"knowledge_gaps": None},
    ]
    refs = _weak_caps_refs(weak_rows)
    assert "CAPS.MATH.G4.T1" in refs
    assert "CAPS.MATH.G4.T2" in refs
    assert "CAPS.MATH.G4.T3" in refs
    assert "invalid_short_gap" not in refs

    # 3. _build_template_schedule (lines 93-117)
    # grade not in {4, None}
    assert _build_template_schedule([], learner_grade=7) is None

    # template missing or failed load
    with patch("app.services.study_plan_service_v2._load_launch_template", return_value=None):
        assert _build_template_schedule([], learner_grade=4) is None

    # successful template schedule build
    mock_template = {
        "weekly_template": [
            {
                "day": "Mon",
                "caps_ref": "CAPS.MATH.G4.T1",
                "activity_type": "lesson",
                "lesson_variant": "standard",
            },
            {
                "day": "Tue",
                "caps_ref": "CAPS.MATH.G4.T2",
            }
        ],
        "topic_sequence": [
            {"caps_ref": "CAPS.MATH.G4.T1", "topic": "Whole Numbers"},
            {"caps_ref": "CAPS.MATH.G4.T2", "topic": "Addition"},
        ]
    }
    with patch("app.services.study_plan_service_v2._load_launch_template", return_value=mock_template):
        sched = _build_template_schedule(weak_rows, learner_grade=4)
        assert sched is not None
        assert len(sched["Mon"]) == 1
        assert sched["Mon"][0]["type"] == "gap-fill"
        assert sched["Mon"][0]["label"] == "Whole Numbers"

    # 4. _build_schedule fallback without template (lines 124-145)
    with patch("app.services.study_plan_service_v2._build_template_schedule", return_value=None):
        # Empty weak items fallback to default subjects
        fallback_sched_empty = _build_schedule([])
        assert "English Review" in fallback_sched_empty["Mon"][0]["label"]

        # Weak items with custom subject
        fallback_sched_custom = _build_schedule([{"subject_code": "Science"}])
        assert "Science Review" in fallback_sched_custom["Mon"][0]["label"]

    # 5. generate_plan and list_plans with mock repos
    learner_repo = AsyncMock()
    learner_repo.get_by_id.return_value = type("Learner", (), {"id": "l1", "grade": 4})()
    sp_repo = AsyncMock()
    sp_repo.get_subject_mastery.return_value = [{"subject_code": "Maths", "mastery_score": 0.3}]
    sp_repo.create.return_value = {"id": "plan-1"}
    sp_repo.list_for_learner.return_value = [{"id": "plan-1"}]

    service = StudyPlanServiceV2(learner_repo, sp_repo)
    with patch("app.services.study_plan_service_v2.AuditService") as mock_audit_cls:
        mock_audit = AsyncMock()
        mock_audit_cls.return_value = mock_audit
        plan = await service.generate_plan("l1")
        assert plan["id"] == "plan-1"
        assert "week_focus" in plan
        mock_audit.log_event.assert_awaited_once()

    plans_list = await service.list_plans("l1")
    assert len(plans_list) == 1
