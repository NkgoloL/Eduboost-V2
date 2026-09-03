"""Batch 215 — app/services/content_production_promotion_gate.py branch coverage expansion.

Tests comprehensive evaluation paths:
- All blocker types: coverage, review, validation, provenance, staging, source_quality, license, configuration
- evaluate_scope and assert_promotable success and exception branches
- _check_coverage with GREEN and non-GREEN layers
- _check_staging_verification: no items, missing artifact, non-active status, active status
- _check_artifact_status: non-approved, missing sources, missing reviews, missing/failed validation reports, fully valid artifacts
"""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.content_coverage import ContentLayer, CoverageLayerStatus
from app.models.content_factory import (
    ContentArtifactReview,
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentReviewAction,
    ContentStagingArtifact,
    ContentStagingSeedItem,
    ContentValidationReport,
)
from app.services.content_production_promotion_gate import (
    ContentProductionPromotionGate,
    ProductionGateBlocker,
    ProductionGateReport,
    ProductionGateStatus,
)


@pytest.fixture
def mock_coverage_service():
    service = MagicMock()
    # Default to green coverage
    green_target = MagicMock()
    green_target.scope_id = "scope-123"
    green_target.layer = ContentLayer.LESSONS
    green_target.coverage_percentage = 100.0
    green_target.target_percentage = 100.0
    green_target.status = CoverageLayerStatus.GREEN

    service.get_coverage = AsyncMock(return_value=green_target)
    return service


@pytest.fixture
def gate(mock_coverage_service):
    return ContentProductionPromotionGate(coverage_service=mock_coverage_service)


# ---------------------------------------------------------------------------
# Status and Blocker Types Mapping
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_evaluate_scope_promotable_when_no_blockers(gate, mock_coverage_service):
    mock_session = AsyncMock()

    # Staging returns active item
    artifact_id = uuid.uuid4()
    item = MagicMock(spec=ContentStagingSeedItem, artifact_id=artifact_id, caps_ref="MATH.4.1")
    staging_art = MagicMock(spec=ContentStagingArtifact, artifact_id=artifact_id, staging_status="active")

    # Artifact returns approved item with source, review, and passed validation
    art = MagicMock(spec=ContentGenerationArtifact, artifact_id=artifact_id, status=ContentArtifactStatus.APPROVED, caps_ref="MATH.4.1")
    source = MagicMock(spec=ContentArtifactSource)
    review = MagicMock(spec=ContentArtifactReview)
    val_report = MagicMock(spec=ContentValidationReport, passed=True)

    # Sequence of session.execute queries:
    # 1. _check_staging_verification seeded items
    res_seeded = MagicMock()
    res_seeded.scalars.return_value.all.return_value = [item]

    # 2. _check_staging_verification staging artifact
    res_staging_art = MagicMock()
    res_staging_art.scalar_one_or_none.return_value = staging_art

    # 3. _check_artifact_status artifacts
    res_artifacts = MagicMock()
    res_artifacts.scalars.return_value.all.return_value = [art]

    # 4. _check_artifact_status source count
    res_source = MagicMock()
    res_source.scalars.return_value.first.return_value = source

    # 5. _check_artifact_status review
    res_review = MagicMock()
    res_review.scalars.return_value.first.return_value = review

    # 6. _check_artifact_status validation report
    res_val = MagicMock()
    res_val.scalar_one_or_none.return_value = val_report

    mock_session.execute.side_effect = [
        res_seeded,
        res_staging_art,
        res_artifacts,
        res_source,
        res_review,
        res_val,
    ]

    report = await gate.evaluate_scope(mock_session, "scope-123", layers=[ContentLayer.LESSONS])

    assert report.status == ProductionGateStatus.PROMOTABLE
    assert len(report.blockers) == 0
    assert report.coverage_summary["lessons"]["status"] == "green"
    assert report.staging_summary["seeded_count"] == 1


