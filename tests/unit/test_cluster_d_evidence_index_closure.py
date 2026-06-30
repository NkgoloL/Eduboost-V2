from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_d_ci_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_cluster_d_evidence_index_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_d_ci_runs_evidence_index_tests() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "cluster-d-ci.yml").read_text(encoding="utf-8")

    assert "make release-evidence-artifacts-check" in workflow
    assert "tests/unit/test_project_evidence_index.py" in workflow
    assert "tests/unit/test_cluster_d_closure_report.py" in workflow


@pytest.mark.unit
def test_cluster_d_ci_runs_release_artifact_tests() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "cluster-d-ci.yml").read_text(encoding="utf-8")

    assert "tests/unit/test_release_evidence_artifacts.py" in workflow
    assert "tests/unit/test_cluster_d_closure_report.py" in workflow
    assert "tests/unit/test_project_evidence_index.py" in workflow
