"""Daily consent-expiry scan and guardian notification hook."""
from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.logging import get_logger
from app.models import ParentalConsent

log = get_logger(__name__)


async def run_consent_expiry_scan() -> int:
    threshold = datetime.now(UTC) + timedelta(days=14)
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ParentalConsent).where(
                ParentalConsent.revoked_at.is_(None),
                ParentalConsent.expires_at < threshold,
            )
        )
        consents = list(result.scalars().all())

    for consent in consents:
        await notify_guardian_consent_expiring(consent.guardian_id, consent.learner_id, consent.expires_at)

    return len(consents)


async def notify_guardian_consent_expiring(guardian_id: str, learner_id: str, expires_at: datetime) -> None:
    # SendGrid integration point. Keep this POPIA-safe: no learner names or emails in logs.
    log.info(
        "consent_expiry_notice_due",
        guardian_id=guardian_id,
        learner_id=learner_id,
        expires_at=expires_at.isoformat(),
    )


async def consent_expiry_loop(interval_seconds: int = 24 * 3600) -> None:
    while True:
        try:
            count = await run_consent_expiry_scan()
            log.info("consent_expiry_scan_complete", count=count)
        except Exception as exc:
            log.warning("consent_expiry_scan_failed", error=str(exc))
        await asyncio.sleep(interval_seconds)
