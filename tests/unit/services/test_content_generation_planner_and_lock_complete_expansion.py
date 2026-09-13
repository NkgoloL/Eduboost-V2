import time
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.content_factory import ContentGenerationRun
from app.services.content_generation_planner import (
    ContentGenerationPlanner,
    GenerationPlanResult,
    _topic_title,
)
from app.services.content_generation_run_lock import (
    ContentGenerationRunLock,
    LockAcquisitionResult,
)


@pytest.mark.asyncio
async def test_content_generation_planner_complete():
    scope_reg = MagicMock()
    readiness_svc = MagicMock()
    context_svc = MagicMock()
    planner = ContentGenerationPlanner(
        scope_registry=scope_reg,
        readiness_service=readiness_svc,
        source_context_service=context_svc,
    )
    session = AsyncMock()
    run_id = uuid.uuid4()

    # 1. Run not found raises LookupError (line 61)
    session.get.return_value = None
    with pytest.raises(LookupError, match=f"Generation run {run_id} not found."):
        await planner.plan_missing_for_run(session, run_id)

    # 2. Scope has unplannable layer or target <= 0 (line 72)
    mock_run = MagicMock(spec=ContentGenerationRun, run_id=run_id, scope_id="math_g4", status="queued", run_metadata={})
    session.get.return_value = mock_run

    scope_mock = MagicMock(scope_id="math_g4")
    scope_reg.get_scope.return_value = scope_mock

    layer_unplannable = MagicMock(layer="unknown_layer", target=5, approved=0, caps_ref="4.M.1")
    layer_zero_target = MagicMock(layer="diagnostic_items", target=0, approved=0, caps_ref="4.M.1")
    layer_valid = MagicMock(layer="diagnostic_items", target=5, approved=2, caps_ref="4.M.1")
    report_mock = MagicMock(layers=[layer_unplannable, layer_zero_target, layer_valid])
    readiness_svc.verify_scope = AsyncMock(return_value=report_mock)

    context_mock = MagicMock(passed=True, errors=[])
    context_svc.build_context = AsyncMock(return_value=context_mock)

    result = await planner.plan_missing_for_run(session, run_id)
    assert result.run_id == run_id
    assert mock_run.status == "planned"
    session.flush.assert_awaited()

    # 3. _topic_title helper (lines 126-128)
    topic1 = MagicMock(caps_ref="4.M.1", title="Fractions and Decimals")
    topic2 = MagicMock(caps_ref="4.M.2", title="Multiplication")
    scope_with_map = MagicMock(topic_map=[topic1, topic2])

    assert _topic_title(scope_with_map, "4.M.1") == "Fractions and Decimals"
    assert _topic_title(scope_with_map, "4.M.99") == "4.M.99"
    assert _topic_title(MagicMock(topic_map=None), "4.M.1") == "4.M.1"


@pytest.mark.asyncio
async def test_content_generation_run_lock_edge_branches():
    lock_mgr = ContentGenerationRunLock(ttl_minutes=1)
    session = AsyncMock()

    # 1. Lock acquired_at is 0 / None (hits line 59->70)
    mock_run = MagicMock(
        spec=ContentGenerationRun,
        run_metadata={
            "full_generation_lock": {
                "holder": "other_user",
                "lock_acquired_at": 0,
                "lock_expires_at": 0,
            }
        },
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_run
    session.execute.return_value = mock_result

    # acquire should see lock_acquired_at=0, bypass early return, release stale, and acquire lock
    res = await lock_mgr.acquire(session, holder="user1")
    assert res.acquired is True
    assert res.lock_holder == "user1"

    # 2. release where lock_info.get("holder") != holder (hits line 151->162)
    mock_run.run_metadata = {
        "full_generation_lock": {
            "holder": "user2",
            "lock_acquired_at": int(time.time()),
        }
    }
    released = await lock_mgr.release(session, holder="user1")
    assert released is False

    # 3. _release_stale_locks where lock is NOT stale (now < lock_acquired_at + ttl) (hits line 203->exit)
    now = time.time()
    mock_run.run_metadata = {
        "full_generation_lock": {
            "holder": "user1",
            "lock_acquired_at": now,  # freshly acquired
        }
    }
    await lock_mgr._release_stale_locks(session)
    # Lock should remain intact
    assert mock_run.run_metadata["full_generation_lock"]["holder"] == "user1"

