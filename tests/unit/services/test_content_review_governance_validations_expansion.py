import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.content_review_governance import (
    ContentReviewGovernanceService,
    ReviewGovernancePolicy,
)
from app.models.content_factory import ContentGenerationArtifact, ContentArtifactStatus


@pytest.mark.asyncio
async def test_quarantine_artifact_validation():
    service = ContentReviewGovernanceService()
    session = AsyncMock()

    with pytest.raises(ValueError, match="Quarantine requires a reason code and explanation"):
        await service.quarantine_artifact(
            session,
            artifact_id=uuid.uuid4(),
            actor_id="admin",
            reason_code="",
            reason="",
        )


@pytest.mark.asyncio
async def test_create_revision_validation():
    service = ContentReviewGovernanceService()
    session = AsyncMock()

    with pytest.raises(ValueError, match="A revised artifact payload is required"):
        await service.create_revision(
            session,
            artifact_id=uuid.uuid4(),
            actor_id="admin",
            artifact_json={},
            reason="Update",
            expected_version=1,
        )
