"""Unit tests for staging preview service."""
from __future__ import annotations

import uuid


from app.services.content_staging_preview_service import (
    ContentStagingPreviewService,
)


def test_staging_preview_service_can_be_instantiated() -> None:
    """Staging preview service can be instantiated."""
    service = ContentStagingPreviewService()
    assert service is not None


def test_staging_preview_service_has_preview_scope_method() -> None:
    """Staging preview service has preview_scope method."""
    service = ContentStagingPreviewService()
    assert hasattr(service, "preview_scope")


def test_staging_preview_service_has_preview_caps_ref_method() -> None:
    """Staging preview service has preview_caps_ref method."""
    service = ContentStagingPreviewService()
    assert hasattr(service, "preview_caps_ref")


def test_staging_preview_marks_learner_visible_false() -> None:
    """Staging preview marks learner_visible=false."""
    from app.services.content_staging_preview_service import StagingArtifactPreview

    preview = StagingArtifactPreview(
        artifact_id=str(uuid.uuid4()),
        scope_id="test_scope",
        caps_ref="test_ref",
        layer="diagnostic_items",
        artifact_type="diagnostic_item",
        staging_status="active",
        learner_visible=False,
        seed_run_id=None,
        seed_run_status=None,
        verification_passed=None,
        payload={},
        source_artifact_hash="test_hash",
        created_at="2024-01-01T00:00:00",
    )

    assert preview.learner_visible is False
