from __future__ import annotations

import hashlib
import json
import pathlib

import pytest

from scripts.technical_audit.verify_post_merge_baseline import verify_record

SHA_A = "a" * 40
SHA_B = "b" * 40
SHA_C = "c" * 40
SHA_D = "d" * 40
SHA_E = "e" * 40


def write_json(path: pathlib.Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refresh_sums(evidence: pathlib.Path) -> None:
    sums_path = evidence / "SHA256SUMS.txt"
    files = [p for p in sorted(evidence.rglob("*")) if p.is_file() and p.name != "SHA256SUMS.txt"]
    sums_path.write_text("".join(f"{sha256(p)}  {p.as_posix()}\n" for p in files), encoding="utf-8")


def build_valid_tree(tmp_path: pathlib.Path) -> pathlib.Path:
    evidence = tmp_path / "docs/release-evidence/technical-audit/phase-13b-post-merge-baseline"
    raw = evidence / "raw"
    raw.mkdir(parents=True)
    record_path = tmp_path / "docs/roadmap/execution/technical_audit_remediation/technical_audit_post_merge_baseline_record.json"
    register_path = tmp_path / "docs/roadmap/execution/technical_audit_remediation/blocker_register.json"
    index_path = evidence / "evidence_index.md"
    index_path.write_text(
        "Post-merge protected-branch technical-audit baseline recorded\n"
        "Production release authorised: false\n"
        "Runtime KG implementation claimed: false\n",
        encoding="utf-8",
    )
    write_json(raw / "git_state.json", {
        "branch": "master",
        "head_sha": SHA_A,
        "remote_target_sha": SHA_A,
        "tracked_worktree_clean_before_capture": True,
    })
    write_json(raw / "blocker_register_snapshot.json", {"status": "phase_12_technical_audit_remediation_closed"})
    write_json(raw / "hosted_ci_authority_record_snapshot.json", {
        "ci_run_sha": SHA_B,
        "evidence_commit_sha": SHA_C,
        "closure_commit_sha": SHA_D,
        "current_terminal_sha": SHA_E,
    })
    for name in [
        "hosted_ci_authority_verification",
        "merge_readiness_verification",
        "release_readiness_verification",
        "technical_audit_closure_verification",
    ]:
        write_json(raw / f"{name}.json", {"valid": True})
    write_json(raw / "github_branch_state.json", {"ok": True, "commit": {"sha": SHA_A}})
    write_json(raw / "github_branch_protection.json", {
        "ok": True,
        "required_status_checks": {"strict": True, "contexts": ["Verify repository authority"]},
        "allow_force_pushes": {"enabled": False},
        "allow_deletions": {"enabled": False},
    })
    write_json(raw / "github_check_runs.json", {
        "ok": True,
        "check_runs": [{"name": "Verify repository authority", "status": "completed", "conclusion": "success"}],
    })
    write_json(raw / "post_merge_baseline_result.json", {
        "valid": True,
        "post_merge_baseline_recorded": True,
        "production_release_authorised": False,
    })
    refresh_sums(evidence)
    write_json(record_path, {
        "schema_version": 1,
        "slice": "TA-PHASE-13B-POST-MERGE-PROTECTED-BRANCH-BASELINE",
        "status": "post_merge_protected_branch_baseline_recorded",
        "repository": "NkgoloL/Eduboost-V2",
        "target_branch": "master",
        "required_check": "Verify repository authority",
        "baseline_owner": "Nkgolo Lebelo",
        "source_commit": SHA_A,
        "remote_target_sha": SHA_A,
        "post_merge_baseline_sha": SHA_A,
        "ci_run_sha": SHA_B,
        "evidence_commit_sha": SHA_C,
        "closure_commit_sha": SHA_D,
        "current_terminal_sha": SHA_E,
        "hosted_ci_provenance_model": "split_ci_run_evidence_closure_terminal_sha",
        "post_merge_baseline_claimed": True,
        "post_merge_baseline_recorded": True,
        "technical_audit_remediation_closed": True,
        "hosted_ci_authority_valid": True,
        "merge_readiness_authorised": True,
        "technical_audit_release_readiness_claimed": True,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "live_learner_traffic_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "full_backend_backed_e2e_claimed": False,
        "evidence_dir": evidence.as_posix(),
        "evidence_index": index_path.as_posix(),
        "sha256sums": (evidence / "SHA256SUMS.txt").as_posix(),
    })
    write_json(register_path, {
        "status": "phase_13b_post_merge_baseline_recorded",
        "active_slice": "technical-audit-post-merge-baseline-recorded",
        "phase_13b_post_merge_baseline_authority": {
            "post_merge_baseline_recorded": True,
            "source_commit": SHA_A,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "live_learner_traffic_authorised": False,
            "runtime_kg_implementation_claimed": False,
        },
    })
    return record_path


def test_valid_post_merge_baseline_record(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    record = build_valid_tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is True
    assert result["post_merge_baseline_recorded"] is True
    assert result["production_release_authorised"] is False


def test_rejects_production_release_authorisation(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    record = build_valid_tree(tmp_path)
    data = json.loads(record.read_text())
    data["production_release_authorised"] = True
    record.write_text(json.dumps(data))
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is False
    assert any("production_release_authorised" in e for e in result["errors"])


def test_rejects_sha_mismatch_between_source_and_remote(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    record = build_valid_tree(tmp_path)
    data = json.loads(record.read_text())
    data["remote_target_sha"] = "f" * 40
    record.write_text(json.dumps(data))
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is False
    assert any("source_commit must match remote_target_sha" in e for e in result["errors"])


def test_requires_split_hosted_ci_provenance(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    record = build_valid_tree(tmp_path)
    data = json.loads(record.read_text())
    data["hosted_ci_provenance_model"] = "legacy_head_sha_only"
    record.write_text(json.dumps(data))
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is False
    assert any("split provenance" in e for e in result["errors"])


def test_rejects_tampered_evidence_file(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    record = build_valid_tree(tmp_path)
    raw_result = tmp_path / "docs/release-evidence/technical-audit/phase-13b-post-merge-baseline/raw/post_merge_baseline_result.json"
    raw_result.write_text(json.dumps({"valid": False}), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is False
    assert any("SHA mismatch" in e for e in result["errors"])


def test_rejects_missing_successful_required_check(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    record = build_valid_tree(tmp_path)
    evidence = tmp_path / "docs/release-evidence/technical-audit/phase-13b-post-merge-baseline"
    check_runs = evidence / "raw/github_check_runs.json"
    write_json(check_runs, {"ok": True, "check_runs": [{"name": "Verify repository authority", "status": "completed", "conclusion": "failure"}]})
    refresh_sums(evidence)
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is False
    assert any("required check run must be successful" in e for e in result["errors"])
