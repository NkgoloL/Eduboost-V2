from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_post_deploy_staging_smoke_checklist import run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_post_deploy_staging_smoke_checklist_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_post_deploy_staging_smoke_checklist_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_post_deploy_staging_smoke_checklist.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Post-deploy staging smoke checklist check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_post_deploy_staging_smoke_checklist_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "post-deploy-staging-smoke-checklist-check:" in text
    assert "scripts/check_post_deploy_staging_smoke_checklist.py" in text
