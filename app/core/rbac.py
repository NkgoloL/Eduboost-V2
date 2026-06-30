"""Role and RBAC policy definitions for V2 routers.

The persisted Guardian.role enum currently supports parent, teacher, and admin
(and student for learner/session contexts). Additional operational roles are
reserved here so policy code and documentation can converge before a database
migration introduces persisted assignments.
"""
from __future__ import annotations

from enum import Enum

from app.core.security import Role, require_roles
from app.models import UserRole


class OperationalRole(str, Enum):
    LEARNER = "student"
    PARENT_GUARDIAN = "parent"
    TEACHER_TUTOR = "teacher"
    ADMIN = "admin"
    SUPPORT_OPERATOR = "support_operator"
    CONTENT_REVIEWER = "content_reviewer"
    COMPLIANCE_AUDITOR = "compliance_auditor"


PERSISTED_ROLES = frozenset(role.value for role in UserRole)
RESERVED_OPERATIONAL_ROLES = frozenset(role.value for role in OperationalRole) - PERSISTED_ROLES

require_role = require_roles

__all__ = [
    "OperationalRole",
    "PERSISTED_ROLES",
    "RESERVED_OPERATIONAL_ROLES",
    "Role",
    "require_role",
    "require_roles",
]
