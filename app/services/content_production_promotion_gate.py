"""Production promotion gate for Content Factory artifacts."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.services.content_coverage_service import ContentCoverageService


class ProductionGateStatus(str, Enum):
    PROMOTABLE = "promotable"
    BLOCKED_BY_COVERAGE = "blocked_by_coverage"
    BLOCKED_BY_REVIEW = "blocked_by_review"
    BLOCKED_BY_VALIDATION = "blocked_by_validation"
    BLOCKED_BY_PROVENANCE = "blocked_by_provenance"
    BLOCKED_BY_STAGING = "blocked_by_staging"
    BLOCKED_BY_SOURCE_QUALITY = "blocked_by_source_quality"
    BLOCKED_BY_LICENSE = "blocked_by_license"
    BLOCKED_BY_CONFIGURATION = "blocked_by_configuration"


@dataclass(frozen=True)
class ProductionGateBlocker:
    type: str
    message: str
    artifact_id: uuid.UUID | None = None
    caps_ref: str | None = None


@dataclass(frozen=True)
class ProductionGateReport:
    scope_id: str
    status: ProductionGateStatus
    blockers: list[ProductionGateBlocker] = field(default_factory=list)
    coverage_summary: dict[str, Any] = field(default_factory=dict)
    staging_summary: dict[str, Any] = field(default_factory=dict)


class ContentProductionPromotionGate:
    def __init__(
        self,
        coverage_service: ContentCoverageService,
    ) -> None:
        self.coverage_service = coverage_service

    async def evaluate_scope(
        self,
        session: AsyncSession,
        scope_id: str,
        *,
        layers: list[ContentLayer] | None = None,
    ) -> ProductionGateReport:
        """Evaluate a scope for production eligibility."""
        layers = [ContentLayer(layer) for layer in (layers or list(ContentLayer))]
        blockers: list[ProductionGateBlocker] = []

        # Check coverage
        coverage_summary = await self._check_coverage(session, scope_id, layers, blockers)

        # Check staging verification
        staging_summary = await self._check_staging_verification(session, scope_id, layers, blockers)

        # Check artifact status and validation
        await self._check_artifact_status(session, scope_id, layers, blockers)

        # Determine overall status
        if blockers:
            # Determine primary blocker type
            blocker_types = {b.type for b in blockers}
            if "coverage" in blocker_types:
                status = ProductionGateStatus.BLOCKED_BY_COVERAGE
            elif "review" in blocker_types:
                status = ProductionGateStatus.BLOCKED_BY_REVIEW
            elif "validation" in blocker_types:
                status = ProductionGateStatus.BLOCKED_BY_VALIDATION
            elif "provenance" in blocker_types:
                status = ProductionGateStatus.BLOCKED_BY_PROVENANCE
            elif "staging" in blocker_types:
                status = ProductionGateStatus.BLOCKED_BY_STAGING
            elif "source_quality" in blocker_types:
                status = ProductionGateStatus.BLOCKED_BY_SOURCE_QUALITY
            elif "license" in blocker_types:
                status = ProductionGateStatus.BLOCKED_BY_LICENSE
            else:
                status = ProductionGateStatus.BLOCKED_BY_CONFIGURATION
        else:
            status = ProductionGateStatus.PROMOTABLE

        return ProductionGateReport(
            scope_id=scope_id,
            status=status,
            blockers=blockers,
            coverage_summary=coverage_summary,
            staging_summary=staging_summary,
        )

    async def assert_promotable(
        self,
        session: AsyncSession,
        scope_id: str,
        *,
        layers: list[ContentLayer] | None = None,
    ) -> None:
        """Assert that a scope is promotable, raising an error if not."""
        report = await self.evaluate_scope(session, scope_id, layers=layers)
        if report.status != ProductionGateStatus.PROMOTABLE:
            error_messages = [b.message for b in report.blockers]
            raise ValueError(
                f"Production promotion gate failed for scope {scope_id}: "
                f"{report.status.value}. "
                + "; ".join(error_messages)
            )

    async def _check_coverage(
        self,
        session: AsyncSession,
        scope_id: str,
        layers: list[ContentLayer],
        blockers: list[ProductionGateBlocker],
    ) -> dict[str, Any]:
        """Check that coverage targets are green."""
        summary = {}

        for layer in layers:
            coverage = await self.coverage_service.get_coverage(session, scope_id, layer)
            layer_name = layer.value if isinstance(layer, ContentLayer) else layer

            if coverage.status != CoverageLayerStatus.GREEN:
                blockers.append(
                    ProductionGateBlocker(
                        type="coverage",
                        message=f"Coverage for layer {layer_name} is {coverage.status.value}, not GREEN",
                    )
                )

            summary[layer_name] = {
                "status": coverage.status.value,
                "coverage_percentage": coverage.coverage_percentage,
                "target_percentage": coverage.target_percentage,
            }

        return summary

    async def _check_staging_verification(
        self,
        session: AsyncSession,
        scope_id: str,
        layers: list[ContentLayer],
        blockers: list[ProductionGateBlocker],
    ) -> dict[str, Any]:
        """Check that staging seed exists and passed read verification."""
        summary = {}

        # Find the latest successful staging seed run for this scope
        result = await session.execute(
            select(ContentStagingSeedItem)
            .join(ContentStagingArtifact, ContentStagingSeedItem.artifact_id == ContentStagingArtifact.artifact_id)
            .where(
                ContentStagingSeedItem.scope_id == scope_id,
                ContentStagingSeedItem.status == "seeded",
            )
        )

        seeded_items = result.scalars().all()

        if not seeded_items:
            blockers.append(
                ProductionGateBlocker(
                    type="staging",
                    message=f"No staged artifacts found for scope {scope_id}",
                )
            )
            return summary

        # Check that staging artifacts are in active state
        for item in seeded_items:
            staging_artifact = await session.execute(
                select(ContentStagingArtifact).where(
                    ContentStagingArtifact.artifact_id == item.artifact_id,
                )
            )
            artifact = staging_artifact.scalar_one_or_none()

            if not artifact:
                blockers.append(
                    ProductionGateBlocker(
                        type="staging",
                        message=f"Staging artifact missing for artifact {item.artifact_id}",
                        artifact_id=item.artifact_id,
                        caps_ref=item.caps_ref,
                    )
                )
                continue

            if artifact.staging_status != "active":
                blockers.append(
                    ProductionGateBlocker(
                        type="staging",
                        message=f"Staging artifact status is {artifact.staging_status}, not active",
                        artifact_id=item.artifact_id,
                        caps_ref=item.caps_ref,
                    )
                )

        summary = {
            "seeded_count": len(seeded_items),
            "scope_id": scope_id,
        }

        return summary

    async def _check_artifact_status(
        self,
        session: AsyncSession,
        scope_id: str,
        layers: list[ContentLayer],
        blockers: list[ProductionGateBlocker],
    ) -> None:
        """Check that all production-bound artifacts are approved and valid."""
        # Get all artifacts for the scope
        layer_values = [layer.value for layer in layers]
        result = await session.execute(
            select(ContentGenerationArtifact).where(
                ContentGenerationArtifact.scope_id == scope_id,
                ContentGenerationArtifact.content_layer.in_(layer_values),
            )
        )

        artifacts = result.scalars().all()

        for artifact in artifacts:
            # Check artifact status
            if artifact.status != ContentArtifactStatus.APPROVED:
                blockers.append(
                    ProductionGateBlocker(
                        type="review",
                        message=f"Artifact status is {artifact.status.value}, not approved",
                        artifact_id=artifact.artifact_id,
                        caps_ref=artifact.caps_ref,
                    )
                )
                continue

            # Check provenance evidence
            source_count_result = await session.execute(
                select(ContentArtifactSource).where(
                    ContentArtifactSource.artifact_id == artifact.artifact_id,
                )
            )
            if not source_count_result.scalars().first():
                blockers.append(
                    ProductionGateBlocker(
                        type="provenance",
                        message="Artifact has no source citation evidence",
                        artifact_id=artifact.artifact_id,
                        caps_ref=artifact.caps_ref,
                    )
                )
                continue

            review_result = await session.execute(
                select(ContentArtifactReview).where(
                    ContentArtifactReview.artifact_id == artifact.artifact_id,
                    ContentArtifactReview.review_action == ContentReviewAction.APPROVE,
                )
            )
            if not review_result.scalars().first():
                blockers.append(
                    ProductionGateBlocker(
                        type="review",
                        message="Artifact has no approval review evidence",
                        artifact_id=artifact.artifact_id,
                        caps_ref=artifact.caps_ref,
                    )
                )
                continue

            # Check validation report
            validation_result = await session.execute(
                select(ContentValidationReport).where(
                    ContentValidationReport.artifact_id == artifact.artifact_id,
                )
            )
            validation_report = validation_result.scalar_one_or_none()

            if not validation_report:
                blockers.append(
                    ProductionGateBlocker(
                        type="validation",
                        message="No validation report found for artifact",
                        artifact_id=artifact.artifact_id,
                        caps_ref=artifact.caps_ref,
                    )
                )
                continue

            if not validation_report.passed:
                blockers.append(
                    ProductionGateBlocker(
                        type="validation",
                        message="Validation report is not clean",
                        artifact_id=artifact.artifact_id,
                        caps_ref=artifact.caps_ref,
                    )
                )
