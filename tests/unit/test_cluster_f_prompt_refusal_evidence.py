from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_f_ai_safety_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-f-ai-safety.yml"


@pytest.mark.unit
def test_cluster_f_prompt_refusal_evidence_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_f_closure_runs_prompt_inventory_and_refusal_checks() -> None:
    source = (REPO_ROOT / "scripts" / "check_cluster_f_closure.py").read_text(encoding="utf-8")

    assert "ai-prompt-surface-inventory-check" in source
    assert "ai-refusal-fixture-check" in source


@pytest.mark.unit
def test_cluster_f_workflow_runs_prompt_inventory_and_refusal_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make ai-prompt-surface-inventory" in text
    assert "make ai-prompt-surface-inventory-check" in text
    assert "make ai-refusal-fixture-check" in text
    assert "tests/unit/test_ai_prompt_surface_inventory.py" in text
    assert "tests/unit/test_ai_refusal_fixtures.py" in text
