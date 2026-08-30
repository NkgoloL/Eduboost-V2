import uuid
import pytest
from unittest.mock import AsyncMock

from app.services.content_review_governance import (
    ContentReviewGovernanceService,
)


@pytest.mark.asyncio
async def test_reassign_assignment_validation():
    service = ContentReviewGovernanceService()
    session = AsyncMock()

    with pytest.raises(ValueError, match="Reassignment requires a reason"):
        await service.reassign_assignment(
            session,
            assignment_id=uuid.uuid4(),
            new_reviewer_id="rev-2",
            assigned_by="admin",
            reason="",
        )
