from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_f_ai_safety_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-f-ai-safety.yml"


@pytest.mark.unit
def test_cluster_f_secret_fixture_coverage_evidence_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_f_closure_runs_secret_and_coverage_checks() -> None:
    source = (REPO_ROOT / "scripts" / "check_cluster_f_closure.py").read_text(encoding="utf-8")

    assert "ai-prompt-secret-leakage-check" in source
    assert "ai-fixture-coverage-check" in source


@pytest.mark.unit
def test_cluster_f_workflow_runs_secret_and_coverage_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make ai-prompt-secret-leakage-check" in text
    assert "make ai-fixture-coverage-check" in text
    assert "tests/unit/test_ai_prompt_secret_leakage.py" in text
    assert "tests/unit/test_ai_fixture_coverage_matrix.py" in text
