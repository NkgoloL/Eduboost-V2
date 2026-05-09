"""Tests for lesson generation write authorization wiring."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_generate_lesson_route_uses_write_authorization_before_enqueue() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "lessons.py").read_text(
        encoding="utf-8"
    )

    block = source.split("async def generate_lesson", maxsplit=1)[1].split(
        "async def _run",
        maxsplit=1,
    )[0]

    assert "current_user: dict = Depends(get_current_user)" in block
    assert "require_learner_write_for_current_user(current_user, str(body.learner_id))" in block
    assert "user_id = UUID(str(current_user[\"sub\"]))" in block
    assert "Depends(get_current_user_id)" not in block
