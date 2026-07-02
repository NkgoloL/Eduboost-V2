from __future__ import annotations

import importlib.util
import json
import pathlib
from typing import Any


def load_verify(repo_root: pathlib.Path):
    module_path = repo_root / "scripts/runtime_readiness/verify_controlled_beta_activation_preflight.py"
    spec = importlib.util.spec_from_file_location("verify_controlled_beta_activation_preflight", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_capture(repo_root: pathlib.Path):
    module_path = repo_root / "scripts/runtime_readiness/capture_controlled_beta_activation_preflight_evidence.py"
    spec = importlib.util.spec_from_file_location("capture_controlled_beta_activation_preflight", module_path)
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
    sha = "c" * 40
    evidence_dir = tmp_path / "docs/release-evidence/runtime-readiness/phase-19-controlled-beta-activation-preflight"
    raw = evidence_dir / "raw"
    raw.mkdir(parents=True)
    record_path = tmp_path / "docs/roadmap/execution/runtime_readiness/phase_19_controlled_beta_activation_preflight_record.json"
    boundary = {
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "controlled_beta_launch_authorised": False,
        "live_learner_traffic_authorised": False,
        "learner_data_migration_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "scope": "controlled_beta_activation_preflight_only",
    }
    result = {
        "valid": True,
        "controlled_beta_activation_preflight_claimed": True,
        "controlled_beta_activation_preflight_recorded": True,
        "phase_18_controlled_beta_launch_governance_valid": True,
        "activation_preflight_documents_valid": True,
        "errors": [],
        "warnings": [],
        **boundary,
    }
    record = {
        "schema_version": 1,
        "slice": "PHASE-19-CONTROLLED-BETA-ACTIVATION-PREFLIGHT-AUTHORITY",
        "status": "controlled_beta_activation_preflight_recorded",
        "beta_scope": "controlled_beta_activation_preflight_gate",
        "controlled_beta_activation_preflight_claimed": True,
        "controlled_beta_activation_preflight_recorded": True,
        "preflight_owner": "Nkgolo Lebelo",
        "captured_at": "2026-07-01T00:00:00Z",
        "target_branch": "master",
        "source_commit": sha,
        "remote_target_sha": sha,
        "evidence_dir": evidence_dir.relative_to(tmp_path).as_posix(),
        "evidence_index": (evidence_dir / "evidence_index.md").relative_to(tmp_path).as_posix(),
        "sha256sums": (evidence_dir / "SHA256SUMS.txt").relative_to(tmp_path).as_posix(),
        "phase_18_controlled_beta_launch_governance_valid": True,
        "activation_preflight_documents_valid": True,
        **boundary,
    }
    index = """# Phase 19 Controlled Beta Activation Preflight Evidence

- Controlled beta activation preflight recorded: true
- Controlled beta launch authorised: false
- Live learner traffic authorised: false
- Learner data migration authorised: false
- Runtime KG implementation claimed: false
"""
    (evidence_dir / "evidence_index.md").write_text(index, encoding="utf-8")
    write_json(raw / "git_state.json", {"head_sha": sha, "tracked_worktree_clean_before_capture": True})
    write_json(raw / "phase18_launch_governance_verification.json", {"returncode": 0, "valid": True, "payload": {"valid": True}})
    write_json(raw / "activation_preflight_documents.json", {"valid": True, "documents": [], "errors": []})
    write_json(raw / "activation_preflight_boundary.json", boundary)
    write_json(raw / "controlled_beta_activation_preflight_result.json", result)
    write_json(raw / "controlled_beta_activation_preflight_record_snapshot.json", record)
    write_sha256sums(evidence_dir)
    record_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(record_path, record)
    return record_path


def test_valid_activation_preflight_record_passes(tmp_path, monkeypatch):
    module = load_verify(pathlib.Path.cwd())
    record_path = build_valid_fixture(tmp_path, monkeypatch)
    result = module.verify_record(record_path)
    assert result["valid"] is True
    assert result["controlled_beta_activation_preflight_recorded"] is True
    assert result["controlled_beta_launch_authorised"] is False


def test_controlled_beta_launch_authorisation_is_rejected(tmp_path, monkeypatch):
    module = load_verify(pathlib.Path.cwd())
    record_path = build_valid_fixture(tmp_path, monkeypatch)
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["controlled_beta_launch_authorised"] = True
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = module.verify_record(record_path)
    assert result["valid"] is False
    assert any("controlled_beta_launch_authorised" in error for error in result["errors"])


def test_missing_phase18_verification_is_rejected(tmp_path, monkeypatch):
    module = load_verify(pathlib.Path.cwd())
    record_path = build_valid_fixture(tmp_path, monkeypatch)
    missing = tmp_path / "docs/release-evidence/runtime-readiness/phase-19-controlled-beta-activation-preflight/raw/phase18_launch_governance_verification.json"
    missing.unlink()
    result = module.verify_record(record_path)
    assert result["valid"] is False
    assert any("phase18_launch_governance_verification" in error for error in result["errors"])


def test_capture_result_requires_claim():
    module = load_capture(pathlib.Path.cwd())
    result = module.build_result(
        claimed=False,
        phase18={"valid": True},
        git={"tracked_worktree_clean_before_capture": True, "head_matches_remote_target": True},
        documents={"valid": True},
    )
    assert result["valid"] is False
    assert result["controlled_beta_activation_preflight_recorded"] is False
    assert result["live_learner_traffic_authorised"] is False
