"""Learner content API router.

This router provides learner-facing read access to production-promoted
Content Factory artifacts only. It enforces the production gate rules:
- Learners see production only
- No learner may see draft, generated, pending_review, rejected, quarantined,
  validation_failed, or staging-only content
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api_v2_deps.auth import AuthContext, require_auth_context
from app.core.security import get_current_user  # noqa: F401
from app.services.content_learner_read_service import (
    ContentLearnerReadService,
    LearnerDiagnosticItem,
    LearnerLesson,
    LearnerScopeContentSummary,
)

router = APIRouter(prefix="/learner/content", tags=["learner-content"])


def get_learner_read_service() -> ContentLearnerReadService:
    """Get learner read service instance."""
    return ContentLearnerReadService()


@router.get("/scopes/{scope_id}/summary")
async def get_scope_summary(
    scope_id: str,
    current_user: Annotated[AuthContext, Depends(require_auth_context)],
    session: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[ContentLearnerReadService, Depends(get_learner_read_service)],
) -> LearnerScopeContentSummary:
    """Get summary of learner-visible content for a scope.

    Args:
        scope_id: Content scope ID

    Returns:
        Summary of learner-visible content
    """
    return await service.get_scope_content_summary(session, scope_id)


@router.get("/scopes/{scope_id}/diagnostic-items")
async def get_diagnostic_items(
    scope_id: str,
    current_user: Annotated[AuthContext, Depends(require_auth_context)],
    session: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[ContentLearnerReadService, Depends(get_learner_read_service)],
    caps_ref: str | None = None,
    limit: int = 20,
) -> list[LearnerDiagnosticItem]:
    """Get learner-visible diagnostic items for a scope.

    Args:
        scope_id: Content scope ID
        caps_ref: Optional CAPS reference filter
        limit: Maximum number of items to return

    Returns:
        List of learner-visible diagnostic items
    """
    return await service.get_diagnostic_items(
        session,
        scope_id=scope_id,
        caps_ref=caps_ref,
        limit=limit,
    )


@router.get("/scopes/{scope_id}/lessons")
async def get_lessons(
    scope_id: str,
    current_user: Annotated[AuthContext, Depends(require_auth_context)],
    session: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[ContentLearnerReadService, Depends(get_learner_read_service)],
    caps_ref: str | None = None,
    limit: int = 20,
) -> list[LearnerLesson]:
    """Get learner-visible lessons for a scope.

    Args:
        scope_id: Content scope ID
        caps_ref: Optional CAPS reference filter
        limit: Maximum number of items to return

    Returns:
        List of learner-visible lessons
    """
    return await service.get_lessons(
        session,
        scope_id=scope_id,
        caps_ref=caps_ref,
        limit=limit,
    )


@router.get("/scopes/{scope_id}/caps/{caps_ref}/diagnostic-items")
async def get_diagnostic_items_by_caps_ref(
    scope_id: str,
    caps_ref: str,
    current_user: Annotated[AuthContext, Depends(require_auth_context)],
    session: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[ContentLearnerReadService, Depends(get_learner_read_service)],
    limit: int = 20,
) -> list[LearnerDiagnosticItem]:
    """Get learner-visible diagnostic items for a scope and CAPS reference.

    Args:
        scope_id: Content scope ID
        caps_ref: CAPS reference
        limit: Maximum number of items to return

    Returns:
        List of learner-visible diagnostic items
    """
    return await service.get_diagnostic_items(
        session,
        scope_id=scope_id,
        caps_ref=caps_ref,
        limit=limit,
    )


@router.get("/scopes/{scope_id}/caps/{caps_ref}/lessons")
async def get_lessons_by_caps_ref(
    scope_id: str,
    caps_ref: str,
    current_user: Annotated[AuthContext, Depends(require_auth_context)],
    session: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[ContentLearnerReadService, Depends(get_learner_read_service)],
    limit: int = 20,
) -> list[LearnerLesson]:
    """Get learner-visible lessons for a scope and CAPS reference.

    Args:
        scope_id: Content scope ID
        caps_ref: CAPS reference
        limit: Maximum number of items to return

    Returns:
        List of learner-visible lessons
    """
    return await service.get_lessons(
        session,
        scope_id=scope_id,
        caps_ref=caps_ref,
        limit=limit,
    )
