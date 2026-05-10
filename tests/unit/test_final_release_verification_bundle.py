from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_final_release_verification_bundle import COMMANDS, run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_final_release_verification_bundle_static_check_passes() -> None:
    failures = [result for result in run_checks(execute=False) if not result.ok]
    assert failures == []


@pytest.mark.unit
def test_final_release_verification_bundle_command_list_is_complete() -> None:
    flattened = "\n".join(" ".join(command) for _, command in COMMANDS)

    assert "generated-artifact-hygiene-check" in flattened
    assert "branch-sync-rebase-checklist-check" in flattened
    assert "beta-release-final-checklist-check" in flattened
    assert "beta-release-execution-plan-check" in flattened
    assert "beta-pr-body-check" in flattened
    assert "cluster-h-release-readiness-check" in flattened
    assert "cluster-h-closure-check" in flattened


@pytest.mark.unit
def test_final_release_verification_bundle_cli_passes_static_mode() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_final_release_verification_bundle.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Final release verification bundle check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_final_release_verification_targets() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "final-release-verification-check:" in text
    assert "final-release-verification:" in text
