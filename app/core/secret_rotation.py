"""Azure Key Vault refresh loop for hot-reloading production secrets."""
from __future__ import annotations

import asyncio

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)


async def refresh_key_vault_secrets_once() -> bool:
    if not settings.is_production() or not settings.AZURE_KEY_VAULT_URL:
        return False

    updated = settings.refresh_from_key_vault()
    log.info("key_vault_secrets_refreshed", updated=sorted(updated))
    return True


async def key_vault_rotation_loop() -> None:
    interval_seconds = max(1, settings.KEY_VAULT_REFRESH_INTERVAL_HOURS) * 3600
    while True:
        try:
            await refresh_key_vault_secrets_once()
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            log.warning("key_vault_secret_refresh_failed", error=str(exc))
        await asyncio.sleep(interval_seconds)
