"""Tests for study-plan write authorization wiring."""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import HTTPException, status

from app.security.dependencies import require_learner_write_for_current_user
from app.security.object_authorization import OwnershipScope

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_current_user_claim_adapter_allows_admin_write() -> None:
    decision = require_learner_write_for_current_user(
        {"sub": "admin-1", "role": "admin"},
        "learner-1",
    )

    assert decision.allowed
    assert decision.scope == OwnershipScope.ADMIN


@pytest.mark.unit
def test_current_user_claim_adapter_allows_learner_self_write() -> None:
    decision = require_learner_write_for_current_user(
        {"sub": "learner-1", "role": "student"},
        "learner-1",
    )

    assert decision.allowed
    assert decision.scope == OwnershipScope.SELF


@pytest.mark.unit
def test_current_user_claim_adapter_allows_guardian_claimed_write() -> None:
    decision = require_learner_write_for_current_user(
        {
            "sub": "guardian-1",
            "role": "parent",
            "guardian_learner_ids": ["learner-1"],
        },
        "learner-1",
    )

    assert decision.allowed
    assert decision.scope == OwnershipScope.GUARDIAN


@pytest.mark.unit
def test_current_user_claim_adapter_rejects_unrelated_guardian_write() -> None:
    with pytest.raises(HTTPException) as exc_info:
        require_learner_write_for_current_user(
            {
                "sub": "guardian-1",
                "role": "parent",
                "guardian_learner_ids": ["learner-2"],
            },
            "learner-1",
        )

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail["code"] == "object_forbidden"
    assert exc_info.value.detail["permission"] == "write"


@pytest.mark.unit
def test_current_user_claim_adapter_rejects_missing_subject() -> None:
    with pytest.raises(HTTPException) as exc_info:
        require_learner_write_for_current_user(
            {"role": "parent", "guardian_learner_ids": ["learner-1"]},
            "learner-1",
        )

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.unit
def test_study_plan_route_uses_write_policy_before_enqueue() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "study_plans.py").read_text(
        encoding="utf-8"
    )

    block = source.split("async def generate_study_plan", maxsplit=1)[1].split(
        "async def _run",
        maxsplit=1,
    )[0]

    assert "current_user: dict = Depends(get_current_user)" in block
    assert "require_learner_write_for_current_user(current_user, learner_id)" in block
