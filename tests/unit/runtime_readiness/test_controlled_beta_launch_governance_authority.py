from __future__ import annotations

import importlib.util
import json
import pathlib
from typing import Any


def load_verify(repo_root: pathlib.Path):
    module_path = repo_root / "scripts/runtime_readiness/verify_controlled_beta_launch_governance.py"
    spec = importlib.util.spec_from_file_location("verify_controlled_beta_launch_governance", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_capture(repo_root: pathlib.Path):
    module_path = repo_root / "scripts/runtime_readiness/capture_controlled_beta_launch_governance_evidence.py"
    spec = importlib.util.spec_from_file_location("capture_controlled_beta_launch_governance", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: pathlib.Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_sha256sums(evidence_dir: pathlib.Path) -> None:
    import hashlib
    lines: list[str] = []
    for path in sorted(evidence_dir.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.as_posix()}\n")
    (evidence_dir / "SHA256SUMS.txt").write_text("".join(lines), encoding="utf-8")


def build_valid_fixture(tmp_path: pathlib.Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    sha = "b" * 40
    evidence_dir = tmp_path / "docs/release-evidence/runtime-readiness/phase-18-controlled-beta-launch-governance"
    raw = evidence_dir / "raw"
    raw.mkdir(parents=True)
    record_path = tmp_path / "docs/roadmap/execution/runtime_readiness/phase_18_controlled_beta_launch_governance_record.json"
    boundary = {
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "controlled_beta_launch_authorised": False,
        "live_learner_traffic_authorised": False,
        "learner_data_migration_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "scope": "controlled_beta_launch_governance_only",
    }
    result = {
        "valid": True,
        "controlled_beta_launch_governance_claimed": True,
        "controlled_beta_launch_governance_recorded": True,
        "phase_17_controlled_beta_readiness_valid": True,
        "launch_operations_documents_valid": True,
        "errors": [],
        "warnings": [],
        **boundary,
    }
    record = {
        "schema_version": 1,
        "slice": "PHASE-18-CONTROLLED-BETA-LAUNCH-GOVERNANCE-AUTHORITY",
        "status": "controlled_beta_launch_governance_recorded",
        "beta_scope": "controlled_beta_launch_governance_gate",
        "controlled_beta_launch_governance_claimed": True,
        "controlled_beta_launch_governance_recorded": True,
        "governance_owner": "Nkgolo Lebelo",
        "captured_at": "2026-07-01T00:00:00Z",
        "target_branch": "master",
        "source_commit": sha,
        "remote_target_sha": sha,
        "evidence_dir": evidence_dir.relative_to(tmp_path).as_posix(),
        "evidence_index": (evidence_dir / "evidence_index.md").relative_to(tmp_path).as_posix(),
        "sha256sums": (evidence_dir / "SHA256SUMS.txt").relative_to(tmp_path).as_posix(),
        "phase_17_controlled_beta_readiness_valid": True,
        "launch_operations_documents_valid": True,
        **boundary,
    }
    index = """# Phase 18 Controlled Beta Launch Governance Evidence

- Controlled beta launch governance recorded: true
- Production release authorised: false
- Deployment authorised: false
- Controlled beta launch authorised: false
- Live learner traffic authorised: false
- Runtime KG implementation claimed: false
"""
    (evidence_dir / "evidence_index.md").write_text(index, encoding="utf-8")
    write_json(raw / "git_state.json", {"head_sha": sha, "tracked_worktree_clean_before_capture": True})
    write_json(raw / "phase17_controlled_beta_readiness_verification.json", {"returncode": 0, "valid": True, "payload": {"valid": True}})
    write_json(raw / "launch_operations_documents.json", {"valid": True, "documents": [], "errors": []})
    write_json(raw / "launch_governance_boundary.json", boundary)
    write_json(raw / "controlled_beta_launch_governance_result.json", result)
    write_json(raw / "controlled_beta_launch_governance_record_snapshot.json", record)
    write_sha256sums(evidence_dir)
    record_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(record_path, record)
    return record_path


def test_valid_launch_governance_record_passes(tmp_path, monkeypatch):
    module = load_verify(pathlib.Path.cwd())
    record_path = build_valid_fixture(tmp_path, monkeypatch)
    result = module.verify_record(record_path)
    assert result["valid"] is True
    assert result["controlled_beta_launch_governance_recorded"] is True
    assert result["controlled_beta_launch_authorised"] is False


def test_live_learner_traffic_authorisation_is_rejected(tmp_path, monkeypatch):
    module = load_verify(pathlib.Path.cwd())
    record_path = build_valid_fixture(tmp_path, monkeypatch)
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["live_learner_traffic_authorised"] = True
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = module.verify_record(record_path)
    assert result["valid"] is False
    assert any("live_learner_traffic_authorised" in error for error in result["errors"])


def test_missing_phase17_verification_is_rejected(tmp_path, monkeypatch):
    module = load_verify(pathlib.Path.cwd())
    record_path = build_valid_fixture(tmp_path, monkeypatch)
    missing = tmp_path / "docs/release-evidence/runtime-readiness/phase-18-controlled-beta-launch-governance/raw/phase17_controlled_beta_readiness_verification.json"
    missing.unlink()
    result = module.verify_record(record_path)
    assert result["valid"] is False
    assert any("phase17_controlled_beta_readiness_verification" in error for error in result["errors"])


def test_capture_result_requires_claim():
    module = load_capture(pathlib.Path.cwd())
    result = module.build_result(
        claimed=False,
        phase17={"valid": True},
        git_state={"tracked_worktree_clean_before_capture": True, "head_matches_remote_target": True},
        documents={"valid": True},
    )
    assert result["valid"] is False
    assert result["controlled_beta_launch_governance_recorded"] is False
    assert result["controlled_beta_launch_authorised"] is False
