from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_cicd_staging_evidence import REQUIRED, check_all

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_cicd_required_files_cover_workflows_docker_env_and_staging() -> None:
    assert ".github/workflows/ci-cd.yml" in REQUIRED
    assert "docker/Dockerfile.api" in REQUIRED
    assert "docs/operations/staging_release_gate.md" in REQUIRED


@pytest.mark.unit
def test_cicd_staging_evidence_passes() -> None:
    assert [r for r in check_all() if not r.ok] == []


@pytest.mark.unit
def test_cicd_staging_cli_passes() -> None:
    result = subprocess.run([sys.executable, "scripts/check_cicd_staging_evidence.py"], cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
