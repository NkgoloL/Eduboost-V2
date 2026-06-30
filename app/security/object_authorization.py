"""Object-level authorization policy helpers.

This module centralizes simple ownership and role checks so routers and
services do not each implement their own inconsistent authorization rules.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Protocol


class Role(str, Enum):
    """Known EduBoost actor roles."""

    ADMIN = "admin"
    EDUCATOR = "educator"
    GUARDIAN = "guardian"
    LEARNER = "learner"
    SUPPORT = "support"
    SYSTEM = "system"


class Permission(str, Enum):
    """Canonical object-level permissions."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class OwnershipScope(str, Enum):
    """Reason an actor is authorized for an object."""

    ADMIN = "admin"
    SELF = "self"
    GUARDIAN = "guardian"
    EDUCATOR = "educator"
    SUPPORT = "support"
    SYSTEM = "system"


@dataclass(frozen=True)
class Actor:
    """Normalized authorization actor."""

    subject_id: str
    roles: frozenset[Role]
    learner_ids: frozenset[str] = frozenset()
    guardian_learner_ids: frozenset[str] = frozenset()
    educator_learner_ids: frozenset[str] = frozenset()

    @classmethod
    def from_values(
        cls,
        *,
        subject_id: str,
        roles: Iterable[str | Role],
        learner_ids: Iterable[str] = (),
        guardian_learner_ids: Iterable[str] = (),
        educator_learner_ids: Iterable[str] = (),
    ) -> "Actor":
        """Build an actor from raw role/id values."""
        return cls(
            subject_id=str(subject_id),
            roles=frozenset(Role(role) for role in roles),
            learner_ids=frozenset(str(value) for value in learner_ids),
            guardian_learner_ids=frozenset(str(value) for value in guardian_learner_ids),
            educator_learner_ids=frozenset(str(value) for value in educator_learner_ids),
        )


@dataclass(frozen=True)
class AuthorizationDecision:
    """Result of an object-level authorization check."""

    allowed: bool
    permission: Permission
    learner_id: str
    scope: OwnershipScope | None
    reason: str

    @classmethod
    def allow(
        cls,
        *,
        permission: Permission,
        learner_id: str,
        scope: OwnershipScope,
        reason: str,
    ) -> "AuthorizationDecision":
        return cls(
            allowed=True,
            permission=permission,
            learner_id=learner_id,
            scope=scope,
            reason=reason,
        )

    @classmethod
    def deny(
        cls,
        *,
        permission: Permission,
        learner_id: str,
        reason: str,
    ) -> "AuthorizationDecision":
        return cls(
            allowed=False,
            permission=permission,
            learner_id=learner_id,
            scope=None,
            reason=reason,
        )


class LearnerOwnedObject(Protocol):
    """Protocol for objects associated with a learner."""

    learner_id: str


READ_ROLES = frozenset(
    {
        Role.ADMIN,
        Role.SUPPORT,
        Role.SYSTEM,
        Role.EDUCATOR,
        Role.GUARDIAN,
        Role.LEARNER,
    }
)

WRITE_ROLES = frozenset(
    {
        Role.ADMIN,
        Role.SYSTEM,
        Role.EDUCATOR,
        Role.GUARDIAN,
        Role.LEARNER,
    }
)

DELETE_ROLES = frozenset(
    {
        Role.ADMIN,
        Role.SYSTEM,
    }
)

ADMIN_ROLES = frozenset(
    {
        Role.ADMIN,
        Role.SYSTEM,
    }
)


def normalize_permission(permission: str | Permission) -> Permission:
    """Normalize a permission value."""
    return Permission(permission)


def actor_has_role(actor: Actor, *roles: Role) -> bool:
    """Return whether an actor has at least one role."""
    return bool(actor.roles.intersection(roles))


def _permission_roles(permission: Permission) -> frozenset[Role]:
    if permission == Permission.READ:
        return READ_ROLES
    if permission == Permission.WRITE:
        return WRITE_ROLES
    if permission == Permission.DELETE:
        return DELETE_ROLES
    if permission == Permission.ADMIN:
        return ADMIN_ROLES
    raise ValueError(f"Unsupported permission: {permission}")


def _scope_for_learner(actor: Actor, learner_id: str) -> OwnershipScope | None:
    if actor_has_role(actor, Role.ADMIN):
        return OwnershipScope.ADMIN

    if actor_has_role(actor, Role.SYSTEM):
        return OwnershipScope.SYSTEM

    if learner_id == actor.subject_id or learner_id in actor.learner_ids:
        return OwnershipScope.SELF

    if learner_id in actor.guardian_learner_ids:
        return OwnershipScope.GUARDIAN

    if learner_id in actor.educator_learner_ids:
        return OwnershipScope.EDUCATOR

    if actor_has_role(actor, Role.SUPPORT):
        return OwnershipScope.SUPPORT

    return None


def can_access_learner(
    actor: Actor,
    learner_id: str,
    permission: str | Permission = Permission.READ,
) -> AuthorizationDecision:
    """Authorize access to a learner-scoped object."""
    normalized_permission = normalize_permission(permission)
    learner_id = str(learner_id)

    permitted_roles = _permission_roles(normalized_permission)
    if not actor.roles.intersection(permitted_roles):
        return AuthorizationDecision.deny(
            permission=normalized_permission,
            learner_id=learner_id,
            reason=(
                f"Actor roles {sorted(actor.roles)} do not allow "
                f"{normalized_permission.value} access."
            ),
        )

    scope = _scope_for_learner(actor, learner_id)
    if scope is None:
        return AuthorizationDecision.deny(
            permission=normalized_permission,
            learner_id=learner_id,
            reason="Actor has no ownership, guardian, educator, support, system, or admin scope.",
        )

    if normalized_permission in {Permission.WRITE, Permission.DELETE, Permission.ADMIN}:
        if scope == OwnershipScope.SUPPORT:
            return AuthorizationDecision.deny(
                permission=normalized_permission,
                learner_id=learner_id,
                reason="Support scope is read-only.",
            )

    if normalized_permission in {Permission.DELETE, Permission.ADMIN}:
        if scope not in {OwnershipScope.ADMIN, OwnershipScope.SYSTEM}:
            return AuthorizationDecision.deny(
                permission=normalized_permission,
                learner_id=learner_id,
                reason="Delete/admin access requires admin or system scope.",
            )

    return AuthorizationDecision.allow(
        permission=normalized_permission,
        learner_id=learner_id,
        scope=scope,
        reason=f"Actor authorized through {scope.value} scope.",
    )


def can_access_object(
    actor: Actor,
    obj: LearnerOwnedObject,
    permission: str | Permission = Permission.READ,
) -> AuthorizationDecision:
    """Authorize access to any object exposing ``learner_id``."""
    return can_access_learner(actor, obj.learner_id, permission=permission)


def require_learner_access(
    actor: Actor,
    learner_id: str,
    permission: str | Permission = Permission.READ,
) -> AuthorizationDecision:
    """Return the authorization decision or raise PermissionError."""
    decision = can_access_learner(actor, learner_id, permission=permission)
    if not decision.allowed:
        raise PermissionError(decision.reason)
    return decision
