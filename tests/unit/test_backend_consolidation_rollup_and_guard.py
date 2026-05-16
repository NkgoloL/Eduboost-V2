from __future__ import annotations

import importlib.util
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


def test_backend_consolidation_adr_exists_and_is_evidence_first():
    text = (ROOT / "docs/adr/ADR-021-backend-consolidation-evidence-first.md").read_text(encoding="utf-8")
    assert "Evidence-First" in text
    assert "Deletion only after" in text


def test_backend_consolidation_release_guard_passes():
    result = subprocess.run(
        [sys.executable, "scripts/check_backend_consolidation_release_guard.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_backend_report_generator_defines_expected_commands():
    module = _load_module("scripts/generate_backend_consolidation_report.py", "backend_consolidation_report_for_test")
    names = [name for name, _command in module.COMMANDS]
    assert "backend dragons" in names
    assert "audit inventory" in names
    assert "consent inventory" in names
    assert "health readiness contract" in names
    assert "schema drift contract" in names


def test_makefile_contains_backend_consolidation_rollup_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "backend-consolidation-report:" in text
    assert "backend-consolidation-release-guard:" in text
    assert "backend-consolidation-full-check:" in text
