from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = REPO_ROOT / "docs" / "operations" / "CLUSTER_E_CLOSURE.md"


@pytest.mark.unit
def test_cluster_e_closure_report_exists() -> None:
    assert REPORT.exists()


@pytest.mark.unit
def test_cluster_e_closure_report_has_required_commands() -> None:
    text = REPORT.read_text(encoding="utf-8")

    assert "Cluster E Data Resilience Closure" in text
    assert "make cluster-e-closure-check" in text
    assert "make database-backup-integrity-check" in text
    assert "make database-restore-integrity-check" in text


@pytest.mark.unit
def test_cluster_e_closure_report_links_required_artifacts() -> None:
    text = REPORT.read_text(encoding="utf-8")

    assert "docs/operations/database_backup_manifest.md" in text
    assert "docs/operations/database_restore_evidence.md" in text
    assert ".github/workflows/cluster-e-data-resilience.yml" in text
