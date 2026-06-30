"""
A.7 — Missing authorization tests.

Tests that:
  - teacher can access only assigned learners
  - support_operator cannot access unlinked learner PII (read_meta only)
  - compliance_auditor can read audit data but cannot mutate data
  - policy helpers fail closed for unrecognised roles
"""
from __future__ import annotations

from app.core.authorization import (
    CurrentUser,
    can_export_learner_data,
    can_generate_lesson_for_learner,
    can_request_erasure,
    can_start_diagnostic_for_learner,
    can_update_learner,
    can_view_billing,
    can_view_learner,
    can_view_parent_report,
    can_view_study_plan,
)
from app.domain.roles import Role


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _user(role: Role, user_id: str = "actor-1",
          linked: frozenset[str] = frozenset(),
          assigned: frozenset[str] = frozenset()) -> CurrentUser:
    return CurrentUser(
        user_id=user_id,
        role=role,
        linked_learner_ids=linked,
        assigned_learner_ids=assigned,
        jti="jti-test",
    )


# ── A.7.1 — Teacher authorization (assigned learners only) ───────────────────

def test_teacher_can_view_assigned_learner():
    teacher = _user(Role.TEACHER, assigned=frozenset(["learner-A"]))
    assert can_view_learner(teacher, "learner-A") is True


def test_teacher_cannot_view_unassigned_learner():
    teacher = _user(Role.TEACHER, assigned=frozenset(["learner-A"]))
    assert can_view_learner(teacher, "learner-B") is False


def test_teacher_can_start_diagnostic_for_assigned():
    teacher = _user(Role.TEACHER, assigned=frozenset(["learner-A"]))
    assert can_start_diagnostic_for_learner(teacher, "learner-A") is True


def test_teacher_cannot_start_diagnostic_for_unassigned():
    teacher = _user(Role.TEACHER, assigned=frozenset(["learner-A"]))
    assert can_start_diagnostic_for_learner(teacher, "learner-C") is False


def test_teacher_can_view_study_plan_for_assigned():
    teacher = _user(Role.TEACHER, assigned=frozenset(["learner-A"]))
    assert can_view_study_plan(teacher, "learner-A") is True


def test_teacher_cannot_update_learner():
    """Teachers must not be able to modify learner profiles."""
    teacher = _user(Role.TEACHER, assigned=frozenset(["learner-A"]))
    assert can_update_learner(teacher, "learner-A") is False


def test_teacher_cannot_export_learner_data():
    """Teachers must not export POPIA data — guardians and admins only."""
    teacher = _user(Role.TEACHER, assigned=frozenset(["learner-A"]))
    assert can_export_learner_data(teacher, "learner-A") is False


def test_teacher_cannot_request_erasure():
    """Teachers must not request erasure — guardians and admins only."""
    teacher = _user(Role.TEACHER, assigned=frozenset(["learner-A"]))
    assert can_request_erasure(teacher, "learner-A") is False


def test_teacher_cannot_view_parent_report():
    """Parent reports are guardian- and admin-only."""
    teacher = _user(Role.TEACHER, assigned=frozenset(["learner-A"]))
    assert can_view_parent_report(teacher, "learner-A") is False


def test_teacher_cannot_generate_lesson():
    """Lesson generation is guardian- and admin-only."""
    teacher = _user(Role.TEACHER, assigned=frozenset(["learner-A"]))
    assert can_generate_lesson_for_learner(teacher, "learner-A") is False


# ── A.7.2 — Support operator PII boundary ────────────────────────────────────

def test_support_operator_can_view_learner_meta():
    """Support operators can view learner records (meta only — PII gated at repo)."""
    support = _user(Role.SUPPORT_OPERATOR)
    assert can_view_learner(support, "any-learner") is True


def test_support_operator_cannot_update_learner():
    """Support operators must not update learner profiles."""
    support = _user(Role.SUPPORT_OPERATOR)
    assert can_update_learner(support, "any-learner") is False


def test_support_operator_cannot_export_data():
    """Support operators must not export POPIA data."""
    support = _user(Role.SUPPORT_OPERATOR)
    assert can_export_learner_data(support, "any-learner") is False


def test_support_operator_cannot_request_erasure():
    """Support operators must not request erasure."""
    support = _user(Role.SUPPORT_OPERATOR)
    assert can_request_erasure(support, "any-learner") is False


