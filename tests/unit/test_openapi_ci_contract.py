"""Tests for Makefile OpenAPI targets and drift workflow."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_makefile_exposes_openapi_targets() -> None:
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "openapi:" in makefile
    assert "openapi-check:" in makefile
    assert "$(PYTHON) scripts/generate_openapi.py" in makefile
    assert "$(PYTHON) scripts/generate_openapi.py --check" in makefile


@pytest.mark.unit
def test_openapi_drift_workflow_is_master_and_release_aware() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "openapi-drift.yml").read_text(
        encoding="utf-8"
    )

    assert "pull_request:" in workflow
    assert "push:" in workflow
    assert "      - master" in workflow
    assert '      - "release/**"' in workflow
    assert "      - main" not in workflow
    assert '      - "main"' not in workflow
    assert "make openapi-check" in workflow