@pytest.mark.asyncio
@pytest.mark.unit
async def test_evaluate_scope_blocked_by_coverage(gate, mock_coverage_service):
    mock_session = AsyncMock()

    red_target = MagicMock()
    red_target.scope_id = "scope-123"
    red_target.layer = ContentLayer.LESSONS
    red_target.coverage_percentage = 40.0
    red_target.target_percentage = 100.0
    red_target.status = CoverageLayerStatus.RED
    mock_coverage_service.get_coverage.return_value = red_target

    # Staging has no items (adds staging blocker too)
    res_seeded = MagicMock()
    res_seeded.scalars.return_value.all.return_value = []

    res_artifacts = MagicMock()
    res_artifacts.scalars.return_value.all.return_value = []

    mock_session.execute.side_effect = [res_seeded, res_artifacts]

    report = await gate.evaluate_scope(mock_session, "scope-123", layers=[ContentLayer.LESSONS])

    # Coverage takes priority in blocker type resolution
    assert report.status == ProductionGateStatus.BLOCKED_BY_COVERAGE
    assert any(b.type == "coverage" for b in report.blockers)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_evaluate_scope_blocked_by_staging_empty(gate):
    mock_session = AsyncMock()

    res_seeded = MagicMock()
    res_seeded.scalars.return_value.all.return_value = []

    res_artifacts = MagicMock()
    res_artifacts.scalars.return_value.all.return_value = []

    mock_session.execute.side_effect = [res_seeded, res_artifacts]

    report = await gate.evaluate_scope(mock_session, "scope-123", layers=[ContentLayer.LESSONS])

    assert report.status == ProductionGateStatus.BLOCKED_BY_STAGING
    assert "No staged artifacts found" in report.blockers[0].message


@pytest.mark.asyncio
@pytest.mark.unit
async def test_evaluate_scope_staging_missing_and_non_active_artifact(gate):
    mock_session = AsyncMock()

    art_id1 = uuid.uuid4()
    art_id2 = uuid.uuid4()
    item1 = MagicMock(spec=ContentStagingSeedItem, artifact_id=art_id1, caps_ref="MATH.4.1")
    item2 = MagicMock(spec=ContentStagingSeedItem, artifact_id=art_id2, caps_ref="MATH.4.2")

    res_seeded = MagicMock()
    res_seeded.scalars.return_value.all.return_value = [item1, item2]

    # item1 has no staging artifact
    res_staging_art1 = MagicMock()
    res_staging_art1.scalar_one_or_none.return_value = None

    # item2 has non-active staging artifact
    staging_art2 = MagicMock(spec=ContentStagingArtifact, artifact_id=art_id2, staging_status="archived")
    res_staging_art2 = MagicMock()
    res_staging_art2.scalar_one_or_none.return_value = staging_art2

    res_artifacts = MagicMock()
    res_artifacts.scalars.return_value.all.return_value = []

    mock_session.execute.side_effect = [
        res_seeded,
        res_staging_art1,
        res_staging_art2,
        res_artifacts,
    ]

    report = await gate.evaluate_scope(mock_session, "scope-123", layers=[ContentLayer.LESSONS])

    assert report.status == ProductionGateStatus.BLOCKED_BY_STAGING
    assert len(report.blockers) == 2
    assert "missing" in report.blockers[0].message
    assert "archived" in report.blockers[1].message


@pytest.mark.asyncio
@pytest.mark.unit
async def test_evaluate_scope_blocked_by_review_unapproved_artifact(gate):
    mock_session = AsyncMock()

    artifact_id = uuid.uuid4()
    item = MagicMock(spec=ContentStagingSeedItem, artifact_id=artifact_id, caps_ref="MATH.4.1")
    staging_art = MagicMock(spec=ContentStagingArtifact, artifact_id=artifact_id, staging_status="active")

    # Artifact is in draft status
    art = MagicMock(spec=ContentGenerationArtifact, artifact_id=artifact_id, status=ContentArtifactStatus.DRAFT, caps_ref="MATH.4.1")

    res_seeded = MagicMock()
    res_seeded.scalars.return_value.all.return_value = [item]

    res_staging_art = MagicMock()
    res_staging_art.scalar_one_or_none.return_value = staging_art

    res_artifacts = MagicMock()
    res_artifacts.scalars.return_value.all.return_value = [art]

    mock_session.execute.side_effect = [res_seeded, res_staging_art, res_artifacts]

    report = await gate.evaluate_scope(mock_session, "scope-123", layers=[ContentLayer.LESSONS])

    assert report.status == ProductionGateStatus.BLOCKED_BY_REVIEW
    assert "draft" in report.blockers[0].message


