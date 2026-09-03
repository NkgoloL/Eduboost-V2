"""Batch 231 — app/services/diagnostic_session_service.py comprehensive branch coverage expansion.

Tests:
- _redis_key formatting helper
- DiagnosticSessionNotFoundError exception
- DiagnosticSessionService:
  - create_session: creates and saves new session state with rolling TTL
  - next_item:
    - returns None if session is already completed
    - delegates to engine.next_item, persists state, returns item
  - record_response:
    - returns state if already completed
    - raises ValueError if DiagnosticItem not found in repository
    - delegates to engine.record_response, updates state, persists state
  - finalise_session: marks state completed, persists, returns engine.session_result
  - recover_session: returns None if missing in Redis, returns restored state if found
  - _load_state & _save_state: raises DiagnosticSessionNotFoundError on cache miss
"""
from __future__ import annotations

import json
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.diagnostics.irt_engine import DiagnosticSessionState
from app.services.diagnostic_session_service import (
    DiagnosticSessionNotFoundError,
    DiagnosticSessionService,
    _redis_key,
)


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_redis():
    return AsyncMock()


@pytest.fixture
def mock_item_bank_svc():
    svc = MagicMock()
    svc.repo = AsyncMock()
    return svc


@pytest.fixture
def mock_irt_engine():
    return AsyncMock()


@pytest.fixture
def service(mock_db, mock_redis, mock_item_bank_svc, mock_irt_engine):
    return DiagnosticSessionService(
        db=mock_db,
        redis=mock_redis,
        item_bank_service=mock_item_bank_svc,
        irt_engine=mock_irt_engine,
    )


@pytest.fixture
def sample_state():
    return DiagnosticSessionState(
        session_id=uuid.uuid4(),
        learner_id=uuid.uuid4(),
        caps_ref="4.M.1.1",
        theta=0.0,
        standard_error=0.5,
        responses=[],
        completed=False,
    )


# ---------------------------------------------------------------------------
# Key Helper & Exception
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_redis_key_and_not_found_error():
    sid = uuid.uuid4()
    assert _redis_key(sid) == f"diagnostic:session:{sid}"

    err = DiagnosticSessionNotFoundError("Session missing")
    assert "Session missing" in str(err)


# ---------------------------------------------------------------------------
# Create Session
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_session(service, mock_redis, mock_irt_engine, sample_state):
    mock_irt_engine.new_session = MagicMock(return_value=sample_state)

    state = await service.create_session(
        learner_id=sample_state.learner_id,
        caps_ref="4.M.1.1",
        prior_theta=0.2,
    )
    assert state == sample_state
    mock_irt_engine.new_session.assert_called_once()
    mock_redis.set.assert_called_once()


# ---------------------------------------------------------------------------
# Next Item
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_next_item_completed_and_active(service, mock_redis, mock_irt_engine, sample_state):
    session_id = sample_state.session_id

    # 1. Already completed session -> returns None
    completed_state = DiagnosticSessionState(
        session_id=session_id,
        learner_id=sample_state.learner_id,
        caps_ref="4.M.1.1",
        theta=0.0,
        standard_error=0.5,
        responses=[],
        completed=True,
    )
    mock_redis.get.return_value = json.dumps(completed_state.to_redis_dict())

    item_none = await service.next_item(session_id)
    assert item_none is None
    mock_irt_engine.next_item.assert_not_called()

    # 2. Active session -> returns item and saves state
    mock_redis.get.return_value = json.dumps(sample_state.to_redis_dict())
    mock_item = MagicMock(item_id=uuid.uuid4())
    mock_irt_engine.next_item = AsyncMock(return_value=mock_item)

    item = await service.next_item(session_id)
    assert item == mock_item
    mock_redis.set.assert_called()


# ---------------------------------------------------------------------------
# Record Response
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_record_response_flow(
    service,
    mock_redis,
    mock_item_bank_svc,
    mock_irt_engine,
    sample_state,
):
    session_id = sample_state.session_id
    item_id = uuid.uuid4()

    # 1. Already completed session -> returns state immediately
    completed_state = DiagnosticSessionState(
        session_id=session_id,
        learner_id=sample_state.learner_id,
        caps_ref="4.M.1.1",
        theta=0.0,
        standard_error=0.5,
        responses=[],
        completed=True,
    )
    mock_redis.get.return_value = json.dumps(completed_state.to_redis_dict())

    res_completed = await service.record_response(session_id, item_id, is_correct=True)
    assert res_completed.completed is True
    mock_irt_engine.record_response.assert_not_called()

    # 2. Item not found in repository -> raises ValueError
    mock_redis.get.return_value = json.dumps(sample_state.to_redis_dict())
    mock_item_bank_svc.repo.get_item = AsyncMock(return_value=None)

    with pytest.raises(ValueError, match="not found in DB"):
        await service.record_response(session_id, item_id, is_correct=True)

    # 3. Active response recorded successfully
    mock_item = MagicMock(item_id=item_id)
    mock_item_bank_svc.repo.get_item = AsyncMock(return_value=mock_item)
    mock_irt_engine.record_response = AsyncMock()

    res_active = await service.record_response(session_id, item_id, is_correct=True)
    assert res_active.session_id == session_id
    mock_irt_engine.record_response.assert_called_once()
    mock_redis.set.assert_called()


# ---------------------------------------------------------------------------
# Finalise & Recover Session
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
async def test_finalise_and_recover_session(
    service,
    mock_redis,
    mock_irt_engine,
    sample_state,
):
    session_id = sample_state.session_id

    # 1. Finalise session
    mock_redis.get.return_value = json.dumps(sample_state.to_redis_dict())
    mock_irt_engine.session_result = MagicMock(
        return_value={
            "theta": 0.5,
            "standard_error": 0.2,
            "items_attempted": 5,
            "below_grade_level": False,
        }
    )

    result = await service.finalise_session(session_id)
    assert result["theta"] == 0.5
    assert result["items_attempted"] == 5

    # 2. Recover session missing in Redis -> returns None
    mock_redis.get.return_value = None
    recovered_none = await service.recover_session(session_id)
    assert recovered_none is None

    # 3. Recover session present in Redis -> returns restored state
    mock_redis.get.return_value = json.dumps(sample_state.to_redis_dict())
    recovered_state = await service.recover_session(session_id)
    assert recovered_state is not None
    assert recovered_state.session_id == session_id

    # 4. _load_state missing in Redis -> raises DiagnosticSessionNotFoundError
    mock_redis.get.return_value = None
    with pytest.raises(DiagnosticSessionNotFoundError, match="not found"):
        await service._load_state(session_id)
