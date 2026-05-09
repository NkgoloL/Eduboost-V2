"""Tests for learner mastery route object-authorization wiring."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_get_mastery_route_uses_phase2_authorization_dependency() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "learners.py").read_text(
        encoding="utf-8"
    )

    get_mastery_block = source.split("async def get_mastery", maxsplit=1)[1].split(
        "@router.delete",
        maxsplit=1,
    )[0]

    assert "require_learner_read_for_current_user(current_user, learner)" in get_mastery_block
    assert "assert_can_access_learner(current_user, learner)" not in get_mastery_block


@pytest.mark.unit
def test_get_learner_and_get_mastery_both_use_same_read_policy() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "learners.py").read_text(
        encoding="utf-8"
    )

    assert source.count("require_learner_read_for_current_user(current_user, learner)") >= 2
