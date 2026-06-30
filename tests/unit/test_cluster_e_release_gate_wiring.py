from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_release_evidence_manifest_includes_cluster_e_closure() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "release_evidence_manifest.md").read_text(encoding="utf-8")

    assert "Cluster E data resilience" in text
    assert "make cluster-e-closure-check" in text


@pytest.mark.unit
def test_staging_release_gate_includes_cluster_e_closure() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "staging_release_gate.md").read_text(encoding="utf-8")

    assert "make cluster-e-closure-check" in text
    assert "docs/operations/CLUSTER_E_CLOSURE.md" in text


@pytest.mark.unit
def test_project_evidence_index_links_data_resilience_index() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "project_evidence_index.md").read_text(encoding="utf-8")

    assert "docs/operations/data_resilience_evidence_index.md" in text
    assert "make cluster-e-closure-check" in text
