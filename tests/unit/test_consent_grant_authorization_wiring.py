"""Tests for consent-grant authorization wiring."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_consent_grant_uses_phase2_write_authorization() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "consent.py").read_text(
        encoding="utf-8"
    )

    block = source.split("async def grant_consent", maxsplit=1)[1].split(
        "@router.post",
        maxsplit=1,
    )[0]

    assert "current_user: dict = Depends(get_current_user)" in block
    assert "learner = await LearnerRepository(db).get_by_id(learner_id)" in block
    assert "require_learner_write_for_current_user(current_user, learner_id)" in block
    assert "str(current_user[\"sub\"])" in block
