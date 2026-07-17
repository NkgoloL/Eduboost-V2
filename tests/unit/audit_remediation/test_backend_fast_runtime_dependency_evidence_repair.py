from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COLLECT = ROOT / "scripts/audit_remediation/collect_backend_fast_runtime_dependency_evidence.sh"
ENV_VERIFY = ROOT / "scripts/audit_remediation/verify_backend_fast_environment.py"
DOC = ROOT / "docs/roadmap/execution/technical_audit_remediation/02b_backend_fast_runtime_dependencies.md"


def test_runtime_dependency_collector_does_not_execute_make_test_fast_while_rendering_markdown() -> None:
    text = COLLECT.read_text(encoding="utf-8")
    assert "\\`make test-fast\\`" in text
    assert "`make test-fast`" not in text.replace("\\`make test-fast\\`", "")
    assert "make test-fast" in text
    assert "$(make test-fast" not in text


def test_runtime_dependency_collector_uses_authority_python_for_environment_verifier() -> None:
    text = COLLECT.read_text(encoding="utf-8")
    assert "AUTHORITY_PYTHON" in text
    assert "--python-bin \"$AUTHORITY_PYTHON\"" in text
    assert '"$AUTHORITY_PYTHON" scripts/audit_remediation/verify_backend_fast_runtime_dependencies.py' in text


def test_environment_verifier_checks_target_interpreter_imports() -> None:
    source = ENV_VERIFY.read_text(encoding="utf-8")
    ast.parse(source)
    assert "subprocess.run" in source
    assert "import_status(python_bin" in source
    assert "importlib.import_module" not in source
    assert "--python-bin" in source


def test_phase_02b_doc_declares_runtime_dependency_boundary_and_kg_non_scope() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "does not create passing backend-fast evidence" in text
    assert "make test-fast" in text
    assert "No runtime knowledge-graph work" in text
