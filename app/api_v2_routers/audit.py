"""Audit routes for EduBoost V2."""

from fastapi import APIRouter

from app.services.audit_service import AuditService

router = APIRouter(prefix="/api/v2/audit", tags=["V2 Audit"])


@router.get("")
async def get_audit_feed(limit: int = 20):
    return await AuditService().get_recent_events(limit=limit)
