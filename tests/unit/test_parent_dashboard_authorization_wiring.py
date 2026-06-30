"""Tests for parent dashboard learner authorization wiring."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_parent_dashboard_checks_each_learner_with_phase2_read_policy() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "parents.py").read_text(
        encoding="utf-8"
    )

    start = source.find("async def get_parent_dashboard")
    assert start != -1

    end = source.find("\n\n\n@router.", start + len("async def get_parent_dashboard"))
    if end == -1:
        end = len(source)

    block = source[start:end]

    assert "require_learner_read_for_current_user(current_user, learner)" in block
    assert block.index("require_learner_read_for_current_user") < block.index(
        "await require_active_consent_for_current_user(db, current_user, learner.id)"
    )
