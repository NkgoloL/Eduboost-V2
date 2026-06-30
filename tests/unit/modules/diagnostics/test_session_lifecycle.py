from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.modules.diagnostics.diagnostic_session_service import DiagnosticSessionService
from app.modules.diagnostics.session_recovery_service import SessionRecoveryService


def item(item_id="i1", caps_ref="4.M.1.1", tags=None):
    return SimpleNamespace(item_id=item_id, caps_ref=caps_ref, discrimination_a=1.0, difficulty_b=0.0, guessing_c=0.25, review_status="approved", safety_passed=True, exposure_count=0, max_exposure=50, misconception_tags=tags or [])


@pytest.mark.asyncio
async def test_session_lifecycle_and_recovery():
    recovery = SessionRecoveryService()
    service = DiagnosticSessionService(recovery_service=recovery)
    snap = await service.start_session("learner-1", "4.M.1.1")
    assert snap.se_estimate == 1.0
    recovered = await service.recover_session(snap.session_id)
    assert recovered is not None
    result = await service.submit_response(snap.session_id, item(tags=["place_value_confusion"]), correct=False, pool_size=10)
    assert result.items_served == 1
    assert result.gap_topics == ["4.M.1.1"]
    assert result.misconception_tags == ["place_value_confusion"]
    completed = await service.complete_session(snap.session_id)
    assert completed["mastery_label"]
    assert await recovery.read_session_snapshot(snap.session_id) is None
