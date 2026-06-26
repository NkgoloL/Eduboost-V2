from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _load(name: str):
    module_path = ROOT / "scripts" / "audit_remediation" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_index(evidence: Path) -> None:
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "evidence_index.md").write_text(
        "**Source commit:** 0123456789abcdef0123456789abcdef01234567\n"
        "**Status:** Candidate verification passed — human approval pending\n"
        "This evidence confirms the backend fast gate and does not claim full product release readiness.\n",
        encoding="utf-8",
    )


def _write_valid_evidence(raw: Path, gate_text: str) -> None:
    raw.mkdir(parents=True, exist_ok=True)
    for name in [
        "phase02r_terminal_gate_control.json",
        "baseline_reset_check.json",
        "openapi_route_contract.json",
        "popia_route_contract.json",
        "frontend_env_contract.json",
        "dependency_scan_workflow.json",
        "backend_fast_preflight.json",
    ]:
        (raw / name).write_text(json.dumps({"valid": True, "errors": []}), encoding="utf-8")
    (raw / "compileall.txt").write_text("", encoding="utf-8")
    (raw / "backend_fast_gate.txt").write_text(gate_text, encoding="utf-8")
    (raw / "backend_fast_gate_result.json").write_text(
        json.dumps({"valid": True, "returncode": 0, "command": "make test-fast"}), encoding="utf-8"
    )
    (raw / "backend_fast_runner_stdout.json").write_text(
        json.dumps({"valid": True, "returncode": 0, "command": "make test-fast"}), encoding="utf-8"
    )
    (raw / "backend_fast_failure_classification.json").write_text(
        json.dumps({"failure_count": 0, "failed_tests": [], "category_names": []}), encoding="utf-8"
    )
    digest = hashlib.sha256((raw / "backend_fast_gate_result.json").read_bytes()).hexdigest()
    (raw / "SHA256SUMS.txt").write_text(f"{digest}  raw/backend_fast_gate_result.json\n", encoding="utf-8")


def test_phase02l_verifier_assets_are_present() -> None:
    module = _load("verify_backend_fast_phase02l")
    result = module.verify(ROOT)
    assert result["valid"], result


def test_backend_fast_evidence_accepts_xfailed_passing_summary(tmp_path: Path) -> None:
    module = _load("verify_backend_fast_evidence")
    evidence = tmp_path / "backend-fast-gate"
    raw = evidence / "raw"
    _write_index(evidence)
    _write_valid_evidence(raw, "2315 passed, 11 skipped, 1 xfailed, 4 warnings in 396.88s\n")
    result = module.verify(evidence)
    assert result["valid"], result


def test_backend_fast_evidence_still_rejects_failed_summary(tmp_path: Path) -> None:
    module = _load("verify_backend_fast_evidence")
    evidence = tmp_path / "backend-fast-gate"
    raw = evidence / "raw"
    _write_index(evidence)
    _write_valid_evidence(raw, "1 failed, 2315 passed, 11 skipped in 396.88s\n")
    result = module.verify(evidence)
    assert result["valid"] is False
    assert any("failure summary" in error for error in result["errors"])


def test_backend_fast_evidence_still_rejects_make_error(tmp_path: Path) -> None:
    module = _load("verify_backend_fast_evidence")
    evidence = tmp_path / "backend-fast-gate"
    raw = evidence / "raw"
    _write_index(evidence)
    _write_valid_evidence(raw, "2315 passed\nmake: *** [Makefile:99: test-fast] Error 2\n")
    result = module.verify(evidence)
    assert result["valid"] is False
    assert any("failure summary" in error for error in result["errors"])
