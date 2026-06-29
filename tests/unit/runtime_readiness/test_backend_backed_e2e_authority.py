from __future__ import annotations

import hashlib
import json
import pathlib

from scripts.runtime_readiness.verify_backend_backed_e2e import verify_record

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


def build_valid_tree(tmp_path: pathlib.Path) -> pathlib.Path:
    evidence = tmp_path / "docs/release-evidence/runtime-readiness/phase-15-backend-backed-e2e"
    raw = evidence / "raw"
    raw.mkdir(parents=True)
    record_path = tmp_path / "docs/roadmap/execution/runtime_readiness/phase_15_backend_backed_e2e_record.json"
    index_path = evidence / "evidence_index.md"
    index_path.write_text(
        "# Phase 15 Backend-Backed E2E Smoke Evidence\n"
        "Required predecessor: Phase 14 live-stack readiness verifier valid.\n"
        "Mocked API used: false\n"
        "E2E scope: backend_backed_smoke\n"
        "Production release authorised: false\n"
        "Live learner traffic authorised: false\n"
        "Runtime KG implementation claimed: false\n",
        encoding="utf-8",
    )
    write_json(raw / "git_state.json", {
        "branch": "master",
        "head_sha": SHA_A,
        "remote_target_sha": SHA_A,
        "tracked_worktree_clean_before_capture": True,
    })
    write_json(raw / "live_stack_readiness_verification.json", {"valid": True})
    for name in ["api_health", "api_ready", "api_deep", "frontend_root", "frontend_api_rewrite"]:
        write_json(raw / f"probe_{name}.json", {"status_code": 200, "json": {"status": "ok"}})
    write_json(raw / "backend_backed_e2e_result.json", {
        "valid": True,
        "backend_backed_e2e_recorded": True,
        "backend_backed_e2e_claimed": True,
        "live_stack_readiness_valid": True,
        "playwright_mock_api": "0",
        "mocked_api_used": False,
        "e2e_scope": "backend_backed_smoke",
        "full_production_e2e_claimed": False,
        "specs": ["tests/e2e/auth.setup.ts", "tests/e2e/learner-vertical-journey.spec.ts"],
        "steps": [
            {"name": "pnpm_version", "command": ["pnpm", "--version"], "returncode": 0},
            {"name": "playwright_backend_backed_smoke", "command": ["pnpm", "exec", "playwright", "test", "tests/e2e/auth.setup.ts"], "returncode": 0},
        ],
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "live_learner_traffic_authorised": False,
        "runtime_kg_implementation_claimed": False,
    })
    refresh_sums(evidence)
    write_json(record_path, {
        "schema_version": 1,
        "slice": "PHASE-15-BACKEND-BACKED-E2E-AUTHORITY",
        "status": "backend_backed_e2e_recorded",
        "target_branch": "master",
        "source_commit": SHA_A,
        "remote_target_sha": SHA_A,
        "e2e_owner": "Nkgolo Lebelo",
        "backend_backed_e2e_claimed": True,
        "backend_backed_e2e_recorded": True,
        "e2e_scope": "backend_backed_smoke",
        "full_production_e2e_claimed": False,
        "live_stack_readiness_valid": True,
        "playwright_mock_api": "0",
        "mocked_api_used": False,
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


def test_valid_backend_backed_e2e_record(tmp_path: pathlib.Path, monkeypatch) -> None:
    record = build_valid_tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is True
    assert result["backend_backed_e2e_recorded"] is True
    assert result["production_release_authorised"] is False


def test_rejects_invalid_live_stack_predecessor(tmp_path: pathlib.Path, monkeypatch) -> None:
    record = build_valid_tree(tmp_path)
    live = tmp_path / "docs/release-evidence/runtime-readiness/phase-15-backend-backed-e2e/raw/live_stack_readiness_verification.json"
    write_json(live, {"valid": False})
    refresh_sums(tmp_path / "docs/release-evidence/runtime-readiness/phase-15-backend-backed-e2e")
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is False
    assert any("live-stack" in e for e in result["errors"])


def test_rejects_mocked_api_flag(tmp_path: pathlib.Path, monkeypatch) -> None:
    record = build_valid_tree(tmp_path)
    data = json.loads(record.read_text())
    data["playwright_mock_api"] = "1"
    record.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is False
    assert any("playwright_mock_api" in e for e in result["errors"])


def test_rejects_mocked_spec_command(tmp_path: pathlib.Path, monkeypatch) -> None:
    record = build_valid_tree(tmp_path)
    raw_result = tmp_path / "docs/release-evidence/runtime-readiness/phase-15-backend-backed-e2e/raw/backend_backed_e2e_result.json"
    payload = json.loads(raw_result.read_text())
    payload["specs"] = ["tests/e2e/learner-mocked-api-journey.spec.ts"]
    payload["steps"][1]["command"] = ["pnpm", "exec", "playwright", "test", "tests/e2e/learner-mocked-api-journey.spec.ts"]
    raw_result.write_text(json.dumps(payload), encoding="utf-8")
    refresh_sums(tmp_path / "docs/release-evidence/runtime-readiness/phase-15-backend-backed-e2e")
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is False
    assert any("mocked" in e for e in result["errors"])


def test_rejects_failed_playwright_step(tmp_path: pathlib.Path, monkeypatch) -> None:
    record = build_valid_tree(tmp_path)
    raw_result = tmp_path / "docs/release-evidence/runtime-readiness/phase-15-backend-backed-e2e/raw/backend_backed_e2e_result.json"
    payload = json.loads(raw_result.read_text())
    payload["steps"][1]["returncode"] = 1
    raw_result.write_text(json.dumps(payload), encoding="utf-8")
    refresh_sums(tmp_path / "docs/release-evidence/runtime-readiness/phase-15-backend-backed-e2e")
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is False
    assert any("must return 0" in e for e in result["errors"])


def test_rejects_production_release_authorisation(tmp_path: pathlib.Path, monkeypatch) -> None:
    record = build_valid_tree(tmp_path)
    data = json.loads(record.read_text())
    data["production_release_authorised"] = True
    record.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is False
    assert any("production_release_authorised" in e for e in result["errors"])


def test_rejects_tampered_evidence_file(tmp_path: pathlib.Path, monkeypatch) -> None:
    record = build_valid_tree(tmp_path)
    raw_result = tmp_path / "docs/release-evidence/runtime-readiness/phase-15-backend-backed-e2e/raw/backend_backed_e2e_result.json"
    raw_result.write_text(json.dumps({"valid": False}), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = verify_record(record)
    assert result["valid"] is False
    assert any("SHA mismatch" in e for e in result["errors"])
