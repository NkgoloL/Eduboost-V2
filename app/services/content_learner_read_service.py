"""Learner production read service.

This service provides learner-facing read access to production-promoted
Content Factory artifacts only. It enforces the production gate rules:
- Learners see production only
- Admins may preview staging (separate service)
- No learner may see draft, generated, pending_review, rejected, quarantined,
  validation_failed, or staging-only content
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import (
    ContentArtifactStatus,
    ContentGenerationArtifact,
    ContentProductionArtifact,
)
from app.services.content_scope_registry import ContentScopeRegistry


@dataclass
class LearnerDiagnosticItem:
    """Learner-facing diagnostic item."""

    artifact_id: str
    scope_id: str
    caps_ref: str | None
    grade: int | None
    subject_code: str | None
    language: str
    title: str | None
    payload: dict[str, Any]
    source_artifact_hash: str
    promotion_event_id: str | None
    created_at: str


@dataclass
class LearnerLesson:
    """Learner-facing lesson."""

    artifact_id: str
    scope_id: str
    caps_ref: str | None
    grade: int | None
    subject_code: str | None
    language: str
    title: str | None
    payload: dict[str, Any]
    source_artifact_hash: str
    promotion_event_id: str | None
    created_at: str


@dataclass
class LearnerScopeContentSummary:
    """Summary of learner-visible content for a scope."""

    scope_id: str
    diagnostic_items_count: int
    lessons_count: int
    total_artifacts_count: int
    last_promotion_at: str | None


class LearnerReadMode(str):
    """Learner read mode configuration."""

    PRODUCTION_ONLY = "production_only"
    PRODUCTION_WITH_LEGACY_FALLBACK = "production_with_legacy_fallback"
    LEGACY_ONLY = "legacy_only"


class ContentLearnerReadService:
    """Service for learner-facing production content reads."""

    def __init__(self, scope_registry: ContentScopeRegistry | None = None) -> None:
        self._read_mode = os.getenv(
            "CONTENT_LEARNER_READ_MODE",
            LearnerReadMode.PRODUCTION_ONLY,
        )
        self._scope_registry = scope_registry or ContentScopeRegistry()

    def _require_learner_visible_scope(self, scope_id: str) -> None:
        self._scope_registry.require_active_scope(scope_id)

    def is_learner_visible_artifact(
        self,
        generation_artifact: ContentGenerationArtifact,
        production_artifact: ContentProductionArtifact | None,
    ) -> bool:
        """Check if an artifact is visible to learners.

        Learner-visible content must satisfy:
        - production_status == "active"
        - artifact.status == "promoted_production"
        - artifact not quarantined
        - artifact not rejected
        - artifact not retired
        - latest validation report is clean (if applicable)
        - provenance exists and is valid
        """
        # Must have an active production artifact
        if not production_artifact:
            return False

        if production_artifact.production_status != "active":
            return False

        # Generation artifact must be promoted to production
        if generation_artifact.status != ContentArtifactStatus.PROMOTED_PRODUCTION:
            return False

        # Must not be quarantined, rejected, or retired
        if generation_artifact.status in (
            ContentArtifactStatus.QUARANTINED,
            ContentArtifactStatus.REJECTED,
            ContentArtifactStatus.RETIRED,
        ):
            return False

        # Must not be validation failed
        if generation_artifact.status == ContentArtifactStatus.VALIDATION_FAILED:
            return False

        # Check if artifact has sources (provenance)
        # Use getattr with a default to handle cases where relationship isn't loaded
        sources = getattr(generation_artifact, "sources", None)
        if sources is None or len(sources) == 0:
            return False

        return True

    async def get_diagnostic_items(
        self,
        session: AsyncSession,
        *,
        scope_id: str,
        caps_ref: str | None = None,
        limit: int = 20,
    ) -> list[LearnerDiagnosticItem]:
        """Get learner-visible diagnostic items for a scope.

        Args:
            session: Database session
            scope_id: Content scope ID
            caps_ref: Optional CAPS reference filter
            limit: Maximum number of items to return

        Returns:
            List of learner-visible diagnostic items
        """
        from app.models.content_factory import ContentLayer

        self._require_learner_visible_scope(scope_id)

        # Query production artifacts for diagnostic items
        query = (
            select(ContentProductionArtifact, ContentGenerationArtifact)
            .join(
                ContentGenerationArtifact,
                ContentProductionArtifact.artifact_id == ContentGenerationArtifact.artifact_id,
            )
            .where(
                ContentProductionArtifact.scope_id == scope_id,
                ContentProductionArtifact.layer == ContentLayer.DIAGNOSTIC_ITEMS.value,
                ContentProductionArtifact.production_status == "active",
            )
        )

        if caps_ref:
            query = query.where(ContentProductionArtifact.caps_ref == caps_ref)

        query = query.limit(limit)

        result = await session.execute(query)
        items = []

        for production_artifact, generation_artifact in result:
            if not self.is_learner_visible_artifact(generation_artifact, production_artifact):
                continue

            items.append(
                LearnerDiagnosticItem(
                    artifact_id=str(generation_artifact.artifact_id),
                    scope_id=production_artifact.scope_id,
                    caps_ref=production_artifact.caps_ref,
                    grade=generation_artifact.grade,
                    subject_code=generation_artifact.subject_code,
                    language=generation_artifact.language or "en",
                    title=generation_artifact.title,
                    payload=production_artifact.payload_json,
                    source_artifact_hash=production_artifact.source_artifact_hash,
                    promotion_event_id=str(production_artifact.created_by_promotion_event_id)
                    if production_artifact.created_by_promotion_event_id
                    else None,
                    created_at=production_artifact.created_at.isoformat(),
                )
            )

        # Fallback to legacy content if configured and no production content found
        if not items and self._read_mode == LearnerReadMode.PRODUCTION_WITH_LEGACY_FALLBACK:
            items = await self._get_legacy_diagnostic_items(
                session,
                scope_id=scope_id,
                caps_ref=caps_ref,
                limit=limit,
            )

        return items

    async def get_lessons(
        self,
        session: AsyncSession,
        *,
        scope_id: str,
        caps_ref: str | None = None,
        limit: int = 20,
    ) -> list[LearnerLesson]:
        """Get learner-visible lessons for a scope.

        Args:
            session: Database session
            scope_id: Content scope ID
            caps_ref: Optional CAPS reference filter
            limit: Maximum number of items to return

        Returns:
            List of learner-visible lessons
        """
        from app.models.content_factory import ContentLayer

        self._require_learner_visible_scope(scope_id)

        # Query production artifacts for lessons
        query = (
            select(ContentProductionArtifact, ContentGenerationArtifact)
            .join(
                ContentGenerationArtifact,
                ContentProductionArtifact.artifact_id == ContentGenerationArtifact.artifact_id,
            )
            .where(
                ContentProductionArtifact.scope_id == scope_id,
                ContentProductionArtifact.layer == ContentLayer.LESSONS.value,
                ContentProductionArtifact.production_status == "active",
            )
        )

        if caps_ref:
            query = query.where(ContentProductionArtifact.caps_ref == caps_ref)

        query = query.limit(limit)

        result = await session.execute(query)
        items = []

        for production_artifact, generation_artifact in result:
            if not self.is_learner_visible_artifact(generation_artifact, production_artifact):
                continue

            items.append(
                LearnerLesson(
                    artifact_id=str(generation_artifact.artifact_id),
                    scope_id=production_artifact.scope_id,
                    caps_ref=production_artifact.caps_ref,
                    grade=generation_artifact.grade,
                    subject_code=generation_artifact.subject_code,
                    language=generation_artifact.language or "en",
                    title=generation_artifact.title,
                    payload=production_artifact.payload_json,
                    source_artifact_hash=production_artifact.source_artifact_hash,
                    promotion_event_id=str(production_artifact.created_by_promotion_event_id)
                    if production_artifact.created_by_promotion_event_id
                    else None,
                    created_at=production_artifact.created_at.isoformat(),
                )
            )

        # Fallback to legacy content if configured and no production content found
        if not items and self._read_mode == LearnerReadMode.PRODUCTION_WITH_LEGACY_FALLBACK:
            items = await self._get_legacy_lessons(
                session,
                scope_id=scope_id,
                caps_ref=caps_ref,
                limit=limit,
            )

        return items

    async def get_scope_content_summary(
        self,
        session: AsyncSession,
        scope_id: str,
    ) -> LearnerScopeContentSummary:
        """Get summary of learner-visible content for a scope.

        Args:
            session: Database session
            scope_id: Content scope ID

        Returns:
            Summary of learner-visible content
        """
        from app.models.content_factory import ContentLayer
        from sqlalchemy import func

        self._require_learner_visible_scope(scope_id)

        # Count production artifacts by layer
        diagnostic_count_query = (
            select(func.count())
            .select_from(ContentProductionArtifact)
            .join(
                ContentGenerationArtifact,
                ContentProductionArtifact.artifact_id == ContentGenerationArtifact.artifact_id,
            )
            .where(
                ContentProductionArtifact.scope_id == scope_id,
                ContentProductionArtifact.layer == ContentLayer.DIAGNOSTIC_ITEMS.value,
                ContentProductionArtifact.production_status == "active",
                ContentGenerationArtifact.status == ContentArtifactStatus.PROMOTED_PRODUCTION,
            )
        )

        lessons_count_query = (
            select(func.count())
            .select_from(ContentProductionArtifact)
            .join(
                ContentGenerationArtifact,
                ContentProductionArtifact.artifact_id == ContentGenerationArtifact.artifact_id,
            )
            .where(
                ContentProductionArtifact.scope_id == scope_id,
                ContentProductionArtifact.layer == ContentLayer.LESSONS.value,
                ContentProductionArtifact.production_status == "active",
                ContentGenerationArtifact.status == ContentArtifactStatus.PROMOTED_PRODUCTION,
            )
        )

        total_count_query = (
            select(func.count())
            .select_from(ContentProductionArtifact)
            .join(
                ContentGenerationArtifact,
                ContentProductionArtifact.artifact_id == ContentGenerationArtifact.artifact_id,
            )
            .where(
                ContentProductionArtifact.scope_id == scope_id,
                ContentProductionArtifact.production_status == "active",
                ContentGenerationArtifact.status == ContentArtifactStatus.PROMOTED_PRODUCTION,
            )
        )

        # Get last promotion timestamp
        last_promotion_query = (
            select(func.max(ContentProductionArtifact.created_at))
            .select_from(ContentProductionArtifact)
            .where(ContentProductionArtifact.scope_id == scope_id)
        )

        diagnostic_count = await session.scalar(diagnostic_count_query) or 0
        lessons_count = await session.scalar(lessons_count_query) or 0
        total_count = await session.scalar(total_count_query) or 0
        last_promotion_at = await session.scalar(last_promotion_query)

        return LearnerScopeContentSummary(
            scope_id=scope_id,
            diagnostic_items_count=diagnostic_count,
            lessons_count=lessons_count,
            total_artifacts_count=total_count,
            last_promotion_at=last_promotion_at.isoformat() if last_promotion_at else None,
        )

    async def _get_legacy_diagnostic_items(
        self,
        session: AsyncSession,
        *,
        scope_id: str,
        caps_ref: str | None = None,
        limit: int = 20,
    ) -> list[LearnerDiagnosticItem]:
        """Get legacy diagnostic items as fallback.

        This method should be implemented to query the legacy launch content
        tables when production content is not available.
        """
        # Legacy fallback is intentionally unsupported until repository-backed fallback is implemented
        return []

    async def _get_legacy_lessons(
        self,
        session: AsyncSession,
        *,
        scope_id: str,
        caps_ref: str | None = None,
        limit: int = 20,
    ) -> list[LearnerLesson]:
        """Get legacy lessons as fallback.

        This method should be implemented to query the legacy launch content
        tables when production content is not available.
        """
        # Legacy fallback is intentionally unsupported until repository-backed fallback is implemented
        return []
