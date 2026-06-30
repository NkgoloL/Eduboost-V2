from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_runtime_integration_proof_scripts_run():
    for command in [
        [sys.executable, "scripts/generate_runtime_integration_proof_reports.py"],
        [sys.executable, "scripts/check_runtime_integration_proof.py"],
    ]:
        result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        assert result.returncode == 0, result.stdout


def test_makefile_contains_831_870_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "runtime-integration-proof-check:" in text
    assert "popia-lifecycle-integration-test:" in text
    assert "backend-implementation-831-870-full-check:" in text
