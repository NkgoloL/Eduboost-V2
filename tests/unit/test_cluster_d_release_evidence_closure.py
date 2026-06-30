from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_d_ci_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_cluster_d_release_evidence_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_d_closure_runs_release_evidence_commands() -> None:
    source = (REPO_ROOT / "scripts" / "check_cluster_d_closure.py").read_text(encoding="utf-8")

    assert "generate_release_evidence_manifest.py" in source
    assert "staging-release-gate-check" in source


@pytest.mark.unit
def test_cluster_d_ci_runs_release_evidence_commands() -> None:
    workflow = (REPO_ROOT / ".github" / "workflows" / "cluster-d-ci.yml").read_text(encoding="utf-8")

    assert "python scripts/generate_release_evidence_manifest.py" in workflow
    assert "make staging-release-gate-check" in workflow
