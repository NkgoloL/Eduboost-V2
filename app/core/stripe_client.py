"""
EduBoost V2 — Stripe Subscription Service (Phase 5)
Tiered billing: Free vs Premium. Webhooks update Guardian.subscription_tier.
"""
from __future__ import annotations

import stripe
from fastapi import HTTPException, status
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.models import Guardian
from app.repositories.auth_repository import GuardianRepository
from app.repositories.stripe_event_repository import StripeEventRepository
from app.services.subscription_service import SubscriptionService

log = get_logger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._guardian_repo = GuardianRepository(db)
        self._event_repo = StripeEventRepository(db)

    async def create_checkout_session(self, guardian_id: str, email_plaintext: str) -> str:
        """Create a Stripe Checkout session. Returns the checkout URL."""
        guardian = await self._guardian_repo.get_by_id(guardian_id)
        if not guardian:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guardian not found")

        # Create or retrieve Stripe customer
        customer_id = guardian.stripe_customer_id
        if not customer_id:
            customer = stripe.Customer.create(email=email_plaintext, metadata={"guardian_id": guardian_id})
            customer_id = customer.id
            await self._db.execute(
                update(Guardian)
                .where(Guardian.id == guardian_id)
                .values(stripe_customer_id=customer_id)
            )
            await self._guardian_repo.update_subscription(guardian_id, "free", None)

        checkout = stripe.checkout.Session.create(
            customer=customer_id,
            mode="subscription",
            line_items=[{"price": settings.STRIPE_PRICE_ID_PREMIUM, "quantity": 1}],
            success_url="http://localhost:3000/dashboard?upgraded=true",
            cancel_url="http://localhost:3000/dashboard?cancelled=true",
            metadata={"guardian_id": guardian_id},
        )
        return checkout.url  # type: ignore[return-value]

    async def handle_webhook(self, payload: bytes, sig_header: str) -> dict:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except stripe.error.SignatureVerificationError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Stripe signature") from exc

        if await self._event_repo.is_processed(event["id"]):
            log.info("stripe_webhook_duplicate", event_id=event["id"])
            return {"status": "already_processed"}

        await self._event_repo.record(event["id"], event["type"], dict(event))

        match event["type"]:
            case "customer.subscription.created" | "customer.subscription.updated":
                await self._handle_subscription_change(event["data"]["object"], active=True)
            case "customer.subscription.deleted":
                await self._handle_subscription_change(event["data"]["object"], active=False)
            case "invoice.payment_failed":
                await self._handle_invoice_payment_failed(event["data"]["object"])

        return {"status": "processed"}

    async def _handle_subscription_change(self, subscription: dict, active: bool) -> None:
        guardian_id = subscription.get("metadata", {}).get("guardian_id")
        if not guardian_id:
            log.warning("stripe_no_guardian_id", subscription_id=subscription.get("id"))
            return
        new_tier = "premium" if active and subscription.get("status") == "active" else "free"
        subscriptions = SubscriptionService(self._db)
        if new_tier == "premium":
            await subscriptions.activate_premium(guardian_id, subscription.get("id"))
        else:
            await subscriptions.downgrade_to_free(guardian_id)
        log.info("subscription_updated", guardian_id=guardian_id, tier=new_tier)

    async def _handle_invoice_payment_failed(self, invoice: dict) -> None:
        subscription_id = invoice.get("subscription")
        customer_id = invoice.get("customer")
        if customer_id:
            guardian = await self._guardian_repo.get_by_stripe_customer_id(customer_id)
            if guardian is not None:
                await SubscriptionService(self._db).downgrade_to_free(guardian.id)
        log.warning("stripe_invoice_payment_failed", subscription_id=subscription_id, customer_id=customer_id)
