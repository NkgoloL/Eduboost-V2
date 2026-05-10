from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
INDEX = REPO_ROOT / "docs" / "frontend" / "frontend_evidence_index.md"


@pytest.mark.unit
def test_frontend_evidence_index_exists() -> None:
    assert INDEX.exists()


@pytest.mark.unit
def test_frontend_evidence_index_links_required_sections() -> None:
    text = INDEX.read_text(encoding="utf-8")

    assert "Frontend Evidence Index" in text
    assert "Cluster G Closure" in text
    assert "Journey Contracts" in text
    assert "Playwright Evidence" in text
    assert "Accessibility and Quality" in text
    assert "docs/frontend/CLUSTER_G_CLOSURE.md" in text
    assert "make cluster-g-closure-check" in text


@pytest.mark.unit
def test_frontend_evidence_index_links_runtime_and_workflow_artifacts() -> None:
    text = INDEX.read_text(encoding="utf-8")

    assert ".github/workflows/cluster-g-frontend.yml" in text
    assert ".github/workflows/frontend-e2e-opt-in.yml" in text
    assert "docs/frontend/frontend_e2e_runtime_commands.md" in text
