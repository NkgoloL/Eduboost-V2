from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth_runtime_boundary import AuthRuntimeContext, build_auth_runtime_context


def get_auth_runtime_context(db: AsyncSession = Depends(get_db)) -> AuthRuntimeContext:
    return build_auth_runtime_context(db)


__all__ = ["AuthRuntimeContext", "get_auth_runtime_context"]
