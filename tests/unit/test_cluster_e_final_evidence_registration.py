from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_e_data_resilience_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_cluster_e_final_evidence_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_e_workflow_runs_final_evidence_tests() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "cluster-e-data-resilience.yml").read_text(encoding="utf-8")

    assert "tests/unit/test_data_resilience_evidence_index.py" in workflow
    assert "tests/unit/test_cluster_e_release_gate_wiring.py" in workflow
