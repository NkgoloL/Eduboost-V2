"""
app/domain/roles.py
--------------------
Canonical role definitions for EduBoost SA V2.

All seven platform roles are defined here as a single source of truth.
Routers, services, and policy helpers import from this module — never
define role strings inline.

§3.5 backlog — Defines: learner, guardian, teacher, admin,
               support_operator, content_reviewer, compliance_auditor
"""

from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    """All valid platform roles.

    Inherits from ``str`` so that SQLAlchemy ``String`` columns and JSON
    serialisers work without extra coercion.
    """

    LEARNER = "learner"
    GUARDIAN = "guardian"          # parent / guardian
    TEACHER = "teacher"
    ADMIN = "admin"
    SUPPORT_OPERATOR = "support_operator"
    CONTENT_REVIEWER = "content_reviewer"
    COMPLIANCE_AUDITOR = "compliance_auditor"


# ---------------------------------------------------------------------------
# Permission matrix — what each role may do
# This is the machine-readable source for docs/security/route_policy_matrix.md
# ---------------------------------------------------------------------------

ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.LEARNER: {
        "lesson:read_own",
        "study_plan:read_own",
        "diagnostic:start_own",
        "gamification:read_own",
    },
    Role.GUARDIAN: {
        "learner:read_linked",
        "learner:update_linked",
        "lesson:generate_for_linked",
        "diagnostic:start_for_linked",
        "study_plan:read_linked",
        "parent_report:read_linked",
        "learner_data:export_linked",
        "erasure:request_linked",
        "billing:read_own",
        "billing:manage_own",
        "consent:manage_linked",
    },
    Role.TEACHER: {
        "learner:read_assigned",
        "lesson:read_assigned",
        "study_plan:read_assigned",
        "diagnostic:read_assigned",
    },
    Role.ADMIN: {
        # Admins get all permissions; enforce this via has_role check, not listing all
        "__all__",
    },
    Role.SUPPORT_OPERATOR: {
        "learner:read_meta",      # no raw PII fields
        "billing:read_any",
        "audit:read",
    },
    Role.CONTENT_REVIEWER: {
        "lesson:read_any",
        "lesson:update_content",
        "caps_item:read_any",
        "caps_item:update",
    },
    Role.COMPLIANCE_AUDITOR: {
        "audit:read",
        "consent:read_any",
        "erasure:read_any",
        # No data mutation rights
    },
}


def role_has_permission(role: Role, permission: str) -> bool:
    """Return True if *role* carries *permission* or is ADMIN."""
    perms = ROLE_PERMISSIONS.get(role, set())
    return "__all__" in perms or permission in perms
