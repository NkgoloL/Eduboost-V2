from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_script(name: str):
    module_path = Path(__file__).resolve().parents[3] / "scripts" / "audit_remediation" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_preflight_fixture(root: Path, *, missing_registry: bool = False) -> None:
    (root / "docs/roadmap/execution/atlas").mkdir(parents=True)
    (root / "docs/roadmap/execution/technical_audit_remediation").mkdir(parents=True)
    (root / "docs/release-evidence/technical-audit/baseline-reset").mkdir(parents=True)
    (root / "docs/release-evidence/technical-audit/openapi-route-contract").mkdir(parents=True)
    (root / "data/content_factory").mkdir(parents=True)
    (root / "app/services/curriculum").mkdir(parents=True)

    (root / "docs/roadmap/execution/atlas/phase_02r_start_gate_control.json").write_text(
        json.dumps({"approved_gate": "2R.8", "authorised_next_gate": None, "phase_status": "closed"}),
        encoding="utf-8",
    )
    evidence_text = "Source commit: 0123456789abcdef0123456789abcdef01234567\nStatus: Candidate verification passed — human approval pending\n"
    (root / "docs/release-evidence/technical-audit/baseline-reset/evidence_index.md").write_text(evidence_text, encoding="utf-8")
    (root / "docs/release-evidence/technical-audit/openapi-route-contract/evidence_index.md").write_text(evidence_text, encoding="utf-8")
    (root / "docs/roadmap/execution/technical_audit_remediation/blocker_register.json").write_text(
        json.dumps({
            "stream": "technical-audit-remediation",
            "remaining_release_blockers_after_reset": [
                {"id": "TA-OPENAPI-001", "status": "evidence_recorded"},
                {"id": "TA-BACKEND-FAST-001", "status": "implementation_in_progress"},
            ],
        }),
        encoding="utf-8",
    )
    if not missing_registry:
        (root / "data/content_factory/scopes.json").write_text(json.dumps({"scopes": [{"id": "grade4-math"}]}), encoding="utf-8")
        (root / "data/content_factory/coverage_targets.json").write_text(json.dumps({"targets": []}), encoding="utf-8")
    (root / "Makefile").write_text("test-fast:\n\tpytest -c pytest.ini tests/unit -q\n", encoding="utf-8")
    (root / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    for name in ("graph.py", "corpus.py", "generation.py", "tutor_grounding.py"):
        (root / "app/services/curriculum" / name).write_text("# fixture\n", encoding="utf-8")


def test_backend_fast_preflight_accepts_clean_fixture(tmp_path: Path) -> None:
    module = load_script("verify_backend_fast_gate_preflight")
    write_preflight_fixture(tmp_path)
    result = module.verify(tmp_path)
    assert result["valid"], result


def test_backend_fast_preflight_rejects_missing_content_factory_registry(tmp_path: Path) -> None:
    module = load_script("verify_backend_fast_gate_preflight")
    write_preflight_fixture(tmp_path, missing_registry=True)
    result = module.verify(tmp_path)
    assert not result["valid"]
    assert any("Content Factory registry" in error for error in result["errors"])


def test_backend_fast_classifier_detects_known_failure_clusters() -> None:
    module = load_script("classify_backend_fast_failures")
    text = """
FAILED tests/unit/test_scope.py::test_scopes - FileNotFoundError: data/content_factory/scopes.json
FAILED tests/unit/test_popia.py::test_export - AttributeError: 'AuthContext' object has no attribute 'get'
ERROR tests/unit/test_openapi.py - OpenAPI drift detected: regenerate docs/openapi.json
= 2 failed, 1 error, 10 passed in 1.0s =
"""
    result = module.classify_text(text)
    assert not result["valid"]
    assert result["failure_count"] == 3
    assert "content_factory_registry" in result["category_names"]
    assert "popia_auth_or_route_contract" in result["category_names"]
    assert "openapi_route_contract" in result["category_names"]


def test_backend_fast_classifier_accepts_passing_output() -> None:
    module = load_script("classify_backend_fast_failures")
    result = module.classify_text("2056 passed, 12 skipped in 33.1s")
    assert result["valid"]
    assert result["failure_count"] == 0


def test_backend_fast_evidence_verifier_accepts_complete_evidence(tmp_path: Path) -> None:
    module = load_script("verify_backend_fast_evidence")
    evidence = tmp_path / "evidence"
    raw = evidence / "raw"
    raw.mkdir(parents=True)
    for name in [
        "phase02r_terminal_gate_control.json",
        "baseline_reset_check.json",
        "openapi_route_contract.json",
        "backend_fast_preflight.json",
    ]:
        (raw / name).write_text(json.dumps({"valid": True, "errors": []}), encoding="utf-8")
    (raw / "compileall.txt").write_text("", encoding="utf-8")
    (raw / "backend_fast_gate.txt").write_text("10 passed in 1s", encoding="utf-8")
    (raw / "backend_fast_gate_result.json").write_text(json.dumps({"valid": True, "returncode": 0}), encoding="utf-8")
    (raw / "backend_fast_failure_classification.json").write_text(
        json.dumps({"failure_count": 0, "category_names": []}),
        encoding="utf-8",
    )
    (raw / "SHA256SUMS.txt").write_text("hash file\n", encoding="utf-8")
    (evidence / "evidence_index.md").write_text(
        "**Source commit:** 0123456789abcdef0123456789abcdef01234567\n**Status:** Candidate verification passed — human approval pending\n",
        encoding="utf-8",
    )
    result = module.verify(evidence)
    assert result["valid"], result
