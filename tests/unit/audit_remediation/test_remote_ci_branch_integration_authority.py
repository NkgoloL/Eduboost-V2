from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.audit_remediation import verify_remote_ci_branch_integration_authority as authority
from scripts.audit_remediation import verify_remote_ci_branch_integration_evidence as evidence


def test_phase08_authority_assets_are_declared() -> None:
    result = authority.verify()
    assert result["phase"] == "08-remote-ci-branch-integration-authority"
    assert result["remote_ci_run_claimed"] is False
    assert result["full_release_readiness_claimed"] is False
    assert set(result["prior_evidence"]) >= {
        "backend_fast_gate",
        "frontend_tooling_authority",
        "ci_authority_workflow",
        "dependency_scan_enforcement",
        "e2e_playwright_authority",
        "openapi_frontend_contract",
    }


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_sha_manifest(raw_dir: Path) -> None:
    lines = []
    for path in sorted(raw_dir.iterdir()):
        if path.name in {"SHA256SUMS.txt", "remote_ci_branch_integration_evidence_check.json"}:
            continue
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            lines.append(f"{digest}  {path.name}\n")
    (raw_dir / "SHA256SUMS.txt").write_text("".join(lines), encoding="utf-8")


def test_phase08_evidence_accepts_static_no_remote_ci_bundle(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "evidence"
    raw = evidence_dir / "raw"
    raw.mkdir(parents=True)
    evidence_dir.joinpath("evidence_index.md").write_text("# Evidence\n", encoding="utf-8")

    _write_json(raw / "remote_ci_branch_integration_verification.json", {"valid": True})
    for filename in evidence.PRIOR_CHECKS:
        _write_json(raw / filename, {"valid": True})
    _write_json(raw / "git_state.json", {"working_tree_clean": True, "head": "abc123"})
    _write_json(raw / "remote_ci_status.json", {"remote_ci_run_claimed": False})
    _write_json(raw / "branch_integration_summary.json", {
        "branch_integration_authority_result": "valid",
        "release_readiness_claimed": False,
        "runtime_kg_implementation_claimed": False,
    })
    _write_sha_manifest(raw)

    result = evidence.verify(evidence_dir)
    assert result["valid"], result
    assert result["remote_ci_run_claimed"] is False


def test_phase08_evidence_rejects_claimed_remote_ci_without_success(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "evidence"
    raw = evidence_dir / "raw"
    raw.mkdir(parents=True)
    evidence_dir.joinpath("evidence_index.md").write_text("# Evidence\n", encoding="utf-8")

    _write_json(raw / "remote_ci_branch_integration_verification.json", {"valid": True})
    for filename in evidence.PRIOR_CHECKS:
        _write_json(raw / filename, {"valid": True})
    _write_json(raw / "git_state.json", {"working_tree_clean": True, "head": "abc123"})
    _write_json(raw / "remote_ci_status.json", {
        "remote_ci_run_claimed": True,
        "conclusion": "failure",
        "head_sha": "abc1234567",
        "workflow": "ci",
    })
    _write_json(raw / "branch_integration_summary.json", {
        "branch_integration_authority_result": "valid",
        "release_readiness_claimed": False,
        "runtime_kg_implementation_claimed": False,
    })
    _write_sha_manifest(raw)

    result = evidence.verify(evidence_dir)
    assert not result["valid"]
    assert any("conclusion is not success" in error for error in result["errors"])


def test_phase08_evidence_rejects_self_hash_entry(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "evidence"
    raw = evidence_dir / "raw"
    raw.mkdir(parents=True)
    evidence_dir.joinpath("evidence_index.md").write_text("# Evidence\n", encoding="utf-8")
    for filename in evidence.REQUIRED_RAW_JSON:
        if filename == "remote_ci_status.json":
            _write_json(raw / filename, {"remote_ci_run_claimed": False})
        elif filename == "git_state.json":
            _write_json(raw / filename, {"working_tree_clean": True, "head": "abc123"})
        elif filename == "branch_integration_summary.json":
            _write_json(raw / filename, {
                "branch_integration_authority_result": "valid",
                "release_readiness_claimed": False,
                "runtime_kg_implementation_claimed": False,
            })
        else:
            _write_json(raw / filename, {"valid": True})
    (raw / "SHA256SUMS.txt").write_text("00  remote_ci_branch_integration_evidence_check.json\n", encoding="utf-8")

    result = evidence.verify(evidence_dir)
    assert not result["valid"]
    assert any("self-mutating" in error for error in result["errors"])
