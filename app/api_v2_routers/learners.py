"""Learner routes for EduBoost V2."""

from fastapi import APIRouter, HTTPException, Depends

from app.services.audit_service import AuditService
from app.services.learner_service import LearnerService
from app.core.dependencies import get_current_user

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


@router.delete("/{learner_id}")
async def delete_learner(
    learner_id: str,
    user: dict = Depends(get_current_user),
):
    """Right to Erasure endpoint. Requires Guardian role and ownership link."""
    from app.repositories.parent_report_repository import ParentReportRepository
    
    # 1. Ensure caller is a Guardian or Admin
    if user.get("role") not in {"Parent", "Admin"}:
        raise HTTPException(status_code=403, detail="Only parents or admins can delete learners")

    # 2. If Parent, verify ownership link
    if user.get("role") == "Parent":
        guardian_id = user.get("sub")
        is_linked = await ParentReportRepository().verify_guardian_link(learner_id, guardian_id)
        if not is_linked:
            raise HTTPException(status_code=403, detail="You do not have authority over this learner")

    # 3. Execute erasure
    success = await LearnerService().delete_learner(learner_id)
    if not success:
        raise HTTPException(status_code=404, detail="Learner not found or already deleted")
    
    return {"status": "erasure_initiated", "learner_id": learner_id}
