from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_communications_monitoring_support_wiring_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_communications_monitoring_support_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make beta-release-communications-plan-check" in text
    assert "make beta-monitoring-incident-trigger-check" in text
    assert "make beta-participant-support-handoff-check" in text
    assert "tests/unit/test_cluster_h_communications_monitoring_support_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_communications_monitoring_support_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")

    assert "docs/operations/beta_release_communications_plan.md" in text
    assert "docs/operations/beta_monitoring_incident_trigger_matrix.md" in text
    assert "docs/operations/beta_participant_support_handoff_checklist.md" in text


@pytest.mark.unit
def test_final_beta_operator_packet_links_support_handoff() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "final_beta_operator_packet_index.md").read_text(encoding="utf-8")

    assert "docs/operations/beta_participant_support_handoff_checklist.md" in text