@pytest.mark.asyncio
@pytest.mark.unit
async def test_evaluate_scope_blocked_by_provenance(gate):
    mock_session = AsyncMock()

    artifact_id = uuid.uuid4()
    item = MagicMock(spec=ContentStagingSeedItem, artifact_id=artifact_id, caps_ref="MATH.4.1")
    staging_art = MagicMock(spec=ContentStagingArtifact, artifact_id=artifact_id, staging_status="active")
    art = MagicMock(spec=ContentGenerationArtifact, artifact_id=artifact_id, status=ContentArtifactStatus.APPROVED, caps_ref="MATH.4.1")

    res_seeded = MagicMock()
    res_seeded.scalars.return_value.all.return_value = [item]

    res_staging_art = MagicMock()
    res_staging_art.scalar_one_or_none.return_value = staging_art

    res_artifacts = MagicMock()
    res_artifacts.scalars.return_value.all.return_value = [art]

    # No source evidence
    res_source = MagicMock()
    res_source.scalars.return_value.first.return_value = None

    mock_session.execute.side_effect = [res_seeded, res_staging_art, res_artifacts, res_source]

    report = await gate.evaluate_scope(mock_session, "scope-123", layers=[ContentLayer.LESSONS])

    assert report.status == ProductionGateStatus.BLOCKED_BY_PROVENANCE
    assert "no source citation" in report.blockers[0].message


@pytest.mark.asyncio
@pytest.mark.unit
async def test_evaluate_scope_blocked_by_review_no_approval_record(gate):
    mock_session = AsyncMock()

    artifact_id = uuid.uuid4()
    item = MagicMock(spec=ContentStagingSeedItem, artifact_id=artifact_id, caps_ref="MATH.4.1")
    staging_art = MagicMock(spec=ContentStagingArtifact, artifact_id=artifact_id, staging_status="active")
    art = MagicMock(spec=ContentGenerationArtifact, artifact_id=artifact_id, status=ContentArtifactStatus.APPROVED, caps_ref="MATH.4.1")
    source = MagicMock(spec=ContentArtifactSource)

    res_seeded = MagicMock()
    res_seeded.scalars.return_value.all.return_value = [item]

    res_staging_art = MagicMock()
    res_staging_art.scalar_one_or_none.return_value = staging_art

    res_artifacts = MagicMock()
    res_artifacts.scalars.return_value.all.return_value = [art]

    res_source = MagicMock()
    res_source.scalars.return_value.first.return_value = source

    # No review record
    res_review = MagicMock()
    res_review.scalars.return_value.first.return_value = None

    mock_session.execute.side_effect = [res_seeded, res_staging_art, res_artifacts, res_source, res_review]

    report = await gate.evaluate_scope(mock_session, "scope-123", layers=[ContentLayer.LESSONS])

    assert report.status == ProductionGateStatus.BLOCKED_BY_REVIEW
    assert "no approval review" in report.blockers[0].message


