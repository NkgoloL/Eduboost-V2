#!/usr/bin/env python3
"""Verify Phase 15 backend-backed E2E smoke readiness evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from typing import Any

RECORD_PATH = pathlib.Path("docs/roadmap/execution/runtime_readiness/phase_15_backend_backed_e2e_record.json")
FALSE_BOUNDARY_FIELDS = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "live_learner_traffic_authorised",
    "runtime_kg_implementation_claimed",
)
REQUIRED_RAW_FILES = (
    "raw/git_state.json",
    "raw/live_stack_readiness_verification.json",
    "raw/probe_api_health.json",
    "raw/probe_api_ready.json",
    "raw/probe_api_deep.json",
    "raw/probe_frontend_root.json",
    "raw/probe_frontend_api_rewrite.json",
    "raw/backend_backed_e2e_result.json",
)


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_sha256sums(sums_path: pathlib.Path) -> list[str]:
    errors: list[str] = []
    if not sums_path.exists():
        return [f"SHA256SUMS file missing: {sums_path}"]
    for line in sums_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            expected, file_name = line.split("  ", 1)
        except ValueError:
            errors.append(f"malformed SHA256SUMS line: {line}")
            continue
        path = pathlib.Path(file_name)
        if not path.exists():
            errors.append(f"SHA target missing: {path}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            errors.append(f"SHA mismatch for {path}: expected {expected}, got {actual}")
    return errors


def _json_raw(evidence_dir: pathlib.Path, rel: str, errors: list[str]) -> dict[str, Any]:
    path = evidence_dir / rel
    if not path.exists():
        errors.append(f"required evidence file missing: {path}")
        return {}
    try:
        payload = load_json(path)
    except Exception as exc:
        errors.append(f"invalid JSON evidence file {path}: {exc}")
        return {}
    return payload if isinstance(payload, dict) else {}


def verify_record(record_path: pathlib.Path = RECORD_PATH) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []

    if not record_path.exists():
        return {
            "valid": False,
            "record": record_path.as_posix(),
            "backend_backed_e2e_recorded": False,
            "errors": [f"record missing: {record_path}"],
            "warnings": warnings,
            "checked": checked,
        }

    record = load_json(record_path)
    checked.append(record_path.as_posix())
    if record.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if record.get("slice") != "PHASE-15-BACKEND-BACKED-E2E-AUTHORITY":
        errors.append("slice must be PHASE-15-BACKEND-BACKED-E2E-AUTHORITY")
    if record.get("status") != "backend_backed_e2e_recorded":
        errors.append("status must be backend_backed_e2e_recorded")
    if record.get("backend_backed_e2e_claimed") is not True:
        errors.append("backend_backed_e2e_claimed must be true")
    if record.get("backend_backed_e2e_recorded") is not True:
        errors.append("backend_backed_e2e_recorded must be true")
    if record.get("live_stack_readiness_valid") is not True:
        errors.append("live_stack_readiness_valid must be true")
    if record.get("e2e_scope") != "backend_backed_smoke":
        errors.append("e2e_scope must be backend_backed_smoke")
    if record.get("full_production_e2e_claimed") is not False:
        errors.append("full_production_e2e_claimed must remain false")
    if record.get("mocked_api_used") is not False:
        errors.append("mocked_api_used must be false")
    if str(record.get("playwright_mock_api")) != "0":
        errors.append("playwright_mock_api must be '0'")
    if not record.get("e2e_owner"):
        errors.append("e2e_owner is required")
    for field in FALSE_BOUNDARY_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field} must remain false")

    evidence_dir_value = record.get("evidence_dir")
    if not isinstance(evidence_dir_value, str):
        errors.append("evidence_dir is required")
        evidence_dir = pathlib.Path("__missing__")
    else:
        evidence_dir = pathlib.Path(evidence_dir_value)
        checked.append(evidence_dir.as_posix())
        if not evidence_dir.exists():
            errors.append(f"evidence_dir missing: {evidence_dir}")

    sums_value = record.get("sha256sums")
    if not isinstance(sums_value, str):
        errors.append("sha256sums is required")
    else:
        sums_path = pathlib.Path(sums_value)
        checked.append(sums_path.as_posix())
        errors.extend(verify_sha256sums(sums_path))

    raw_payloads: dict[str, dict[str, Any]] = {}
    for rel in REQUIRED_RAW_FILES:
        raw_payloads[rel] = _json_raw(evidence_dir, rel, errors)

    git_state = raw_payloads.get("raw/git_state.json") or {}
    if git_state:
        if git_state.get("branch") != record.get("target_branch"):
            errors.append("git_state.branch must equal record target_branch")
        if git_state.get("head_sha") != record.get("source_commit"):
            errors.append("git_state.head_sha must equal record source_commit")
        if git_state.get("remote_target_sha") != record.get("remote_target_sha"):
            errors.append("git_state.remote_target_sha must equal record remote_target_sha")
        if git_state.get("tracked_worktree_clean_before_capture") is not True:
            errors.append("tracked worktree must have been clean before capture")

    live_stack = raw_payloads.get("raw/live_stack_readiness_verification.json") or {}
    if live_stack.get("valid") is not True:
        errors.append("Phase 14 live-stack readiness verification must be valid")

    for rel, label in [
        ("raw/probe_api_health.json", "API /health"),
        ("raw/probe_api_ready.json", "API /ready"),
        ("raw/probe_api_deep.json", "API /api/v2/health/deep"),
        ("raw/probe_frontend_root.json", "frontend root"),
        ("raw/probe_frontend_api_rewrite.json", "frontend /api/v2/system/health rewrite"),
    ]:
        payload = raw_payloads.get(rel) or {}
        if payload.get("status_code") != 200:
            errors.append(f"{label} probe must return HTTP 200")

    result = raw_payloads.get("raw/backend_backed_e2e_result.json") or {}
    if result:
        if result.get("valid") is not True:
            errors.append("backend_backed_e2e_result.valid must be true")
        if result.get("backend_backed_e2e_recorded") is not True:
            errors.append("backend_backed_e2e_result.backend_backed_e2e_recorded must be true")
        if result.get("mocked_api_used") is not False:
            errors.append("backend_backed_e2e_result.mocked_api_used must be false")
        if str(result.get("playwright_mock_api")) != "0":
            errors.append("backend_backed_e2e_result.playwright_mock_api must be '0'")
        specs = result.get("specs") if isinstance(result.get("specs"), list) else []
        if not specs:
            errors.append("backend_backed_e2e_result.specs must be non-empty")
        for spec in specs:
            name = pathlib.Path(str(spec)).name.lower()
            if "mock" in name:
                errors.append(f"mocked Playwright spec is not allowed in backend-backed E2E evidence: {spec}")
        steps = result.get("steps") if isinstance(result.get("steps"), list) else []
        if not steps:
            errors.append("backend_backed_e2e_result.steps must be non-empty")
        if not any(step.get("name") == "playwright_backend_backed_smoke" for step in steps if isinstance(step, dict)):
            errors.append("playwright_backend_backed_smoke step is required")
        for step in steps:
            if not isinstance(step, dict):
                continue
            if step.get("returncode") != 0:
                errors.append(f"step {step.get('name')} must return 0")
            command_text = " ".join(str(part) for part in step.get("command", []))
            if "mocked-api" in command_text:
                errors.append("backend-backed E2E command must not run mocked-api specs")
        for field in FALSE_BOUNDARY_FIELDS:
            if result.get(field) is not False:
                errors.append(f"backend_backed_e2e_result.{field} must remain false")

    index_value = record.get("evidence_index")
    if not isinstance(index_value, str):
        errors.append("evidence_index is required")
    else:
        index_path = pathlib.Path(index_value)
        checked.append(index_path.as_posix())
        if not index_path.exists():
            errors.append(f"evidence_index missing: {index_path}")
        else:
            text = index_path.read_text(encoding="utf-8")
            for phrase in [
                "Phase 15 Backend-Backed E2E Smoke Evidence",
                "Required predecessor: Phase 14 live-stack readiness verifier valid.",
                "Mocked API used: false",
                "E2E scope: backend_backed_smoke",
                "Production release authorised: false",
                "Live learner traffic authorised: false",
                "Runtime KG implementation claimed: false",
            ]:
                if phrase not in text:
                    errors.append(f"evidence_index.md missing required phrase: {phrase}")

    return {
        "valid": len(errors) == 0,
        "record": record_path.as_posix(),
        "backend_backed_e2e_recorded": bool(record.get("backend_backed_e2e_recorded")),
        "live_stack_readiness_valid": bool(record.get("live_stack_readiness_valid")),
        "e2e_scope": record.get("e2e_scope"),
        "mocked_api_used": bool(record.get("mocked_api_used")),
        "full_production_e2e_claimed": bool(record.get("full_production_e2e_claimed")),
        "production_release_authorised": bool(record.get("production_release_authorised")),
        "deployment_authorised": bool(record.get("deployment_authorised")),
        "release_tag_authorised": bool(record.get("release_tag_authorised")),
        "live_learner_traffic_authorised": bool(record.get("live_learner_traffic_authorised")),
        "runtime_kg_implementation_claimed": bool(record.get("runtime_kg_implementation_claimed")),
        "errors": errors,
        "warnings": warnings,
        "checked": checked,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", nargs="?", default=str(RECORD_PATH))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify_record(pathlib.Path(args.record))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid:", result["valid"])
        for error in result["errors"]:
            print("ERROR:", error)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
