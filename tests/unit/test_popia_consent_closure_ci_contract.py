from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "popia-consent-audit.yml"


@pytest.mark.unit
def test_popia_ci_runs_closure_check() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make popia-consent-closure-check" in text


@pytest.mark.unit
def test_popia_ci_runs_closure_check_tests() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "tests/unit/test_popia_consent_closure_check.py" in text
