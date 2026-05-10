from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_cluster_g_frontend_evidence import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "cluster-g-frontend.yml"


@pytest.mark.unit
def test_cluster_g_parent_denial_evidence_registered() -> None:
    subprocess.run(
        [sys.executable, "scripts/generate_frontend_route_inventory.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_cluster_g_workflow_runs_parent_denial_checks() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "make parent-vertical-journey-contract-check" in text
    assert "make frontend-auth-consent-denial-check" in text
    assert "tests/unit/test_parent_vertical_journey_contract.py" in text
    assert "tests/unit/test_frontend_auth_consent_denial_contract.py" in text
