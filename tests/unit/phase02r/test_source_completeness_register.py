from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts/curriculum/validate_source_completeness_register.py"
spec = importlib.util.spec_from_file_location("phase02r_inventory_validator", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def load_register():
    import json

    return json.loads(module.DEFAULT_REGISTER.read_text(encoding="utf-8"))


def test_draft_inventory_is_structurally_valid() -> None:
    document = load_register()
    assert module.validate(document, require_frozen=False) == []


def test_draft_inventory_cannot_be_used_as_closure_evidence() -> None:
    document = load_register()
    errors = module.validate(document, require_frozen=True)
    assert any("status=frozen" in error for error in errors)
    assert any("frozen_by" in error for error in errors)


def test_manifest_hash_detects_changes() -> None:
    document = load_register()
    document["scope"]["grade"] = 5
    errors = module.validate(document, require_frozen=False)
    assert any("manifest_sha256" in error for error in errors)
