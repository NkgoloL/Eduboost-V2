"""tests/unit/test_subscription_service.py
Unit tests for SubscriptionService tier orchestration.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.services.subscription_service import SubscriptionService


@pytest.mark.unit
def test_subscription_service_init_stores_db():
    """Verify constructor stores database session."""
    db = AsyncMock()
    service = SubscriptionService(db)
    assert service.guardians is not None


@pytest.mark.unit
async def test_activate_premium_updates_guardian_and_cache():
    """Verify activate_premium updates guardian tier and cache."""
    db = AsyncMock()
    service = SubscriptionService(db)

    with patch.object(service.guardians, "update_subscription", new_callable=AsyncMock) as mock_update:
        with patch("app.services.subscription_service.cache_set", new_callable=AsyncMock) as mock_cache_set:
            with patch.object(service, "reset_ai_quota", new_callable=AsyncMock) as mock_reset:
                await service.activate_premium("guardian-123", "sub_456")

                mock_update.assert_called_once_with("guardian-123", "premium", "sub_456")
                mock_cache_set.assert_called_once_with("user_tier:guardian-123", "premium", ttl=30 * 24 * 3600)
                mock_reset.assert_called_once_with("guardian-123")


@pytest.mark.unit
async def test_activate_premium_without_stripe_id():
    """Verify activate_premium works without stripe subscription ID."""
    db = AsyncMock()
    service = SubscriptionService(db)

    with patch.object(service.guardians, "update_subscription", new_callable=AsyncMock) as mock_update:
        with patch("app.services.subscription_service.cache_set", new_callable=AsyncMock) as mock_cache_set:
            with patch.object(service, "reset_ai_quota", new_callable=AsyncMock) as mock_reset:
                await service.activate_premium("guardian-123")

                mock_update.assert_called_once_with("guardian-123", "premium", None)
                mock_cache_set.assert_called_once_with("user_tier:guardian-123", "premium", ttl=30 * 24 * 3600)
                mock_reset.assert_called_once_with("guardian-123")


@pytest.mark.unit
async def test_downgrade_to_free_updates_guardian_and_cache():
    """Verify downgrade_to_free updates guardian tier and cache."""
    db = AsyncMock()
    service = SubscriptionService(db)

    with patch.object(service.guardians, "update_subscription", new_callable=AsyncMock) as mock_update:
        with patch("app.services.subscription_service.cache_set", new_callable=AsyncMock) as mock_cache_set:
            with patch.object(service, "reset_ai_quota", new_callable=AsyncMock) as mock_reset:
                await service.downgrade_to_free("guardian-123")

                mock_update.assert_called_once_with("guardian-123", "free", None)
                mock_cache_set.assert_called_once_with("user_tier:guardian-123", "free", ttl=30 * 24 * 3600)
                mock_reset.assert_called_once_with("guardian-123")


@pytest.mark.unit
async def test_reset_ai_quota_deletes_cache_pattern():
    """Verify reset_ai_quota deletes AI quota cache pattern."""
    db = AsyncMock()
    service = SubscriptionService(db)

    with patch("app.services.subscription_service.cache_delete_pattern", new_callable=AsyncMock) as mock_delete:
        await service.reset_ai_quota("guardian-123")

        mock_delete.assert_called_once_with("ai_quota:guardian-123:*")
