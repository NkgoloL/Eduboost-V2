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


def test_backend_consolidation_dragons_documented():
    text = (ROOT / "docs/release/backend_consolidation_dragons.md").read_text(encoding="utf-8")
    assert "Split audit persistence" in text
    assert "Split consent persistence" in text
    assert "ORM/schema drift" in text
    assert "Delete-first consolidation risk" in text


def test_backend_consolidation_dragon_checker_runs():
    result = subprocess.run(
        [sys.executable, "scripts/check_backend_consolidation_dragons.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout


def test_schema_compare_collects_orm_tables_without_database():
    module = _load_module("scripts/compare_orm_tables_to_database.py", "compare_orm_tables_to_database_for_test")
    tables = module.collect_orm_tables()
    assert isinstance(tables, set)
    assert tables


def test_makefile_contains_backend_consolidation_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "backend-consolidation-dragons-check:" in text
    assert "schema-drift-check:" in text
    assert "backend-consolidation-diagnostics-check:" in text
