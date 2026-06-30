"""Tests for parent learner-progress authorization wiring."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_parent_progress_uses_phase2_read_authorization() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "parents.py").read_text(
        encoding="utf-8"
    )

    block = source.split("async def get_learner_progress", maxsplit=1)[1].split(
        "@router.delete",
        maxsplit=1,
    )[0]

    assert "require_learner_read_for_current_user(current_user, learner)" in block
    assert "Not authorised to view this learner" not in block
