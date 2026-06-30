"""tests/unit/test_study_plan_service_v2.py
Unit tests for StudyPlanServiceV2 plan generation.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.services.study_plan_service_v2 import (
    StudyPlanServiceV2,
    _build_schedule,
    _load_launch_template,
    _template_lookup,
    _weak_caps_refs,
)


@pytest.mark.unit
def test_study_plan_service_init_with_defaults():
    """Verify constructor uses default repositories when None provided."""
    service = StudyPlanServiceV2()
    assert service.learner_repository is not None
    assert service.study_plan_repository is not None


@pytest.mark.unit
def test_study_plan_service_init_with_custom_repos():
    """Verify constructor uses provided repositories."""
    mock_learner = AsyncMock()
    mock_plan = AsyncMock()
    service = StudyPlanServiceV2(learner_repository=mock_learner, study_plan_repository=mock_plan)
    assert service.learner_repository is mock_learner
    assert service.study_plan_repository is mock_plan


@pytest.mark.unit
async def test_generate_plan_raises_when_learner_not_found():
    """Verify generate_plan raises ValueError when learner not found."""
    service = StudyPlanServiceV2()
    with pytest.raises(ValueError, match="Learner not found"):
        await service.generate_plan("nonexistent-learner")


@pytest.mark.unit
async def test_list_plans_raises_when_learner_not_found():
    """Verify list_plans raises ValueError when learner not found."""
    service = StudyPlanServiceV2()
    with pytest.raises(ValueError, match="Learner not found"):
        await service.list_plans("nonexistent-learner")




@pytest.mark.unit
def test_weak_caps_refs_extracts_string_gaps():
    """Verify _weak_caps_refs extracts string CAPS references."""
    weak = [
        {"knowledge_gaps": ["CAPS.4.MAT.1.1", "CAPS.4.MAT.2.3"]},
        {"knowledge_gaps": ["CAPS.4.ENG.1.1"]},
    ]
    refs = _weak_caps_refs(weak)
    assert "CAPS.4.MAT.1.1" in refs
    assert "CAPS.4.MAT.2.3" in refs
    assert "CAPS.4.ENG.1.1" in refs


@pytest.mark.unit
def test_weak_caps_refs_extracts_dict_gaps():
    """Verify _weak_caps_refs extracts CAPS references from dict gaps."""
    weak = [
        {"knowledge_gaps": [{"caps_ref": "CAPS.4.MAT.1.1"}, {"caps_reference": "CAPS.4.MAT.2.3"}]},
    ]
    refs = _weak_caps_refs(weak)
    assert "CAPS.4.MAT.1.1" in refs
    assert "CAPS.4.MAT.2.3" in refs


@pytest.mark.unit
def test_weak_caps_refs_handles_mixed_formats():
    """Verify _weak_caps_refs handles mixed string and dict formats."""
    weak = [
        {"knowledge_gaps": ["CAPS.4.MAT.1.1", {"caps_ref": "CAPS.4.MAT.2.3"}]},
    ]
    refs = _weak_caps_refs(weak)
    assert "CAPS.4.MAT.1.1" in refs
    assert "CAPS.4.MAT.2.3" in refs


@pytest.mark.unit
def test_template_lookup_creates_dict_by_caps_ref():
    """Verify _template_lookup creates a dictionary keyed by caps_ref."""
    template = {
        "topic_sequence": [
            {"caps_ref": "CAPS.4.MAT.1.1", "topic": "Numbers"},
            {"caps_ref": "CAPS.4.MAT.2.3", "topic": "Operations"},
        ]
    }
    result = _template_lookup(template)
    assert result["CAPS.4.MAT.1.1"]["topic"] == "Numbers"
    assert result["CAPS.4.MAT.2.3"]["topic"] == "Operations"


@pytest.mark.unit
def test_build_schedule_returns_fallback_when_no_template():
    """Verify _build_schedule returns fallback schedule when template unavailable."""
    weak = []
    schedule = _build_schedule(weak, learner_grade=5)
    assert "Mon" in schedule
    assert "Tue" in schedule
    assert len(schedule["Mon"]) == 1


@pytest.mark.unit
def test_build_schedule_returns_fallback_for_non_grade4():
    """Verify _build_schedule returns fallback for non-grade 4 learners."""
    weak = []
    schedule = _build_schedule(weak, learner_grade=5)
    assert "Mon" in schedule
    assert len(schedule["Mon"]) == 1


@pytest.mark.unit
def test_load_launch_template_returns_none_when_file_missing():
    """Verify _load_launch_template returns None when file doesn't exist."""
    with patch("app.services.study_plan_service_v2._LAUNCH_TEMPLATE_PATH") as mock_path:
        mock_path.exists.return_value = False
        result = _load_launch_template()
        assert result is None


@pytest.mark.unit
def test_load_launch_template_returns_none_on_json_error():
    """Verify _load_launch_template returns None on JSON parse error."""
    with patch("app.services.study_plan_service_v2._LAUNCH_TEMPLATE_PATH") as mock_path:
        mock_path.exists.return_value = True
        mock_path.read_text.return_value = "invalid json"
        result = _load_launch_template()
        assert result is None
