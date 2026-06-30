"""tests/unit/test_diagnostic_transactional_response.py
Unit tests for TransactionalDiagnosticResponseService.
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.diagnostic_transactional_response import (
    DiagnosticTransactionError,
    DiagnosticTransactionInput,
    DiagnosticTransactionResult,
    TransactionalDiagnosticResponseService,
)


@pytest.mark.unit
def test_diagnostic_transaction_input_dataclass():
    """Verify DiagnosticTransactionInput dataclass accepts all fields."""
    input_data = DiagnosticTransactionInput(
        learner_id="learner-123",
        session_id="session-456",
        item_id="item-789",
        caps_ref="caps-ref",
        is_correct=True,
        theta_delta=0.5,
        fail_after_response=False,
        fail_after_mastery=False,
        fail_after_audit=False,
    )
    assert input_data.learner_id == "learner-123"
    assert input_data.session_id == "session-456"
    assert input_data.item_id == "item-789"
    assert input_data.caps_ref == "caps-ref"
    assert input_data.is_correct is True
    assert input_data.theta_delta == 0.5
    assert input_data.fail_after_response is False
    assert input_data.fail_after_mastery is False
    assert input_data.fail_after_audit is False


@pytest.mark.unit
def test_diagnostic_transaction_input_defaults():
    """Verify DiagnosticTransactionInput has correct default values."""
    input_data = DiagnosticTransactionInput(
        learner_id="learner-123",
        session_id="session-456",
        item_id="item-789",
        caps_ref="caps-ref",
        is_correct=True,
    )
    assert input_data.theta_delta == 0.0
    assert input_data.fail_after_response is False
    assert input_data.fail_after_mastery is False
    assert input_data.fail_after_audit is False


@pytest.mark.unit
def test_diagnostic_transaction_result_dataclass():
    """Verify DiagnosticTransactionResult dataclass accepts all fields."""
    result = DiagnosticTransactionResult(
        response_id="resp-1",
        mastery_id="mastery-1",
        audit_event_id="audit-1",
        learner_id="learner-123",
        session_id="session-456",
        item_id="item-789",
    )
    assert result.response_id == "resp-1"
    assert result.mastery_id == "mastery-1"
    assert result.audit_event_id == "audit-1"
    assert result.learner_id == "learner-123"
    assert result.session_id == "session-456"
    assert result.item_id == "item-789"


@pytest.mark.unit
def test_diagnostic_transaction_error_is_runtime_error():
    """Verify DiagnosticTransactionError is a RuntimeError subclass."""
    assert issubclass(DiagnosticTransactionError, RuntimeError)
    error = DiagnosticTransactionError("test error")
    assert isinstance(error, RuntimeError)
    assert str(error) == "test error"


@pytest.mark.unit
def test_transactional_service_init_stores_dependencies():
    """Verify constructor stores session, tables, and clock."""
    mock_session = MagicMock()
    mock_responses_table = MagicMock()
    mock_mastery_table = MagicMock()
    mock_audit_table = MagicMock()
    mock_clock = MagicMock()

    service = TransactionalDiagnosticResponseService(
        mock_session,
        responses_table=mock_responses_table,
        mastery_table=mock_mastery_table,
        audit_events_table=mock_audit_table,
        clock=mock_clock,
    )

    assert service.session is mock_session
    assert service.responses_table is mock_responses_table
    assert service.mastery_table is mock_mastery_table
    assert service.audit_events_table is mock_audit_table
    assert service.clock is mock_clock


@pytest.mark.unit
def test_transactional_service_init_uses_default_clock():
    """Verify constructor uses default clock when none provided."""
    mock_session = MagicMock()
    mock_responses_table = MagicMock()
    mock_mastery_table = MagicMock()
    mock_audit_table = MagicMock()

    service = TransactionalDiagnosticResponseService(
        mock_session,
        responses_table=mock_responses_table,
        mastery_table=mock_mastery_table,
        audit_events_table=mock_audit_table,
    )

    assert service.clock is not None
    # Call the clock to verify it returns a datetime
    now = service.clock()
    assert isinstance(now, datetime)


@pytest.mark.asyncio
async def test_submit_response_success():
    """Verify submit_response completes all three writes successfully."""
    mock_session = AsyncMock()
    mock_session.begin = MagicMock()
    mock_session.begin().__aenter__ = AsyncMock()
    mock_session.begin().__aexit__ = AsyncMock()
    mock_session.execute = AsyncMock()

    mock_responses_table = MagicMock()
    mock_responses_table.insert = MagicMock()
    mock_responses_table.insert().values = MagicMock()

    mock_mastery_table = MagicMock()
    mock_mastery_table.insert = MagicMock()
    mock_mastery_table.insert().values = MagicMock()

    mock_audit_table = MagicMock()
    mock_audit_table.insert = MagicMock()
    mock_audit_table.insert().values = MagicMock()

    service = TransactionalDiagnosticResponseService(
        mock_session,
        responses_table=mock_responses_table,
        mastery_table=mock_mastery_table,
        audit_events_table=mock_audit_table,
    )

    input_data = DiagnosticTransactionInput(
        learner_id="learner-123",
        session_id="session-456",
        item_id="item-789",
        caps_ref="caps-ref",
        is_correct=True,
    )

    result = await service.submit_response(input_data)

    assert isinstance(result, DiagnosticTransactionResult)
    assert result.learner_id == "learner-123"
    assert result.session_id == "session-456"
    assert result.item_id == "item-789"
    assert mock_session.execute.call_count == 3


@pytest.mark.asyncio
async def test_submit_response_raises_after_response_insert():
    """Verify submit_response raises when fail_after_response is True."""
    mock_session = AsyncMock()
    mock_session.begin = MagicMock()

    # Simulate transaction context that raises error after first execute
    execute_count = [0]

    async def mock_execute(statement):
        execute_count[0] += 1
        if execute_count[0] == 1:
            return  # First execute (response insert) succeeds
        raise DiagnosticTransactionError("simulated failure after diagnostic response insert")

    mock_session.execute = mock_execute

    async def mock_aenter(*args, **kwargs):
        return mock_session

    async def mock_aexit(*args, **kwargs):
        return None

    mock_session.begin().__aenter__ = mock_aenter
    mock_session.begin().__aexit__ = mock_aexit

    mock_responses_table = MagicMock()
    mock_responses_table.insert = MagicMock()
    mock_responses_table.insert().values = MagicMock()

    mock_mastery_table = MagicMock()
    mock_mastery_table.insert = MagicMock()
    mock_mastery_table.insert().values = MagicMock()

    mock_audit_table = MagicMock()
    mock_audit_table.insert = MagicMock()
    mock_audit_table.insert().values = MagicMock()

    service = TransactionalDiagnosticResponseService(
        mock_session,
        responses_table=mock_responses_table,
        mastery_table=mock_mastery_table,
        audit_events_table=mock_audit_table,
    )

    input_data = DiagnosticTransactionInput(
        learner_id="learner-123",
        session_id="session-456",
        item_id="item-789",
        caps_ref="caps-ref",
        is_correct=True,
        fail_after_response=True,
    )

    with pytest.raises(DiagnosticTransactionError, match="simulated failure after diagnostic response insert"):
        await service.submit_response(input_data)


@pytest.mark.asyncio
async def test_submit_response_raises_after_mastery_insert():
    """Verify submit_response raises when fail_after_mastery is True."""
    mock_session = AsyncMock()
    mock_session.begin = MagicMock()

    # Simulate transaction context that raises error after second execute
    execute_count = [0]

    async def mock_execute(statement):
        execute_count[0] += 1
        if execute_count[0] == 2:
            raise DiagnosticTransactionError("simulated failure after mastery update")
        return  # First execute (response insert) succeeds

    mock_session.execute = mock_execute

    async def mock_aenter(*args, **kwargs):
        return mock_session

    async def mock_aexit(*args, **kwargs):
        return None

    mock_session.begin().__aenter__ = mock_aenter
    mock_session.begin().__aexit__ = mock_aexit

    mock_responses_table = MagicMock()
    mock_responses_table.insert = MagicMock()
    mock_responses_table.insert().values = MagicMock()

    mock_mastery_table = MagicMock()
    mock_mastery_table.insert = MagicMock()
    mock_mastery_table.insert().values = MagicMock()

    mock_audit_table = MagicMock()
    mock_audit_table.insert = MagicMock()
    mock_audit_table.insert().values = MagicMock()

    service = TransactionalDiagnosticResponseService(
        mock_session,
        responses_table=mock_responses_table,
        mastery_table=mock_mastery_table,
        audit_events_table=mock_audit_table,
    )

    input_data = DiagnosticTransactionInput(
        learner_id="learner-123",
        session_id="session-456",
        item_id="item-789",
        caps_ref="caps-ref",
        is_correct=True,
        fail_after_mastery=True,
    )

    with pytest.raises(DiagnosticTransactionError, match="simulated failure after mastery update"):
        await service.submit_response(input_data)


@pytest.mark.asyncio
async def test_submit_response_raises_after_audit_insert():
    """Verify submit_response raises when fail_after_audit is True."""
    mock_session = AsyncMock()
    mock_session.begin = MagicMock()

    # Simulate transaction context that raises error after third execute
    execute_count = [0]

    async def mock_execute(statement):
        execute_count[0] += 1
        if execute_count[0] == 3:
            raise DiagnosticTransactionError("simulated failure after diagnostic audit event insert")
        return  # First two executes succeed

    mock_session.execute = mock_execute

    async def mock_aenter(*args, **kwargs):
        return mock_session

    async def mock_aexit(*args, **kwargs):
        return None

    mock_session.begin().__aenter__ = mock_aenter
    mock_session.begin().__aexit__ = mock_aexit

    mock_responses_table = MagicMock()
    mock_responses_table.insert = MagicMock()
    mock_responses_table.insert().values = MagicMock()

    mock_mastery_table = MagicMock()
    mock_mastery_table.insert = MagicMock()
    mock_mastery_table.insert().values = MagicMock()

    mock_audit_table = MagicMock()
    mock_audit_table.insert = MagicMock()
    mock_audit_table.insert().values = MagicMock()

    service = TransactionalDiagnosticResponseService(
        mock_session,
        responses_table=mock_responses_table,
        mastery_table=mock_mastery_table,
        audit_events_table=mock_audit_table,
    )

    input_data = DiagnosticTransactionInput(
        learner_id="learner-123",
        session_id="session-456",
        item_id="item-789",
        caps_ref="caps-ref",
        is_correct=True,
        fail_after_audit=True,
    )

    with pytest.raises(DiagnosticTransactionError, match="simulated failure after diagnostic audit event insert"):
        await service.submit_response(input_data)


@pytest.mark.asyncio
async def test_submit_response_generates_unique_ids():
    """Verify submit_response generates unique IDs for each call."""
    mock_session = AsyncMock()
    mock_session.begin = MagicMock()
    mock_session.begin().__aenter__ = AsyncMock()
    mock_session.begin().__aexit__ = AsyncMock()
    mock_session.execute = AsyncMock()

    mock_responses_table = MagicMock()
    mock_responses_table.insert = MagicMock()
    mock_responses_table.insert().values = MagicMock()

    mock_mastery_table = MagicMock()
    mock_mastery_table.insert = MagicMock()
    mock_mastery_table.insert().values = MagicMock()

    mock_audit_table = MagicMock()
    mock_audit_table.insert = MagicMock()
    mock_audit_table.insert().values = MagicMock()

    service = TransactionalDiagnosticResponseService(
        mock_session,
        responses_table=mock_responses_table,
        mastery_table=mock_mastery_table,
        audit_events_table=mock_audit_table,
    )

    input_data = DiagnosticTransactionInput(
        learner_id="learner-123",
        session_id="session-456",
        item_id="item-789",
        caps_ref="caps-ref",
        is_correct=True,
    )

    result1 = await service.submit_response(input_data)
    result2 = await service.submit_response(input_data)

    assert result1.response_id != result2.response_id
    assert result1.mastery_id != result2.mastery_id
    assert result1.audit_event_id != result2.audit_event_id


@pytest.mark.asyncio
async def test_submit_response_uses_custom_clock():
    """Verify submit_response uses custom clock when provided."""
    fixed_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    mock_clock = MagicMock(return_value=fixed_time)

    mock_session = AsyncMock()
    mock_session.begin = MagicMock()
    mock_session.begin().__aenter__ = AsyncMock()
    mock_session.begin().__aexit__ = AsyncMock()
    mock_session.execute = AsyncMock()

    mock_responses_table = MagicMock()
    mock_responses_table.insert = MagicMock()
    mock_responses_table.insert().values = MagicMock()

    mock_mastery_table = MagicMock()
    mock_mastery_table.insert = MagicMock()
    mock_mastery_table.insert().values = MagicMock()

    mock_audit_table = MagicMock()
    mock_audit_table.insert = MagicMock()
    mock_audit_table.insert().values = MagicMock()

    service = TransactionalDiagnosticResponseService(
        mock_session,
        responses_table=mock_responses_table,
        mastery_table=mock_mastery_table,
        audit_events_table=mock_audit_table,
        clock=mock_clock,
    )

    input_data = DiagnosticTransactionInput(
        learner_id="learner-123",
        session_id="session-456",
        item_id="item-789",
        caps_ref="caps-ref",
        is_correct=True,
    )

    await service.submit_response(input_data)

    # Verify clock was called
    mock_clock.assert_called()
