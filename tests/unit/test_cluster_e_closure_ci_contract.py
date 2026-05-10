from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_e_data_resilience_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-e-data-resilience.yml"


@pytest.mark.unit
def test_cluster_e_closure_evidence_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_e_workflow_runs_closure_check_and_tests() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make cluster-e-closure-check" in text
    assert "tests/unit/test_cluster_e_closure_check.py" in text
    assert "tests/unit/test_cluster_e_closure_report.py" in text


@pytest.mark.unit
def test_project_evidence_index_links_cluster_e_closure() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "project_evidence_index.md").read_text(encoding="utf-8")

    assert "Data Resilience Contract" in text
    assert "docs/operations/CLUSTER_E_CLOSURE.md" in text
    assert "make cluster-e-closure-check" in text
