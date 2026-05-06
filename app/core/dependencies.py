"""
EduBoost SA — FastAPI Dependencies
Reusable dependency injections: current user, consent gate, DB session.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AuthenticationError, ConsentRequiredError
from app.core.metrics import consent_gate_blocks_total
from app.core.security import decode_token
from app.repositories.consent_repository import ConsentRepository

_bearer = HTTPBearer(auto_error=False)


# ── Repositories & Services ───────────────────────────────────────────────────

async def get_consent_repo() -> ConsentRepository:
    return ConsentRepository()


# ── Current User ──────────────────────────────────────────────────────────────

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> UUID:
    """Extract and validate the current user's UUID from the Bearer token."""
    if credentials is None:
        raise AuthenticationError("Authorization header missing")
    try:
        payload = decode_token(credentials.credentials)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise ValueError("Token subject missing")
        return UUID(user_id_str)
    except (JWTError, ValueError) as exc:
        raise AuthenticationError("Invalid or expired token") from exc


async def get_current_guardian_id(
    user_id: UUID = Depends(get_current_user_id),
) -> UUID:
    """Alias for guardian-only endpoints (role check can be added here)."""
    return user_id


# ── Consent Gate ──────────────────────────────────────────────────────────────

async def require_active_consent(
    learner_id: UUID,
    db: AsyncSession = Depends(get_db),
    repo: ConsentRepository = Depends(get_consent_repo),
) -> None:
    """
    POPIA consent gate — inject as a router-level dependency.
    Blocks any learner-data endpoint if active parental consent is absent.

    Usage:
        @router.get(
            "/lessons/{lesson_id}",
            dependencies=[Depends(require_active_consent)],
        )
        async def get_lesson(lesson_id: UUID, learner_id: UUID): ...

    This makes the consent requirement:
    - Declarative (visible in the function signature and OpenAPI schema)
    - Impossible to forget (not an inline service call)
    - Consistently enforced across all learner-data routes
    """
    consent = await repo.get_active(learner_id, db)

    if consent is None:
        consent_gate_blocks_total.labels(endpoint="unknown").inc()
        raise ConsentRequiredError(
            "Active parental consent is required to access learner data. "
            "Please ask a guardian to grant consent via the parent portal.",
            details={"learner_id": str(learner_id)},
        )


async def require_active_consent_for_current_learner(
    learner_id: UUID,
    db: AsyncSession = Depends(get_db),
    repo: ConsentRepository = Depends(get_consent_repo),
    _user_id: UUID = Depends(get_current_user_id),
) -> UUID:
    """
    Combined auth + consent gate for learner-scoped endpoints.
    Returns learner_id for use in endpoint handler.
    """
    await require_active_consent(learner_id, db, repo)
    return learner_id


# ── Observability ─────────────────────────────────────────────────────────────

from fastapi import Request

async def get_request_id(request: Request) -> str:
    """Retrieve the correlation/request ID from the headers."""
    return request.headers.get("X-Request-ID", "unknown")
