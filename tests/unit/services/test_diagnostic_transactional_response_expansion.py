"""Batch 203: Unit tests for diagnostic_transactional_response service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.services.diagnostic_transactional_response import (
    DiagnosticTransactionError,
    DiagnosticTransactionInput,
    DiagnosticTransactionResult,
    TransactionalDiagnosticResponseService,
)


# ─────────────────────────────────────────────
# DiagnosticTransactionInput
# ─────────────────────────────────────────────


class TestDiagnosticTransactionInput:
    def test_required_fields(self):
        inp = DiagnosticTransactionInput(
            learner_id="L1", session_id="S1", item_id="I1",
            caps_ref="CAPS:MATH", is_correct=True,
        )
        assert inp.learner_id == "L1"
        assert inp.is_correct is True
        assert inp.theta_delta == 0.0
        assert inp.fail_after_response is False

    def test_fail_flags(self):
        inp = DiagnosticTransactionInput(
            learner_id="L1", session_id="S1", item_id="I1",
            caps_ref="CAPS", is_correct=False,
            fail_after_response=True, fail_after_mastery=True, fail_after_audit=True,
        )
        assert inp.fail_after_response is True
        assert inp.fail_after_mastery is True
        assert inp.fail_after_audit is True

    def test_frozen_immutable(self):
        inp = DiagnosticTransactionInput(
            learner_id="L1", session_id="S1", item_id="I1",
            caps_ref="CAPS", is_correct=True,
        )
        with pytest.raises(Exception):
            inp.learner_id = "mutated"


# ─────────────────────────────────────────────
# DiagnosticTransactionResult
# ─────────────────────────────────────────────


class TestDiagnosticTransactionResult:
    def test_fields(self):
        result = DiagnosticTransactionResult(
            response_id="r-1", mastery_id="m-1", audit_event_id="a-1",
            learner_id="L1", session_id="S1", item_id="I1",
        )
        assert result.response_id == "r-1"
        assert result.mastery_id == "m-1"
        assert result.audit_event_id == "a-1"

    def test_frozen_immutable(self):
        result = DiagnosticTransactionResult(
            response_id="r", mastery_id="m", audit_event_id="a",
            learner_id="L", session_id="S", item_id="I",
        )
        with pytest.raises(Exception):
            result.response_id = "mutated"


# ─────────────────────────────────────────────
# DiagnosticTransactionError
# ─────────────────────────────────────────────


class TestDiagnosticTransactionError:
    def test_is_runtime_error(self):
        err = DiagnosticTransactionError("test")
        assert isinstance(err, RuntimeError)

    def test_message_preserved(self):
        err = DiagnosticTransactionError("custom msg")
        assert "custom msg" in str(err)


# ─────────────────────────────────────────────
# TransactionalDiagnosticResponseService — async context mock
# ─────────────────────────────────────────────


def _make_mock_session():
    """Build a properly mocked SQLAlchemy async session with begin() context manager."""
    mock_session = MagicMock()
    mock_session.execute = AsyncMock()

    # begin() must return an object that supports `async with`
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=None)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)
    mock_session.begin = MagicMock(return_value=mock_ctx)

    return mock_session


def _make_service(session, fail_after_response=False, fail_after_mastery=False, fail_after_audit=False):
    mock_responses = MagicMock()
    mock_responses.insert.return_value.values.return_value = MagicMock()
    mock_mastery = MagicMock()
    mock_mastery.insert.return_value.values.return_value = MagicMock()
    mock_audit = MagicMock()
    mock_audit.insert.return_value.values.return_value = MagicMock()
    now = datetime(2025, 1, 1, tzinfo=timezone.utc)
    return TransactionalDiagnosticResponseService(
        session=session,
        responses_table=mock_responses,
        mastery_table=mock_mastery,
        audit_events_table=mock_audit,
        clock=lambda: now,
    )


class TestTransactionalDiagnosticResponseService:
    @pytest.mark.asyncio
    async def test_successful_submit_returns_result(self):
        session = _make_mock_session()
        service = _make_service(session)
        data = DiagnosticTransactionInput(
            learner_id="L1", session_id="S1", item_id="I1",
            caps_ref="CAPS:MATH", is_correct=True, theta_delta=0.5,
        )
        result = await service.submit_response(data)
        assert isinstance(result, DiagnosticTransactionResult)
        assert result.learner_id == "L1"
        assert result.session_id == "S1"
        assert result.item_id == "I1"
        assert session.execute.call_count == 3

    @pytest.mark.asyncio
    async def test_fail_after_response_raises(self):
        session = _make_mock_session()
        service = _make_service(session)
        data = DiagnosticTransactionInput(
            learner_id="L1", session_id="S1", item_id="I1",
            caps_ref="CAPS", is_correct=True, fail_after_response=True,
        )
        with pytest.raises(DiagnosticTransactionError, match="after diagnostic response"):
            await service.submit_response(data)

    @pytest.mark.asyncio
    async def test_fail_after_mastery_raises(self):
        session = _make_mock_session()
        service = _make_service(session)
        data = DiagnosticTransactionInput(
            learner_id="L1", session_id="S1", item_id="I1",
            caps_ref="CAPS", is_correct=True, fail_after_mastery=True,
        )
        with pytest.raises(DiagnosticTransactionError, match="after mastery"):
            await service.submit_response(data)

    @pytest.mark.asyncio
    async def test_fail_after_audit_raises(self):
        session = _make_mock_session()
        service = _make_service(session)
        data = DiagnosticTransactionInput(
            learner_id="L1", session_id="S1", item_id="I1",
            caps_ref="CAPS", is_correct=True, fail_after_audit=True,
        )
        with pytest.raises(DiagnosticTransactionError, match="after diagnostic audit"):
            await service.submit_response(data)

    @pytest.mark.asyncio
    async def test_result_ids_are_unique_uuids(self):
        session = _make_mock_session()
        service = _make_service(session)
        data = DiagnosticTransactionInput(
            learner_id="L1", session_id="S1", item_id="I1",
            caps_ref="CAPS", is_correct=True,
        )
        result1 = await service.submit_response(data)
        result2 = await service.submit_response(data)
        assert result1.response_id != result2.response_id
        assert result1.mastery_id != result2.mastery_id
        assert result1.audit_event_id != result2.audit_event_id

    def test_default_clock_returns_datetime(self):
        service = TransactionalDiagnosticResponseService(
            session=MagicMock(),
            responses_table=MagicMock(),
            mastery_table=MagicMock(),
            audit_events_table=MagicMock(),
        )
        result = service.clock()
        assert isinstance(result, datetime)
