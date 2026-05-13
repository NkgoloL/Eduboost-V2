"""Audit routes for EduBoost V2."""

from fastapi import APIRouter
from app.core.envelope_route import EnvelopedRoute

from app.services.audit_service import AuditService

router = APIRouter(route_class=EnvelopedRoute, prefix="/audit", tags=["V2 Audit"])


@router.get("")
async def get_audit_feed(limit: int = 20):
    return await AuditService().get_recent_events(limit=limit)


@router.get("/feed")
async def get_audit_feed_alias(limit: int = 20):
    return await AuditService().get_recent_events(limit=limit)
