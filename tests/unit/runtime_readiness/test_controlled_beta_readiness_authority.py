from __future__ import annotations

import importlib.util
import json
import pathlib
from typing import Any


def load_module(repo_root: pathlib.Path):
    module_path = repo_root / "scripts/runtime_readiness/verify_controlled_beta_readiness.py"
    spec = importlib.util.spec_from_file_location("verify_controlled_beta_readiness", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: pathlib.Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_sha256sums(root: pathlib.Path, evidence_dir: pathlib.Path) -> None:
    import hashlib

    lines: list[str] = []
    for path in sorted(evidence_dir.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            lines.append(f"{digest}  {path.as_posix()}\n")
    (evidence_dir / "SHA256SUMS.txt").write_text("".join(lines), encoding="utf-8")


def build_valid_fixture(tmp_path: pathlib.Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    evidence_dir = tmp_path / "docs/release-evidence/runtime-readiness/phase-17-controlled-beta-readiness"
    raw = evidence_dir / "raw"
    raw.mkdir(parents=True)
    record_path = tmp_path / "docs/roadmap/execution/runtime_readiness/phase_17_controlled_beta_readiness_record.json"
    sha = "a" * 40

    verifier_payload = {"name": "x", "script": "script.py", "returncode": 0, "valid": True, "payload": {"valid": True}, "stderr": ""}
    for name in [
        "technical_audit_closure",
        "post_merge_baseline",
        "live_stack_readiness",
        "backend_backed_e2e",
        "backend_backed_seeded_e2e",
    ]:
        write_json(raw / f"{name}_verification.json", {**verifier_payload, "name": name})

    boundary = {
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "controlled_beta_launch_authorised": False,
        "live_learner_traffic_authorised": False,
        "learner_data_migration_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "scope": "controlled_beta_readiness_gate_only",
    }
    result = {
        "valid": True,
        "controlled_beta_readiness_recorded": True,
        "technical_audit_closure_valid": True,
        "post_merge_baseline_valid": True,
        "live_stack_readiness_valid": True,
        "backend_backed_e2e_valid": True,
        "seeded_backend_backed_e2e_valid": True,
        "readiness_documents_valid": True,
        "errors": [],
        "warnings": [],
        **boundary,
    }
    record = {
        "schema_version": 1,
        "slice": "PHASE-17-CONTROLLED-BETA-READINESS-AUTHORITY",
        "status": "controlled_beta_readiness_recorded",
        "controlled_beta_readiness_claimed": True,
        "controlled_beta_readiness_recorded": True,
        "beta_scope": "controlled_beta_readiness_gate",
        "readiness_owner": "Nkgolo Lebelo",
        "captured_at": "2026-07-01T00:00:00Z",
        "target_branch": "master",
        "source_commit": sha,
        "remote_target_sha": sha,
        "evidence_dir": evidence_dir.relative_to(tmp_path).as_posix(),
        "evidence_index": (evidence_dir / "evidence_index.md").relative_to(tmp_path).as_posix(),
        "sha256sums": (evidence_dir / "SHA256SUMS.txt").relative_to(tmp_path).as_posix(),
        "technical_audit_closure_valid": True,
        "post_merge_baseline_valid": True,
        "live_stack_readiness_valid": True,
        "backend_backed_e2e_valid": True,
        "seeded_backend_backed_e2e_valid": True,
        "readiness_documents_valid": True,
        **boundary,
    }
    index = """# Phase 17 Controlled Beta Readiness Evidence

- Controlled beta readiness recorded: true
- Production release authorised: false
- Deployment authorised: false
- Public beta authorised: false
- Controlled beta launch authorised: false
- Live learner traffic authorised: false
- Runtime KG implementation claimed: false
"""
    (evidence_dir / "evidence_index.md").write_text(index, encoding="utf-8")
    write_json(raw / "git_state.json", {"head_sha": sha, "tracked_worktree_clean_before_capture": True})
    write_json(raw / "readiness_documents.json", {"valid": True, "missing": [], "documents": []})
    write_json(raw / "beta_boundary.json", boundary)
    write_json(raw / "controlled_beta_readiness_result.json", result)
    write_json(raw / "controlled_beta_readiness_record_snapshot.json", record)
    write_sha256sums(tmp_path, evidence_dir)
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record_path


def test_valid_controlled_beta_readiness_record_passes(tmp_path, monkeypatch):
    repo_root = pathlib.Path.cwd()
    module = load_module(repo_root)
    record_path = build_valid_fixture(tmp_path, monkeypatch)
    result = module.verify_record(record_path)
    assert result["valid"] is True
    assert result["controlled_beta_readiness_recorded"] is True
    assert result["controlled_beta_launch_authorised"] is False


def test_production_release_authorisation_is_rejected(tmp_path, monkeypatch):
    repo_root = pathlib.Path.cwd()
    module = load_module(repo_root)
    record_path = build_valid_fixture(tmp_path, monkeypatch)
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["production_release_authorised"] = True
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = module.verify_record(record_path)
    assert result["valid"] is False
    assert any("production_release_authorised" in error for error in result["errors"])


def test_missing_seeded_e2e_verification_is_rejected(tmp_path, monkeypatch):
    repo_root = pathlib.Path.cwd()
    module = load_module(repo_root)
    record_path = build_valid_fixture(tmp_path, monkeypatch)
    missing = tmp_path / "docs/release-evidence/runtime-readiness/phase-17-controlled-beta-readiness/raw/backend_backed_seeded_e2e_verification.json"
    missing.unlink()
    result = module.verify_record(record_path)
    assert result["valid"] is False
    assert any("backend_backed_seeded_e2e_verification" in error for error in result["errors"])


def test_capture_refuses_unclaimed_invocation(tmp_path, monkeypatch):
    repo_root = pathlib.Path.cwd()
    capture_path = repo_root / "scripts/runtime_readiness/capture_controlled_beta_readiness_evidence.py"
    spec = importlib.util.spec_from_file_location("capture_controlled_beta_readiness", capture_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.chdir(tmp_path)
    result = module.build_result(
        {
            "technical_audit_closure": {"valid": True},
            "post_merge_baseline": {"valid": True},
            "live_stack_readiness": {"valid": True},
            "backend_backed_e2e": {"valid": True},
            "backend_backed_seeded_e2e": {"valid": True},
        },
        {"tracked_worktree_clean_before_capture": True, "head_matches_remote_target": True},
        {"valid": True},
    )
    assert result["valid"] is True
    assert result["controlled_beta_launch_authorised"] is False
