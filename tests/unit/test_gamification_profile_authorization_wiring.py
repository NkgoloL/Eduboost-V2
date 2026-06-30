"""Tests for gamification profile authorization wiring."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_gamification_profile_uses_phase2_read_authorization() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "gamification.py").read_text(
        encoding="utf-8"
    )

    block = source.split("async def get_profile", maxsplit=1)[1].split(
        "@router.post",
        maxsplit=1,
    )[0]

    assert "learner = await LearnerRepository(db).get_by_id(learner_id)" in block
    assert "require_learner_read_for_current_user(current_user, learner)" in block
    assert block.index("require_learner_read_for_current_user") < block.index(
        "await require_active_consent_for_current_user(db, current_user, learner_id)"
    )
