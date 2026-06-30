from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_h_release_readiness import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-h-release-readiness.yml"


@pytest.mark.unit
def test_cluster_h_acceptance_memo_record_closure_continuity_wiring_registered() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_cluster_h_workflow_runs_acceptance_memo_record_closure_continuity_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "make final-acceptance-memo-check" in text
    assert "make release-record-closure-ledger-check" in text
    assert "make post-merge-evidence-continuity-note-check" in text
    assert "tests/unit/test_cluster_h_acceptance_memo_record_closure_continuity_wiring.py" in text


@pytest.mark.unit
def test_cluster_h_closure_links_acceptance_memo_record_closure_continuity_artifacts() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "CLUSTER_H_CLOSURE.md").read_text(encoding="utf-8")
    assert "docs/operations/final_acceptance_memo.md" in text
    assert "docs/operations/release_record_closure_ledger.md" in text
    assert "docs/operations/post_merge_evidence_continuity_note.md" in text


@pytest.mark.unit
def test_pr_merge_summary_links_final_acceptance_memo() -> None:
    text = (REPO_ROOT / "docs" / "operations" / "pr_merge_evidence_summary.md").read_text(encoding="utf-8")
    assert "docs/operations/final_acceptance_memo.md" in text
