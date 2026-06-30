from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def load_script(name: str):
    module_path = ROOT / "scripts" / "audit_remediation" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_valid_evidence(evidence: Path, *, category_names: list[str] | None = None) -> None:
    raw = evidence / "raw"
    raw.mkdir(parents=True)
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
    (raw / "backend_fast_gate.txt").write_text(
        "2315 passed, 11 skipped, 1 xfailed, 4 warnings in 12.3s\n",
        encoding="utf-8",
    )
    (raw / "backend_fast_gate_result.json").write_text(
        json.dumps({"valid": True, "returncode": 0, "command": "make test-fast"}, sort_keys=True),
        encoding="utf-8",
    )
    (raw / "backend_fast_runner_stdout.json").write_text(
        json.dumps({"valid": True, "returncode": 0, "command": "make test-fast"}, sort_keys=True),
        encoding="utf-8",
    )
    (raw / "backend_fast_failure_classification.json").write_text(
        json.dumps(
            {
                "valid": True,
                "failure_count": 0,
                "failed_tests": [],
                "category_names": category_names or [],
                "summary_counts": {"passed": 2315, "skipped": 11, "xfailed": 1},
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    lines = []
    for path in sorted(raw.iterdir()):
        if path.name in {"SHA256SUMS.txt", "backend_fast_evidence_check.json"}:
            continue
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  raw/{path.name}\n")
    (raw / "SHA256SUMS.txt").write_text("".join(lines), encoding="utf-8")
    (evidence / "evidence_index.md").write_text(
        "**Source commit:** 0123456789abcdef0123456789abcdef01234567\n"
        "**Status:** Candidate verification passed — human approval pending\n"
        "This evidence confirms the backend fast gate and does not claim full product release readiness.\n",
        encoding="utf-8",
    )


def test_phase02n_verifier_assets_are_present() -> None:
    module = load_script("verify_backend_fast_phase02n")
    result = module.verify(ROOT)
    assert result["valid"], result


def test_classifier_does_not_emit_categories_for_green_output_with_keywords() -> None:
    module = load_script("classify_backend_fast_failures")
    text = "2315 passed, 1 xfailed, 4 warnings in 12s\nwarning: POPIA AsyncMock cleanup note\n"
    result = module.classify_text(text)
    assert result["valid"] is True
    assert result["failure_count"] == 0
    assert result["category_names"] == []


def test_backend_fast_verifier_accepts_green_classification_with_legacy_categories(tmp_path: Path) -> None:
    module = load_script("verify_backend_fast_evidence")
    evidence = tmp_path / "evidence"
    _write_valid_evidence(evidence, category_names=["popia_auth_or_route_contract"])
    result = module.verify(evidence)
    assert result["valid"], result
    assert any("diagnostic categories despite zero failures" in warning for warning in result["warnings"])


def test_backend_fast_verifier_rejects_hash_mismatch(tmp_path: Path) -> None:
    module = load_script("verify_backend_fast_evidence")
    evidence = tmp_path / "evidence"
    _write_valid_evidence(evidence)
    (evidence / "raw/backend_fast_gate.txt").write_text("tampered\n", encoding="utf-8")
    result = module.verify(evidence)
    assert not result["valid"]
    assert any("digest mismatch" in error for error in result["errors"])


def test_collector_clears_raw_dir_and_excludes_self_check_from_sha_manifest() -> None:
    collector = (ROOT / "scripts/audit_remediation/collect_backend_fast_evidence.sh").read_text(encoding="utf-8")
    assert 'rm -rf "$RAW_DIR"' in collector
    assert "! -name 'backend_fast_evidence_check.json'" in collector
    assert "derived self-check JSON is intentionally" in collector
