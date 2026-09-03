"""EduBoost V2 — Stripe Router (Phase 5.3)"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Header, Request, status
from app.core.envelope_route import EnvelopedRoute
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v2_deps.auth import AuthContext, require_parent_or_admin
from app.core.database import get_db
from app.domain.schemas import CheckoutSessionResponse
from app.services.audit_service import AuditService
from app.core import providers
from app.services.billing_guard import assert_billing_authorized
from app.services.stripe_service import StripeService

router = APIRouter(route_class=EnvelopedRoute, prefix="/billing", tags=["billing"])


@router.post("/checkout", response_model=CheckoutSessionResponse)
@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout(
    db: AsyncSession = Depends(get_db),
    current_user: AuthContext = Depends(require_parent_or_admin),
    _auth_guard: None = Depends(assert_billing_authorized),
):
    assert_billing_authorized()
    svc = StripeService(db)
    # Note: In production, retrieve email from encrypted field and decrypt
    url = await svc.create_checkout_session(
        guardian_id=current_user.user_id,
        email_plaintext="billing-placeholder",
    )
    return CheckoutSessionResponse(checkout_url=url)


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    stripe_signature: str = Header(alias="stripe-signature"),
    audit: AuditService = Depends(providers.get_audit_service),
    _auth_guard: None = Depends(assert_billing_authorized),
):
    assert_billing_authorized()
    payload = await request.body()
    svc = StripeService(db)
    result = await svc.handle_webhook(payload, stripe_signature)

    # Record to audit trail
    await audit.record("STRIPE_WEBHOOK", payload=result)

    return result

