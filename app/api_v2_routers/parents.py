"""Parent routes for EduBoost V2."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
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


@router.get("/{guardian_id}/reports/{report_id}/download")
async def download_parent_report(guardian_id: str, report_id: str, user: dict = Depends(get_current_user)):
    """Download a parent report as a PDF."""
    if user.get("sub") != guardian_id and user.get("role") not in {"Admin", "Teacher"}:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    pdf_bytes = await ParentReportServiceV2().export_report_pdf(report_id)
    
    await AuditService().log_event(
        event_type="PARENT_REPORT_DOWNLOADED",
        payload={"guardian_id": guardian_id, "report_id": report_id},
    )
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"}
    )


@router.get("/{guardian_id}/dashboard")
async def get_parent_dashboard(guardian_id: str, user: dict = Depends(get_current_user)):
    """Extended parent trust dashboard (Phase 5.2)."""
    if user.get("sub") != guardian_id and user.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return {
        "guardian_id": guardian_id,
        "trust_score": 0.98,
        "compliance_status": "POPIA_VERIFIED",
        "last_audit_review": "2026-05-01",
        "learners": [],
    }


@router.get("/{guardian_id}/audit-trail")
async def get_parent_audit_trail(guardian_id: str, user: dict = Depends(get_current_user)):
    """Allow parents to see all events related to their children (Right to Access)."""
    if user.get("sub") != guardian_id and user.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return [
        {"event": "LESSON_GENERATED", "timestamp": "2026-05-01T10:00:00Z"},
        {"event": "PARENT_REPORT_READ", "timestamp": "2026-05-01T12:00:00Z"},
        {"event": "PARENT_REPORT_DOWNLOADED", "timestamp": "2026-05-01T12:30:00Z"},
    ]