@pytest.mark.asyncio
@pytest.mark.unit
async def test_evaluate_scope_blocked_by_validation_missing_or_failed(gate):
    mock_session = AsyncMock()

    artifact_id = uuid.uuid4()
    item = MagicMock(spec=ContentStagingSeedItem, artifact_id=artifact_id, caps_ref="MATH.4.1")
    staging_art = MagicMock(spec=ContentStagingArtifact, artifact_id=artifact_id, staging_status="active")
    art = MagicMock(spec=ContentGenerationArtifact, artifact_id=artifact_id, status=ContentArtifactStatus.APPROVED, caps_ref="MATH.4.1")
    source = MagicMock(spec=ContentArtifactSource)
    review = MagicMock(spec=ContentArtifactReview)

    # Missing validation report
    mock_session.execute.side_effect = [
        MagicMock(scalars=lambda: MagicMock(all=lambda: [item])),
        MagicMock(scalar_one_or_none=lambda: staging_art),
        MagicMock(scalars=lambda: MagicMock(all=lambda: [art])),
        MagicMock(scalars=lambda: MagicMock(first=lambda: source)),
        MagicMock(scalars=lambda: MagicMock(first=lambda: review)),
        MagicMock(scalar_one_or_none=lambda: None),
    ]

    report = await gate.evaluate_scope(mock_session, "scope-123", layers=[ContentLayer.LESSONS])
    assert report.status == ProductionGateStatus.BLOCKED_BY_VALIDATION
    assert "No validation report" in report.blockers[0].message

    # Failed validation report
    val_report_failed = MagicMock(spec=ContentValidationReport, passed=False)
    mock_session.execute.side_effect = [
        MagicMock(scalars=lambda: MagicMock(all=lambda: [item])),
        MagicMock(scalar_one_or_none=lambda: staging_art),
        MagicMock(scalars=lambda: MagicMock(all=lambda: [art])),
        MagicMock(scalars=lambda: MagicMock(first=lambda: source)),
        MagicMock(scalars=lambda: MagicMock(first=lambda: review)),
        MagicMock(scalar_one_or_none=lambda: val_report_failed),
    ]

    report2 = await gate.evaluate_scope(mock_session, "scope-123", layers=[ContentLayer.LESSONS])
    assert report2.status == ProductionGateStatus.BLOCKED_BY_VALIDATION
    assert "not clean" in report2.blockers[0].message


# ---------------------------------------------------------------------------
# Additional Blocker Types (Source Quality, License, Configuration)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_evaluate_scope_other_blocker_types(gate):
    mock_session = AsyncMock()

    # Direct test of blocker type resolution logic via patched internal method
    gate._check_coverage = AsyncMock(return_value={})
    gate._check_staging_verification = AsyncMock(return_value={})

    async def inject_source_quality(session, scope_id, layers, blockers):
        blockers.append(ProductionGateBlocker(type="source_quality", message="poor quality"))

    gate._check_artifact_status = inject_source_quality
    report = await gate.evaluate_scope(mock_session, "scope-1")
    assert report.status == ProductionGateStatus.BLOCKED_BY_SOURCE_QUALITY

    async def inject_license(session, scope_id, layers, blockers):
        blockers.append(ProductionGateBlocker(type="license", message="unlicensed"))

    gate._check_artifact_status = inject_license
    report = await gate.evaluate_scope(mock_session, "scope-1")
    assert report.status == ProductionGateStatus.BLOCKED_BY_LICENSE

    async def inject_config(session, scope_id, layers, blockers):
        blockers.append(ProductionGateBlocker(type="unknown_custom", message="bad config"))

    gate._check_artifact_status = inject_config
    report = await gate.evaluate_scope(mock_session, "scope-1")
    assert report.status == ProductionGateStatus.BLOCKED_BY_CONFIGURATION


# ---------------------------------------------------------------------------
# assert_promotable
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_assert_promotable_success(gate):
    mock_session = AsyncMock()
    promotable_report = ProductionGateReport(
        scope_id="scope-123",
        status=ProductionGateStatus.PROMOTABLE,
    )
    gate.evaluate_scope = AsyncMock(return_value=promotable_report)

    # Should not raise
    await gate.assert_promotable(mock_session, "scope-123")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_assert_promotable_raises_value_error(gate):
    mock_session = AsyncMock()
    blocked_report = ProductionGateReport(
        scope_id="scope-123",
        status=ProductionGateStatus.BLOCKED_BY_REVIEW,
        blockers=[
            ProductionGateBlocker(type="review", message="Draft artifact pending review"),
        ],
    )
    gate.evaluate_scope = AsyncMock(return_value=blocked_report)

    with pytest.raises(ValueError, match="Production promotion gate failed for scope scope-123"):
        await gate.assert_promotable(mock_session, "scope-123")
