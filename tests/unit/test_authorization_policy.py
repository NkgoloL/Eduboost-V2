from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.core.authorization import assert_can_access_learner, can_access_learner
from app.models import UserRole


def learner(learner_id: str = "learner-1", guardian_id: str = "guardian-1"):
    return SimpleNamespace(id=learner_id, guardian_id=guardian_id)


def test_parent_can_access_only_linked_learner() -> None:
    assert can_access_learner({"sub": "guardian-1", "role": UserRole.PARENT}, learner()) is True
    assert can_access_learner({"sub": "guardian-2", "role": UserRole.PARENT}, learner()) is False


def test_admin_can_access_learner() -> None:
    assert can_access_learner({"sub": "admin-1", "role": UserRole.ADMIN}, learner()) is True


def test_unassigned_teacher_is_denied_until_assignment_policy_exists() -> None:
    assert can_access_learner({"sub": "teacher-1", "role": UserRole.TEACHER}, learner()) is False


def test_assert_can_access_learner_raises_403() -> None:
    with pytest.raises(HTTPException) as exc:
        assert_can_access_learner({"sub": "guardian-2", "role": UserRole.PARENT}, learner())
    assert exc.value.status_code == 403
