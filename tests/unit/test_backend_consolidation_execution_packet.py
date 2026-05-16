from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_execution_packet_documents_forbidden_actions():
    text = (ROOT / "docs/release/backend_consolidation_execution_packet.md").read_text(encoding="utf-8")
    assert "Explicitly forbidden" in text
    assert "deleting audit repositories before call-site migration" in text
    assert "using `alembic stamp head` as a blind repair" in text


def test_check_backend_consolidation_execution_packet_passes():
    result = subprocess.run(
        [sys.executable, "scripts/check_backend_consolidation_execution_packet.py"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_generate_backend_consolidation_execution_report_runs():
    result = subprocess.run(
        [sys.executable, "scripts/generate_backend_consolidation_execution_report.py"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout
    assert (ROOT / "docs/release/backend_consolidation_execution_report.md").exists()


def test_makefile_contains_execution_packet_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "backend-consolidation-execution-packet-check:" in text
    assert "backend-consolidation-execution-report:" in text
    assert "backend-consolidation-execution-full-check:" in text
