"""Tests for diagnostic submit write authorization wiring."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_submit_diagnostic_uses_phase2_write_authorization() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "diagnostics.py").read_text(
        encoding="utf-8"
    )

    block = source.split("async def submit_diagnostic", maxsplit=1)[1]

    assert "require_learner_write_for_current_user(current_user, body.learner_id)" in block
    submit_before_guardian = block.split("guardian = await GuardianRepository", maxsplit=1)[0]
    assert "assert_can_access_learner(current_user, learner)" not in submit_before_guardian
