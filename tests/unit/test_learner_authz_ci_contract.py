from __future__ import annotations

from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "learner-authz-coverage.yml"


@pytest.mark.unit
def test_learner_authz_workflow_exists() -> None:
    assert WORKFLOW.exists()


@pytest.mark.unit
def test_learner_authz_workflow_runs_guard() -> None:
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))

    assert data["name"] == "Learner Authorization Coverage"
    jobs = data["jobs"]
    assert "learner-authz-coverage" in jobs

    rendered = WORKFLOW.read_text(encoding="utf-8")
    assert "make learner-authz-check" in rendered
    assert "pull_request:" in rendered
    assert "master" in rendered
    assert "release/**" in rendered
