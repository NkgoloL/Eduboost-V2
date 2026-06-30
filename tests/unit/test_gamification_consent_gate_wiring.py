from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTER = REPO_ROOT / "app" / "api_v2_routers" / "gamification.py"


@pytest.mark.unit
def test_gamification_routes_use_central_consent_adapter() -> None:
    source = ROUTER.read_text(encoding="utf-8")

    assert "require_active_consent_for_current_user" in source
    assert "from app.services.consent import ConsentService" not in source


@pytest.mark.unit
def test_profile_route_authorizes_before_consent_gate() -> None:
    source = ROUTER.read_text(encoding="utf-8")
    block = source.split("async def get_profile", maxsplit=1)[1].split("@router.post(\"/award-xp\")", maxsplit=1)[0]

    assert "require_learner_read_for_current_user(current_user, learner)" in block
    assert "await require_active_consent_for_current_user(db, current_user, learner_id)" in block
    assert block.index("require_learner_read_for_current_user(current_user, learner)") < block.index(
        "await require_active_consent_for_current_user(db, current_user, learner_id)"
    )


@pytest.mark.unit
def test_award_xp_route_authorizes_before_consent_gate() -> None:
    source = ROUTER.read_text(encoding="utf-8")
    block = source.split("async def award_xp", maxsplit=1)[1].split("@router.get(\"/leaderboard\")", maxsplit=1)[0]

    assert "require_learner_write_for_current_user(current_user, body.learner_id)" in block
    assert "await require_active_consent_for_current_user(db, current_user, body.learner_id)" in block
    assert block.index("require_learner_write_for_current_user(current_user, body.learner_id)") < block.index(
        "await require_active_consent_for_current_user(db, current_user, body.learner_id)"
    )
