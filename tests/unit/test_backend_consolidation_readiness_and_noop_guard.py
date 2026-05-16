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

def test_readiness_matrix_and_retention_checklist_exist():
    matrix = (ROOT / "docs/release/backend_consolidation_readiness_matrix.md").read_text(encoding="utf-8")
    retention = (ROOT / "docs/release/backend_data_retention_decision_checklist.md").read_text(encoding="utf-8")
    assert "Implementation unlock rule" in matrix
    assert "Deletion unlock rule" in matrix
    assert "fresh-start audit acceptable" in retention
    assert "default: NO" in retention

def test_deletion_candidate_inventory_generator_renders_rows():
    module = _load_module("scripts/generate_backend_deletion_candidate_inventory.py", "backend_deletion_candidate_inventory_for_test")
    rows = module.collect_candidates()
    rendered = module.render(rows)
    assert "# Backend Deletion Candidate Inventory" in rendered
    assert "This inventory is diagnostic only" in rendered

def test_backend_consolidation_noop_guard_passes():
    result = subprocess.run(
        [sys.executable, "scripts/check_backend_consolidation_noop_guard.py"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout

def test_readiness_report_generator_defines_expected_commands():
    module = _load_module("scripts/generate_backend_consolidation_readiness_report.py", "backend_consolidation_readiness_report_for_test")
    names = [name for name, _command in module.COMMANDS]
    assert "deletion candidate inventory" in names
    assert "no-op guard" in names

def test_makefile_contains_readiness_noop_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "backend-deletion-candidate-inventory:" in text
    assert "backend-consolidation-noop-guard:" in text
    assert "backend-consolidation-readiness-report:" in text
    assert "backend-consolidation-readiness-full-check:" in text
