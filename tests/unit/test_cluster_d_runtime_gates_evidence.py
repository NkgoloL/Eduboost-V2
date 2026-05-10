from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_cluster_d_ci_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-d-ci.yml"


@pytest.mark.unit
def test_cluster_d_runtime_gates_evidence_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_d_ci_runs_runtime_gate_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make production-secret-placeholder-check" in text
    assert "make dev-only-endpoint-check" in text
    assert "tests/unit/test_production_secret_placeholders.py" in text
    assert "tests/unit/test_dev_only_endpoint_exposure.py" in text
