"""Audit routes for EduBoost V2."""

from fastapi import APIRouter, Depends
from app.core.envelope_route import EnvelopedRoute
from app.api_v2_deps.auth import require_auth_context
from app.core.security import get_current_user  # noqa: F401

from app.services.audit_service import AuditService

router = APIRouter(route_class=EnvelopedRoute, prefix="/audit", tags=["V2 Audit"])


@router.get("", dependencies=[Depends(require_auth_context)])
async def get_audit_feed(limit: int = 20):
    return await AuditService().get_recent_events(limit=limit)


@router.get("/feed", dependencies=[Depends(require_auth_context)])
async def get_audit_feed_alias(limit: int = 20):
    return await AuditService().get_recent_events(limit=limit)
