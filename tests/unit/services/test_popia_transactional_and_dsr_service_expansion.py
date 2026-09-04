"""Comprehensive unit tests for POPIA transactional lifecycle and DSR service coverage expansion."""
from __future__ import annotations

import inspect
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.domain.data_subject_rights import (
    CorrectionRequest,
    DataExportRequest,
    ErasureRequest,
    RequestStatus,
    RestrictionRequest,
)
from app.services.data_subject_rights_service import DataSubjectRightsService
from app.services.popia_transactional_lifecycle import (
    POPIATransactionError,
    TransactionalPOPIAConsentLifecycleService,
    _call_flexible,
    _filter_kwargs,
    _has_active_transaction,
    _maybe_await,
    _NullAsyncContext,
    _transaction_context,
)


# ==============================================================================
# POPIA Transactional Lifecycle Unit Tests
# ==============================================================================

class TestPOPIATransactionalLifecycleExpansion:
    @pytest.mark.asyncio
    async def test_null_async_context(self):
        ctx = _NullAsyncContext()
        async with ctx as val:
            assert val is None

    @pytest.mark.asyncio
    async def test_maybe_await(self):
        async def coroutine_val():
            return 42

        assert await _maybe_await(coroutine_val()) == 42
        assert await _maybe_await("synchronous_str") == "synchronous_str"

    def test_has_active_transaction(self):
        # 1. db with in_transaction returning True
        db_active = MagicMock()
        db_active.in_transaction.return_value = True
        assert _has_active_transaction(db_active) is True

        # 2. db with in_transaction returning False
        db_inactive = MagicMock()
        db_inactive.in_transaction.return_value = False
        assert _has_active_transaction(db_inactive) is False

        # 3. db with in_transaction raising exception
        db_err = MagicMock()
        db_err.in_transaction.side_effect = RuntimeError("Broken")
        assert _has_active_transaction(db_err) is False

        # 4. db without in_transaction
        assert _has_active_transaction(None) is False
        assert _has_active_transaction(object()) is False

    def test_transaction_context(self):
        # 1. db is None or without begin
        assert isinstance(_transaction_context(None), _NullAsyncContext)
        assert isinstance(_transaction_context(object()), _NullAsyncContext)

        # 2. db in transaction
        db_in_tx = MagicMock()
        db_in_tx.in_transaction.return_value = True
        assert isinstance(_transaction_context(db_in_tx), _NullAsyncContext)

        # 3. db not in transaction
        db_not_in_tx = MagicMock()
        db_not_in_tx.in_transaction.return_value = False
        mock_begin = MagicMock()
        db_not_in_tx.begin.return_value = mock_begin
        assert _transaction_context(db_not_in_tx) == mock_begin

    def test_filter_kwargs(self):
        def sample_func(a, b, c=1):
            pass

        filtered = _filter_kwargs(sample_func, {"a": 10, "b": 20, "extra": 30})
        assert filtered == {"a": 10, "b": 20}

        def func_with_kwargs(a, **kw):
            pass

        assert _filter_kwargs(func_with_kwargs, {"a": 1, "other": 2}) == {"a": 1, "other": 2}

        # Non-callable or signature failure
        assert _filter_kwargs(None, {"x": 1}) == {"x": 1}

    @pytest.mark.asyncio
    async def test_call_flexible_success_and_error(self):
        class DummyTarget:
            def fallback_method(self, foo="default"):
                return "success_val"

        target = DummyTarget()
        res = await _call_flexible(target, ("missing_first", "fallback_method"), foo="bar")
        assert res == "success_val"

        with pytest.raises(POPIATransactionError, match="Missing lifecycle method"):
            await _call_flexible(target, ("missing_1", "missing_2"))

    @pytest.mark.asyncio
    async def test_transactional_service_full_transitions(self):
        db = MagicMock()
        db.in_transaction.return_value = False
        mock_ctx = AsyncMock()
        db.begin.return_value = mock_ctx

        consent_service = MagicMock()
        consent_service.grant = AsyncMock(return_value={"state": "granted"})
        consent_service.deny = AsyncMock(return_value={"state": "denied"})
        consent_service.withdraw = AsyncMock(return_value={"state": "withdrawn"})
        consent_service.renew = AsyncMock(return_value={"state": "renewed"})

        audit_service = MagicMock()
        audit_service.log_event = AsyncMock()

        svc = TransactionalPOPIAConsentLifecycleService(
            db=db,
            consent_service=consent_service,
            audit_service=audit_service,
        )

        # Grant
        g = await svc.grant(learner_id="l1", actor_id="a1")
        assert g == {"state": "granted"}
        consent_service.grant.assert_awaited_once()

        # Deny
        d = await svc.deny(learner_id="l1", actor_id="a1")
        assert d == {"state": "denied"}
        consent_service.deny.assert_awaited_once()

        # Withdraw
        w = await svc.withdraw(learner_id="l1", actor_id="a1")
        assert w == {"state": "withdrawn"}
        consent_service.withdraw.assert_awaited_once()

        # Renew
        r = await svc.renew(learner_id="l1", actor_id="a1")
        assert r == {"state": "renewed"}
        consent_service.renew.assert_awaited_once()


