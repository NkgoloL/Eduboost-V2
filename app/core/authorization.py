"""
app/core/authorization.py
--------------------------
Object-level authorization policy helpers for EduBoost SA V2.

Implements §3.6 P0 — all named policy helpers:
  can_view_learner, can_update_learner, can_generate_lesson_for_learner,
  can_start_diagnostic_for_learner, can_view_study_plan,
  can_view_parent_report, can_export_learner_data, can_request_erasure,
  can_view_billing

Each helper takes a resolved ``CurrentUser`` and the relevant resource
identifier, returning bool.  Routers call these helpers and raise HTTP 403
on False — business logic must never access a resource without passing the
relevant check.

Audit events for privileged access are emitted here (§3.6 P0).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from app.domain.roles import Role

logger = logging.getLogger("eduboost.authorization")


# ---------------------------------------------------------------------------
# CurrentUser protocol — satisfied by the JWT claims dataclass resolved in
# app.core.dependencies.get_current_user
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CurrentUser:
    user_id: str
    role: Role
    linked_learner_ids: frozenset[str]   # guardian: learners they manage
    assigned_learner_ids: frozenset[str] # teacher: learners in their classes
    jti: str                             # for audit events


class AuthorizationError(Exception):
    """Raised when a policy check fails — routers catch and map to HTTP 403."""


# ---------------------------------------------------------------------------
# Internal audit helper
# ---------------------------------------------------------------------------

def _audit(event: str, actor: CurrentUser, resource_id: str) -> None:
    """Emit a structured audit log entry for privileged access (§3.6 P0)."""
    logger.info(
        "privileged_access",
        extra={
            "event": event,
            "actor_id": actor.user_id,
            "actor_role": actor.role.value,
            "resource_id": resource_id,
            "jti": actor.jti,
        },
    )


# ---------------------------------------------------------------------------
# Policy helpers (§3.6 P0)
# ---------------------------------------------------------------------------

def can_view_learner(actor: CurrentUser, learner_id: str) -> bool:
    """Guardian can view their linked learners; teacher can view assigned; admin all."""
    match actor.role:
        case Role.ADMIN:
            _audit("can_view_learner:admin", actor, learner_id)
            return True
        case Role.GUARDIAN:
            allowed = learner_id in actor.linked_learner_ids
            if allowed:
                _audit("can_view_learner:guardian", actor, learner_id)
            return allowed
        case Role.TEACHER:
            allowed = learner_id in actor.assigned_learner_ids
            if allowed:
                _audit("can_view_learner:teacher", actor, learner_id)
            return allowed
        case Role.SUPPORT_OPERATOR:
            # Support sees meta only — full PII gating is done at repo level
            _audit("can_view_learner:support_meta", actor, learner_id)
            return True
        case Role.LEARNER:
            # Learner can only view themselves
            return actor.user_id == learner_id
        case _:
            return False


def can_update_learner(actor: CurrentUser, learner_id: str) -> bool:
    """Only guardians (for linked learners) and admins may update learner profiles."""
    match actor.role:
        case Role.ADMIN:
            _audit("can_update_learner:admin", actor, learner_id)
            return True
        case Role.GUARDIAN:
            allowed = learner_id in actor.linked_learner_ids
            if allowed:
                _audit("can_update_learner:guardian", actor, learner_id)
            return allowed
        case _:
            return False


def can_generate_lesson_for_learner(actor: CurrentUser, learner_id: str) -> bool:
    """Guardians and admins may trigger lesson generation for a learner."""
    match actor.role:
        case Role.ADMIN:
            return True
        case Role.GUARDIAN:
            return learner_id in actor.linked_learner_ids
        case _:
            return False


def can_start_diagnostic_for_learner(actor: CurrentUser, learner_id: str) -> bool:
    """Guardians, teachers (assigned), and admins may start a diagnostic."""
    match actor.role:
        case Role.ADMIN:
            return True
        case Role.GUARDIAN:
            return learner_id in actor.linked_learner_ids
        case Role.TEACHER:
            return learner_id in actor.assigned_learner_ids
        case _:
            return False


def can_view_study_plan(actor: CurrentUser, learner_id: str) -> bool:
    """Learner (own), guardian (linked), teacher (assigned), admin."""
    match actor.role:
        case Role.ADMIN:
            return True
        case Role.LEARNER:
            return actor.user_id == learner_id
        case Role.GUARDIAN:
            return learner_id in actor.linked_learner_ids
        case Role.TEACHER:
            return learner_id in actor.assigned_learner_ids
        case _:
            return False


def can_view_parent_report(actor: CurrentUser, learner_id: str) -> bool:
    """Parent reports are guardian- and admin-only."""
    match actor.role:
        case Role.ADMIN:
            _audit("can_view_parent_report:admin", actor, learner_id)
            return True
        case Role.GUARDIAN:
            allowed = learner_id in actor.linked_learner_ids
            if allowed:
                _audit("can_view_parent_report:guardian", actor, learner_id)
            return allowed
        case _:
            return False


def can_export_learner_data(actor: CurrentUser, learner_id: str) -> bool:
    """POPIA data export — guardian (linked) and admin only (§3.6 P0)."""
    match actor.role:
        case Role.ADMIN:
            _audit("can_export_learner_data:admin", actor, learner_id)
            return True
        case Role.GUARDIAN:
            allowed = learner_id in actor.linked_learner_ids
            if allowed:
                _audit("can_export_learner_data:guardian", actor, learner_id)
            return allowed
        case _:
            return False


def can_request_erasure(actor: CurrentUser, learner_id: str) -> bool:
    """POPIA right-to-erasure — guardian (linked) and admin only (§3.6 P0)."""
    match actor.role:
        case Role.ADMIN:
            _audit("can_request_erasure:admin", actor, learner_id)
            return True
        case Role.GUARDIAN:
            allowed = learner_id in actor.linked_learner_ids
            if allowed:
                _audit("can_request_erasure:guardian", actor, learner_id)
            return allowed
        case _:
            return False


def can_view_billing(actor: CurrentUser, account_id: str) -> bool:
    """Billing: guardian (own account), support_operator, admin."""
    match actor.role:
        case Role.ADMIN:
            _audit("can_view_billing:admin", actor, account_id)
            return True
        case Role.GUARDIAN:
            # account_id must match the actor's own account
            allowed = actor.user_id == account_id
            if allowed:
                _audit("can_view_billing:guardian", actor, account_id)
            return allowed
        case Role.SUPPORT_OPERATOR:
            _audit("can_view_billing:support", actor, account_id)
            return True
        case _:
            return False


# ---------------------------------------------------------------------------
# FastAPI dependency — raise HTTP 403 if check fails
# ---------------------------------------------------------------------------

def require(check: bool, detail: str = "Access denied") -> None:
    """Call inside a route handler after running a policy helper.

    Example::

        require(can_view_learner(current_user, learner_id))
    """
    if not check:
        from fastapi import HTTPException  # noqa: PLC0415
        raise HTTPException(status_code=403, detail=detail)


def assert_can_access_learner(actor: dict | CurrentUser, learner: Any) -> None:
    """Compatibility helper for existing routes (§3.6 P0).

    DEPRECATED: This earlier definition is overridden by the simpler, canonical
    implementation lower in this module (which delegates to ``can_access_learner``).
    Kept here only because it documents the original policy mapping; it is
    immediately rebound by the later definition and is therefore unreachable.
    """
    # 1. Resolve actor attributes
    if isinstance(actor, dict):
        role_val = actor.get("role", "")
        user_id = actor.get("sub", "")
        linked_ids = set(actor.get("linked_learner_ids", []))
        assigned_ids = set(actor.get("assigned_learner_ids", []))
    else:
        role_val = actor.role
        user_id = actor.user_id
        linked_ids = set(actor.linked_learner_ids)
        assigned_ids = set(actor.assigned_learner_ids)

    # 2. Extract learner_id
    learner_id = str(getattr(learner, "id", learner))

    # 3. Policy mapping (normalized to strings)
    role_str = str(role_val).lower().split(".")[-1]  # handle Enum.VALUE or "value"

    allowed = False
    if role_str in ("admin", "support_operator"):
        allowed = True
    elif role_str in ("parent", "guardian"):
        allowed = learner_id in linked_ids
    elif role_str == "teacher":
        allowed = learner_id in assigned_ids
    elif role_str in ("student", "learner"):
        allowed = user_id == learner_id

    if not allowed:
        from fastapi import HTTPException  # noqa: PLC0415
        raise HTTPException(status_code=403, detail="Access denied to learner resource")

# ---------------------------------------------------------------------------
# Compatibility helpers used by legacy unit tests and dependency adapters
# ---------------------------------------------------------------------------

def _actor_role_value(actor: object) -> str:
    if isinstance(actor, dict):
        role = actor.get("role")
    else:
        role = getattr(actor, "role", None)
    value = getattr(role, "value", role)
    value = str(value or "").lower()
    if value == "parent":
        return "guardian"
    if value == "student":
        return "learner"
    return value


def _actor_user_id(actor: object) -> str:
    if isinstance(actor, dict):
        return str(actor.get("sub") or actor.get("user_id") or actor.get("id") or "")
    return str(getattr(actor, "user_id", getattr(actor, "id", "")))


def can_access_learner(actor: object, learner: object) -> bool:
    """Return whether an actor can access a learner object."""
    role = _actor_role_value(actor)
    actor_id = _actor_user_id(actor)
    learner_id = str(getattr(learner, "id", learner))
    guardian_id = str(getattr(learner, "guardian_id", ""))

    if role == "admin":
        return True
    if role == "guardian":
        linked = getattr(actor, "linked_learner_ids", None)
        if linked is None and isinstance(actor, dict):
            linked = actor.get("linked_learner_ids")
        if linked is not None:
            return learner_id in {str(item) for item in linked}
        return bool(guardian_id and actor_id == guardian_id)
    if role == "teacher":
        assigned = getattr(actor, "assigned_learner_ids", None)
        if assigned is None and isinstance(actor, dict):
            assigned = actor.get("assigned_learner_ids")
        return learner_id in {str(item) for item in (assigned or [])}
    if role == "learner":
        return actor_id == learner_id
    return False


def assert_can_access_learner(actor: object, learner: object) -> None:  # noqa: F811 — later def shadows this; kept for backward compat
    """Raise HTTP 403 unless the actor may access the learner."""
    if not can_access_learner(actor, learner):
        from fastapi import HTTPException  # noqa: PLC0415
        raise HTTPException(status_code=403, detail="Access denied")
