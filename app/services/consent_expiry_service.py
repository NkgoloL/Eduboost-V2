"""Daily consent renewal reminder scheduler for expiring parental consent."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.core.logging import get_logger
from app.services.consent_renewal_service import ConsentRenewalService, SendGridEmailGateway

log = get_logger(__name__)


async def run_consent_expiry_scan() -> int:
    async with AsyncSessionLocal() as session:
        service = ConsentRenewalService(session, SendGridEmailGateway(settings), settings)
        stats = await service.run()
    return stats["reminded"]


async def consent_expiry_loop(
    interval_seconds: int = 24 * 3600,
    *,
    run_once: Callable[[], Awaitable[int]] = run_consent_expiry_scan,
) -> None:
    while True:
        try:
            count = await run_once()
            log.info("consent_expiry_scan_complete", count=count)
        except Exception as exc:
            log.warning("consent_expiry_scan_failed", error=str(exc))
        await asyncio.sleep(interval_seconds)
