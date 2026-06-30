"""Tests for parent learner-erasure authorization wiring."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_parent_erasure_uses_phase2_write_authorization() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "parents.py").read_text(
        encoding="utf-8"
    )

    block = source.split("async def request_erasure", maxsplit=1)[1].split(
        "async def _log_purge_request",
        maxsplit=1,
    )[0]

    assert "require_learner_write_for_current_user(current_user, learner_id)" in block
    assert "Not authorised to erase this learner" not in block
