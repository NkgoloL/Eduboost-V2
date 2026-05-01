"""System routes for EduBoost V2."""

from fastapi import APIRouter

from app.services.system_service_v2 import SystemServiceV2

router = APIRouter(prefix="/api/v2/system", tags=["V2 System"])


@router.get("/health")
async def get_health():
    return await SystemServiceV2().health()


@router.get("/pillars")
async def get_pillars():
    return await SystemServiceV2().pillars()


@router.get("/schema-status")
async def get_schema_status():
    return await SystemServiceV2().schema_status()
