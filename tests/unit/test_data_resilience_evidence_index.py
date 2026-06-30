from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
INDEX = REPO_ROOT / "docs" / "operations" / "data_resilience_evidence_index.md"


@pytest.mark.unit
def test_data_resilience_evidence_index_exists() -> None:
    assert INDEX.exists()


@pytest.mark.unit
def test_data_resilience_evidence_index_links_backup_restore_and_readiness() -> None:
    text = INDEX.read_text(encoding="utf-8")

    assert "Cluster E Closure" in text
    assert "Backup Evidence" in text
    assert "Restore Evidence" in text
    assert "Restore Readiness" in text
    assert "docs/operations/CLUSTER_E_CLOSURE.md" in text
    assert "docs/operations/database_backup_manifest.md" in text
    assert "docs/operations/database_restore_evidence.md" in text
    assert "docs/operations/production_restore_approval.md" in text


@pytest.mark.unit
def test_data_resilience_evidence_index_links_required_commands() -> None:
    text = INDEX.read_text(encoding="utf-8")

    assert "make cluster-e-closure-check" in text
    assert "make database-backup-integrity-check" in text
    assert "make database-restore-integrity-check" in text
    assert "make production-restore-approval-check" in text
