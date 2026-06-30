from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_archival_lock_pr_ready_toc_wiring_registered() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_archival_lock_pr_ready_toc_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "make archival-lock-assertion-check" in text
    assert "make pr-ready-final-closure-certificate-check" in text
    assert "make final-release-evidence-toc-check" in text
    assert "tests/unit/test_cluster_h_archival_lock_pr_ready_toc_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_archival_lock_pr_ready_toc_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")
    assert "docs/operations/archival_lock_assertion.md" in text
    assert "docs/operations/pr_ready_final_closure_certificate.md" in text
    assert "docs/operations/final_release_evidence_toc.md" in text


@pytest.mark.unit
def test_final_acceptance_packet_links_toc() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "final_acceptance_packet_index.md").read_text(encoding="utf-8")
    assert "docs/operations/final_release_evidence_toc.md" in text
