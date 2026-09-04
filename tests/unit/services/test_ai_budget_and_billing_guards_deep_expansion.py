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
    @pytest.fixture(autouse=True)
    def reset_guard(self):
        AIBudgetGuard().reset_usage()
        yield
        AIBudgetGuard().reset_usage()

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

    def test_current_usage_setter(self):
        guard = AIBudgetGuard()
        guard._current_usage = 1234
        assert guard._current_usage == 1234
        guard.reset_usage()

    @pytest.mark.asyncio
    async def test_check_and_reserve_async_validation_errors(self):
        guard = AIBudgetGuard(max_tokens_per_request=1000, daily_budget=5000)
        with pytest.raises(ValueError, match="must be positive"):
            await guard.check_and_reserve_async(0)
        with pytest.raises(ValueError, match="must be positive"):
            await guard.check_and_reserve_async(-5)
        with pytest.raises(AIBudgetExceededError, match="exceed maximum single-request limit"):
            await guard.check_and_reserve_async(1500)

    @pytest.mark.asyncio
    async def test_check_and_reserve_async_without_redis(self):
        guard = AIBudgetGuard(max_tokens_per_request=1000, daily_budget=5000)
        used = await guard.check_and_reserve_async(400)
        assert used == 400

    @pytest.mark.asyncio
    async def test_check_and_reserve_async_with_redis_success(self):
        from unittest.mock import AsyncMock
        mock_redis = AsyncMock()
        mock_redis.incrby = AsyncMock(return_value=500)
        mock_redis.expire = AsyncMock(return_value=True)

        guard = AIBudgetGuard(max_tokens_per_request=1000, daily_budget=2000, redis_client=mock_redis)
        used = await guard.check_and_reserve_async(500)
        assert used == 500
        mock_redis.incrby.assert_awaited_once()
        mock_redis.expire.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_check_and_reserve_async_with_redis_exhausted(self):
        from unittest.mock import AsyncMock
        mock_redis = AsyncMock()
        mock_redis.incrby = AsyncMock(return_value=2500)
        mock_redis.decrby = AsyncMock(return_value=2000)

        guard = AIBudgetGuard(max_tokens_per_request=1000, daily_budget=2000, redis_client=mock_redis)
        with pytest.raises(AIBudgetExceededError, match="Daily AI budget exhausted"):
            await guard.check_and_reserve_async(500)
        mock_redis.decrby.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_check_and_reserve_async_redis_exception_fallback(self):
        from unittest.mock import AsyncMock
        mock_redis = AsyncMock()
        mock_redis.incrby = AsyncMock(side_effect=RuntimeError("Redis connection lost"))

        guard = AIBudgetGuard(max_tokens_per_request=1000, daily_budget=2000, redis_client=mock_redis)
        used = await guard.check_and_reserve_async(300)
        assert used == 300

    def test_get_ai_budget_guard_singleton(self):
        from app.services import ai_budget_guard
        from unittest.mock import patch

        ai_budget_guard._DEFAULT_GUARD = None
        with patch("app.core.redis.get_redis", side_effect=Exception("No redis")):
            g1 = ai_budget_guard.get_ai_budget_guard()
            assert isinstance(g1, AIBudgetGuard)

        # Calling again returns singleton
        g2 = ai_budget_guard.get_ai_budget_guard()
        assert g1 is g2

        # Updating redis_client on singleton
        from unittest.mock import MagicMock
        dummy_client = MagicMock()
        g3 = ai_budget_guard.get_ai_budget_guard(redis_client=dummy_client)
        assert g3.redis_client is dummy_client

        # Initial creation when redis client succeeds
        ai_budget_guard._DEFAULT_GUARD = None
        with patch("app.core.redis.get_redis", return_value=dummy_client):
            g4 = ai_budget_guard.get_ai_budget_guard()
            assert g4.redis_client is dummy_client

        # Initial creation when redis_client is explicitly provided
        ai_budget_guard._DEFAULT_GUARD = None
        g5 = ai_budget_guard.get_ai_budget_guard(redis_client=dummy_client)
        assert g5.redis_client is dummy_client


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

    def test_check_live_billing_authorization_invalid_json(self, tmp_path):
        reg_dir = tmp_path / "docs" / "roadmap" / "production_readiness"
        reg_dir.mkdir(parents=True)
        reg_file = reg_dir / "true_state_remediation_register.json"
        reg_file.write_text("NOT_VALID_JSON", encoding="utf-8")

        assert check_live_billing_authorization(tmp_path) is False

    def test_check_live_billing_authorization_authorized_and_unauthorized(self, tmp_path):
        import json
        reg_dir = tmp_path / "docs" / "roadmap" / "production_readiness"
        reg_dir.mkdir(parents=True)
        reg_file = reg_dir / "true_state_remediation_register.json"

        # Unauthorized
        data_unauth = {
            "authority_boundaries": {
                "live_payment_processing_authorised": False,
                "billing_launch_authorised": True,
            }
        }
        reg_file.write_text(json.dumps(data_unauth), encoding="utf-8")
        assert check_live_billing_authorization(tmp_path) is False

        # Authorized
        data_auth = {
            "authority_boundaries": {
                "live_payment_processing_authorised": True,
                "billing_launch_authorised": True,
            }
        }
        reg_file.write_text(json.dumps(data_auth), encoding="utf-8")
        assert check_live_billing_authorization(tmp_path) is True
        assert_billing_authorized(tmp_path)

    def test_find_register_path_parent_walk(self, tmp_path):
        from app.services.billing_guard import _find_register_path
        reg_dir = tmp_path / "docs" / "roadmap" / "production_readiness"
        reg_dir.mkdir(parents=True)
        reg_file = reg_dir / "true_state_remediation_register.json"
        reg_file.write_text("{}", encoding="utf-8")

        nested_child = tmp_path / "a" / "b" / "c"
        nested_child.mkdir(parents=True)

        found = _find_register_path(nested_child)
        assert found == reg_file.resolve()

    def test_sanitize_billing_webhook(self, tmp_path):
        from app.services.billing_guard import sanitize_billing_webhook
        import json

        # Locked -> raises
        with pytest.raises(BillingLockError):
            sanitize_billing_webhook({"id": "evt_123"}, root_dir=tmp_path)

        # Unlocked -> returns processed
        reg_dir = tmp_path / "docs" / "roadmap" / "production_readiness"
        reg_dir.mkdir(parents=True)
        reg_file = reg_dir / "true_state_remediation_register.json"
        data_auth = {
            "authority_boundaries": {
                "live_payment_processing_authorised": True,
                "billing_launch_authorised": True,
            }
        }
        reg_file.write_text(json.dumps(data_auth), encoding="utf-8")

        result = sanitize_billing_webhook({"id": "evt_123"}, root_dir=tmp_path)
        assert result == {"status": "processed", "event_id": "evt_123"}
