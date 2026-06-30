from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(relative: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_schema_drift_preflight_rejects_placeholder_credentials():
    module = _load("scripts/run_disposable_schema_drift_proof.py", "schema_drift_proof_for_test")
    failures = module.preflight("postgresql+asyncpg://user:pass@localhost:5432/eduboost_test")
    assert "DATABASE_URL contains placeholder credentials" in failures


def test_schema_drift_dry_run_writes_valid_payload(tmp_path):
    module = _load("scripts/run_disposable_schema_drift_proof.py", "schema_drift_proof_dry_for_test")
    payload = module.run_proof(
        "postgresql+asyncpg://real_user:real_password@localhost:5432/eduboost_test",
        dry_run=True,
    )
    json_path = tmp_path / "schema.json"
    md_path = tmp_path / "schema.md"
    module.write_outputs(payload, json_path=json_path, markdown_path=md_path)
    assert json.loads(json_path.read_text(encoding="utf-8"))["passed"] is True
    assert module.validate(json_path, require_pass=True) is True


def test_deep_readiness_specs_are_read_only_and_guard_rejects_writes():
    module = _load("app/services/deep_readiness_readonly.py", "deep_readiness_readonly_for_test")
    summary = module.summarize_specs()
    assert summary["read_only"] is True
    assert "required_core_tables" in summary["names"]
    for bad in ["session.commit()", "INSERT INTO audit_events", "alembic stamp head"]:
        try:
            module.assert_read_only_operation(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected rejection for {bad}")


def test_audit_canonicalization_slice_records_through_adapter():
    module = _load("app/services/audit_canonicalization_slice.py", "audit_canonicalization_slice_for_test")

    class Repo:
        def __init__(self):
            self.calls = []

        async def record(self, **kwargs):
            self.calls.append(kwargs)
            return {"ok": True}

    async def run():
        repo = Repo()
        result = await module.record_learner_audit_event(
            repo,
            action="learner.read",
            actor_id="guardian-1",
            learner_id="learner-1",
            metadata={"source": "unit"},
        )
        assert result == {"ok": True}
        assert repo.calls[0]["action"] == "learner.read"
        assert repo.calls[0]["resource_type"] == "learner"
        assert repo.calls[0]["resource_id"] == "learner-1"
        assert repo.calls[0]["payload"]["learner_id"] == "learner-1"

    asyncio.run(run())


def test_new_check_scripts_pass():
    for script in [
        "scripts/check_deep_readiness_readonly_guard.py",
        "scripts/check_audit_canonicalization_slice.py",
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


def test_makefile_contains_364_366_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "schema-drift-disposable-proof:" in text
    assert "deep-readiness-readonly-check:" in text
    assert "audit-canonicalization-slice-check:" in text
    assert "backend-implementation-364-366-full-check:" in text
