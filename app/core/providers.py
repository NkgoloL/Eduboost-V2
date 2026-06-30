"""Centralized service providers for FastAPI dependency injection.

This module exposes small dependency functions that construct service
objects with their infrastructure dependencies (primarily `db`).
Routers should `Depends(providers.get_learner_service)` instead of
constructing services inline.
"""
from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

# Import service classes lazily to avoid import cycles
from app.services.learner_service import LearnerService
from app.services.audit_service import AuditService


async def get_learner_service(db: AsyncSession = Depends(get_db)) -> LearnerService:
    return LearnerService(db)


async def get_audit_service(db: AsyncSession = Depends(get_db)) -> AuditService:
    return AuditService(db)


# Add more providers as needed. Example:
async def get_lesson_service(db: AsyncSession = Depends(get_db)):
    from app.services.lesson_service_v2 import LessonServiceV2

    return LessonServiceV2(db)
