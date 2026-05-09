"""Tests for learner route object-authorization wiring."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, status

from app.security.dependencies import require_learner_read_for_current_user
from app.security.object_authorization import OwnershipScope

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def learner() -> SimpleNamespace:
    return SimpleNamespace(id="learner-1", guardian_id="guardian-1")


@pytest.mark.unit
def test_current_user_adapter_allows_admin_read(learner: SimpleNamespace) -> None:
    decision = require_learner_read_for_current_user(
        {"sub": "admin-1", "role": "admin"},
        learner,
    )

    assert decision.allowed
    assert decision.scope == OwnershipScope.ADMIN


@pytest.mark.unit
def test_current_user_adapter_allows_guardian_read_for_assigned_learner(
    learner: SimpleNamespace,
) -> None:
    decision = require_learner_read_for_current_user(
        {"sub": "guardian-1", "role": "parent"},
        learner,
    )

    assert decision.allowed
    assert decision.scope == OwnershipScope.GUARDIAN


@pytest.mark.unit
def test_current_user_adapter_allows_learner_self_read(learner: SimpleNamespace) -> None:
    decision = require_learner_read_for_current_user(
        {"sub": "learner-1", "role": "student"},
        learner,
    )

    assert decision.allowed
    assert decision.scope == OwnershipScope.SELF


@pytest.mark.unit
def test_current_user_adapter_rejects_unrelated_guardian(learner: SimpleNamespace) -> None:
    with pytest.raises(HTTPException) as exc_info:
        require_learner_read_for_current_user(
            {"sub": "guardian-2", "role": "parent"},
            learner,
        )

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail["code"] == "object_forbidden"
    assert exc_info.value.detail["learner_id"] == "learner-1"
    assert exc_info.value.detail["permission"] == "read"


@pytest.mark.unit
def test_current_user_adapter_rejects_missing_subject(learner: SimpleNamespace) -> None:
    with pytest.raises(HTTPException) as exc_info:
        require_learner_read_for_current_user(
            {"role": "parent"},
            learner,
        )

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.unit
def test_current_user_adapter_rejects_unknown_role(learner: SimpleNamespace) -> None:
    with pytest.raises(HTTPException) as exc_info:
        require_learner_read_for_current_user(
            {"sub": "user-1", "role": "owner"},
            learner,
        )

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Unsupported authenticated role" in str(exc_info.value.detail)


@pytest.mark.unit
def test_get_learner_route_uses_phase2_authorization_dependency() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "learners.py").read_text(
        encoding="utf-8"
    )

    get_learner_block = source.split("async def get_learner", maxsplit=1)[1].split(
        "@router.get",
        maxsplit=1,
    )[0]

    assert "require_learner_read_for_current_user(current_user, learner)" in get_learner_block
    assert "assert_can_access_learner(current_user, learner)" not in get_learner_block
