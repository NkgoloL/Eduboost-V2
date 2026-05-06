"""Audit routes for EduBoost V2."""

from fastapi import APIRouter, Depends

from app.services.audit_service import AuditService
from app.core import providers

router = APIRouter(prefix="/audit", tags=["V2 Audit"])


@router.get("")
async def get_audit_feed(limit: int = 20, audit: AuditService = Depends(providers.get_audit_service)):
    return await audit.get_recent_events(limit=limit)


@router.get("/feed")
async def get_audit_feed_alias(limit: int = 20, audit: AuditService = Depends(providers.get_audit_service)):
    return await audit.get_recent_events(limit=limit)
