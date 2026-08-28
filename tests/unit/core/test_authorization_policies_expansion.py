"""Comprehensive unit tests for object-level authorization policy helpers."""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.domain.roles import Role
from app.core.authorization import (
    CurrentUser,
    AuthorizationError,
    can_view_learner,
    can_update_learner,
    can_generate_lesson_for_learner,
    can_start_diagnostic_for_learner,
    can_view_study_plan,
    can_view_parent_report,
    can_export_learner_data,
    can_request_erasure,
    can_view_billing,
    require,
)


@pytest.fixture
def admin_user():
    return CurrentUser(
        user_id="admin_1",
        role=Role.ADMIN,
        linked_learner_ids=frozenset(),
        assigned_learner_ids=frozenset(),
        jti="jti_admin_1",
    )


@pytest.fixture
def guardian_user():
    return CurrentUser(
        user_id="guardian_1",
        role=Role.GUARDIAN,
        linked_learner_ids=frozenset(["learner_100", "learner_101"]),
        assigned_learner_ids=frozenset(),
        jti="jti_guardian_1",
    )


@pytest.fixture
def teacher_user():
    return CurrentUser(
        user_id="teacher_1",
        role=Role.TEACHER,
        linked_learner_ids=frozenset(),
        assigned_learner_ids=frozenset(["learner_100", "learner_200"]),
        jti="jti_teacher_1",
    )


@pytest.fixture
def learner_user():
    return CurrentUser(
        user_id="learner_100",
        role=Role.LEARNER,
        linked_learner_ids=frozenset(),
        assigned_learner_ids=frozenset(),
        jti="jti_learner_100",
    )


# ---------------------------------------------------------------------------
# Policy Tests
# ---------------------------------------------------------------------------

class TestAuthorizationPolicies:
    def test_can_view_learner(self, admin_user, guardian_user, teacher_user, learner_user):
        assert can_view_learner(admin_user, "learner_999") is True
        assert can_view_learner(guardian_user, "learner_100") is True
        assert can_view_learner(guardian_user, "learner_999") is False
        assert can_view_learner(teacher_user, "learner_100") is True
        assert can_view_learner(teacher_user, "learner_999") is False
        assert can_view_learner(learner_user, "learner_100") is True
        assert can_view_learner(learner_user, "learner_101") is False

    def test_can_update_learner(self, admin_user, guardian_user, teacher_user, learner_user):
        assert can_update_learner(admin_user, "learner_999") is True
        assert can_update_learner(guardian_user, "learner_100") is True
        assert can_update_learner(guardian_user, "learner_999") is False
        assert can_update_learner(teacher_user, "learner_100") is False
        assert can_update_learner(learner_user, "learner_100") is False

    def test_can_generate_lesson(self, admin_user, guardian_user, teacher_user):
        assert can_generate_lesson_for_learner(admin_user, "learner_999") is True
        assert can_generate_lesson_for_learner(guardian_user, "learner_100") is True
        assert can_generate_lesson_for_learner(guardian_user, "learner_999") is False
        assert can_generate_lesson_for_learner(teacher_user, "learner_100") is False

    def test_can_start_diagnostic(self, admin_user, guardian_user, teacher_user):
        assert can_start_diagnostic_for_learner(admin_user, "learner_999") is True
        assert can_start_diagnostic_for_learner(guardian_user, "learner_100") is True
        assert can_start_diagnostic_for_learner(teacher_user, "learner_100") is True
        assert can_start_diagnostic_for_learner(teacher_user, "learner_999") is False

    def test_can_view_study_plan(self, admin_user, guardian_user, teacher_user, learner_user):
        assert can_view_study_plan(admin_user, "learner_999") is True
        assert can_view_study_plan(guardian_user, "learner_100") is True
        assert can_view_study_plan(teacher_user, "learner_100") is True
        assert can_view_study_plan(learner_user, "learner_100") is True
        assert can_view_study_plan(learner_user, "learner_999") is False

    def test_can_view_parent_report(self, admin_user, guardian_user, teacher_user):
        assert can_view_parent_report(admin_user, "learner_999") is True
        assert can_view_parent_report(guardian_user, "learner_100") is True
        assert can_view_parent_report(guardian_user, "learner_999") is False
        assert can_view_parent_report(teacher_user, "learner_100") is False

    def test_can_export_and_request_erasure(self, admin_user, guardian_user, teacher_user):
        assert can_export_learner_data(admin_user, "learner_999") is True
        assert can_export_learner_data(guardian_user, "learner_100") is True
        assert can_export_learner_data(guardian_user, "learner_999") is False
        assert can_export_learner_data(teacher_user, "learner_100") is False

        assert can_request_erasure(admin_user, "learner_999") is True
        assert can_request_erasure(guardian_user, "learner_100") is True
        assert can_request_erasure(guardian_user, "learner_999") is False
        assert can_request_erasure(teacher_user, "learner_100") is False

    def test_can_view_billing(self, admin_user, guardian_user, teacher_user):
        assert can_view_billing(admin_user, "any_account") is True
        assert can_view_billing(guardian_user, "guardian_1") is True
        assert can_view_billing(guardian_user, "other_account") is False
        assert can_view_billing(teacher_user, "teacher_1") is False

    def test_require_helper(self):
        require(True)
        with pytest.raises(HTTPException) as exc:
            require(False, detail="Action prohibited")
        assert exc.value.status_code == 403
        assert exc.value.detail == "Action prohibited"

    def test_authorization_error(self):
        err = AuthorizationError("Policy denied access")
        assert isinstance(err, Exception)
