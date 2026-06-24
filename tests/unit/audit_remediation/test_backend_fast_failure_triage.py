from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


ROOT = Path(__file__).resolve().parents[3]
REPORT = _load(ROOT / "scripts/audit_remediation/backend_fast_failure_report.py")
ENV = _load(ROOT / "scripts/audit_remediation/verify_backend_fast_environment.py")
TRIAGE = _load(ROOT / "scripts/audit_remediation/verify_backend_fast_failure_triage.py")


def test_backend_fast_failure_report_extracts_summary_and_missing_modules() -> None:
    text = """
    ERROR tests/unit/test_api_v2_router_contract.py
    ModuleNotFoundError: No module named 'structlog'
    FAILED tests/unit/test_sprint3_popia_router_data_rights.py::test_contract
    161 failed, 1255 passed, 10 skipped, 1 xfailed, 111 errors in 99.0s
    """
    result = REPORT.build_report(text, root=ROOT, source="sample")
    assert result["valid"] is False
    assert result["summary_counts"]["failed"] == 161
    assert result["summary_counts"]["errors"] == 111
    assert "structlog" in result["missing_modules"]
    assert "popia" in result["domain_counts"]
    assert result["recommendations"]


def test_backend_fast_environment_required_imports_include_gate_options() -> None:
    modules = {module for module, _reason, _hint in ENV.REQUIRED_IMPORTS}
    assert "xdist" in modules
    assert "pytest_cov" in modules
    assert "hypothesis" in modules
    assert "asyncpg" in modules
    assert "structlog" in modules


def test_failure_triage_verifier_accepts_control_files_without_imported_failure_evidence(tmp_path: Path) -> None:
    root = tmp_path
    (root / "docs/roadmap/execution/technical_audit_remediation").mkdir(parents=True)
    (root / "scripts/audit_remediation").mkdir(parents=True)
    (root / "docs/roadmap/execution/technical_audit_remediation/02a_backend_fast_failure_triage.md").write_text(
        "Failed authority gate captured — remediation pending\nruntime knowledge-graph non-scope\n",
        encoding="utf-8",
    )
    for rel_path in TRIAGE.REQUIRED_SCRIPTS:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    register = {
        "active_slice": "02a-backend-fast-failure-triage",
        "backend_fast_failure": {
            "passing_evidence_policy": "Do not create backend-fast-gate candidate evidence until make test-fast exits 0."
        },
        "remaining_release_blockers_after_reset": [
            {"id": "TA-BACKEND-FAST-001", "status": "blocked_failed_authority_gate"}
        ],
    }
    (root / "docs/roadmap/execution/technical_audit_remediation/blocker_register.json").write_text(
        json.dumps(register), encoding="utf-8"
    )
    result = TRIAGE.verify(root)
    assert result["valid"] is True
    assert result["warnings"]


def test_failure_triage_verifier_rejects_passing_status_in_failed_evidence(tmp_path: Path) -> None:
    root = tmp_path
    (root / "docs/roadmap/execution/technical_audit_remediation").mkdir(parents=True)
    (root / "scripts/audit_remediation").mkdir(parents=True)
    (root / "docs/roadmap/execution/technical_audit_remediation/02a_backend_fast_failure_triage.md").write_text(
        "Failed authority gate captured — remediation pending\nruntime knowledge-graph non-scope\n",
        encoding="utf-8",
    )
    for rel_path in TRIAGE.REQUIRED_SCRIPTS:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    (root / "docs/roadmap/execution/technical_audit_remediation/blocker_register.json").write_text(
        json.dumps({
            "active_slice": "02a-backend-fast-failure-triage",
            "backend_fast_failure": {"passing_evidence_policy": "policy"},
            "remaining_release_blockers_after_reset": [
                {"id": "TA-BACKEND-FAST-001", "status": "blocked_failed_authority_gate"}
            ],
        }),
        encoding="utf-8",
    )
    evidence = root / "docs/release-evidence/technical-audit/backend-fast-gate-failure/attempt/raw"
    evidence.mkdir(parents=True)
    (evidence.parent / "evidence_index.md").write_text(
        "**Source commit:** 0123456789abcdef0123456789abcdef01234567\n"
        "**Status:** Candidate verification passed — human approval pending\n",
        encoding="utf-8",
    )
    (evidence / "backend_fast_failure_report.json").write_text(json.dumps({"valid": False}), encoding="utf-8")
    result = TRIAGE.verify(root, require_failure_evidence=True)
    assert result["valid"] is False
    assert any("must use non-passing status" in error or "must not claim" in error for error in result["errors"])


def test_find_backend_fast_log_accepts_directory(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    log = raw / "backend_fast_gate.txt"
    log.write_text("1 failed", encoding="utf-8")
    assert REPORT.find_backend_fast_log(tmp_path) == log


def test_failed_evidence_importer_escapes_markdown_command_backticks() -> None:
    script = (ROOT / "scripts/audit_remediation/import_backend_fast_failed_evidence.sh").read_text(encoding="utf-8")
    assert "\\`make test-fast\\`" in script
    assert "until `make test-fast` exits" not in script
