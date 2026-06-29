from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CAPTURE_PATH = ROOT / "scripts/technical_audit/capture_release_readiness_evidence.py"
VERIFY_PATH = ROOT / "scripts/technical_audit/verify_release_readiness_authority.py"


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _valid_register() -> dict:
    return {
        "remaining_release_blockers_after_reset": [
            {"id": blocker_id, "status": "evidence_recorded"}
            for blocker_id in [
                "TA-OPENAPI-001",
                "TA-BACKEND-FAST-001",
                "TA-FRONTEND-001",
                "TA-E2E-001",
                "TA-SECURITY-001",
                "TA-CI-001",
                "TA-REMOTE-CI-001",
                "TA-HOSTED-CI-001",
            ]
        ]
    }


def test_blocker_summary_requires_hosted_ci_merge_readiness_flags() -> None:
    module = _load(CAPTURE_PATH)
    register = _valid_register()
    hosted = register["remaining_release_blockers_after_reset"][-1]
    hosted.update(
        {
            "remote_ci_run_claimed": True,
            "branch_protection_claimed": True,
            "merge_readiness_authorised": True,
        }
    )
    summary = module.build_blocker_summary(register)
    assert summary["required_blockers_closed"] is True


def test_blocker_summary_rejects_missing_branch_protection_flag() -> None:
    module = _load(CAPTURE_PATH)
    register = _valid_register()
    register["remaining_release_blockers_after_reset"][-1].update(
        {"remote_ci_run_claimed": True, "merge_readiness_authorised": True}
    )
    summary = module.build_blocker_summary(register)
    assert summary["required_blockers_closed"] is False
    assert "TA-HOSTED-CI-001" in summary["failed_blockers"]


def test_release_readiness_evaluator_requires_explicit_claim_and_owner() -> None:
    module = _load(CAPTURE_PATH)
    result = module.evaluate_release_readiness(
        claim=False,
        release_owner=None,
        source_commit="a" * 40,
        tracked_clean=True,
        merge_result={
            "valid": True,
            "hosted_ci_run_claimed": True,
            "branch_protection_claimed": True,
            "merge_readiness_authorised": True,
        },
        hosted_record={
            "hosted_ci_run_claimed": True,
            "hosted_ci_conclusion": "success",
            "branch_protection_claimed": True,
            "merge_readiness_authorised": True,
            "head_sha": "a" * 40,
        },
        blocker_summary={"required_blockers_closed": True, "failed_blockers": []},
    )
    assert result["valid"] is False
    assert result["release_readiness_claimed"] is False


def test_release_readiness_evaluator_accepts_valid_explicit_claim() -> None:
    module = _load(CAPTURE_PATH)
    result = module.evaluate_release_readiness(
        claim=True,
        release_owner="Nkgolo Lebelo",
        source_commit="a" * 40,
        tracked_clean=True,
        merge_result={
            "valid": True,
            "hosted_ci_run_claimed": True,
            "branch_protection_claimed": True,
            "merge_readiness_authorised": True,
        },
        hosted_record={
            "hosted_ci_run_claimed": True,
            "hosted_ci_conclusion": "success",
            "branch_protection_claimed": True,
            "merge_readiness_authorised": True,
            "head_sha": "a" * 40,
        },
        blocker_summary={"required_blockers_closed": True, "failed_blockers": []},
    )
    assert result["valid"] is True
    assert result["release_readiness_claimed"] is True
    assert result["production_release_authorised"] is False
    assert result["runtime_kg_implementation_claimed"] is False


def test_release_readiness_verifier_accepts_valid_record(tmp_path: Path, monkeypatch) -> None:
    module = _load(VERIFY_PATH)
    monkeypatch.chdir(tmp_path)
    evidence = tmp_path / "docs/release-evidence/technical-audit/phase-11-release-readiness"
    raw = evidence / "raw"
    raw.mkdir(parents=True)
    git_state = {"head_sha": "a" * 40, "tracked_worktree_clean_before_capture": True}
    merge = {"valid": True, "hosted_ci_run_claimed": True, "branch_protection_claimed": True, "merge_readiness_authorised": True}
    blockers = {"required_blockers_closed": True, "failed_blockers": []}
    result = {"valid": True, "release_readiness_claimed": True, "production_release_authorised": False, "runtime_kg_implementation_claimed": False}
    for name, payload in {
        "git_state.json": git_state,
        "blocker_register_snapshot.json": {},
        "hosted_ci_authority_record_snapshot.json": {},
        "merge_readiness_verification.json": merge,
        "required_blocker_summary.json": blockers,
        "release_readiness_result.json": result,
    }.items():
        _write_json(raw / name, payload)
    index = evidence / "evidence_index.md"
    index.write_text(
        "Technical-audit release readiness authorised\nProduction release authorised: false\nRuntime KG implementation claimed: false\n",
        encoding="utf-8",
    )
    index_hash = evidence / "evidence_index.sha256"
    index_hash.write_text(f"{_sha(index)}  {index.as_posix()}\n", encoding="utf-8")
    sums = evidence / "SHA256SUMS.txt"
    files = list(raw.glob("*.json")) + [index, index_hash]
    sums.write_text("".join(f"{_sha(path)}  {path.as_posix()}\n" for path in files), encoding="utf-8")
    record = tmp_path / "docs/roadmap/execution/technical_audit_remediation/technical_audit_release_readiness_record.json"
    _write_json(
        record,
        {
            "schema_version": 1,
            "slice": "TA-PHASE-11-TECHNICAL-AUDIT-RELEASE-READINESS",
            "status": "technical_audit_release_readiness_authorised",
            "source_commit": "a" * 40,
            "release_owner": "Nkgolo Lebelo",
            "release_decision": "authorised",
            "release_readiness_claimed": True,
            "technical_audit_release_readiness_claimed": True,
            "production_release_authorised": False,
            "runtime_kg_implementation_claimed": False,
            "full_backend_backed_e2e_claimed": False,
            "hosted_ci_run_claimed": True,
            "branch_protection_claimed": True,
            "merge_readiness_authorised": True,
            "required_blockers_closed": True,
            "evidence_dir": evidence.as_posix(),
            "evidence_index": index.as_posix(),
            "sha256sums": sums.as_posix(),
        },
    )
    outcome = module.verify_record(record)
    assert outcome["valid"] is True, outcome


def test_release_readiness_verifier_rejects_unclaimed_record(tmp_path: Path) -> None:
    module = _load(VERIFY_PATH)
    record = tmp_path / "record.json"
    _write_json(
        record,
        {
            "schema_version": 1,
            "slice": "TA-PHASE-11-TECHNICAL-AUDIT-RELEASE-READINESS",
            "status": "release_readiness_unclaimed",
            "source_commit": "a" * 40,
            "release_readiness_claimed": False,
            "technical_audit_release_readiness_claimed": False,
            "production_release_authorised": False,
            "runtime_kg_implementation_claimed": False,
            "full_backend_backed_e2e_claimed": False,
        },
    )
    outcome = module.verify_record(record)
    assert outcome["valid"] is False
    assert any("release_readiness_claimed" in error for error in outcome["errors"])

