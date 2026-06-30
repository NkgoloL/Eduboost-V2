"""Tests for POPIA data-export authorization wiring."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_popia_export_uses_phase2_read_authorization() -> None:
    source = (REPO_ROOT / "app" / "services" / "popia_service.py").read_text(
        encoding="utf-8"
    )

    block = source.split("async def build_learner_export", maxsplit=1)[1]

    assert "self.load_learner_for_write(learner_id, current_user)" in block
    assert "self.load_learner_for_read(learner_id, current_user)" in block
