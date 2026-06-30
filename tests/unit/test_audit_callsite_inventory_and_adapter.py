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


def test_normalize_audit_kwargs_maps_learner_to_resource_payload():
    module = _load_module("app/repositories/audit_compat.py", "audit_compat_for_test")
    event = module.normalize_audit_kwargs(
        event_type="consent.granted",
        actor_id="guardian-1",
        learner_id="learner-1",
        metadata={"source": "unit"},
    )
    payload = event.to_canonical_payload()
    assert payload["action"] == "consent.granted"
    assert payload["resource_id"] == "learner-1"
    assert payload["payload"]["learner_id"] == "learner-1"
    assert payload["payload"]["source"] == "unit"


def test_audit_adapter_prefers_record_method():
    module = _load_module("app/repositories/audit_compat.py", "audit_compat_record_for_test")

    class Repo:
        def __init__(self):
            self.calls = []

        async def record(self, **kwargs):
            self.calls.append(kwargs)
            return {"ok": True}

    async def run():
        repo = Repo()
        adapter = module.AuditRepositoryCompatAdapter(repo)
        result = await adapter.append(action="x", resource_id="r1")
        assert result == {"ok": True}
        assert repo.calls[0]["action"] == "x"
        assert repo.calls[0]["resource_id"] == "r1"

    import asyncio

    asyncio.run(run())


def test_audit_inventory_generator_writes_markdown(tmp_path):
    module = _load_module("scripts/generate_audit_callsite_inventory.py", "audit_inventory_for_test")
    output = tmp_path / "audit_inventory.md"
    module.main.__wrapped__() if hasattr(module.main, "__wrapped__") else None
    # Exercise pure functions instead of CLI argv mutation.
    rows = module.collect_rows()
    rendered = module.render_markdown(rows)
    output.write_text(rendered, encoding="utf-8")
    text = output.read_text(encoding="utf-8")
    assert "# Audit Call-Site Inventory" in text
    assert "Review checklist" in text


def test_makefile_contains_audit_inventory_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "audit-callsite-inventory:" in text
    assert "audit-compatibility-check:" in text
