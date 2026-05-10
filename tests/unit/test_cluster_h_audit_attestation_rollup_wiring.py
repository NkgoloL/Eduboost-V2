from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_audit_attestation_rollup_wiring_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_audit_attestation_rollup_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make release-audit-trail-index-check" in text
    assert "make beta-release-closure-attestation-check" in text
    assert "make cluster-h-final-closeout-rollup-check" in text
    assert "tests/unit/test_cluster_h_audit_attestation_rollup_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_audit_attestation_rollup_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")

    assert "docs/operations/release_audit_trail_index.md" in text
    assert "docs/operations/beta_release_closure_attestation.md" in text
    assert "docs/operations/final_cluster_h_closeout_rollup.md" in text


@pytest.mark.unit
def test_final_pr_merge_readiness_links_audit_attestation_rollup() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "final_pr_merge_readiness_contract.md").read_text(encoding="utf-8")

    assert "docs/operations/release_audit_trail_index.md" in text
    assert "docs/operations/beta_release_closure_attestation.md" in text
    assert "docs/operations/final_cluster_h_closeout_rollup.md" in text
