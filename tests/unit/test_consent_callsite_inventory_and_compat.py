from __future__ import annotations

import importlib.util
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


def test_consent_audit_normalizer_maps_learner_to_resource():
    module = _load_module("app/services/consent_compat.py", "consent_compat_for_test")
    event = module.normalize_consent_audit_event(
        action="consent.granted",
        actor_id="guardian-1",
        learner_id="learner-1",
        metadata={"source": "unit"},
    )
    payload = event.to_audit_kwargs()
    assert payload["action"] == "consent.granted"
    assert payload["resource_type"] == "learner_consent"
    assert payload["resource_id"] == "learner-1"
    assert payload["metadata"]["learner_id"] == "learner-1"
    assert payload["metadata"]["source"] == "unit"


def test_consent_action_classification():
    module = _load_module("app/services/consent_compat.py", "consent_compat_classify_for_test")
    assert module.classify_consent_action("consent.status.read") == "read"
    assert module.classify_consent_action("consent.granted") == "write"
    assert module.classify_consent_action("custom") == "unknown"


def test_consent_inventory_generator_writes_markdown(tmp_path):
    module = _load_module("scripts/generate_consent_callsite_inventory.py", "consent_inventory_for_test")
    rows = module.collect_rows()
    rendered = module.render_markdown(rows)
    output = tmp_path / "consent_inventory.md"
    output.write_text(rendered, encoding="utf-8")
    text = output.read_text(encoding="utf-8")
    assert "# Consent Call-Site Inventory" in text
    assert "Review checklist" in text


def test_makefile_contains_consent_inventory_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "consent-callsite-inventory:" in text
    assert "consent-compatibility-check:" in text
