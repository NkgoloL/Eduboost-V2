"""
Archived legacy API entrypoint compatibility shim.

Phase 7 (7.6): The /api/v1/lessons/generate route is retained only as a
410 Gone tombstone so that any stale clients receive a clear deprecation
signal rather than a 404. No V1 business logic is present here; all active
routes are on /api/v2/. The _has_legacy_lesson_generate_route guard has been
removed — the tombstone is registered unconditionally.
"""
from __future__ import annotations

import logging
from importlib import import_module

from fastapi import FastAPI, HTTPException

log = logging.getLogger(__name__)

_canonical_app = import_module("app.api_v2").app

app = FastAPI(
    title=_canonical_app.title,
    version=_canonical_app.version,
    description=_canonical_app.description,
    docs_url=_canonical_app.docs_url,
    redoc_url=_canonical_app.redoc_url,
)
app.router.routes = list(_canonical_app.router.routes)
app.exception_handlers.update(_canonical_app.exception_handlers)


async def legacy_lesson_generate_gone() -> None:
    """410 tombstone for the retired V1 lesson-generation endpoint."""
    log.warning(
        "deprecated_v1_route_called",
        extra={"path": "/api/v1/lessons/generate", "action": "rejected_410"},
    )
    raise HTTPException(
        status_code=410,
        detail="Legacy lesson generation moved to /api/v2/lessons/generate.",
    )


# Register 410 tombstone unconditionally — no active V1 routes remain (7.6).
app.add_api_route(
    "/api/v1/lessons/generate",
    legacy_lesson_generate_gone,
    methods=["POST"],
    include_in_schema=False,
    name="legacy_lesson_generate_gone",
)
