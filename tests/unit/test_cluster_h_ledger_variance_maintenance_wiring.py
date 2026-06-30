from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_ledger_variance_maintenance_wiring_registered() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_ledger_variance_maintenance_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "make final-release-evidence-ledger-check" in text
    assert "make frozen-scope-variance-register-check" in text
    assert "make post-closeout-maintenance-boundary-check" in text
    assert "tests/unit/test_cluster_h_ledger_variance_maintenance_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_ledger_variance_maintenance_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")
    assert "docs/operations/final_release_evidence_ledger.md" in text
    assert "docs/operations/frozen_scope_variance_register.md" in text
    assert "docs/operations/post_closeout_maintenance_boundary.md" in text


@pytest.mark.unit
def test_final_project_closeout_links_final_release_evidence_ledger() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "final_project_closeout_attestation.md").read_text(encoding="utf-8")
    assert "docs/operations/final_release_evidence_ledger.md" in text
