"""Learner routes for EduBoost V2."""

from fastapi import APIRouter, HTTPException

from app.services.audit_service import AuditService
from app.services.learner_service import LearnerService

router = APIRouter(prefix="/api/v2/learners", tags=["V2 Learners"])


@router.get("/{learner_id}")
async def get_learner(learner_id: str):
    learner = await LearnerService().get_learner_summary(learner_id)
    if learner is None:
        raise HTTPException(status_code=404, detail="Learner not found")
    await AuditService().log_event(
        event_type="LEARNER_READ",
        learner_id=learner_id,
        payload={"route": "/api/v2/learners/{learner_id}"},
    )
    return learner
