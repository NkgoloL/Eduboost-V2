from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services.popia_service import POPIADataRightsService


class FakeService(POPIADataRightsService):
    def __init__(self, learner):
        self.learner = learner

    async def load_authorized_learner(self, learner_id, current_user):
        return self.learner


@pytest.mark.asyncio
async def test_erasure_requires_guardian_or_admin() -> None:
    svc = FakeService(SimpleNamespace(id="learner-1", guardian_id="guardian-1", deletion_requested_at=None))
    with pytest.raises(HTTPException) as exc:
        await svc.request_erasure("learner-1", {"sub": "guardian-2", "role": "parent"})
    assert exc.value.status_code == 403
