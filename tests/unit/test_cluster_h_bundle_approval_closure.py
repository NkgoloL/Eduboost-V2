from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_bundle_approval_closure_registered() -> None:
    for script in (
        "scripts/generate_staging_smoke_evidence_manifest.py",
        "scripts/generate_beta_signoff_manifest.py",
        "scripts/generate_beta_release_evidence_bundle.py",
        "scripts/generate_release_candidate_tag_manifest.py",
    ):
        subprocess.run(
            [sys.executable, script],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_bundle_approval_closure_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make beta-release-evidence-bundle" in text
    assert "make release-candidate-tag-manifest" in text
    assert "make beta-release-evidence-bundle-check" in text
    assert "make release-approval-workflow-contract-check" in text
    assert "make release-candidate-tag-manifest-check" in text
    assert "make cluster-h-closure-check" in text


@pytest.mark.unit
def test_beta_readiness_contract_links_bundle_approval_closure() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "beta_release_readiness_contract.md").read_text(encoding="utf-8")

    assert "docs/operations/beta_release_evidence_bundle.md" in text
    assert "docs/operations/release_approval_workflow_contract.md" in text
    assert "docs/operations/release_candidate_tag_manifest.md" in text
    assert "docs/operations/CLUSTER_H_CLOSURE.md" in text
