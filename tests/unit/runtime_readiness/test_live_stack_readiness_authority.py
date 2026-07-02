from __future__ import annotations

import hashlib
import json
import pathlib

import pytest

from scripts.runtime_readiness.verify_live_stack_readiness import verify_record

SHA_A = "a" * 40


def write_json(path: pathlib.Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refresh_sums(evidence: pathlib.Path) -> None:
    sums_path = evidence / "SHA256SUMS.txt"
    files = [p for p in sorted(evidence.rglob("*")) if p.is_file() and p.name != "SHA256SUMS.txt"]
    sums_path.write_text("".join(f"{sha256(p)}  {p.as_posix()}\n" for p in files), encoding="utf-8")


def deep_payload() -> dict[str, object]:
    return {
        "status": "ok",
        "critical": {
            "secrets": {"status": "ok"},
            "postgres": {"status": "ok"},
            "redis": {"status": "ok"},
            "migrations": {"status": "ok"},
            "audit_repository": {"status": "ok"},
        },
        "optional": {
            "llm_provider": {"status": "skipped"},
            "judiciary": {"status": "ok"},
        },
    }


def build_valid_tree(tmp_path: pathlib.Path) -> pathlib.Path:
    evidence = tmp_path / "docs/release-evidence/runtime-readiness/phase-14-live-stack-readiness"
    raw = evidence / "raw"
    raw.mkdir(parents=True)
    record_path = tmp_path / "docs/roadmap/execution/runtime_readiness/phase_14_live_stack_readiness_record.json"
    index_path = evidence / "evidence_index.md"
    index_path.write_text(
        "# Phase 14 Live-Stack Readiness Evidence\n"
        "Critical components required: secrets, postgres, redis, migrations, audit_repository\n"
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
    write_json(raw / "post_merge_baseline_verification.json", {"valid": True})
    write_json(raw / "probe_health.json", {"status_code": 200, "json": {"status": "ok"}})
    write_json(raw / "probe_openapi.json", {"status_code": 200, "json": {"openapi": "3.1.0"}})
    for name in ["ready", "deep_v2", "deep_api_v2"]:
        write_json(raw / f"probe_{name}.json", {"status_code": 200, "json": deep_payload()})
    write_json(raw / "live_stack_readiness_result.json", {
        "valid": True,
        "live_stack_readiness_recorded": True,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "live_learner_traffic_authorised": False,
        "runtime_kg_implementation_claimed": False,
    })
    refresh_sums(evidence)
    write_json(record_path, {
        "schema_version": 1,
        "slice": "PHASE-14-LIVE-STACK-READINESS-AUTHORITY",
        "status": "live_stack_readiness_recorded",
        "base_url": "http://127.0.0.1:8000",
        "target_branch": "master",
        "readiness_owner": "Nkgolo Lebelo",
        "source_commit": SHA_A,
        "remote_target_sha": SHA_A,
        "post_merge_baseline_valid": True,
        "live_stack_readiness_claimed": True,
        "live_stack_readiness_recorded": True,
        "postgres_readiness_claimed": True,
        "redis_readiness_claimed": True,
        "migration_readiness_claimed": True,
        "audit_repository_readiness_claimed": True,
        "allow_optional_degraded": False,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "live_learner_traffic_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "evidence_dir": evidence.as_posix(),
        "evidence_index": index_path.as_posix(),
        "sha256sums": (evidence / "SHA256SUMS.txt").as_posix(),
    })
    return record_path


def test_valid_live_stack_readiness_record(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    record = build_valid_tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is True
    assert result["live_stack_readiness_recorded"] is True
    assert result["production_release_authorised"] is False


def test_rejects_missing_postgres_readiness(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    record = build_valid_tree(tmp_path)
    ready = tmp_path / "docs/release-evidence/runtime-readiness/phase-14-live-stack-readiness/raw/probe_ready.json"
    payload = json.loads(ready.read_text())
    payload["json"]["critical"]["postgres"]["status"] = "error"
    ready.write_text(json.dumps(payload), encoding="utf-8")
    refresh_sums(tmp_path / "docs/release-evidence/runtime-readiness/phase-14-live-stack-readiness")
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is False
    assert any("critical.postgres" in e for e in result["errors"])


def test_rejects_missing_redis_readiness_claim(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    record = build_valid_tree(tmp_path)
    data = json.loads(record.read_text())
    data["redis_readiness_claimed"] = False
    record.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is False
    assert any("redis_readiness_claimed" in e for e in result["errors"])


def test_rejects_production_release_authorisation(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    record = build_valid_tree(tmp_path)
    data = json.loads(record.read_text())
    data["production_release_authorised"] = True
    record.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is False
    assert any("production_release_authorised" in e for e in result["errors"])


def test_rejects_invalid_post_merge_baseline(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    record = build_valid_tree(tmp_path)
    post_merge = tmp_path / "docs/release-evidence/runtime-readiness/phase-14-live-stack-readiness/raw/post_merge_baseline_verification.json"
    post_merge.write_text(json.dumps({"valid": False}), encoding="utf-8")
    refresh_sums(tmp_path / "docs/release-evidence/runtime-readiness/phase-14-live-stack-readiness")
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is False
    assert any("post-merge baseline" in e for e in result["errors"])


def test_rejects_tampered_evidence_file(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    record = build_valid_tree(tmp_path)
    raw_result = tmp_path / "docs/release-evidence/runtime-readiness/phase-14-live-stack-readiness/raw/live_stack_readiness_result.json"
    raw_result.write_text(json.dumps({"valid": False}), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is False
    assert any("SHA mismatch" in e for e in result["errors"])