# ==============================================================================
# DataSubjectRightsService Comprehensive Tests
# ==============================================================================

class TestDataSubjectRightsServiceExpansion:
    @pytest.fixture
    def mock_pool(self):
        pool = AsyncMock()
        pool.execute = AsyncMock()
        pool.fetchrow = AsyncMock()
        pool.fetch = AsyncMock(return_value=[])
        return pool

    @pytest.fixture
    def mock_audit(self):
        audit = AsyncMock()
        audit.record = AsyncMock()
        return audit

    @pytest.fixture
    def dsr_service(self, mock_pool, mock_audit):
        return DataSubjectRightsService(pool=mock_pool, audit_repo=mock_audit)

    @pytest.mark.asyncio
    async def test_build_and_complete_export_json_and_csv(self, dsr_service, mock_pool, mock_audit):
        req_id = uuid.uuid4()
        learner_id = uuid.uuid4()
        actor_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        export_row_json = {
            "id": req_id,
            "learner_id": learner_id,
            "requested_by": actor_id,
            "status": "pending",
            "format": "json",
            "download_url": None,
            "sla_deadline": now,
            "created_at": now,
            "completed_at": None,
            "artifact_path": None,
        }
        mock_pool.fetchrow.side_effect = [
            export_row_json,  # for _require_export_request
            {"id": learner_id, "display_name": "Test Learner"},  # profile
        ]
        mock_pool.fetch.side_effect = [
            [{"id": uuid.uuid4(), "score": 80}],  # diagnostic_sessions
            [{"id": uuid.uuid4(), "subject": "math"}],  # lesson_records
            [{"id": uuid.uuid4(), "state": "granted"}],  # consent_records
        ]

        completed_json = await dsr_service.build_and_complete_export(req_id, actor_id)
        assert completed_json.status == RequestStatus.COMPLETED
        assert completed_json.format == "json"
        assert completed_json.artifact_path == f"/exports/{req_id}.json"
        mock_audit.record.assert_awaited_once()

        # CSV format test
        export_row_csv = dict(export_row_json)
        export_row_csv["format"] = "csv"
        mock_pool.fetchrow.side_effect = [
            export_row_csv,
            {"id": learner_id, "display_name": "Test Learner"},
        ]
        mock_pool.fetch.side_effect = [
            [{"id": uuid.uuid4(), "score": 80}],
            [],
            [],
        ]

        completed_csv = await dsr_service.build_and_complete_export(req_id, actor_id)
        assert completed_csv.status == RequestStatus.COMPLETED
        assert completed_csv.format == "csv"
        assert completed_csv.artifact_path == f"/exports/{req_id}.csv"

    @pytest.mark.asyncio
    async def test_require_export_request_raises_not_found(self, dsr_service, mock_pool):
        mock_pool.fetchrow.return_value = None
        with pytest.raises(ValueError, match="Export request .* not found"):
            await dsr_service._require_export_request(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_get_erasure_status_and_approve_erasure(self, dsr_service, mock_pool):
        req_id = uuid.uuid4()
        learner_id = uuid.uuid4()
        approver_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        erasure_row = {
            "id": req_id,
            "learner_id": learner_id,
            "requested_by": approver_id,
            "status": "in_progress",
            "review_notes": "approved by admin",
            "legal_hold": False,
            "sla_deadline": now,
            "created_at": now,
            "approved_at": now,
            "executed_at": None,
        }
        mock_pool.fetchrow.return_value = erasure_row

        status = await dsr_service.get_erasure_status(req_id)
        assert status is not None
        assert status.status == RequestStatus.IN_PROGRESS

        approved = await dsr_service.approve_erasure(req_id, approver_id, "approved by admin")
        assert approved.status == RequestStatus.IN_PROGRESS
        mock_pool.execute.assert_awaited()

    @pytest.mark.asyncio
    async def test_execute_erasure_success_and_errors(self, dsr_service, mock_pool, mock_audit):
        req_id = uuid.uuid4()
        learner_id = uuid.uuid4()
        executor_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        # 1. Request not found
        mock_pool.fetchrow.return_value = None
        with pytest.raises(ValueError, match="Erasure request .* not found"):
            await dsr_service.execute_erasure(req_id, executor_id)

        # 2. Cannot execute due to legal hold
        erasure_row_held = {
            "id": req_id,
            "learner_id": learner_id,
            "requested_by": executor_id,
            "status": "in_progress",
            "review_notes": "hold",
            "legal_hold": True,
            "sla_deadline": now,
            "created_at": now,
            "approved_at": now,
            "executed_at": None,
        }
        mock_pool.fetchrow.return_value = erasure_row_held
        with pytest.raises(PermissionError, match="cannot be executed"):
            await dsr_service.execute_erasure(req_id, executor_id)

        # 3. Successful execution
        erasure_row_valid = dict(erasure_row_held)
        erasure_row_valid["legal_hold"] = False

        mock_conn = AsyncMock()
        mock_tx = AsyncMock()
        mock_conn.transaction = MagicMock(return_value=mock_tx)
        mock_tx.__aenter__.return_value = None
        mock_tx.__aexit__.return_value = None

        mock_acquire_cm = AsyncMock()
        mock_acquire_cm.__aenter__.return_value = mock_conn
        mock_acquire_cm.__aexit__.return_value = None
        mock_pool.acquire = MagicMock(return_value=mock_acquire_cm)

        mock_pool.fetchrow.return_value = erasure_row_valid

        executed = await dsr_service.execute_erasure(req_id, executor_id)
        assert executed.status == RequestStatus.COMPLETED
        assert mock_conn.execute.await_count >= 5
        mock_audit.record.assert_awaited()

    @pytest.mark.asyncio
    async def test_complete_correction_and_lift_restriction(self, dsr_service, mock_pool):
        req_id = uuid.uuid4()
        learner_id = uuid.uuid4()
        actor_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        # Complete correction
        correction_row = {
            "id": req_id,
            "learner_id": learner_id,
            "requested_by": actor_id,
            "field_name": "display_name",
            "old_value": "Old",
            "new_value": "New",
            "status": "completed",
            "created_at": now,
            "completed_at": now,
        }
        mock_pool.fetchrow.return_value = correction_row
        cor = await dsr_service.complete_correction(req_id, actor_id)
        assert cor.status == RequestStatus.COMPLETED
        assert cor.new_value == "New"

        # Lift restriction
        restriction_row = {
            "id": req_id,
            "learner_id": learner_id,
            "requested_by": actor_id,
            "reason": "Resolved",
            "status": "completed",
            "created_at": now,
            "lifted_at": now,
        }
        mock_pool.fetchrow.return_value = restriction_row
        res = await dsr_service.lift_restriction(req_id, actor_id)
        assert res.status == RequestStatus.COMPLETED
        assert res.reason == "Resolved"

    @pytest.mark.asyncio
    async def test_list_overdue_requests(self, dsr_service, mock_pool):
        req_id = uuid.uuid4()
        learner_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        export_row = {
            "id": req_id,
            "learner_id": learner_id,
            "requested_by": uuid.uuid4(),
            "status": "pending",
            "format": "json",
            "download_url": None,
            "sla_deadline": now,
            "created_at": now,
            "completed_at": None,
            "artifact_path": None,
        }
        erasure_row = {
            "id": req_id,
            "learner_id": learner_id,
            "requested_by": uuid.uuid4(),
            "status": "pending",
            "review_notes": None,
            "legal_hold": False,
            "sla_deadline": now,
            "created_at": now,
            "approved_at": None,
            "executed_at": None,
        }

        mock_pool.fetch.side_effect = [[export_row], [erasure_row]]

        overdue_exports = await dsr_service.list_overdue_export_requests()
        assert len(overdue_exports) == 1
        assert overdue_exports[0].id == req_id

        overdue_erasures = await dsr_service.list_overdue_erasure_requests()
        assert len(overdue_erasures) == 1
        assert overdue_erasures[0].id == req_id
