from __future__ import annotations
import pytest
pytestmark = pytest.mark.integration

import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import pytest  # noqa: E402

from scripts.check_cluster_g_frontend_evidence import run_checks  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-g-frontend.yml"
if not WORKFLOW.exists() and (REPO_ROOT / 'archive' / 'github_workflows' / WORKFLOW.name).exists():
    WORKFLOW = REPO_ROOT / 'archive' / 'github_workflows' / WORKFLOW.name


@pytest.mark.unit
def test_cluster_g_build_e2e_workflow_evidence_registered() -> None:
    for script in (
        "scripts/generate_frontend_route_inventory.py",
        "scripts/generate_frontend_api_client_inventory.py",
        "scripts/generate_frontend_runtime_inventory.py",
    ):
        subprocess.run(
            [sys.executable, script],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_cluster_g_workflow_runs_build_e2e_workflow_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make frontend-build-test-lint-contract-check" in text
    assert "make frontend-e2e-opt-in-workflow-check" in text
    assert "tests/unit/test_frontend_build_test_lint_contract.py" in text
    assert "tests/unit/test_frontend_e2e_opt_in_workflow.py" in text
