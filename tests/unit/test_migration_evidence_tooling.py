from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_module():
    path = ROOT / "scripts/capture_migration_evidence.py"
    spec = importlib.util.spec_from_file_location("capture_migration_evidence_for_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["capture_migration_evidence_for_test"] = module
    spec.loader.exec_module(module)
    return module


def test_database_url_disposable_detection():
    module = _load_module()
    assert module._database_url_is_disposable("sqlite+aiosqlite:///./test.db") is True
    assert module._database_url_is_disposable("postgresql+asyncpg://u:p@localhost:5432/eduboost_test") is True
    assert module._database_url_is_disposable("postgresql+asyncpg://u:p@localhost:5432/eduboost") is False


def test_redacts_database_url_password():
    module = _load_module()
    redacted = module._redact_database_url("postgresql+asyncpg://user:secret@localhost:5432/eduboost_test")
    assert "secret" not in redacted
    assert "user:***" in redacted


def test_build_plan_contains_upgrade_head():
    module = _load_module()
    commands = dict(module.build_plan(include_downgrade=False))
    assert commands["alembic_current_before"] == ["alembic", "current"]
    assert commands["alembic_upgrade_head"] == ["alembic", "upgrade", "head"]


def test_validate_payload_can_require_pass(tmp_path):
    module = _load_module()
    path = tmp_path / "migration_latest.json"
    path.write_text(
        json.dumps(
            {
                "captured_at": "2026-05-16T00:00:00Z",
                "database_url_redacted": "postgresql+asyncpg://user:***@localhost:5432/eduboost_test",
                "passed": False,
                "results": [
                    {
                        "name": "alembic_upgrade_head",
                        "command": ["alembic", "upgrade", "head"],
                        "return_code": 1,
                        "stdout": "failed",
                        "passed": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    assert module.validate_payload(path) is True
    assert module.validate_payload(path, require_pass=True) is False


def test_makefile_contains_migration_evidence_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "migration-evidence-capture:" in text
    assert "migration-evidence-check:" in text
    assert "migration-evidence-schema-check:" in text


def test_placeholder_database_credentials_are_rejected():
    module = _load_module()
    assert module._database_url_has_placeholder_credentials(
        "postgresql+asyncpg://user:pass@localhost:5432/eduboost_test"
    ) is True
    assert module._database_url_has_placeholder_credentials(
        "postgresql+asyncpg://real_user:real-secret@localhost:5432/eduboost_test"
    ) is False
