from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_acceptance_packet_handoff_freeze_access_policy_wiring_registered() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_acceptance_packet_handoff_freeze_access_policy_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "make final-acceptance-packet-index-check" in text
    assert "make release-handoff-freeze-assertion-check" in text
    assert "make post-closeout-evidence-access-policy-check" in text
    assert "tests/unit/test_cluster_h_acceptance_packet_handoff_freeze_access_policy_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_acceptance_packet_handoff_freeze_access_policy_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")
    assert "docs/operations/final_acceptance_packet_index.md" in text
    assert "docs/operations/release_handoff_freeze_assertion.md" in text
    assert "docs/operations/post_closeout_evidence_access_policy.md" in text


@pytest.mark.unit
def test_final_release_evidence_ledger_links_acceptance_packet() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "final_release_evidence_ledger.md").read_text(encoding="utf-8")
    assert "docs/operations/final_acceptance_packet_index.md" in text
