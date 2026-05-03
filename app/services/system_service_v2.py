from __future__ import annotations

from app.api.version import __version__


class SystemServiceV2:
    async def health(self) -> dict:
        return {"status": "ok", "version": __version__, "mode": "v2-baseline"}

    async def pillars(self) -> dict:
        return {
            "pillars": [
                "diagnostics",
                "executive",
                "judiciary",
                "audit",
                "ether",
            ]
        }

    async def schema_status(self) -> dict:
        return {"status": "ok", "schema": "v2"}
