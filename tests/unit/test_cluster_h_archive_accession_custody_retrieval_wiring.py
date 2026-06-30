from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_archive_accession_custody_retrieval_wiring_registered() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_archive_accession_custody_retrieval_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "make final-archive-accession-record-check" in text
    assert "make post-closeout-custody-register-check" in text
    assert "make terminal-evidence-retrieval-guide-check" in text
    assert "tests/unit/test_cluster_h_archive_accession_custody_retrieval_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_archive_accession_custody_retrieval_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")
    assert "docs/operations/final_archive_accession_record.md" in text
    assert "docs/operations/post_closeout_custody_register.md" in text
    assert "docs/operations/terminal_evidence_retrieval_guide.md" in text


@pytest.mark.unit
def test_final_sealed_package_manifest_links_archive_accession_record() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "final_sealed_package_manifest.md").read_text(encoding="utf-8")
    assert "docs/operations/final_archive_accession_record.md" in text
