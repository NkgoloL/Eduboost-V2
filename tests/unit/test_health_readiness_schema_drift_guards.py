from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_module(relative: str, name: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_health_readiness_contract_mentions_false_positive_controls():
    text = (ROOT / "docs/release/health_readiness_diagnostic_contract.md").read_text(encoding="utf-8")
    assert "false positives" in text
    assert "required core table presence" in text
    assert "no unsafe public write operations" in text


def test_health_readiness_checker_runs():
    result = subprocess.run(
        [sys.executable, "scripts/check_health_readiness_contract.py"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_schema_drift_contract_checker_runs_without_database():
    result = subprocess.run(
        [sys.executable, "scripts/check_schema_drift_contract.py"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_health_checker_detects_write_like_patterns():
    module = _load_module("scripts/check_health_readiness_contract.py", "health_readiness_contract_for_test")
    assert module._source_has_unsafe_write("session.commit()") is True
    assert module._source_has_unsafe_write("return {'status': 'ok'}") is False


def test_makefile_contains_health_schema_guard_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "health-readiness-contract-check:" in text
    assert "schema-drift-contract-check:" in text
    assert "backend-runtime-diagnostics-check:" in text
