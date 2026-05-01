from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.domain.entities import AuditLog, LearnerProfile
from app.services.audit_service import AuditService
from app.services.learner_service import LearnerService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_learner_service_returns_summary():
    repo = AsyncMock()
    repo.get_by_id.return_value = LearnerProfile(
        learner_id="learner-1",
        grade=4,
        home_language="eng",
        overall_mastery=0.72,
    )
    service = LearnerService(repository=repo)

    result = await service.get_learner_summary("learner-1")

    assert result is not None
    assert result.learner_id == "learner-1"
    assert result.grade == 4
    assert result.overall_mastery == 0.72


@pytest.mark.unit
@pytest.mark.asyncio
async def test_audit_service_returns_logged_event():
    repo = AsyncMock()
    repo.append.return_value = AuditLog(
        event_id="event-1",
        learner_id="learner-1",
        event_type="LEARNER_READ",
        occurred_at=datetime.now(timezone.utc),
        payload={"route": "/api/v2/learners/{learner_id}"},
    )
    service = AuditService(repository=repo)

    result = await service.log_event("LEARNER_READ", {"route": "x"}, learner_id="learner-1")

    assert result.event_id == "event-1"
    assert result.learner_id == "learner-1"
    assert result.event_type == "LEARNER_READ"
