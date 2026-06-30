"""Tests for FastAPI authorization dependency adapters."""
from __future__ import annotations

import pytest
from fastapi import HTTPException, status

from app.security.dependencies import (
    build_actor_from_headers,
    raise_for_learner_access,
    require_learner_delete,
    require_learner_read,
    require_learner_write,
)
from app.security.object_authorization import OwnershipScope, Permission, Role


@pytest.mark.unit
def test_build_actor_from_headers_parses_roles_and_relationships() -> None:
    actor = build_actor_from_headers(
        subject_id="guardian-1",
        roles="guardian, educator",
        guardian_learner_ids="learner-1, learner-2",
        educator_learner_ids="learner-3",
    )

    assert actor.subject_id == "guardian-1"
    assert actor.roles == frozenset({Role.GUARDIAN, Role.EDUCATOR})
    assert actor.guardian_learner_ids == frozenset({"learner-1", "learner-2"})
    assert actor.educator_learner_ids == frozenset({"learner-3"})


@pytest.mark.unit
def test_build_actor_from_headers_requires_subject() -> None:
    with pytest.raises(HTTPException) as exc_info:
        build_actor_from_headers(subject_id=None, roles="learner")

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Missing authenticated subject."


@pytest.mark.unit
def test_build_actor_from_headers_requires_roles() -> None:
    with pytest.raises(HTTPException) as exc_info:
        build_actor_from_headers(subject_id="learner-1", roles=None)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Missing authenticated roles."


@pytest.mark.unit
def test_build_actor_from_headers_rejects_unknown_role() -> None:
    with pytest.raises(HTTPException) as exc_info:
        build_actor_from_headers(subject_id="user-1", roles="owner")

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Unsupported role" in str(exc_info.value.detail)


@pytest.mark.unit
def test_require_learner_read_allows_self_scope() -> None:
    actor = build_actor_from_headers(subject_id="learner-1", roles="learner")

    decision = require_learner_read(actor, "learner-1")

    assert decision.allowed
    assert decision.permission == Permission.READ
    assert decision.scope == OwnershipScope.SELF


@pytest.mark.unit
def test_require_learner_write_allows_guardian_scope() -> None:
    actor = build_actor_from_headers(
        subject_id="guardian-1",
        roles="guardian",
        guardian_learner_ids="learner-1",
    )

    decision = require_learner_write(actor, "learner-1")

    assert decision.allowed
    assert decision.permission == Permission.WRITE
    assert decision.scope == OwnershipScope.GUARDIAN


@pytest.mark.unit
def test_require_learner_delete_rejects_guardian_scope() -> None:
    actor = build_actor_from_headers(
        subject_id="guardian-1",
        roles="guardian",
        guardian_learner_ids="learner-1",
    )

    with pytest.raises(HTTPException) as exc_info:
        require_learner_delete(actor, "learner-1")

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail["code"] == "object_forbidden"
    assert exc_info.value.detail["permission"] == "delete"


@pytest.mark.unit
def test_raise_for_learner_access_uses_structured_forbidden_detail() -> None:
    actor = build_actor_from_headers(subject_id="learner-1", roles="learner")

    with pytest.raises(HTTPException) as exc_info:
        raise_for_learner_access(
            actor=actor,
            learner_id="learner-2",
            permission=Permission.READ,
        )

    detail = exc_info.value.detail
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert detail["code"] == "object_forbidden"
    assert detail["learner_id"] == "learner-2"
    assert detail["permission"] == "read"
    assert "not authorized" in detail["message"]
