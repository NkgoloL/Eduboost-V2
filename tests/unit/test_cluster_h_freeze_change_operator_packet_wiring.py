from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_freeze_change_operator_packet_wiring_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_freeze_change_operator_packet_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make beta-release-freeze-window-check" in text
    assert "make release-change-control-exception-log-check" in text
    assert "make final-beta-operator-packet-check" in text
    assert "tests/unit/test_cluster_h_freeze_change_operator_packet_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_freeze_change_operator_packet_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")

    assert "docs/operations/beta_release_freeze_window_contract.md" in text
    assert "docs/operations/release_change_control_exception_log.md" in text
    assert "docs/operations/final_beta_operator_packet_index.md" in text


@pytest.mark.unit
def test_final_cluster_h_closeout_links_operator_packet() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "final_cluster_h_closeout_rollup.md").read_text(encoding="utf-8")

    assert "docs/operations/final_beta_operator_packet_index.md" in text
