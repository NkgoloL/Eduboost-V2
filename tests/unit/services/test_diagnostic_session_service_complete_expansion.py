import json
import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.models.diagnostic_item import DiagnosticItem
from app.modules.diagnostics.irt_engine import DiagnosticSessionState, IRTEngine
from app.modules.diagnostics.item_bank_service import ItemBankService
from app.repositories.item_bank_repository import ItemBankRepository
from app.services.diagnostic_session_service import (
    DiagnosticSessionNotFoundError,
    DiagnosticSessionService,
    _redis_key,
)


@pytest.mark.asyncio
async def test_diagnostic_session_service_lifecycle():
    db = AsyncMock()
    redis = AsyncMock()
    item_bank_svc = MagicMock(spec=ItemBankService)
    irt_engine = MagicMock(spec=IRTEngine)

    service = DiagnosticSessionService(
        db=db,
        redis=redis,
        item_bank_service=item_bank_svc,
        irt_engine=irt_engine,
    )

    learner_id = uuid.uuid4()
    caps_ref = "4.M.1"
    session_id = uuid.uuid4()

    # 1. create_session
    mock_state = DiagnosticSessionState(
        session_id=session_id,
        learner_id=learner_id,
        caps_ref=caps_ref,
        theta=0.0,
        standard_error=1.0,
        responses=[],
        completed=False,
    )
    irt_engine.new_session.return_value = mock_state

    created = await service.create_session(learner_id, caps_ref, prior_theta=0.5)
    assert created.session_id == session_id
    assert created.learner_id == learner_id
    redis.set.assert_awaited_once()

    # 2. _load_state when key not in redis raises DiagnosticSessionNotFoundError
    redis.get.return_value = None
    with pytest.raises(DiagnosticSessionNotFoundError, match="It may have expired"):
        await service._load_state(session_id)

    # 3. next_item when session already completed
    completed_state = DiagnosticSessionState(
        session_id=session_id,
        learner_id=learner_id,
        caps_ref=caps_ref,
        theta=0.0,
        standard_error=1.0,
        responses=[],
        completed=True,
    )
    redis.get.return_value = json.dumps(completed_state.to_redis_dict())
    item_when_completed = await service.next_item(session_id)
    assert item_when_completed is None

    # 4. next_item active session
    active_state = DiagnosticSessionState(
        session_id=session_id,
        learner_id=learner_id,
        caps_ref=caps_ref,
        theta=0.0,
        standard_error=1.0,
        responses=[],
        completed=False,
    )
    redis.get.return_value = json.dumps(active_state.to_redis_dict())
    mock_item = MagicMock(spec=DiagnosticItem, id=uuid.uuid4())
    irt_engine.next_item = AsyncMock(return_value=mock_item)

    item = await service.next_item(session_id)
    assert item == mock_item

    # 5. record_response when session already completed
    redis.get.return_value = json.dumps(completed_state.to_redis_dict())
    state_ignored = await service.record_response(session_id, mock_item.id, is_correct=True)
    assert state_ignored.completed is True

    # 6. record_response item not found in DB
    redis.get.return_value = json.dumps(active_state.to_redis_dict())
    mock_repo = MagicMock(spec=ItemBankRepository)
    mock_repo.get_item = AsyncMock(return_value=None)
    item_bank_svc.repo = mock_repo

    with pytest.raises(ValueError, match="not found in DB"):
        await service.record_response(session_id, mock_item.id, is_correct=True)

    # 7. record_response success
    mock_repo.get_item = AsyncMock(return_value=mock_item)
    irt_engine.record_response = AsyncMock()

    recorded = await service.record_response(session_id, mock_item.id, is_correct=True)
    assert recorded.session_id == session_id
    irt_engine.record_response.assert_awaited_once()

    # 8. finalise_session
    redis.get.return_value = json.dumps(active_state.to_redis_dict())
    irt_engine.session_result.return_value = {
        "theta": 0.5,
        "standard_error": 0.3,
        "items_attempted": 5,
        "below_grade_level": False,
    }
    final_res = await service.finalise_session(session_id)
    assert final_res["theta"] == 0.5
    assert final_res["items_attempted"] == 5

    # 9. recover_session (none and found)
    redis.get.return_value = None
    recovered_none = await service.recover_session(session_id)
    assert recovered_none is None

    redis.get.return_value = json.dumps(active_state.to_redis_dict())
    recovered_found = await service.recover_session(session_id)
    assert recovered_found is not None
    assert recovered_found.session_id == session_id

    # 10. helper _redis_key
    assert _redis_key(session_id) == f"diagnostic:session:{session_id}"
