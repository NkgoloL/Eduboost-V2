from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_f_ai_safety_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-f-ai-safety.yml"


@pytest.mark.unit
def test_cluster_f_fixture_validation_evidence_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_f_closure_runs_fixture_validation() -> None:
    source = (REPO_ROOT / "scripts" / "check_cluster_f_closure.py").read_text(encoding="utf-8")

    assert "ai-output-fixture-validation-check" in source
    assert "tests/unit/test_ai_output_fixtures.py" in source
    assert "tests/unit/test_validate_ai_output_fixtures.py" in source


@pytest.mark.unit
def test_cluster_f_workflow_runs_fixture_validation() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make ai-output-fixture-validation-check" in text
    assert "tests/unit/test_ai_output_fixtures.py" in text
    assert "tests/unit/test_validate_ai_output_fixtures.py" in text
