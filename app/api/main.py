"""Legacy API entrypoint compatibility shim."""
from __future__ import annotations

from fastapi import HTTPException, status

from app.api_v2 import app


@app.post("/api/v1/lessons/generate", include_in_schema=False)
async def legacy_lesson_generate() -> None:
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="The V1 lesson generation endpoint has moved to /api/v2/lessons/generate.",
    )
