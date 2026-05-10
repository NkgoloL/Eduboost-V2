from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_execution_guardrail_closeout_checksum_wiring_registered() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_execution_guardrail_closeout_checksum_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "make release-owner-execution-guardrail-check" in text
    assert "make final-project-closeout-attestation-check" in text
    assert "make cluster-h-release-evidence-checksum-index-check" in text
    assert "tests/unit/test_cluster_h_execution_guardrail_closeout_checksum_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_execution_guardrail_closeout_checksum_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")
    assert "docs/operations/release_owner_execution_guardrail.md" in text
    assert "docs/operations/final_project_closeout_attestation.md" in text
    assert "docs/operations/cluster_h_release_evidence_checksum_index.md" in text


@pytest.mark.unit
def test_final_release_handoff_links_checksum_index() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "final_release_handoff_package.md").read_text(encoding="utf-8")
    assert "docs/operations/cluster_h_release_evidence_checksum_index.md" in text
