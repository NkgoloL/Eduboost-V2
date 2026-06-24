from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts/audit_remediation/verify_backend_fast_runtime_dependencies.py"
SYNC = ROOT / "scripts/audit_remediation/sync_backend_fast_runtime_dependencies.sh"
COLLECT = ROOT / "scripts/audit_remediation/collect_backend_fast_runtime_dependency_evidence.sh"
DOC = ROOT / "docs/roadmap/execution/technical_audit_remediation/02b_backend_fast_runtime_dependencies.md"


def _load_module():
    spec = importlib.util.spec_from_file_location("verify_backend_fast_runtime_dependencies", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_verifier_script_exists_and_exposes_required_imports() -> None:
    module = _load_module()
    required = module.REQUIRED_IMPORTS
    for name in ["fastapi", "hypothesis", "jinja2", "httpx", "structlog", "yaml", "psycopg2", "redis", "anthropic", "arq", "pypdf"]:
        assert name in required


def test_static_verifier_cli_returns_json() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--json", "--static-only"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    assert result.returncode == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["valid"] is True
    assert payload["static_only"] is True
    assert "authority_interpreter" in payload


def test_sync_and_collect_scripts_are_executable_and_boundary_safe() -> None:
    for path in [SYNC, COLLECT]:
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "make test-fast" not in text or "Authority command remains" in text
    assert "requirements/dev.txt" in SYNC.read_text(encoding="utf-8")
    assert "not backend-fast candidate evidence" in COLLECT.read_text(encoding="utf-8")


def test_document_declares_backend_fast_evidence_boundary() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "make test-fast" in text
    assert "does not create passing backend-fast evidence" in text
    assert "No runtime knowledge-graph work" in text
