"""Tests for object-level authorization policy helpers."""
from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.security.object_authorization import (
    Actor,
    OwnershipScope,
    Permission,
    Role,
    can_access_learner,
    can_access_object,
    require_learner_access,
)


@dataclass(frozen=True)
class LearnerRecord:
    learner_id: str


@pytest.mark.unit
def test_admin_can_read_write_delete_any_learner() -> None:
    actor = Actor.from_values(subject_id="admin-1", roles=[Role.ADMIN])

    read_decision = can_access_learner(actor, "learner-1", Permission.READ)
    write_decision = can_access_learner(actor, "learner-1", Permission.WRITE)
    delete_decision = can_access_learner(actor, "learner-1", Permission.DELETE)

    assert read_decision.allowed
    assert write_decision.allowed
    assert delete_decision.allowed
    assert delete_decision.scope == OwnershipScope.ADMIN


@pytest.mark.unit
def test_learner_can_access_self_owned_data() -> None:
    actor = Actor.from_values(subject_id="learner-1", roles=[Role.LEARNER])

    decision = can_access_learner(actor, "learner-1", Permission.READ)

    assert decision.allowed
    assert decision.scope == OwnershipScope.SELF


@pytest.mark.unit
def test_learner_cannot_access_other_learner_data() -> None:
    actor = Actor.from_values(subject_id="learner-1", roles=[Role.LEARNER])

    decision = can_access_learner(actor, "learner-2", Permission.READ)

    assert not decision.allowed
    assert decision.scope is None
    assert "no ownership" in decision.reason


@pytest.mark.unit
def test_guardian_can_read_and_write_assigned_learner_data() -> None:
    actor = Actor.from_values(
        subject_id="guardian-1",
        roles=[Role.GUARDIAN],
        guardian_learner_ids=["learner-1"],
    )

    read_decision = can_access_learner(actor, "learner-1", Permission.READ)
    write_decision = can_access_learner(actor, "learner-1", Permission.WRITE)

    assert read_decision.allowed
    assert write_decision.allowed
    assert read_decision.scope == OwnershipScope.GUARDIAN


@pytest.mark.unit
def test_guardian_cannot_delete_learner_data() -> None:
    actor = Actor.from_values(
        subject_id="guardian-1",
        roles=[Role.GUARDIAN],
        guardian_learner_ids=["learner-1"],
    )

    decision = can_access_learner(actor, "learner-1", Permission.DELETE)

    assert not decision.allowed
    assert "do not allow delete access" in decision.reason


@pytest.mark.unit
def test_educator_can_access_assigned_learner_data() -> None:
    actor = Actor.from_values(
        subject_id="educator-1",
        roles=[Role.EDUCATOR],
        educator_learner_ids=["learner-1"],
    )

    decision = can_access_learner(actor, "learner-1", Permission.READ)

    assert decision.allowed
    assert decision.scope == OwnershipScope.EDUCATOR


@pytest.mark.unit
def test_support_scope_is_read_only() -> None:
    actor = Actor.from_values(subject_id="support-1", roles=[Role.SUPPORT])

    read_decision = can_access_learner(actor, "learner-1", Permission.READ)
    write_decision = can_access_learner(actor, "learner-1", Permission.WRITE)

    assert read_decision.allowed
    assert read_decision.scope == OwnershipScope.SUPPORT
    assert not write_decision.allowed
    assert "do not allow write access" in write_decision.reason


@pytest.mark.unit
def test_object_authorization_uses_learner_id_protocol() -> None:
    actor = Actor.from_values(subject_id="learner-1", roles=[Role.LEARNER])
    record = LearnerRecord(learner_id="learner-1")

    decision = can_access_object(actor, record, Permission.READ)

    assert decision.allowed
    assert decision.learner_id == "learner-1"


@pytest.mark.unit
def test_require_learner_access_raises_permission_error_when_denied() -> None:
    actor = Actor.from_values(subject_id="learner-1", roles=[Role.LEARNER])

    with pytest.raises(PermissionError, match="no ownership"):
        require_learner_access(actor, "learner-2", Permission.READ)
