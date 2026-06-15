"""Strict API schemas for Phase 6 AI operations and budgets."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)


class BudgetCounterView(StrictModel):
    scope_type: Literal["user", "tenant", "global"]
    scope_id: str
    period_key: str
    used_tokens: int = Field(ge=0)
    reserved_tokens: int = Field(ge=0)
    token_limit: int = Field(gt=0)
    remaining_tokens: int = Field(ge=0)
    used_cost_usd: Decimal = Field(ge=0)
    alert_threshold_reached: bool
    updated_at: datetime


class UsageEventView(StrictModel):
    event_id: UUID
    operation_id: str
    user_id: str
    tenant_id: str
    purpose: str
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: Decimal
    outcome: str
    created_at: datetime


class ReservationCancelRequest(StrictModel):
    reason: str = Field(min_length=3, max_length=96)


class ReservationView(StrictModel):
    reservation_id: UUID
    operation_id: str
    user_id: str
    tenant_id: str
    purpose: str
    estimated_tokens: int
    status: str
    failure_reason: str | None
    reserved_at: datetime
    expires_at: datetime
    finalized_at: datetime | None


class ProviderHealthView(StrictModel):
    provider: str
    calls_24h: int
    errors_24h: int
    fallback_24h: int
    error_rate: float = Field(ge=0, le=1)
    status: Literal["healthy", "degraded", "unavailable", "unused"]
