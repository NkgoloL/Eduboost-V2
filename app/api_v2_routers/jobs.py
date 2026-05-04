"""Background job status routes for EduBoost V2."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.jobs import get_job
from app.core.security import get_current_user
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
