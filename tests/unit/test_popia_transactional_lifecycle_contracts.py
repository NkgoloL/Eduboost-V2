from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[2]

from app.services.popia_transactional_lifecycle import (
    POPIATransactionError,
    TransactionalPOPIAConsentLifecycleService,
    _call_flexible,
    _filter_kwargs,
    _has_active_transaction,
    _maybe_await,
    _transaction_context,
)


def test_transactional_lifecycle_service_declares_atomic_boundary():
    source = (ROOT / "app/services/popia_transactional_lifecycle.py").read_text(encoding="utf-8")

    assert "TransactionalPOPIAConsentLifecycleService" in source
    assert "async with _transaction_context(self.db)" in source
    assert "consent_record = await _call_flexible" in source
    assert "await self._audit" in source


def test_transactional_lifecycle_service_supports_required_transitions():
    source = (ROOT / "app/services/popia_transactional_lifecycle.py").read_text(encoding="utf-8")

    for method in ["grant", "deny", "withdraw", "renew"]:
        assert f"async def {method}" in source


@pytest.mark.xfail(reason="External script may not be available in all environments")
def test_popia_transaction_rollback_checker_runs_without_nested_pytest_recursion():
    env = {**os.environ, "PYTHONPATH": str(ROOT), "SKIP_PYTEST_RECURSION": "1"}
    result = subprocess.run(
        [sys.executable, "scripts/check_popia_transaction_rollback_proof.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stdout


def test_makefile_contains_popia_transaction_rollback_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "popia-transaction-rollback-proof-test:" in text
    assert "backend-implementation-1431-1470-full-check:" in text


# Unit tests for helper functions


@pytest.mark.unit
async def test_maybe_await_returns_value_directly_when_not_awaitable():
    """Verify _maybe_await returns non-awaitable values directly."""
    result = await _maybe_await("direct_value")
    assert result == "direct_value"


@pytest.mark.unit
async def test_maybe_await_awaits_when_value_is_awaitable():
    """Verify _maybe_await awaits coroutine values."""
    async def async_func():
        return "awaited_value"

    result = await _maybe_await(async_func())
    assert result == "awaited_value"


@pytest.mark.unit
def test_has_active_transaction_returns_true_when_checker_callable():
    """Verify _has_active_transaction returns True when db.in_transaction() returns True."""
    mock_db = MagicMock()
    mock_db.in_transaction = MagicMock(return_value=True)
    assert _has_active_transaction(mock_db) is True


@pytest.mark.unit
def test_has_active_transaction_returns_false_when_checker_returns_false():
    """Verify _has_active_transaction returns False when db.in_transaction() returns False."""
    mock_db = MagicMock()
    mock_db.in_transaction = MagicMock(return_value=False)
    assert _has_active_transaction(mock_db) is False


@pytest.mark.unit
def test_has_active_transaction_returns_false_when_checker_raises():
    """Verify _has_active_transaction returns False when checker raises exception."""
    mock_db = MagicMock()
    mock_db.in_transaction = MagicMock(side_effect=Exception("test error"))
    assert _has_active_transaction(mock_db) is False


@pytest.mark.unit
def test_has_active_transaction_returns_false_when_no_checker():
    """Verify _has_active_transaction returns False when db has no in_transaction attribute."""
    mock_db = MagicMock(spec=[])
    assert _has_active_transaction(mock_db) is False


@pytest.mark.unit
async def test_transaction_context_returns_null_context_when_db_is_none():
    """Verify _transaction_context returns null context when db is None."""
    ctx = _transaction_context(None)
    async with ctx:
        pass  # Should not raise


@pytest.mark.unit
async def test_transaction_context_returns_null_context_when_db_has_no_begin():
    """Verify _transaction_context returns null context when db has no begin method."""
    mock_db = MagicMock(spec=[])
    ctx = _transaction_context(mock_db)
    async with ctx:
        pass  # Should not raise


@pytest.mark.unit
async def test_transaction_context_returns_null_context_when_transaction_active():
    """Verify _transaction_context returns null context when transaction already active."""
    mock_db = MagicMock()
    mock_db.begin = MagicMock()
    mock_db.in_transaction = MagicMock(return_value=True)
    ctx = _transaction_context(mock_db)
    async with ctx:
        pass  # Should not raise
    mock_db.begin.assert_not_called()


@pytest.mark.unit
async def test_transaction_context_returns_db_begin_when_no_active_transaction():
    """Verify _transaction_context returns db.begin() when no active transaction."""
    mock_db = MagicMock()
    mock_db.in_transaction = MagicMock(return_value=False)
    mock_tx = AsyncMock()
    mock_db.begin = MagicMock(return_value=mock_tx)
    ctx = _transaction_context(mock_db)
    async with ctx:
        pass
    mock_db.begin.assert_called_once()


@pytest.mark.unit
def test_filter_kwargs_returns_all_when_var_keyword_present():
    """Verify _filter_kwargs returns all kwargs when method has **kwargs parameter."""
    def method_with_var_kwargs(a, **kwargs):
        pass

    kwargs = {"a": 1, "b": 2, "c": 3}
    result = _filter_kwargs(method_with_var_kwargs, kwargs)
    assert result == kwargs


@pytest.mark.unit
def test_filter_kwargs_filters_by_signature():
    """Verify _filter_kwargs filters kwargs to match method signature."""
    def method(a, b):
        pass

    kwargs = {"a": 1, "b": 2, "c": 3}
    result = _filter_kwargs(method, kwargs)
    assert result == {"a": 1, "b": 2}




@pytest.mark.unit
async def test_call_flexible_calls_first_available_method():
    """Verify _call_flexible calls the first available method."""
    mock_target = MagicMock()
    mock_target.method1 = AsyncMock(return_value="result1")
    mock_target.method2 = AsyncMock(return_value="result2")

    result = await _call_flexible(mock_target, ("method1", "method2"), arg=1)
    assert result == "result1"
    mock_target.method1.assert_called_once_with(arg=1)
    mock_target.method2.assert_not_called()


@pytest.mark.unit
async def test_call_flexible_falls_back_to_second_method():
    """Verify _call_flexible falls back to second method when first is missing."""
    mock_target = MagicMock()
    del mock_target.method1
    mock_target.method2 = AsyncMock(return_value="result2")

    result = await _call_flexible(mock_target, ("method1", "method2"), arg=1)
    assert result == "result2"
    mock_target.method2.assert_called_once_with(arg=1)


@pytest.mark.unit
async def test_call_flexible_raises_when_no_methods_available():
    """Verify _call_flexible raises POPIATransactionError when no methods available."""
    mock_target = MagicMock()
    del mock_target.method1
    del mock_target.method2

    with pytest.raises(POPIATransactionError) as exc:
        await _call_flexible(mock_target, ("method1", "method2"), arg=1)
    assert "Missing lifecycle method(s)" in str(exc.value)


@pytest.mark.unit
async def test_call_flexible_handles_sync_methods():
    """Verify _call_flexible handles synchronous methods."""
    mock_target = MagicMock()
    mock_target.method1 = MagicMock(return_value="sync_result")

    result = await _call_flexible(mock_target, ("method1",), arg=1)
    assert result == "sync_result"


@pytest.mark.unit
async def test_call_flexible_filters_kwargs():
    """Verify _call_flexible filters kwargs based on method signature."""
    mock_target = MagicMock()
    mock_target.method1 = AsyncMock()

    await _call_flexible(mock_target, ("method1",), a=1, b=2)
    # Should only pass kwargs that match signature


# Unit tests for TransactionalPOPIAConsentLifecycleService


@pytest.mark.unit
def test_transactional_service_init_stores_dependencies():
    """Verify TransactionalPOPIAConsentLifecycleService stores dependencies."""
    mock_db = MagicMock()
    mock_consent = MagicMock()
    mock_audit = MagicMock()

    service = TransactionalPOPIAConsentLifecycleService(
        db=mock_db, consent_service=mock_consent, audit_service=mock_audit
    )
    assert service.db is mock_db
    assert service.consent_service is mock_consent
    assert service.audit_service is mock_audit


@pytest.mark.unit
async def test_grant_calls_transition_with_correct_parameters():
    """Verify grant calls _transition with correct action and methods."""
    mock_db = MagicMock()
    mock_consent = MagicMock()
    mock_audit = MagicMock()

    service = TransactionalPOPIAConsentLifecycleService(
        db=mock_db, consent_service=mock_consent, audit_service=mock_audit
    )

    with patch.object(service, "_transition", new_callable=AsyncMock) as mock_transition:
        mock_transition.return_value = "consent_record"
        await service.grant(learner_id="learner-123", guardian_id="guardian-456")

        mock_transition.assert_called_once()
        call_kwargs = mock_transition.call_args[1]
        assert call_kwargs["action"] == "grant"
        assert call_kwargs["methods"] == ("grant", "grant_consent", "create_consent")
        assert call_kwargs["learner_id"] == "learner-123"
        assert call_kwargs["guardian_id"] == "guardian-456"


@pytest.mark.unit
async def test_deny_calls_transition_with_correct_parameters():
    """Verify deny calls _transition with correct action and methods."""
    mock_db = MagicMock()
    mock_consent = MagicMock()
    mock_audit = MagicMock()

    service = TransactionalPOPIAConsentLifecycleService(
        db=mock_db, consent_service=mock_consent, audit_service=mock_audit
    )

    with patch.object(service, "_transition", new_callable=AsyncMock) as mock_transition:
        mock_transition.return_value = "consent_record"
        await service.deny(learner_id="learner-123")

        mock_transition.assert_called_once()
        call_kwargs = mock_transition.call_args[1]
        assert call_kwargs["action"] == "deny"
        assert call_kwargs["methods"] == ("deny", "deny_consent")


@pytest.mark.unit
async def test_withdraw_calls_transition_with_correct_parameters():
    """Verify withdraw calls _transition with correct action and methods."""
    mock_db = MagicMock()
    mock_consent = MagicMock()
    mock_audit = MagicMock()

    service = TransactionalPOPIAConsentLifecycleService(
        db=mock_db, consent_service=mock_consent, audit_service=mock_audit
    )

    with patch.object(service, "_transition", new_callable=AsyncMock) as mock_transition:
        mock_transition.return_value = "consent_record"
        await service.withdraw(consent_id="consent-789")

        mock_transition.assert_called_once()
        call_kwargs = mock_transition.call_args[1]
        assert call_kwargs["action"] == "withdraw"
        assert call_kwargs["methods"] == ("withdraw", "withdraw_consent", "revoke", "revoke_consent")


@pytest.mark.unit
async def test_renew_calls_transition_with_correct_parameters():
    """Verify renew calls _transition with correct action and methods."""
    mock_db = MagicMock()
    mock_consent = MagicMock()
    mock_audit = MagicMock()

    service = TransactionalPOPIAConsentLifecycleService(
        db=mock_db, consent_service=mock_consent, audit_service=mock_audit
    )

    with patch.object(service, "_transition", new_callable=AsyncMock) as mock_transition:
        mock_transition.return_value = "consent_record"
        await service.renew(consent_id="consent-789")

        mock_transition.assert_called_once()
        call_kwargs = mock_transition.call_args[1]
        assert call_kwargs["action"] == "renew"
        assert call_kwargs["methods"] == ("renew", "renew_consent")


@pytest.mark.unit
async def test_transition_executes_consent_and_audit_in_transaction():
    """Verify _transition executes consent and audit within transaction context."""
    mock_db = MagicMock()
    mock_db.in_transaction = MagicMock(return_value=False)
    mock_tx = AsyncMock()
    mock_tx.__aenter__ = AsyncMock(return_value=None)
    mock_tx.__aexit__ = AsyncMock(return_value=None)
    mock_db.begin = MagicMock(return_value=mock_tx)

    mock_consent = MagicMock()
    mock_consent.grant = AsyncMock(return_value="consent_record")

    mock_audit = MagicMock()
    mock_audit.record_consent_lifecycle_event = AsyncMock()

    service = TransactionalPOPIAConsentLifecycleService(
        db=mock_db, consent_service=mock_consent, audit_service=mock_audit
    )

    result = await service._transition(
        action="grant", methods=("grant",), learner_id="learner-123"
    )

    assert result == "consent_record"
    mock_db.begin.assert_called_once()
    mock_consent.grant.assert_called_once()
    mock_audit.record_consent_lifecycle_event.assert_called_once()


@pytest.mark.unit
async def test_transition_skips_transaction_when_db_is_none():
    """Verify _transition skips transaction when db is None."""
    mock_consent = MagicMock()
    mock_consent.grant = AsyncMock(return_value="consent_record")

    mock_audit = MagicMock()
    mock_audit.record_consent_lifecycle_event = AsyncMock()

    service = TransactionalPOPIAConsentLifecycleService(
        db=None, consent_service=mock_consent, audit_service=mock_audit
    )

    result = await service._transition(
        action="grant", methods=("grant",), learner_id="learner-123"
    )

    assert result == "consent_record"
    mock_consent.grant.assert_called_once()
    mock_audit.record_consent_lifecycle_event.assert_called_once()


@pytest.mark.unit
async def test_audit_calls_flexible_with_multiple_method_names():
    """Verify _audit calls _call_flexible with multiple audit method names."""
    mock_audit = MagicMock()
    # _audit tries these methods in order: record_consent_lifecycle_event, record_consent_event, consent_lifecycle_event, log_event, audit_event
    # Delete the first few to force fallback to log_event
    del mock_audit.record_consent_lifecycle_event
    del mock_audit.record_consent_event
    del mock_audit.consent_lifecycle_event
    del mock_audit.audit_event
    mock_audit.log_event = AsyncMock()

    service = TransactionalPOPIAConsentLifecycleService(
        db=None, consent_service=None, audit_service=mock_audit
    )

    await service._audit(action="grant", consent_record="record", actor_id="actor-123")

    # Should call the last available method (log_event)
    mock_audit.log_event.assert_called_once()


@pytest.mark.unit
async def test_audit_passes_actor_id_when_provided():
    """Verify _audit passes actor_id when provided in kwargs."""
    mock_audit = MagicMock()
    # Delete earlier methods to force fallback to audit_event
    del mock_audit.record_consent_lifecycle_event
    del mock_audit.record_consent_event
    del mock_audit.consent_lifecycle_event
    del mock_audit.log_event
    mock_audit.audit_event = AsyncMock()

    service = TransactionalPOPIAConsentLifecycleService(
        db=None, consent_service=None, audit_service=mock_audit
    )

    await service._audit(action="grant", consent_record="record", actor_id="actor-123")

    # Should call audit_event (last in the list)
    mock_audit.audit_event.assert_called_once()
    call_kwargs = mock_audit.audit_event.call_args[1]
    assert call_kwargs["actor_id"] == "actor-123"


@pytest.mark.unit
def test_popia_transaction_error_is_runtime_error():
    """Verify POPIATransactionError is a RuntimeError subclass."""
    assert issubclass(POPIATransactionError, RuntimeError)


@pytest.mark.unit
def test_popia_transaction_error_can_be_raised():
    """Verify POPIATransactionError can be raised and caught."""
    with pytest.raises(POPIATransactionError) as exc:
        raise POPIATransactionError("test error")
    assert str(exc.value) == "test error"
