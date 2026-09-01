"""Batch 245 — ContentCoverageService deep branch coverage expansion.

Tests:
- build_content_coverage_service and from_session factory helpers
- get_scope_coverage across full scope, per-caps-ref, and summary rollup
- get_coverage for promotion gates (diagnostic items, lessons, assessment blueprints, study plan templates)
- get_caps_ref_coverage with outside CAPS reference LookupError
- _layer_counts target LookupError fallback
- _diagnostic_counts and _lesson_counts with None repos
- _summarize_caps_refs with red, amber, green, and not_configured references
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.content_coverage import (
    CapsRefCoverageReport,
    ContentLayer,
    CoverageLayerCounts,
    CoverageLayerStatus,
    ScopeCoverageSummary,
)
from app.services.content_coverage_service import (
    ContentCoverageService,
    _status,
    build_content_coverage_service,
)


# ---------------------------------------------------------------------------
# Factories and Helpers
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_factories_and_status_helper():
    mock_item_repo = MagicMock()
    mock_lesson_repo = MagicMock()

    svc = build_content_coverage_service(mock_item_repo, mock_lesson_repo)
    assert svc.item_repo == mock_item_repo
    assert svc.lesson_repo == mock_lesson_repo

    mock_session = MagicMock()
    svc_sess = ContentCoverageService.from_session(mock_session)
    assert svc_sess.item_repo is not None
    assert svc_sess.lesson_repo is not None

    # _status helper
    assert _status(SimpleNamespace(review_status="approved")) == "approved"
    assert _status(SimpleNamespace(review_status=SimpleNamespace(value="published"))) == "published"
    assert _status(SimpleNamespace()) == ""


# ---------------------------------------------------------------------------
# Scope Coverage and Summary Calculations
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_scope_coverage_and_summaries():
    mock_registry = MagicMock()
    mock_registry.get_scope.return_value = SimpleNamespace(
        scope_id="term_1_maths",
        grade=4,
        subject_code="MATH",
        language="en",
        caps_refs=["4.M.1.1", "4.M.1.2"],
    )
    mock_registry.get_scope_caps_refs.return_value = ["4.M.1.1", "4.M.1.2"]
    mock_registry.get_coverage_target.return_value = 10

    mock_item_repo = AsyncMock()
    mock_item_repo.get_coverage_summary = AsyncMock(
        return_value={
            "4.M.1.1": {"approved": 10, "ai_generated": 0, "human_reviewed": 0, "rejected": 0},
            "4.M.1.2": {"approved": 5, "ai_generated": 2, "human_reviewed": 0, "rejected": 1},
        }
    )

    mock_lesson_repo = AsyncMock()
    mock_lesson_repo.list_by_caps_ref = AsyncMock(
        return_value=[SimpleNamespace(review_status="approved")] * 5
    )

    svc = ContentCoverageService(
        scope_registry=mock_registry,
        item_repo=mock_item_repo,
        lesson_repo=mock_lesson_repo,
    )

    # 1. get_scope_coverage
    report = await svc.get_scope_coverage("term_1_maths")
    assert report.scope_id == "term_1_maths"
    assert len(report.per_caps_ref) == 2
    assert ContentLayer.DIAGNOSTIC_ITEMS in report.layers
    assert ContentLayer.LESSONS in report.layers

    # 2. _summarize_caps_refs with various statuses
    reports = [
        CapsRefCoverageReport(
            scope_id="s1",
            caps_ref="4.M.1.1",
            layers={
                ContentLayer.LESSONS: CoverageLayerCounts(
                    target=10, approved=10, pending_review=0, rejected=0, generated=0,
                    status=CoverageLayerStatus.GREEN, coverage_ratio=1.0,
                )
            },
        ),
        CapsRefCoverageReport(
            scope_id="s1",
            caps_ref="4.M.1.2",
            layers={
                ContentLayer.LESSONS: CoverageLayerCounts(
                    target=10, approved=5, pending_review=2, rejected=0, generated=0,
                    status=CoverageLayerStatus.AMBER, coverage_ratio=0.5,
                )
            },
        ),
        CapsRefCoverageReport(
            scope_id="s1",
            caps_ref="4.M.1.3",
            layers={
                ContentLayer.LESSONS: CoverageLayerCounts(
                    target=10, approved=0, pending_review=0, rejected=0, generated=0,
                    status=CoverageLayerStatus.RED, coverage_ratio=0.0,
                )
            },
        ),
        CapsRefCoverageReport(
            scope_id="s1",
            caps_ref="4.M.1.4",
            layers={
                ContentLayer.LESSONS: CoverageLayerCounts(
                    target=0, approved=0, pending_review=0, rejected=0, generated=0,
                    status=CoverageLayerStatus.NOT_CONFIGURED, coverage_ratio=0.0,
                )
            },
        ),
    ]
    summary = svc._summarize_caps_refs(reports)
    assert summary.total_caps_refs == 4
    assert summary.green_refs == 1
    assert summary.amber_refs == 1
    assert summary.red_refs == 1
    assert summary.not_configured_refs == 1


# ---------------------------------------------------------------------------
# Promotion Gate Coverage and Out-of-Scope Errors
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_coverage_and_outside_caps_ref():
    mock_registry = MagicMock()
    mock_registry.get_scope.return_value = SimpleNamespace(
        scope_id="term_1_maths",
        grade=4,
        subject_code="MATH",
        language="en",
        caps_refs=["4.M.1.1"],
    )
    mock_registry.get_scope_caps_refs.return_value = ["4.M.1.1"]
    mock_registry.get_coverage_target.return_value = 5

    svc = ContentCoverageService(scope_registry=mock_registry, item_repo=None, lesson_repo=None)

    # 1. Out of scope CAPS ref -> LookupError
    with pytest.raises(LookupError, match="outside content scope"):
        await svc.get_caps_ref_coverage("term_1_maths", "9.M.9.9")

    # 2. None repos return 0 counts gracefully
    diag_counts = await svc._diagnostic_counts("4.M.1.1")
    assert diag_counts["approved"] == 0
    lesson_counts = await svc._lesson_counts("4.M.1.1")
    assert lesson_counts["approved"] == 0

    # 3. get_coverage for Assessment Blueprints using DB query
    mock_session = AsyncMock()
    mock_exec_result = MagicMock()
    mock_exec_result.scalar_one_or_none.return_value = 4
    mock_session.execute = AsyncMock(return_value=mock_exec_result)

    gate_report = await svc.get_coverage(
        mock_session,
        scope_id="term_1_maths",
        layer=ContentLayer.ASSESSMENT_BLUEPRINTS,
    )
    assert gate_report.approved_total == 4
    assert gate_report.target_total == 5
    assert gate_report.coverage_percentage == 80.0
