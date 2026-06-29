from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
from typing import Any


def load_module(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: pathlib.Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def good_inputs():
    source = "a" * 40
    register = {
        "status": "phase_12_technical_audit_closure_authority_ready",
        "active_slice": "technical-audit-remediation-closure-authority",
        "phase_11_release_readiness_authority": {
            "technical_audit_release_readiness_claimed": True,
            "production_release_authorised": False,
        },
    }
    hosted = {
        "hosted_ci_run_claimed": True,
        "branch_protection_claimed": True,
        "merge_readiness_authorised": True,
        "production_release_authorised": False,
        "runtime_kg_implementation_claimed": False,
    }
    release = {
        "status": "technical_audit_release_readiness_authorised",
        "source_commit": source,
        "release_readiness_claimed": True,
        "technical_audit_release_readiness_claimed": True,
        "required_blockers_closed": True,
        "hosted_ci_run_claimed": True,
        "branch_protection_claimed": True,
        "merge_readiness_authorised": True,
        "production_release_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "full_backend_backed_e2e_claimed": False,
    }
    release_verification = {
        "valid": True,
        "release_readiness_claimed": True,
        "technical_audit_release_readiness_claimed": True,
        "production_release_authorised": False,
        "merge_readiness_authorised": True,
    }
    return source, register, hosted, release, release_verification


def test_evaluate_closure_requires_explicit_claim(monkeypatch):
    capture = load_module(pathlib.Path("scripts/technical_audit/capture_technical_audit_closure_evidence.py"), "capture_closure")
    source, register, hosted, release, release_verification = good_inputs()
    monkeypatch.setattr(capture, "git_is_ancestor_or_equal", lambda candidate, descendant: True)
    result = capture.evaluate_closure(
        claim=False,
        closure_owner="Nkgolo Lebelo",
        source_commit=source,
        tracked_clean=True,
        register=register,
        hosted_record=hosted,
        release_record=release,
        release_verification=release_verification,
    )
    assert result["valid"] is False
    assert result["technical_audit_remediation_closed"] is False
    assert any("--claim-closure" in error for error in result["errors"])


def test_evaluate_closure_accepts_valid_prerequisites(monkeypatch):
    capture = load_module(pathlib.Path("scripts/technical_audit/capture_technical_audit_closure_evidence.py"), "capture_closure_valid")
    source, register, hosted, release, release_verification = good_inputs()
    monkeypatch.setattr(capture, "git_is_ancestor_or_equal", lambda candidate, descendant: True)
    result = capture.evaluate_closure(
        claim=True,
        closure_owner="Nkgolo Lebelo",
        source_commit=source,
        tracked_clean=True,
        register=register,
        hosted_record=hosted,
        release_record=release,
        release_verification=release_verification,
    )
    assert result["valid"] is True
    assert result["technical_audit_remediation_closed"] is True
    assert result["production_release_authorised"] is False
    assert result["runtime_kg_implementation_claimed"] is False


def test_evaluate_closure_rejects_production_release_authority(monkeypatch):
    capture = load_module(pathlib.Path("scripts/technical_audit/capture_technical_audit_closure_evidence.py"), "capture_closure_reject")
    source, register, hosted, release, release_verification = good_inputs()
    release["production_release_authorised"] = True
    monkeypatch.setattr(capture, "git_is_ancestor_or_equal", lambda candidate, descendant: True)
    result = capture.evaluate_closure(
        claim=True,
        closure_owner="Nkgolo Lebelo",
        source_commit=source,
        tracked_clean=True,
        register=register,
        hosted_record=hosted,
        release_record=release,
        release_verification=release_verification,
    )
    assert result["valid"] is False
    assert any("production_release_authorised=false" in error for error in result["errors"])


def build_valid_closure_tree(base: pathlib.Path) -> pathlib.Path:
    source = "b" * 40
    evidence_dir = base / "docs/release-evidence/technical-audit/phase-12-closure"
    raw = evidence_dir / "raw"
    raw.mkdir(parents=True)
    raw_payloads = {
        raw / "git_state.json": {
            "tracked_worktree_clean_before_capture": True,
            "head_sha": source,
        },
        raw / "blocker_register_snapshot.json": {
            "status": "phase_12_technical_audit_closure_authority_ready",
        },
        raw / "hosted_ci_authority_record_snapshot.json": {
            "hosted_ci_run_claimed": True,
            "branch_protection_claimed": True,
            "merge_readiness_authorised": True,
        },
        raw / "release_readiness_record_snapshot.json": {
            "status": "technical_audit_release_readiness_authorised",
            "technical_audit_release_readiness_claimed": True,
            "production_release_authorised": False,
            "runtime_kg_implementation_claimed": False,
        },
        raw / "release_readiness_verification.json": {
            "valid": True,
            "release_readiness_claimed": True,
            "technical_audit_release_readiness_claimed": True,
            "production_release_authorised": False,
        },
        raw / "technical_audit_closure_result.json": {
            "valid": True,
            "technical_audit_remediation_closed": True,
            "production_release_authorised": False,
            "runtime_kg_implementation_claimed": False,
        },
    }
    for path, payload in raw_payloads.items():
        write_json(path, payload)
    index = evidence_dir / "evidence_index.md"
    index.write_text(
        "Technical-audit remediation closure authorised\n"
        "Production release authorised: false\n"
        "Runtime KG implementation claimed: false\n",
        encoding="utf-8",
    )
    index_hash = evidence_dir / "evidence_index.sha256"
    index_hash.write_text(f"{sha(index)}  {index.as_posix()}\n", encoding="utf-8")
    sums = evidence_dir / "SHA256SUMS.txt"
    files = [*raw_payloads.keys(), index, index_hash]
    sums.write_text("".join(f"{sha(path)}  {path.as_posix()}\n" for path in sorted(files)), encoding="utf-8")
    record = base / "docs/roadmap/execution/technical_audit_remediation/technical_audit_closure_record.json"
    write_json(
        record,
        {
            "schema_version": 1,
            "slice": "TA-PHASE-12-TECHNICAL-AUDIT-REMEDIATION-CLOSURE",
            "status": "technical_audit_remediation_closed",
            "source_commit": source,
            "closure_owner": "Nkgolo Lebelo",
            "closure_decision": "authorised",
            "technical_audit_remediation_closure_claimed": True,
            "technical_audit_remediation_closed": True,
            "technical_audit_release_readiness_claimed": True,
            "release_readiness_claimed": True,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "live_learner_traffic_authorised": False,
            "runtime_kg_implementation_claimed": False,
            "full_backend_backed_e2e_claimed": False,
            "evidence_dir": evidence_dir.as_posix(),
            "evidence_index": index.as_posix(),
            "sha256sums": sums.as_posix(),
        },
    )
    write_json(
        base / "docs/roadmap/execution/technical_audit_remediation/blocker_register.json",
        {
            "status": "phase_12_technical_audit_remediation_closed",
            "active_slice": "technical-audit-remediation-closed",
            "phase_12_technical_audit_closure_authority": {
                "authority_record": record.as_posix(),
                "technical_audit_remediation_closed": True,
                "production_release_authorised": False,
            },
        },
    )
    return record


def test_verify_record_accepts_valid_closure_tree(tmp_path, monkeypatch):
    verify = load_module(pathlib.Path("scripts/technical_audit/verify_technical_audit_closure.py"), "verify_closure")
    record = build_valid_closure_tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = verify.verify_record(record)
    assert result["valid"] is True
    assert result["technical_audit_remediation_closed"] is True
    assert result["production_release_authorised"] is False


def test_verify_record_fails_when_raw_evidence_missing(tmp_path, monkeypatch):
    verify = load_module(pathlib.Path("scripts/technical_audit/verify_technical_audit_closure.py"), "verify_closure_missing")
    record = build_valid_closure_tree(tmp_path)
    missing = tmp_path / "docs/release-evidence/technical-audit/phase-12-closure/raw/git_state.json"
    missing.unlink()
    monkeypatch.chdir(tmp_path)
    result = verify.verify_record(record)
    assert result["valid"] is False
    assert any("git_state.json" in error for error in result["errors"])

