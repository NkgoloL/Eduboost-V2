from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts/validate_phase02r_authority_schema.py"
spec = importlib.util.spec_from_file_location("phase02r_authority_validator", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_phase02r_authority_schema_is_complete() -> None:
    assert module.validate() == []


def test_translation_permissions_are_separate() -> None:
    columns = module.model_tables()["curriculum_rights_decisions"]
    assert "may_translate" in columns
    assert "may_publish_translation" in columns


def test_logical_source_and_source_version_do_not_expose_mutable_status() -> None:
    tables = module.model_tables()
    assert "status" not in tables["curriculum_sources"]
    assert "status" not in tables["curriculum_source_versions"]
