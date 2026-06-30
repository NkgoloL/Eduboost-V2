"""Tests for consent-revoke authorization wiring."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_consent_revoke_uses_phase2_write_authorization() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "consent.py").read_text(
        encoding="utf-8"
    )

    block = source.split("async def revoke_consent", maxsplit=1)[1].split(
        "@router.get",
        maxsplit=1,
    )[0]

    assert "current_user: AuthContext = Depends(require_auth_context)" in block
    assert "learner = await LearnerRepository(db).get_by_id(learner_id)" in block
    assert "require_learner_write_for_current_user(current_user, learner_id)" in block
    assert "guardian_id=current_user.user_id" in block
