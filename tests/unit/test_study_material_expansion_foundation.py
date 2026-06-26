from __future__ import annotations

import pytest

from app.services.content_learner_read_service import ContentLearnerReadService
from app.services.content_scope_registry import ContentScopeRegistry
from scripts.curriculum.report_content_coverage import build_report
from scripts.curriculum.validate_scope_content import validate_scope


pytestmark = pytest.mark.unit


class NoDbSession:
    async def execute(self, query):  # pragma: no cover - non-active scopes must fail before DB access
        raise AssertionError("planned scopes must not query learner-visible content")

    async def scalar(self, query):  # pragma: no cover - non-active scopes must fail before DB access
        raise AssertionError("planned scopes must not query learner-visible content")


def test_review_scopes_are_registered_generation_ready_but_not_active() -> None:
    registry = ContentScopeRegistry()

    review_scope = registry.get_scope("grade5_mathematics_en")

    assert review_scope.status.value == "review"
    assert len(review_scope.caps_refs) == 16
    assert review_scope.topic_map_path == "data/caps/topic_maps/grade5_mathematics_en.json"
    assert "grade5_mathematics_en" not in {scope.scope_id for scope in registry.list_active_scopes()}
    assert "grade4_mathematics_en" in {scope.scope_id for scope in registry.list_active_scopes()}


def test_review_scope_validation_is_skipped_but_generation_ready() -> None:
    result = validate_scope("grade5_mathematics_en", strict=True)

    assert result.passed is True
    assert result.skipped is True
    assert result.status == "review"
    assert result.item_counts == {}
    assert result.lesson_counts == {}


@pytest.mark.asyncio
async def test_review_scope_cannot_be_served_to_learners() -> None:
    service = ContentLearnerReadService()

    with pytest.raises(LookupError, match="not active"):
        await service.get_scope_content_summary(NoDbSession(), "grade5_mathematics_en")
    with pytest.raises(LookupError, match="not active"):
        await service.get_diagnostic_items(NoDbSession(), scope_id="grade5_mathematics_en")
    with pytest.raises(LookupError, match="not active"):
        await service.get_lessons(NoDbSession(), scope_id="grade5_mathematics_en")


def test_generic_scope_validator_preserves_grade4_math_launch_strict_gate() -> None:
    result = validate_scope("grade4_mathematics_en", strict=True)

    assert result.passed is True
    assert result.skipped is False
    assert result.item_counts == {"4.M.1.1": 40, "4.M.1.2": 40, "4.M.1.3": 40}
    assert result.lesson_counts == {"4.M.1.1": 8, "4.M.1.2": 8, "4.M.1.3": 8}


def test_coverage_report_separates_active_and_planned_scopes() -> None:
    report = build_report(strict_counts=True)

    assert report["summary"]["scopes.active"] == 1
    assert report["summary"]["scopes.learner_visible"] == 1
    assert report["summary"]["scopes.review"] == 50
    assert report["summary"]["caps_refs.active"] == 3
    grade5 = next(row for row in report["scopes"] if row["scope_id"] == "grade5_mathematics_en")
    assert grade5["status"] == "review"
    assert grade5["learner_visible"] is False
    assert grade5["caps_ref_count"] == 16
    assert grade5["validation_status"] == "not_applicable"
