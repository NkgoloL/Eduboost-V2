from __future__ import annotations

import hashlib
import json
import pathlib

from scripts.runtime_readiness.verify_backend_backed_seeded_e2e import verify_record

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
    evidence = tmp_path / "docs/release-evidence/runtime-readiness/phase-16-backend-backed-seeded-e2e"
    raw = evidence / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    record_path = tmp_path / "docs/roadmap/execution/runtime_readiness/phase_16_backend_backed_seeded_e2e_record.json"
    index_path = evidence / "evidence_index.md"
    index_path.write_text(
        "# Phase 16 Backend-Backed Seeded E2E Evidence\n"
        "Required predecessor: Phase 15 backend-backed E2E verifier valid.\n"
        "Mocked API used: false\n"
        "E2E scope: backend_backed_seeded_journeys\n"
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
    write_json(raw / "phase15_backend_backed_e2e_verification.json", {"valid": True})
    for name in ["api_health", "api_ready", "api_deep", "frontend_root", "frontend_api_rewrite"]:
        write_json(raw / f"probe_{name}.json", {"status_code": 200, "json": {"status": "ok"}})
    write_json(raw / "seeded_backend_backed_e2e_result.json", {
        "valid": True,
        "seeded_e2e_recorded": True,
        "seeded_e2e_claimed": True,
        "backend_backed_e2e_valid": True,
        "playwright_mock_api": "0",
        "mocked_api_used": False,
        "e2e_scope": "backend_backed_seeded_journeys",
        "full_production_e2e_claimed": False,
        "specs": [
            "tests/e2e/auth.setup.ts",
            "tests/e2e/diagnostic.spec.ts",
            "tests/e2e/study_plan_and_lesson.spec.ts",
            "tests/e2e/parent_portal.spec.ts",
        ],
        "steps": [
            {"name": "playwright_seeded_01_auth_setup", "command": ["pnpm", "exec", "playwright", "test", "tests/e2e/auth.setup.ts"], "returncode": 0},
            {"name": "playwright_seeded_02_diagnostic", "command": ["pnpm", "exec", "playwright", "test", "tests/e2e/diagnostic.spec.ts"], "returncode": 0},
            {"name": "playwright_seeded_03_study_plan_and_lesson", "command": ["pnpm", "exec", "playwright", "test", "tests/e2e/study_plan_and_lesson.spec.ts"], "returncode": 0},
            {"name": "playwright_seeded_04_parent_portal", "command": ["pnpm", "exec", "playwright", "test", "tests/e2e/parent_portal.spec.ts"], "returncode": 0},
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
        "slice": "PHASE-16-BACKEND-BACKED-SEEDED-E2E-AUTHORITY",
        "status": "seeded_backend_backed_e2e_recorded",
        "target_branch": "master",
        "source_commit": SHA_A,
        "remote_target_sha": SHA_A,
        "e2e_owner": "Nkgolo Lebelo",
        "seeded_e2e_claimed": True,
        "seeded_e2e_recorded": True,
        "backend_backed_e2e_valid": True,
        "e2e_scope": "backend_backed_seeded_journeys",
        "full_production_e2e_claimed": False,
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


def test_valid_seeded_e2e_record_passes(tmp_path: pathlib.Path) -> None:
    record_path = build_valid_tree(tmp_path)
    result = verify_record(record_path)
    assert result["valid"] is True
    assert result["seeded_e2e_recorded"] is True
    assert result["backend_backed_e2e_valid"] is True
    assert result["e2e_scope"] == "backend_backed_seeded_journeys"


def test_rejects_unclaimed_seeded_e2e(tmp_path: pathlib.Path) -> None:
    record_path = build_valid_tree(tmp_path)
    record = json.loads(record_path.read_text())
    record["seeded_e2e_claimed"] = False
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    result = verify_record(record_path)
    assert result["valid"] is False
    assert any("seeded_e2e_claimed" in error for error in result["errors"])


def test_rejects_missing_phase15_validity(tmp_path: pathlib.Path) -> None:
    record_path = build_valid_tree(tmp_path)
    record = json.loads(record_path.read_text())
    record["backend_backed_e2e_valid"] = False
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    result = verify_record(record_path)
    assert result["valid"] is False
    assert any("backend_backed_e2e_valid" in error for error in result["errors"])


def test_rejects_mocked_api_or_mock_specs(tmp_path: pathlib.Path) -> None:
    record_path = build_valid_tree(tmp_path)
    record = json.loads(record_path.read_text())
    record["mocked_api_used"] = True
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    result = verify_record(record_path)
    assert result["valid"] is False
    assert any("mocked_api_used" in error for error in result["errors"])

    record_path = build_valid_tree(tmp_path)
    evidence = tmp_path / "docs/release-evidence/runtime-readiness/phase-16-backend-backed-seeded-e2e"
    result_path = evidence / "raw/seeded_backend_backed_e2e_result.json"
    payload = json.loads(result_path.read_text())
    payload["specs"].append("tests/e2e/learner-mocked-api-journey.spec.ts")
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    refresh_sums(evidence)
    result = verify_record(record_path)
    assert result["valid"] is False
    assert any("mocked spec" in error for error in result["errors"])


def test_rejects_missing_required_specs(tmp_path: pathlib.Path) -> None:
    record_path = build_valid_tree(tmp_path)
    evidence = tmp_path / "docs/release-evidence/runtime-readiness/phase-16-backend-backed-seeded-e2e"
    result_path = evidence / "raw/seeded_backend_backed_e2e_result.json"
    payload = json.loads(result_path.read_text())
    payload["specs"].remove("tests/e2e/parent_portal.spec.ts")
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    refresh_sums(evidence)
    result = verify_record(record_path)
    assert result["valid"] is False
    assert any("parent_portal" in error for error in result["errors"])


def test_rejects_failing_execution_step(tmp_path: pathlib.Path) -> None:
    record_path = build_valid_tree(tmp_path)
    evidence = tmp_path / "docs/release-evidence/runtime-readiness/phase-16-backend-backed-seeded-e2e"
    result_path = evidence / "raw/seeded_backend_backed_e2e_result.json"
    payload = json.loads(result_path.read_text())
    payload["steps"][2]["returncode"] = 1
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    refresh_sums(evidence)
    result = verify_record(record_path)
    assert result["valid"] is False
    assert any("failing steps" in error for error in result["errors"])


def test_rejects_boundary_overreach(tmp_path: pathlib.Path) -> None:
    record_path = build_valid_tree(tmp_path)
    record = json.loads(record_path.read_text())
    record["live_learner_traffic_authorised"] = True
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    result = verify_record(record_path)
    assert result["valid"] is False
    assert any("live_learner_traffic_authorised" in error for error in result["errors"])


def test_rejects_sha_mismatch(tmp_path: pathlib.Path) -> None:
    record_path = build_valid_tree(tmp_path)
    evidence = tmp_path / "docs/release-evidence/runtime-readiness/phase-16-backend-backed-seeded-e2e"
    (evidence / "raw/probe_api_health.json").write_text('{"status_code": 500}\n')
    result = verify_record(record_path)
    assert result["valid"] is False
    assert any("SHA mismatch" in error for error in result["errors"])
