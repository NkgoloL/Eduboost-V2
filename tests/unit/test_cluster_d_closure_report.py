from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = REPO_ROOT / "docs" / "operations" / "CLUSTER_D_CLOSURE.md"


@pytest.mark.unit
def test_cluster_d_closure_report_exists() -> None:
    assert REPORT.exists()


@pytest.mark.unit
def test_cluster_d_closure_report_has_required_commands() -> None:
    text = REPORT.read_text(encoding="utf-8")

    assert "Cluster D CI/Deployment/Environment Closure" in text
    assert "make cluster-d-closure-check" in text
    assert "make release-evidence-artifacts-check" in text
    assert "make staging-release-gate-check" in text


@pytest.mark.unit
def test_cluster_d_closure_report_links_required_artifacts() -> None:
    text = REPORT.read_text(encoding="utf-8")

    assert "docs/operations/release_evidence_manifest.md" in text
    assert "docs/operations/staging_release_gate.md" in text
    assert ".github/workflows/cluster-d-ci.yml" in text
