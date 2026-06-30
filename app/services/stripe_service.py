"""Billing service facade with graceful optional-provider behavior."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.degraded_mode import require_optional_capability
from app.core.stripe_client import StripeService as _StripeService


class StripeService(_StripeService):
	def __init__(self, db: AsyncSession) -> None:
		require_optional_capability("billing")
		super().__init__(db)