def test_support_operator_can_view_billing():
    """Support operators may view billing for customer support purposes."""
    support = _user(Role.SUPPORT_OPERATOR)
    assert can_view_billing(support, "any-account") is True


def test_support_operator_cannot_generate_lessons():
    """Support operators must not generate AI lessons."""
    support = _user(Role.SUPPORT_OPERATOR)
    assert can_generate_lesson_for_learner(support, "any-learner") is False


# ── A.7.3 — Compliance auditor boundary ─────────────────────────────────────

def test_compliance_auditor_cannot_view_learner():
    """Compliance auditors are audit-read-only — no learner data access."""
    auditor = _user(Role.COMPLIANCE_AUDITOR)
    assert can_view_learner(auditor, "any-learner") is False


def test_compliance_auditor_cannot_update_learner():
    auditor = _user(Role.COMPLIANCE_AUDITOR)
    assert can_update_learner(auditor, "any-learner") is False


def test_compliance_auditor_cannot_export_data():
    auditor = _user(Role.COMPLIANCE_AUDITOR)
    assert can_export_learner_data(auditor, "any-learner") is False


def test_compliance_auditor_cannot_request_erasure():
    auditor = _user(Role.COMPLIANCE_AUDITOR)
    assert can_request_erasure(auditor, "any-learner") is False


def test_compliance_auditor_cannot_generate_lessons():
    auditor = _user(Role.COMPLIANCE_AUDITOR)
    assert can_generate_lesson_for_learner(auditor, "any-learner") is False


def test_compliance_auditor_cannot_view_billing():
    auditor = _user(Role.COMPLIANCE_AUDITOR)
    assert can_view_billing(auditor, "any-account") is False


def test_compliance_auditor_cannot_view_parent_report():
    auditor = _user(Role.COMPLIANCE_AUDITOR)
    assert can_view_parent_report(auditor, "any-learner") is False


# ── A.7.4 — Content reviewer boundary ────────────────────────────────────────

def test_content_reviewer_cannot_view_learner():
    reviewer = _user(Role.CONTENT_REVIEWER)
    assert can_view_learner(reviewer, "any-learner") is False


def test_content_reviewer_cannot_export_data():
    reviewer = _user(Role.CONTENT_REVIEWER)
    assert can_export_learner_data(reviewer, "any-learner") is False


# ── A.7.5 — Learner self-access ───────────────────────────────────────────────

def test_learner_can_view_themselves():
    learner = _user(Role.LEARNER, user_id="learner-self")
    assert can_view_learner(learner, "learner-self") is True


def test_learner_cannot_view_another_learner():
    learner = _user(Role.LEARNER, user_id="learner-1")
    assert can_view_learner(learner, "learner-2") is False


def test_learner_cannot_update_own_profile_via_can_update():
    """Profile updates go through the profile router with its own auth — not can_update_learner."""
    learner = _user(Role.LEARNER, user_id="learner-1")
    assert can_update_learner(learner, "learner-1") is False


# ── A.7.6 — Admin has all access ─────────────────────────────────────────────

def test_admin_can_view_any_learner():
    admin = _user(Role.ADMIN)
    assert can_view_learner(admin, "any-learner") is True


def test_admin_can_update_any_learner():
    admin = _user(Role.ADMIN)
    assert can_update_learner(admin, "any-learner") is True


def test_admin_can_export_any_learner():
    admin = _user(Role.ADMIN)
    assert can_export_learner_data(admin, "any-learner") is True


def test_admin_can_request_erasure():
    admin = _user(Role.ADMIN)
    assert can_request_erasure(admin, "any-learner") is True


# ── A.7.7 — Unknown role fails closed ────────────────────────────────────────

def test_unknown_role_fails_closed_for_view():
    """Any unrecognised role must default to deny on all policy checks."""
    # Create a user with a synthetic unknown role value
    _user(Role.LEARNER)
    # Simulate an unknown role by monkeypatching

    # We can verify the _default case by passing an object whose role is unmapped
    class UnknownRole:
        value = "unknown_role"

    unknown_user = CurrentUser(
        user_id="x",
        role=UnknownRole(),  # type: ignore[arg-type]
        linked_learner_ids=frozenset(),
        assigned_learner_ids=frozenset(),
        jti="jti-unknown",
    )
    assert can_view_learner(unknown_user, "any-learner") is False
