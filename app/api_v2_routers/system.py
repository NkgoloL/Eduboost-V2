"""System routes for EduBoost V2."""

from fastapi import APIRouter
from app.core.envelope_route import EnvelopedRoute

from app.services.system_service_v2 import SystemServiceV2
from app.core.degraded_mode import capabilities_payload

router = APIRouter(route_class=EnvelopedRoute, prefix="/system", tags=["V2 System"])


@router.get("/health")
async def get_health():
    return await SystemServiceV2().health()


@router.get("/pillars")
async def get_pillars():
    return await SystemServiceV2().pillars()


@router.get("/schema-status")
async def get_schema_status():
    return await SystemServiceV2().schema_status()


@router.get("/capabilities")
async def get_capabilities():
    return capabilities_payload()
