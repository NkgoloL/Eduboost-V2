from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_d_ci_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-d-ci.yml"


@pytest.mark.unit
def test_cluster_d_closure_evidence_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_d_ci_runs_closure_command_and_tests() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make cluster-d-closure-check" in text
    assert "tests/unit/test_production_key_vault_behavior.py" in text
    assert "tests/unit/test_cluster_d_closure_check.py" in text
