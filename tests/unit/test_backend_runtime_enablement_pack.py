from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from pathlib import Path

from app.services.backend_candidate_execution_harness import run_all_candidate_execution_harnesses


ROOT = Path(__file__).resolve().parents[2]


def test_candidate_execution_harnesses_pass():
    results = asyncio.run(run_all_candidate_execution_harnesses())
    assert results
    assert all(result.passed for result in results)


def test_runtime_enablement_docs_keep_destructive_actions_blocked():
    text = (ROOT / "docs/release/backend_data_retention_approval_update.md").read_text(encoding="utf-8")
    assert "`audit_logs` deletion: blocked" in text
    assert "consent table merge" not in text.lower() or "blocked" in text.lower()


def test_runtime_enablement_guard_and_blocklist_pass():
    for command in [
        [sys.executable, "scripts/check_backend_runtime_enablement_guard.py"],
        [sys.executable, "scripts/check_backend_destructive_action_blocklist.py"],
        [sys.executable, "scripts/generate_backend_runtime_enablement_report.py"],
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


def test_runtime_enablement_checksum_manifest_generated():
    assert (ROOT / "docs/release/backend_runtime_enablement_checksum_manifest.md").exists()


def test_makefile_contains_401_420_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "backend-runtime-enablement-guard:" in text
    assert "backend-destructive-action-blocklist-check:" in text
    assert "backend-runtime-enablement-report:" in text
    assert "backend-runtime-enablement-full-check:" in text
