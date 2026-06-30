from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth_application_service import AuthApplicationService, build_auth_application_service


def get_auth_application_service(db: AsyncSession = Depends(get_db)) -> AuthApplicationService:
    return build_auth_application_service(db)


__all__ = ["AuthApplicationService", "get_auth_application_service"]
