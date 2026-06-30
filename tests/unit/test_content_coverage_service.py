from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.domain.content_coverage import ContentLayer, coverage_status
from app.services.content_coverage_service import ContentCoverageService


pytestmark = pytest.mark.unit


class FakeItemRepo:
    def __init__(self, counts: dict[str, dict[str, int]]) -> None:
        self.counts = counts

    async def get_coverage_summary(self, caps_refs: list[str] | None = None) -> dict[str, dict[str, int]]:
        if caps_refs is None:
            return self.counts
        return {ref: self.counts.get(ref, {}) for ref in caps_refs}


@dataclass
class Lesson:
    review_status: str


class FakeLessonRepo:
    def __init__(self, lessons: dict[str, list[Lesson]]) -> None:
        self.lessons = lessons

    async def list_by_caps_ref(self, caps_ref: str, include_all_statuses: bool = False) -> list[Lesson]:
        assert include_all_statuses is True
        return self.lessons.get(caps_ref, [])


def _service(
    item_counts: dict[str, dict[str, int]] | None = None,
    lessons: dict[str, list[Lesson]] | None = None,
) -> ContentCoverageService:
    return ContentCoverageService(
        item_repo=FakeItemRepo(item_counts or {}),
        lesson_repo=FakeLessonRepo(lessons or {}),
    )


def test_coverage_status_thresholds() -> None:
    assert coverage_status(0, 0).value == "not_configured"
    assert coverage_status(0, 40).value == "red"
    assert coverage_status(12, 40).value == "amber"
    assert coverage_status(40, 40).value == "green"
    assert coverage_status(41, 40).value == "green"


@pytest.mark.asyncio
async def test_computes_registry_targets_for_diagnostic_items_and_lessons() -> None:
    service = _service(
        item_counts={"4.M.1.1": {"approved": 20, "ai_generated": 2, "human_reviewed": 1, "rejected": 3}},
        lessons={
            "4.M.1.1": [
                Lesson("approved"),
                Lesson("approved"),
                Lesson("ai_generated"),
                Lesson("rejected"),
            ]
        },
    )

    report = await service.get_caps_ref_coverage(
        "grade4_mathematics_en",
        "4.M.1.1",
        layers=[ContentLayer.DIAGNOSTIC_ITEMS, ContentLayer.LESSONS],
    )

    diagnostic = report.layers[ContentLayer.DIAGNOSTIC_ITEMS]
    lessons = report.layers[ContentLayer.LESSONS]
    assert diagnostic.target == 40
    assert diagnostic.approved == 20
    assert diagnostic.pending_review == 3
    assert diagnostic.rejected == 3
    assert diagnostic.status.value == "amber"
    assert lessons.target == 8
    assert lessons.approved == 2
    assert lessons.pending_review == 1
    assert lessons.rejected == 1
    assert lessons.status.value == "amber"


@pytest.mark.asyncio
async def test_scope_coverage_summarizes_green_amber_and_red_refs() -> None:
    service = _service(
        item_counts={
            "4.M.1.1": {"approved": 40},
            "4.M.1.2": {"approved": 20},
            "4.M.1.3": {"approved": 0},
        },
        lessons={
            "4.M.1.1": [Lesson("approved") for _ in range(8)],
            "4.M.1.2": [Lesson("approved") for _ in range(8)],
            "4.M.1.3": [Lesson("approved") for _ in range(8)],
        },
    )

    report = await service.get_scope_coverage(
        "grade4_mathematics_en",
        layers=[ContentLayer.DIAGNOSTIC_ITEMS, ContentLayer.LESSONS],
    )

    assert report.summary.total_caps_refs == 3
    assert report.summary.green_refs == 1
    assert report.summary.amber_refs == 1
    assert report.summary.red_refs == 1
    assert report.layers[ContentLayer.DIAGNOSTIC_ITEMS].target_total == 120
    assert report.layers[ContentLayer.DIAGNOSTIC_ITEMS].approved_total == 60
    assert report.layers[ContentLayer.LESSONS].target_total == 24
    assert report.layers[ContentLayer.LESSONS].approved_total == 24


@pytest.mark.asyncio
async def test_rejects_unknown_scope_id() -> None:
    with pytest.raises(LookupError, match="Unknown content scope"):
        await _service().get_scope_coverage("unknown_scope")


@pytest.mark.asyncio
async def test_rejects_caps_ref_outside_scope() -> None:
    with pytest.raises(LookupError, match="outside content scope"):
        await _service().get_caps_ref_coverage("grade4_mathematics_en", "4.M.9.9")


@pytest.mark.asyncio
async def test_future_layers_return_configured_zero_count_placeholders() -> None:
    service = _service()

    report = await service.get_caps_ref_coverage(
        "grade4_mathematics_en",
        "4.M.1.1",
        layers=[ContentLayer.ASSESSMENT_BLUEPRINTS, ContentLayer.STUDY_PLAN_TEMPLATES],
    )

    assert report.layers[ContentLayer.ASSESSMENT_BLUEPRINTS].target == 4
    assert report.layers[ContentLayer.ASSESSMENT_BLUEPRINTS].approved == 0
    assert report.layers[ContentLayer.ASSESSMENT_BLUEPRINTS].status.value == "red"
    assert report.layers[ContentLayer.STUDY_PLAN_TEMPLATES].target == 3
    assert report.layers[ContentLayer.STUDY_PLAN_TEMPLATES].approved == 0


@pytest.mark.asyncio
async def test_scope_coverage_defaults_to_all_learner_facing_layers() -> None:
    report = await _service().get_caps_ref_coverage("grade4_mathematics_en", "4.M.1.1")

    assert set(report.layers) == {
        ContentLayer.DIAGNOSTIC_ITEMS,
        ContentLayer.LESSONS,
        ContentLayer.ASSESSMENT_BLUEPRINTS,
        ContentLayer.STUDY_PLAN_TEMPLATES,
    }
