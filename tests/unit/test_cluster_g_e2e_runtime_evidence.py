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


@pytest.mark.unit
def test_cluster_g_e2e_runtime_evidence_registered() -> None:
    subprocess.run(
        [sys.executable, "scripts/generate_frontend_route_inventory.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [sys.executable, "scripts/generate_frontend_api_client_inventory.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [sys.executable, "scripts/generate_frontend_runtime_inventory.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_cluster_g_workflow_runs_e2e_runtime_evidence_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make frontend-e2e-env-contract-check" in text
    assert "make frontend-e2e-runtime-command-check" in text
    assert "tests/unit/test_frontend_e2e_environment_contract.py" in text
    assert "tests/unit/test_frontend_e2e_runtime_commands.py" in text
