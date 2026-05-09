"""FastAPI dependency adapters for object-level authorization."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Annotated

from fastapi import Header, HTTPException, status

from app.security.object_authorization import (
    Actor,
    AuthorizationDecision,
    Permission,
    Role,
    can_access_learner,
)

ROLE_HEADER = "X-EduBoost-Roles"
SUBJECT_HEADER = "X-EduBoost-Subject-Id"
LEARNER_IDS_HEADER = "X-EduBoost-Learner-Ids"
GUARDIAN_LEARNER_IDS_HEADER = "X-EduBoost-Guardian-Learner-Ids"
EDUCATOR_LEARNER_IDS_HEADER = "X-EduBoost-Educator-Learner-Ids"


def _split_header_values(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(part.strip() for part in value.split(",") if part.strip())


def _parse_roles(raw_roles: Iterable[str]) -> tuple[Role, ...]:
    roles: list[Role] = []
    for raw_role in raw_roles:
        try:
            roles.append(Role(raw_role))
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Unsupported role: {raw_role}",
            ) from exc
    return tuple(roles)


def build_actor_from_headers(
    *,
    subject_id: str | None,
    roles: str | None,
    learner_ids: str | None = None,
    guardian_learner_ids: str | None = None,
    educator_learner_ids: str | None = None,
) -> Actor:
    """Build an authorization Actor from request header values."""
    if not subject_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authenticated subject.",
        )

    parsed_roles = _parse_roles(_split_header_values(roles))
    if not parsed_roles:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authenticated roles.",
        )

    return Actor.from_values(
        subject_id=subject_id,
        roles=parsed_roles,
        learner_ids=_split_header_values(learner_ids),
        guardian_learner_ids=_split_header_values(guardian_learner_ids),
        educator_learner_ids=_split_header_values(educator_learner_ids),
    )


async def get_authorization_actor(
    subject_id: Annotated[str | None, Header(alias=SUBJECT_HEADER)] = None,
    roles: Annotated[str | None, Header(alias=ROLE_HEADER)] = None,
    learner_ids: Annotated[str | None, Header(alias=LEARNER_IDS_HEADER)] = None,
    guardian_learner_ids: Annotated[
        str | None,
        Header(alias=GUARDIAN_LEARNER_IDS_HEADER),
    ] = None,
    educator_learner_ids: Annotated[
        str | None,
        Header(alias=EDUCATOR_LEARNER_IDS_HEADER),
    ] = None,
) -> Actor:
    """Resolve the current request's authorization actor."""
    return build_actor_from_headers(
        subject_id=subject_id,
        roles=roles,
        learner_ids=learner_ids,
        guardian_learner_ids=guardian_learner_ids,
        educator_learner_ids=educator_learner_ids,
    )


def raise_for_learner_access(
    *,
    actor: Actor,
    learner_id: str,
    permission: str | Permission = Permission.READ,
) -> AuthorizationDecision:
    """Authorize learner access or raise a FastAPI 403 error."""
    decision = can_access_learner(actor, learner_id, permission=permission)
    if decision.allowed:
        return decision

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "code": "object_forbidden",
            "message": "Actor is not authorized to access this learner-scoped object.",
            "reason": decision.reason,
            "learner_id": decision.learner_id,
            "permission": decision.permission.value,
        },
    )


def require_learner_read(actor: Actor, learner_id: str) -> AuthorizationDecision:
    """Authorize learner read access or raise 403."""
    return raise_for_learner_access(
        actor=actor,
        learner_id=learner_id,
        permission=Permission.READ,
    )


def require_learner_write(actor: Actor, learner_id: str) -> AuthorizationDecision:
    """Authorize learner write access or raise 403."""
    return raise_for_learner_access(
        actor=actor,
        learner_id=learner_id,
        permission=Permission.WRITE,
    )


def require_learner_delete(actor: Actor, learner_id: str) -> AuthorizationDecision:
    """Authorize learner delete access or raise 403."""
    return raise_for_learner_access(
        actor=actor,
        learner_id=learner_id,
        permission=Permission.DELETE,
    )
