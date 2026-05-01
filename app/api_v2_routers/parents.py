"""Parent routes for EduBoost V2."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
from app.services.parent_report_service_v2 import ParentReportServiceV2

router = APIRouter(prefix="/api/v2/parents", tags=["V2 Parents"])
bearer = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return AuthService().decode_token(credentials.credentials)


@router.get("/{guardian_id}/reports/{learner_id}")
async def get_parent_report(guardian_id: str, learner_id: str, user: dict = Depends(get_current_user)):
    if user.get("sub") != guardian_id and user.get("role") not in {"Admin", "Teacher"}:
        raise HTTPException(status_code=403, detail="Forbidden")
    report = await ParentReportServiceV2().build_report(learner_id=learner_id, guardian_id=guardian_id)
    await AuditService().log_event(
        event_type="PARENT_REPORT_READ",
        learner_id=learner_id,
        payload={"guardian_id": guardian_id},
    )
    return report
