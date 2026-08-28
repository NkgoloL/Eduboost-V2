"""Tests for gamification award-xp authorization wiring."""
from __future__ import annotations

from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_gamification_award_xp_uses_phase2_write_authorization() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "gamification.py").read_text(encoding="utf-8")
    block = source.split("async def award_xp", maxsplit=1)[1]
    assert "learner = await LearnerService(db).get_learner_summary(body.learner_id)" in block
    assert "require_learner_write_for_current_user(current_user, body.learner_id)" in block
    assert "await require_active_consent_for_current_user(db, current_user, body.learner_id)" in block
    assert block.index("require_learner_write_for_current_user") > block.index("learner = await LearnerService(db).get_learner_summary(body.learner_id)")
    assert block.index("require_learner_write_for_current_user") < block.index("GamificationServiceV2.from_session(db)")
