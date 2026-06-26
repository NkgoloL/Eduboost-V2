from __future__ import annotations

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


def _write_passing_json_set(raw: Path) -> None:
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
    (raw / "backend_fast_gate.txt").write_text("2304 passed, 11 skipped, 1 xfailed in 268.81s\n", encoding="utf-8")
    (raw / "backend_fast_gate_result.json").write_text(
        json.dumps({"valid": True, "returncode": 0, "command": "make test-fast"}), encoding="utf-8"
    )
    (raw / "backend_fast_runner_stdout.json").write_text(
        json.dumps({"valid": True, "returncode": 0, "command": "make test-fast"}), encoding="utf-8"
    )
    (raw / "backend_fast_failure_classification.json").write_text(
        json.dumps({"failure_count": 0, "failed_tests": [], "category_names": []}), encoding="utf-8"
    )
    (raw / "SHA256SUMS.txt").write_text("0" * 64 + "  raw/backend_fast_gate_result.json\n", encoding="utf-8")


def test_phase02k_verifier_assets_are_present() -> None:
    module = _load("verify_backend_fast_phase02k")
    result = module.verify(ROOT)
    assert result["valid"], result


def test_candidate_evidence_rejects_stale_failed_gate_result(tmp_path: Path) -> None:
    module = _load("verify_backend_fast_evidence")
    evidence = tmp_path / "backend-fast-gate"
    raw = evidence / "raw"
    _write_index(evidence)
    _write_passing_json_set(raw)
    (raw / "backend_fast_gate_result.json").write_text(
        json.dumps({"valid": False, "returncode": 2, "command": "make test-fast"}), encoding="utf-8"
    )
    (raw / "backend_fast_failure_classification.json").write_text(
        json.dumps({"failure_count": 1, "failed_tests": ["tests/unit/test_topic_map_worklist.py::test_x"], "category_names": ["content_factory_registry"]}),
        encoding="utf-8",
    )
    (raw / "backend_fast_gate.txt").write_text("FAILED tests/unit/test_topic_map_worklist.py::test_x\n1 failed, 2303 passed\nmake: *** Error 2\n", encoding="utf-8")
    result = module.verify(evidence)
    assert result["valid"] is False
    assert any("returncode 0" in error for error in result["errors"])
    assert any("zero failures" in error for error in result["errors"])
    assert any("failed/error test lines" in error for error in result["errors"])


def test_candidate_evidence_rejects_command_prefixed_json(tmp_path: Path) -> None:
    module = _load("verify_backend_fast_evidence")
    evidence = tmp_path / "backend-fast-gate"
    raw = evidence / "raw"
    _write_index(evidence)
    _write_passing_json_set(raw)
    (raw / "backend_fast_preflight.json").write_text("$ python script.py --json\n{\"valid\": true}\n", encoding="utf-8")
    result = module.verify(evidence)
    assert result["valid"] is False
    assert any("must be valid JSON" in error for error in result["errors"])


def test_candidate_evidence_rejects_sha_self_reference(tmp_path: Path) -> None:
    module = _load("verify_backend_fast_evidence")
    evidence = tmp_path / "backend-fast-gate"
    raw = evidence / "raw"
    _write_index(evidence)
    _write_passing_json_set(raw)
    (raw / "SHA256SUMS.txt").write_text("0" * 64 + "  raw/SHA256SUMS.txt\n", encoding="utf-8")
    result = module.verify(evidence)
    assert result["valid"] is False
    assert any("self-referential" in error for error in result["errors"])


def test_collector_captures_json_without_command_banner() -> None:
    text = (ROOT / "scripts/audit_remediation/collect_backend_fast_evidence.sh").read_text(encoding="utf-8")
    assert "run_json_capture" in text
    assert "echo \"$ $*\"" not in text
    assert "! -name 'SHA256SUMS.txt'" in text
