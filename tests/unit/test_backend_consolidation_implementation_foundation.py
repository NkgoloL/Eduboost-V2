from __future__ import annotations

import asyncio
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


def test_canonical_audit_write_records_through_adapter():
    module = _load_module("app/services/backend_consolidation_runtime.py", "backend_consolidation_runtime_for_test")

    class Repo:
        def __init__(self):
            self.calls = []

        async def record(self, **kwargs):
            self.calls.append(kwargs)
            return {"ok": True}

    async def run():
        repo = Repo()
        event = module.CanonicalAuditWrite(action="audit.test", actor_id="system", resource_id="r1")
        result = await module.record_canonical_audit_event(repo, event)
        assert result == {"ok": True}
        assert repo.calls[0]["action"] == "audit.test"
        assert repo.calls[0]["resource_id"] == "r1"

    asyncio.run(run())


def test_consent_audit_event_records_with_learner_resource_id():
    module = _load_module("app/services/backend_consolidation_runtime.py", "backend_consolidation_runtime_consent_for_test")

    class Repo:
        def __init__(self):
            self.calls = []

        def append(self, **kwargs):
            self.calls.append(kwargs)
            return "recorded"

    async def run():
        repo = Repo()
        result = await module.record_consent_audit_event(
            repo,
            action="consent.granted",
            actor_id="guardian-1",
            learner_id="learner-1",
            metadata={"source": "unit"},
        )
        assert result == "recorded"
        assert repo.calls[0]["action"] == "consent.granted"
        assert repo.calls[0]["resource_id"] == "learner-1"
        assert repo.calls[0]["payload"]["learner_id"] == "learner-1"

    asyncio.run(run())


def test_probe_constructor_reports_import_failures_without_raising():
    module = _load_module("app/services/backend_consolidation_runtime.py", "backend_consolidation_runtime_probe_for_test")
    result = module.probe_constructor("not.a.real.module", "Missing")
    assert result.importable is False
    assert result.constructable_without_args is False
    assert result.error


def test_adr_022_keeps_destructive_option_not_approved():
    text = (ROOT / "docs/adr/ADR-022-audit-consent-table-ownership-options.md").read_text(encoding="utf-8")
    assert "Option D" in text
    assert "Not approved" in text
    assert "Do not discard audit or consent history" in text


def test_implementation_foundation_check_and_report_pass():
    for script in [
        "scripts/check_backend_consolidation_implementation_foundation.py",
        "scripts/generate_backend_consolidation_implementation_report.py",
    ]:
        result = subprocess.run(
            [sys.executable, script],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        assert result.returncode == 0, result.stdout


def test_makefile_contains_merged_implementation_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "backend-consolidation-implementation-foundation-check:" in text
    assert "backend-consolidation-implementation-foundation-report:" in text
    assert "backend-consolidation-implementation-foundation-full-check:" in text
