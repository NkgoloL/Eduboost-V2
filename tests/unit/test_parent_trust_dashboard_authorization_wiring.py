"""Tests for parent trust-dashboard learner authorization wiring."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_parent_trust_dashboard_checks_each_learner_with_phase2_read_policy() -> None:
    source = (REPO_ROOT / "app" / "api_v2_routers" / "parents.py").read_text(
        encoding="utf-8"
    )

    block = source.split("async def get_parent_trust_dashboard", maxsplit=1)[1].split(
        '@router.get("/{guardian_id}/export")',
        maxsplit=1,
    )[0]

    assert "require_learner_read_for_current_user(current_user, learner)" in block
    assert block.index("require_learner_read_for_current_user") < block.index(
        "await consent_service.require_active_consent"
    )
