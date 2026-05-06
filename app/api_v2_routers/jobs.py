"""Background job status routes for EduBoost V2."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.jobs import get_job
from app.core.security import get_current_user, require_admin
from app.core.redis import get_redis
from app.domain.api_v2_models import JobStatusResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    _: dict = Depends(get_current_user),
) -> JobStatusResponse:
    job = await get_job(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return JobStatusResponse.model_validate(job)


@router.get("/stats/worker", tags=["ops"])
async def get_worker_stats(
    _: dict = Depends(require_admin),
) -> dict:
    """Get basic arq worker stats from Redis."""
    try:
        redis = get_redis()
        # arq uses several keys. We can look for the health check key or just general info.
        keys = await redis.keys("arq:health-check:*")
        health = {}
        for key in keys:
            val = await redis.get(key)
            health[key] = val
            
        return {
            "status": "ok",
            "health_checks": health,
            "queue_name": "default"
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "detail": str(exc)}
