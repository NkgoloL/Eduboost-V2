import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.services.mastery_engine import (
    MasteryEngine,
    MasteryEstimate,
    MasteryStateEnum,
)
from app.services.study_plan_service_v2 import (
    StudyPlanServiceV2,
    _MemoryStudyPlanRepository,
    _MissingLearnerRepository,
    _build_schedule,
    _build_template_schedule,
    _load_launch_template,
    _weak_caps_refs,
)


@pytest.mark.asyncio
async def test_study_plan_service_v2_complete():
    # 1. Default repositories (_MissingLearnerRepository and _MemoryStudyPlanRepository)
    missing_repo = _MissingLearnerRepository()
    assert await missing_repo.get_by_id("any") is None

    mem_repo = _MemoryStudyPlanRepository()
    assert await mem_repo.get_subject_mastery("l1") == []
    created_mem = await mem_repo.create(test_key="val")
    assert created_mem["plan_id"] == "local-plan"
    assert await mem_repo.list_for_learner("l1") == []

    # 2. StudyPlanServiceV2 initialization defaults & error handling
    default_svc = StudyPlanServiceV2()
    with pytest.raises(ValueError, match="Learner not found"):
        await default_svc.generate_plan("unknown-learner")

    with pytest.raises(ValueError, match="Learner not found"):
        await default_svc.list_plans("unknown-learner")

    # 3. Successful list_plans
    mock_learner_repo = AsyncMock()
    mock_learner_repo.get_by_id.return_value = SimpleNamespace(id="l1", grade=4)
    mock_plan_repo = AsyncMock()
    mock_plan_repo.list_for_learner.return_value = [{"plan_id": "p1"}]

    svc = StudyPlanServiceV2(
        learner_repository=mock_learner_repo,
        study_plan_repository=mock_plan_repo,
    )
    plans = await svc.list_plans("l1")
    assert plans == [{"plan_id": "p1"}]

    # 4. generate_plan with weak subjects (lines 20-38)
    weak_mastery = [
        {"subject_code": "MATH", "mastery_score": 0.2, "knowledge_gaps": ["CAPS.G4.M.1", {"caps_ref": "CAPS.G4.M.2"}]},
        {"subject_code": "SCI", "mastery_score": 0.4, "knowledge_gaps": [{"caps_reference": "CAPS.G4.S.1"}]},
    ]
    mock_plan_repo.get_subject_mastery.return_value = weak_mastery
    mock_plan_repo.create.return_value = {"plan_id": "generated-p1"}

    plan = await svc.generate_plan("l1", gap_ratio=0.5)
    assert "MATH" in plan["week_focus"]
    assert "schedule" in plan
    assert "days" in plan

    # 5. generate_plan without weak subjects (empty mastery)
    mock_plan_repo.get_subject_mastery.return_value = []
    plan_empty = await svc.generate_plan("l1", gap_ratio=0.5)
    assert plan_empty["week_focus"] == "Balanced revision and grade-level progress"

    # 6. _weak_caps_refs helper
    assert "CAPS.G4.M.1" in _weak_caps_refs(weak_mastery)
    assert "CAPS.G4.M.2" in _weak_caps_refs(weak_mastery)
    assert "CAPS.G4.S.1" in _weak_caps_refs(weak_mastery)

    # 7. _load_launch_template with missing file and invalid JSON
    with patch("pathlib.Path.exists", return_value=False):
        assert _load_launch_template() is None

    with patch("pathlib.Path.exists", return_value=True), patch("pathlib.Path.read_text", return_value="invalid json"):
        assert _load_launch_template() is None

    # 8. _build_template_schedule with non-grade 4 learner (line 94-95)
    assert _build_template_schedule([], learner_grade=7) is None

    # 9. _build_template_schedule with template loaded (lines 101-117)
    sample_template = {
        "topic_sequence": [
            {"caps_ref": "CAPS.G4.M.1", "topic": "Numbers"},
            {"caps_ref": "CAPS.G4.M.2", "topic": "Fractions"},
        ],
        "weekly_template": [
            {"day": "Mon", "caps_ref": "CAPS.G4.M.1", "activity_type": "lesson", "lesson_variant": "standard"},
            {"day": "Tue", "caps_ref": "CAPS.G4.M.2"},
        ],
    }
    with patch("app.services.study_plan_service_v2._load_launch_template", return_value=sample_template):
        sched = _build_template_schedule(weak_mastery, learner_grade=4)
        assert sched is not None
        assert len(sched["Mon"]) == 1
        assert sched["Mon"][0]["type"] == "gap-fill"
        assert sched["Mon"][0]["caps_ref"] == "CAPS.G4.M.1"

    # 10. _build_schedule fallback (lines 125-145) with grade 7 and no template
    with patch("app.services.study_plan_service_v2._load_launch_template", return_value=None):
        # with weak subjects
        fallback_with_weak = _build_schedule([{"subject_code": "Natural Sciences"}], learner_grade=7)
        assert fallback_with_weak["Mon"][0]["label"] == "Natural Sciences Review"

        # without weak subjects (empty) -> triggers gap_subjects = ["English", "Mathematics"] (line 127)
        fallback_no_weak = _build_schedule([], learner_grade=7)
        assert fallback_no_weak["Mon"][0]["label"] == "English Review"
        assert fallback_no_weak["Tue"][0]["label"] == "Mathematics Practice"


def test_mastery_engine_complete():
    engine = MasteryEngine()

    # 1. Invalid response counts (line 86)
    with pytest.raises(ValueError, match="Invalid response counts"):
        engine.calculate_node_mastery("l1", "node1", correct_responses=-1, total_responses=5)

    with pytest.raises(ValueError, match="Invalid response counts"):
        engine.calculate_node_mastery("l1", "node1", correct_responses=6, total_responses=5)

    # 2. total_responses == 0 with prior_score (lines 90-103)
    res_zero_prior = engine.calculate_node_mastery("l1", "node1", correct_responses=0, total_responses=0, prior_score=0.75)
    assert res_zero_prior.mastery_score == 0.75
    assert res_zero_prior.confidence == 0.10
    assert res_zero_prior.state == MasteryStateEnum.TENTATIVE

    # 3. to_dict method (lines 48-59)
    d = res_zero_prior.to_dict()
    assert d["learner_id"] == "l1"
    assert d["node_id"] == "node1"
    assert d["mastery_score"] == 0.75
    assert d["state"] == "tentative"
    assert d["confidence"] == 0.1
