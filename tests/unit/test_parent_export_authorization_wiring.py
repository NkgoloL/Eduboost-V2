"""Tests for parent access-bundle export authorization wiring."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_parent_export_checks_each_learner_with_phase2_read_policy() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "parents.py").read_text(
        encoding="utf-8"
    )

    block = source.split("async def export_parent_access_bundle", maxsplit=1)[1].split(
        "@router.get",
        maxsplit=1,
    )[0]

    assert "require_learner_read_for_current_user(current_user, learner)" in block
