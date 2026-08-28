"""Comprehensive unit tests for AIBudgetGuard and BillingGuard fail-closed locks."""
from __future__ import annotations

import pytest

from app.services.ai_budget_guard import (
    DEFAULT_MAX_TOKENS_PER_REQUEST,
    DEFAULT_DAILY_TOKEN_BUDGET,
    AIBudgetExceededError,
    AIBudgetGuard,
)
from app.services.billing_guard import (
    BillingLockError,
    check_live_billing_authorization,
    assert_billing_authorized,
)


class TestAIBudgetGuard:
    def test_default_constants(self):
        assert DEFAULT_MAX_TOKENS_PER_REQUEST == 4096
        assert DEFAULT_DAILY_TOKEN_BUDGET == 500000

    def test_check_and_reserve_success(self):
        guard = AIBudgetGuard(max_tokens_per_request=1000, daily_budget=5000)
        usage = guard.check_and_reserve(500)
        assert usage == 500
        usage2 = guard.check_and_reserve(300)
        assert usage2 == 800

    def test_check_and_reserve_invalid_tokens_raises(self):
        guard = AIBudgetGuard()
        with pytest.raises(ValueError, match="must be positive"):
            guard.check_and_reserve(0)
        with pytest.raises(ValueError, match="must be positive"):
            guard.check_and_reserve(-100)

    def test_check_and_reserve_single_request_limit_raises(self):
        guard = AIBudgetGuard(max_tokens_per_request=1000, daily_budget=5000)
        with pytest.raises(AIBudgetExceededError, match="exceed maximum single-request limit"):
            guard.check_and_reserve(1001)

    def test_check_and_reserve_daily_budget_exhausted_raises(self):
        guard = AIBudgetGuard(max_tokens_per_request=1000, daily_budget=2000)
        guard.check_and_reserve(1000)
        guard.check_and_reserve(1000)
        with pytest.raises(AIBudgetExceededError, match="Daily AI budget exhausted"):
            guard.check_and_reserve(500)

    def test_reset_usage(self):
        guard = AIBudgetGuard()
        guard.check_and_reserve(1000)
        assert guard._current_usage == 1000
        guard.reset_usage()
        assert guard._current_usage == 0


class TestBillingGuard:
    def test_billing_lock_error_attributes(self):
        err = BillingLockError()
        assert err.status_code == 403
        assert err.headers["X-Billing-Lock"] == "LOCKED_FAIL_CLOSED"

    def test_check_live_billing_authorization_missing_file_fail_closed(self, tmp_path):
        # Empty tmp directory has no register -> fails closed
        assert check_live_billing_authorization(tmp_path) is False

    def test_assert_billing_authorized_raises_when_locked(self, tmp_path):
        with pytest.raises(BillingLockError, match="Commercial Release Boundary Lock"):
            assert_billing_authorized(tmp_path)
