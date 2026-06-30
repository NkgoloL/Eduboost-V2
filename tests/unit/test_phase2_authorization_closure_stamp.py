from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = REPO_ROOT / "docs" / "security" / "PHASE2_AUTHORIZATION_CLOSURE.md"


@pytest.mark.unit
def test_phase2_closure_report_has_closure_stamp() -> None:
    text = REPORT.read_text(encoding="utf-8")

    assert "## Closure Stamp" in text
    assert "make phase2-authz-closure" in text
    assert "make learner-authz-check" in text
    assert "make phase2-authz-check" in text
