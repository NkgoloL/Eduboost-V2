"""Admin staging preview service.

This service provides admin-only preview access to staging artifacts.
It shows seed run provenance, staging verification state, and clearly labels
content as not learner-visible.

Core rule:
- Admins may preview staging
- Never expose through learner routes
- Clearly mark learner_visible=false
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import (
    ContentGenerationArtifact,
    ContentStagingArtifact,
)


@dataclass
class StagingArtifactPreview:
    """Preview of a staging artifact."""

    artifact_id: str
    scope_id: str
    caps_ref: str | None
    layer: str
    artifact_type: str
    staging_status: str
    learner_visible: bool
    seed_run_id: str | None
    seed_run_status: str | None
    verification_passed: bool | None
    payload: dict[str, Any]
    source_artifact_hash: str
    created_at: str


@dataclass
class StagingPreviewReport:
    """Report of staging preview for a scope."""

    scope_id: str
    layers: list[str]
    total_artifacts_count: int
    active_artifacts_count: int
    pending_artifacts_count: int
    learner_visible_count: int
    artifacts: list[StagingArtifactPreview]


@dataclass
class StagingCapsRefPreview:
    """Preview of staging artifacts for a specific CAPS reference."""

    scope_id: str
    caps_ref: str
    layers: list[str]
    total_artifacts_count: int
    active_artifacts_count: int
    learner_visible_count: int
    artifacts: list[StagingArtifactPreview]


class ContentStagingPreviewService:
    """Service for admin-only staging preview."""

    async def preview_scope(
        self,
        session: AsyncSession,
        scope_id: str,
        *,
        layers: list[str] | None = None,
    ) -> StagingPreviewReport:
        """Preview staging artifacts for a scope.

        Args:
            session: Database session
            scope_id: Content scope ID
            layers: Optional layer filter

        Returns:
            Staging preview report
        """
        # Query staging artifacts
        query = select(ContentStagingArtifact, ContentGenerationArtifact).join(
            ContentGenerationArtifact,
            ContentStagingArtifact.artifact_id == ContentGenerationArtifact.artifact_id,
        ).where(ContentStagingArtifact.scope_id == scope_id)

        if layers:
            query = query.where(ContentStagingArtifact.layer.in_(layers))

        result = await session.execute(query)
        artifacts = []

        active_count = 0
        pending_count = 0
        learner_visible_count = 0
        unique_layers = set()

        for staging_artifact, generation_artifact in result:
            unique_layers.add(staging_artifact.layer)

            # Get seed run info
            seed_run_id = staging_artifact.created_by_seed_run_id
            seed_run_status = None
            verification_passed = None

            if seed_run_id:
                seed_run_status = await self._get_seed_run_status(session, seed_run_id)
                verification_passed = await self._get_staging_verification_status(
                    session, seed_run_id
                )

            # Staging artifacts are never learner-visible
            learner_visible = False

            if staging_artifact.staging_status == "active":
                active_count += 1
            elif staging_artifact.staging_status == "pending":
                pending_count += 1

            artifacts.append(
                StagingArtifactPreview(
                    artifact_id=str(generation_artifact.artifact_id),
                    scope_id=staging_artifact.scope_id,
                    caps_ref=staging_artifact.caps_ref,
                    layer=staging_artifact.layer,
                    artifact_type=staging_artifact.artifact_type,
                    staging_status=staging_artifact.staging_status,
                    learner_visible=learner_visible,
                    seed_run_id=str(seed_run_id) if seed_run_id else None,
                    seed_run_status=seed_run_status,
                    verification_passed=verification_passed,
                    payload=staging_artifact.payload_json,
                    source_artifact_hash=staging_artifact.source_artifact_hash,
                    created_at=staging_artifact.created_at.isoformat(),
                )
            )

        return StagingPreviewReport(
            scope_id=scope_id,
            layers=list(unique_layers),
            total_artifacts_count=len(artifacts),
            active_artifacts_count=active_count,
            pending_artifacts_count=pending_count,
            learner_visible_count=learner_visible_count,
            artifacts=artifacts,
        )

    async def preview_caps_ref(
        self,
        session: AsyncSession,
        scope_id: str,
        caps_ref: str,
        *,
        layers: list[str] | None = None,
    ) -> StagingCapsRefPreview:
        """Preview staging artifacts for a specific CAPS reference.

        Args:
            session: Database session
            scope_id: Content scope ID
            caps_ref: CAPS reference
            layers: Optional layer filter

        Returns:
            Staging CAPS reference preview
        """
        # Query staging artifacts for CAPS ref
        query = (
            select(ContentStagingArtifact, ContentGenerationArtifact)
            .join(
                ContentGenerationArtifact,
                ContentStagingArtifact.artifact_id == ContentGenerationArtifact.artifact_id,
            )
            .where(
                ContentStagingArtifact.scope_id == scope_id,
                ContentStagingArtifact.caps_ref == caps_ref,
            )
        )

        if layers:
            query = query.where(ContentStagingArtifact.layer.in_(layers))

        result = await session.execute(query)
        artifacts = []

        active_count = 0
        unique_layers = set()

        for staging_artifact, generation_artifact in result:
            unique_layers.add(staging_artifact.layer)

            # Get seed run info
            seed_run_id = staging_artifact.created_by_seed_run_id
            seed_run_status = None
            verification_passed = None

            if seed_run_id:
                seed_run_status = await self._get_seed_run_status(session, seed_run_id)
                verification_passed = await self._get_staging_verification_status(
                    session, seed_run_id
                )

            # Staging artifacts are never learner-visible
            learner_visible = False

            if staging_artifact.staging_status == "active":
                active_count += 1

            artifacts.append(
                StagingArtifactPreview(
                    artifact_id=str(generation_artifact.artifact_id),
                    scope_id=staging_artifact.scope_id,
                    caps_ref=staging_artifact.caps_ref,
                    layer=staging_artifact.layer,
                    artifact_type=staging_artifact.artifact_type,
                    staging_status=staging_artifact.staging_status,
                    learner_visible=learner_visible,
                    seed_run_id=str(seed_run_id) if seed_run_id else None,
                    seed_run_status=seed_run_status,
                    verification_passed=verification_passed,
                    payload=staging_artifact.payload_json,
                    source_artifact_hash=staging_artifact.source_artifact_hash,
                    created_at=staging_artifact.created_at.isoformat(),
                )
            )

        return StagingCapsRefPreview(
            scope_id=scope_id,
            caps_ref=caps_ref,
            layers=list(unique_layers),
            total_artifacts_count=len(artifacts),
            active_artifacts_count=active_count,
            learner_visible_count=0,  # Staging is never learner-visible
            artifacts=artifacts,
        )

    async def _get_seed_run_status(
        self, session: AsyncSession, seed_run_id: str
    ) -> str | None:
        """Get the status of a seed run.

        Args:
            session: Database session
            seed_run_id: Seed run ID

        Returns:
            Seed run status or None
        """
        from app.models.content_factory import ContentSeedRun

        query = select(ContentSeedRun.status).where(
            ContentSeedRun.run_id == seed_run_id
        )
        return await session.scalar(query)

    async def _get_staging_verification_status(
        self, session: AsyncSession, seed_run_id: str
    ) -> bool | None:
        """Get the staging verification status for a seed run.

        Args:
            session: Database session
            seed_run_id: Seed run ID

        Returns:
            Verification status or None
        """
        from app.models.content_factory import ContentStagingVerification

        query = select(ContentStagingVerification.passed).where(
            ContentStagingVerification.seed_run_id == seed_run_id
        )
        return await session.scalar(query)
