from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from app.services.backend_runtime_wiring_preflight import all_preflights_pass, run_all_preflights


ROOT = Path(__file__).resolve().parents[2]


def test_backend_runtime_wiring_preflights_pass():
    results = run_all_preflights()
    assert results
    assert all(result.passed for result in results)
    assert all_preflights_pass() is True


def test_decision_ledger_blocks_destructive_defaults():
    text = (ROOT / "docs/release/backend_implementation_decision_ledger.md").read_text(encoding="utf-8")
    assert "All destructive decisions default to blocked" in text
    assert "`audit_logs` deletion allowed" in text
    assert "`alembic stamp head` allowed as repair" in text


def test_runtime_wiring_preflight_check_and_report_run():
    for command in [
        [sys.executable, "scripts/check_backend_runtime_wiring_preflight.py"],
        [sys.executable, "scripts/generate_backend_runtime_wiring_preflight_report.py"],
    ]:
        result = subprocess.run(
            command,
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        assert result.returncode == 0, result.stdout


def test_makefile_contains_376_382_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "backend-runtime-wiring-preflight-check:" in text
    assert "backend-runtime-wiring-preflight-report:" in text
    assert "backend-implementation-376-382-full-check:" in text
