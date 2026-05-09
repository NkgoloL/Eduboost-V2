"""Tests for consent-status authorization wiring."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_consent_status_uses_phase2_read_authorization() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "consent.py").read_text(
        encoding="utf-8"
    )

    block = source.split("async def consent_status", maxsplit=1)[1]

    assert "current_user: dict = Depends(get_current_user)" in block
    assert "learner = await LearnerRepository(db).get_by_id(str(learner_id))" in block
    assert "require_learner_read_for_current_user(current_user, learner)" in block
    assert "guardian_id: UUID = Depends(get_current_guardian_id)" not in block
