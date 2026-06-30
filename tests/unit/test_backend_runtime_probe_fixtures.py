from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "tests/fixtures/backend_consolidation"


def test_backend_runtime_probe_fixtures_are_present_and_versioned():
    for name in [
        "audit_canonical_events.json",
        "consent_runtime_events.json",
        "deep_readiness_expected_checks.json",
    ]:
        payload = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
        assert payload["version"] == 1


def test_runtime_probe_fixture_checker_passes():
    result = subprocess.run(
        [sys.executable, "scripts/check_backend_runtime_probe_fixtures.py"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_runtime_probe_report_generator_passes():
    result = subprocess.run(
        [sys.executable, "scripts/generate_backend_runtime_probe_report.py"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout
    assert (ROOT / "docs/release/backend_runtime_probe_report.md").exists()


def test_makefile_contains_runtime_probe_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "backend-runtime-probe-fixtures-check:" in text
    assert "backend-runtime-probe-report:" in text
    assert "backend-runtime-probe-full-check:" in text
