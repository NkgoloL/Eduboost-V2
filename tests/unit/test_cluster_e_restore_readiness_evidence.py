from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_e_data_resilience_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-e-data-resilience.yml"


@pytest.mark.unit
def test_cluster_e_restore_readiness_evidence_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_e_closure_runs_restore_readiness_checks() -> None:
    source = (REPO_ROOT / "scripts" / "check_cluster_e_closure.py").read_text(encoding="utf-8")

    assert "database-resilience-env-matrix-check" in source
    assert "production-restore-approval-check" in source


@pytest.mark.unit
def test_cluster_e_workflow_runs_restore_readiness_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make database-resilience-env-matrix-check" in text
    assert "make production-restore-approval-check" in text
    assert "tests/unit/test_database_resilience_env_matrix.py" in text
    assert "tests/unit/test_production_restore_approval.py" in text
