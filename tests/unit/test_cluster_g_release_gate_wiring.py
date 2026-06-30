from __future__ import annotations
import pytest
pytestmark = pytest.mark.integration

from pathlib import Path

import pytest

from scripts.check_cluster_g_frontend_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_cluster_g_release_gate_evidence_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_release_evidence_manifest_includes_cluster_g_closure() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "release_evidence_manifest.md").read_text(encoding="utf-8")

    assert "Cluster G frontend journey" in text
    assert "make cluster-g-closure-check" in text


@pytest.mark.unit
def test_staging_release_gate_includes_cluster_g_closure() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "staging_release_gate.md").read_text(encoding="utf-8")

    assert "make cluster-g-closure-check" in text
    assert "docs/frontend/CLUSTER_G_CLOSURE.md" in text


@pytest.mark.unit
def test_project_evidence_index_links_cluster_g() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "project_evidence_index.md").read_text(encoding="utf-8")

    assert "Frontend Journey Contract" in text
    assert "docs/frontend/frontend_evidence_index.md" in text
    assert "make cluster-g-closure-check" in text
