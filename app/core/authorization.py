"""Object-level authorization policy helpers for learner-scoped resources."""
from __future__ import annotations

from typing import Any, Protocol

from fastapi import HTTPException, status

from app.models import UserRole


class LearnerLike(Protocol):
    id: str
    guardian_id: str


def normalize_role(role: Any) -> str:
    value = getattr(role, "value", role)
    return str(value or "").lower()


def can_access_learner(current_user: dict[str, Any], learner: LearnerLike) -> bool:
    """Return whether the current actor may access learner-level data.

    Current policy baseline:
    - admins may access learner records for operational/legal workflows
    - parent/guardian actors may access only learners linked to their account
    - learner self-access is allowed only when the token subject matches learner.id
    - teacher/support/content/compliance roles require assignment/scope tables before access
    """
    role = normalize_role(current_user.get("role"))
    subject = str(current_user.get("sub") or "")

    if role == UserRole.ADMIN.value:
        return True
    if role == UserRole.PARENT.value and str(learner.guardian_id) == subject:
        return True
    if role == UserRole.STUDENT.value and str(learner.id) == subject:
        return True
    return False


def assert_can_access_learner(current_user: dict[str, Any], learner: LearnerLike) -> None:
    if not can_access_learner(current_user, learner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised to access this learner",
        )


__all__ = ["assert_can_access_learner", "can_access_learner", "normalize_role"]
