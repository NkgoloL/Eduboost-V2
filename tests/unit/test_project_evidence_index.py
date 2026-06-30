from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
INDEX = REPO_ROOT / "docs" / "operations" / "project_evidence_index.md"


@pytest.mark.unit
def test_project_evidence_index_exists() -> None:
    assert INDEX.exists()


@pytest.mark.unit
def test_project_evidence_index_covers_clusters_a_to_d() -> None:
    text = INDEX.read_text(encoding="utf-8")

    assert "Runtime/API Contract" in text
    assert "Authorization Contract" in text
    assert "POPIA Consent/Audit Contract" in text
    assert "CI/Deployment/Environment Contract" in text


@pytest.mark.unit
def test_project_evidence_index_links_release_gate_commands() -> None:
    text = INDEX.read_text(encoding="utf-8")

    assert "make staging-release-gate-check" in text
    assert "make release-evidence-artifacts-check" in text
    assert "make cluster-d-closure-check" in text
