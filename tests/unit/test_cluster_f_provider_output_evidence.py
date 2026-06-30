from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_f_ai_safety_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-f-ai-safety.yml"


@pytest.mark.unit
def test_cluster_f_provider_output_evidence_registered() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_f_workflow_runs_provider_output_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make llm-provider-fallback-contract-check" in text
    assert "make ai-output-schema-contract-check" in text
    assert "tests/unit/test_llm_provider_fallback_contract.py" in text
    assert "tests/unit/test_ai_output_schema_contract.py" in text
