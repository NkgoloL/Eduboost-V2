from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_cluster_f_closure import COMMANDS, run_checks


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_cluster_f_closure_command_list_is_complete() -> None:
    flattened = "\n".join(" ".join(command) for _, command in COMMANDS)

    assert "caps-alignment-contract-check" in flattened
    assert "ai-safety-boundary-check" in flattened
    assert "ai-prompt-input-contract-check" in flattened
    assert "diagnostic-generation-safety-check" in flattened
    assert "lesson-generation-safety-check" in flattened
    assert "remediation-safety-contract-check" in flattened
    assert "llm-provider-fallback-contract-check" in flattened
    assert "ai-output-schema-contract-check" in flattened
    assert "cluster-f-ai-safety-check" in flattened


@pytest.mark.unit
def test_cluster_f_closure_check_passes() -> None:
    failures = [result for result in run_checks() if not result.ok]

    assert failures == []


@pytest.mark.unit
def test_cluster_f_closure_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_cluster_f_closure.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Cluster F closure check" in result.stdout


@pytest.mark.unit
def test_makefile_exposes_cluster_f_closure_check() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "cluster-f-closure-check:" in text
    assert "scripts/check_cluster_f_closure.py" in text
