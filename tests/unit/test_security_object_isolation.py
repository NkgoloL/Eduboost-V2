"""Unit tests for Multi-Tenant & Object-Level Authorization Isolation (TSR-8)."""
from __future__ import annotations

import pytest
from fastapi import HTTPException, status
from types import SimpleNamespace

from app.security.object_authorization import Role
from app.security.dependencies import (
    require_learner_read_for_current_user,
    require_learner_write_for_current_user,
    build_actor_from_current_user_for_learner,
)


@pytest.mark.unit
def test_guardian_can_read_own_linked_learner():
    guardian_id = "guardian-uuid-1"
    learner_id = "learner-uuid-1"

    learner = SimpleNamespace(id=learner_id, guardian_id=guardian_id)
    current_user = {"sub": guardian_id, "role": "guardian", "guardian_learner_ids": [learner_id]}

    decision = require_learner_read_for_current_user(current_user, learner)
    assert decision.allowed is True


@pytest.mark.unit
def test_guardian_rejected_when_accessing_unrelated_learner():
    guardian_id = "guardian-uuid-1"
    unrelated_guardian_id = "guardian-uuid-2"
    learner_id = "learner-uuid-1"

    # Learner belongs to guardian 2, caller is guardian 1
    learner = SimpleNamespace(id=learner_id, guardian_id=unrelated_guardian_id)
    current_user = {"sub": guardian_id, "role": "guardian", "guardian_learner_ids": ["other-learner-id"]}

    with pytest.raises(HTTPException) as exc:
        require_learner_read_for_current_user(current_user, learner)

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.unit
def test_cross_learner_write_isolation():
    learner_a_id = "learner-a"
    learner_b_id = "learner-b"

    # Learner A tries to write data for Learner B
    current_user = {"sub": learner_a_id, "role": "learner"}

    with pytest.raises(HTTPException) as exc:
        require_learner_write_for_current_user(current_user, learner_b_id)

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.unit
def test_admin_has_elevated_access():
    admin_id = "admin-user"
    learner_id = "learner-uuid-1"

    learner = SimpleNamespace(id=learner_id, guardian_id="guardian-1")
    current_user = {"sub": admin_id, "role": "admin"}

    decision = require_learner_read_for_current_user(current_user, learner)
    assert decision.allowed is True
