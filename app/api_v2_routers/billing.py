"""EduBoost V2 — Stripe Router (Phase 5.3)"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_parent_or_admin
from app.domain.schemas import CheckoutSessionResponse
from app.services.audit_service import AuditService
from app.services.stripe_service import StripeService

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/checkout", response_model=CheckoutSessionResponse)
@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_parent_or_admin),
):
    svc = StripeService(db)
    # Note: In production, retrieve email from encrypted field and decrypt
    url = await svc.create_checkout_session(
        guardian_id=current_user["sub"],
        email_plaintext="billing-placeholder",
    )
    return CheckoutSessionResponse(checkout_url=url)


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    stripe_signature: str = Header(alias="stripe-signature"),
):
    payload = await request.body()
    svc = StripeService(db)
    result = await svc.handle_webhook(payload, stripe_signature)

    # Record to audit trail
    audit = AuditService(db)
    await audit.record("STRIPE_WEBHOOK", payload=result)

    return result
