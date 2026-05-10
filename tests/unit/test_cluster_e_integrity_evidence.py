from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_e_data_resilience_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-e-data-resilience.yml"


@pytest.mark.unit
def test_cluster_e_integrity_evidence_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_e_workflow_runs_integrity_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make database-backup-integrity-check" in text
    assert "make database-restore-integrity-check" in text
    assert "tests/unit/test_database_backup_integrity.py" in text
    assert "tests/unit/test_database_restore_integrity.py" in text
