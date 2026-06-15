"""Phase 6 admin AI operations, budget, and provider-health routes."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v2_deps.auth import AuthContext, require_admin
from app.core.database import get_db
from app.core.envelope_route import EnvelopedRoute
from app.domain.ai_operations_schemas import (
    BudgetCounterView,
    ProviderHealthView,
    ReservationCancelRequest,
    ReservationView,
    UsageEventView,
)
from app.models.ai_operations import AIUsageEvent, AIUsageReservation
from app.services.ai_operations import AIOperationsService

router = APIRouter(
    route_class=EnvelopedRoute,
    prefix="/admin/ai-operations",
    tags=["admin-ai-operations"],
    dependencies=[Depends(require_admin)],
)


@router.get("/budgets/users/{user_id}", response_model=BudgetCounterView)
async def get_user_budget(user_id: str, db: AsyncSession = Depends(get_db)):
    return BudgetCounterView.model_validate(
        await AIOperationsService(db).counter_view(scope_type="user", scope_id=user_id)
    )


@router.get("/budgets/tenants/{tenant_id}", response_model=BudgetCounterView)
async def get_tenant_budget(tenant_id: str, db: AsyncSession = Depends(get_db)):
    return BudgetCounterView.model_validate(
        await AIOperationsService(db).counter_view(scope_type="tenant", scope_id=tenant_id)
    )


@router.get("/usage", response_model=list[UsageEventView])
async def list_usage(
    tenant_id: str | None = Query(default=None),
    provider: str | None = Query(default=None),
    purpose: str | None = Query(default=None),
    hours: int = Query(default=24, ge=1, le=24 * 31),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(AIUsageEvent).where(
        AIUsageEvent.created_at >= datetime.now(UTC) - timedelta(hours=hours)
    )
    if tenant_id:
        stmt = stmt.where(AIUsageEvent.tenant_id == tenant_id)
    if provider:
        stmt = stmt.where(AIUsageEvent.provider == provider)
    if purpose:
        stmt = stmt.where(AIUsageEvent.purpose == purpose)
    rows = list((await db.scalars(stmt.order_by(AIUsageEvent.created_at.desc()).limit(limit))).all())
    return [UsageEventView.model_validate(row) for row in rows]


@router.get("/providers/health", response_model=list[ProviderHealthView])
async def provider_health(db: AsyncSession = Depends(get_db)):
    return [ProviderHealthView.model_validate(row) for row in await AIOperationsService(db).provider_health()]


@router.get("/reservations", response_model=list[ReservationView])
async def list_reservations(
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(AIUsageReservation)
    if status:
        stmt = stmt.where(AIUsageReservation.status == status)
    rows = list((await db.scalars(stmt.order_by(AIUsageReservation.reserved_at.desc()).limit(limit))).all())
    return [ReservationView.model_validate(row) for row in rows]


@router.post("/reservations/{operation_id}/cancel", response_model=ReservationView)
async def cancel_reservation(
    operation_id: str,
    body: ReservationCancelRequest,
    auth: AuthContext = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    reservation = await AIOperationsService(db).cancel(operation_id, body.reason)
    if reservation is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="AI usage reservation not found")
    reservation.metadata_json = {
        **(reservation.metadata_json or {}),
        "cancelled_by": str(auth.user_id),
    }
    await db.commit()
    await db.refresh(reservation)
    return ReservationView.model_validate(reservation)
