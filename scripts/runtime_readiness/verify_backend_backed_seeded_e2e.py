#!/usr/bin/env python3
"""Verify Phase 16 backend-backed seeded E2E journey readiness evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from typing import Any

RECORD_PATH = pathlib.Path("docs/roadmap/execution/runtime_readiness/phase_16_backend_backed_seeded_e2e_record.json")
FALSE_BOUNDARY_FIELDS = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "live_learner_traffic_authorised",
    "full_production_e2e_claimed",
    "runtime_kg_implementation_claimed",
)
REQUIRED_RAW_FILES = (
    "raw/git_state.json",
    "raw/phase15_backend_backed_e2e_verification.json",
    "raw/probe_api_health.json",
    "raw/probe_api_ready.json",
    "raw/probe_api_deep.json",
    "raw/probe_frontend_root.json",
    "raw/probe_frontend_api_rewrite.json",
    "raw/seeded_backend_backed_e2e_result.json",
)
REQUIRED_SPECS = (
    "tests/e2e/auth.setup.ts",
    "tests/e2e/diagnostic.spec.ts",
    "tests/e2e/study_plan_and_lesson.spec.ts",
    "tests/e2e/parent_portal.spec.ts",
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
            "seeded_e2e_recorded": False,
            "errors": [f"record missing: {record_path}"],
            "warnings": warnings,
            "checked": checked,
        }

    record = load_json(record_path)
    checked.append(record_path.as_posix())
    if record.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if record.get("slice") != "PHASE-16-BACKEND-BACKED-SEEDED-E2E-AUTHORITY":
        errors.append("slice must be PHASE-16-BACKEND-BACKED-SEEDED-E2E-AUTHORITY")
    if record.get("status") != "seeded_backend_backed_e2e_recorded":
        errors.append("status must be seeded_backend_backed_e2e_recorded")
    if record.get("seeded_e2e_claimed") is not True:
        errors.append("seeded_e2e_claimed must be true")
    if record.get("seeded_e2e_recorded") is not True:
        errors.append("seeded_e2e_recorded must be true")
    if record.get("backend_backed_e2e_valid") is not True:
        errors.append("backend_backed_e2e_valid must be true")
    if record.get("e2e_scope") != "backend_backed_seeded_journeys":
        errors.append("e2e_scope must be backend_backed_seeded_journeys")
    if record.get("mocked_api_used") is not False:
        errors.append("mocked_api_used must be false")
    if str(record.get("playwright_mock_api")) != "0":
        errors.append("playwright_mock_api must be '0'")
    for field in FALSE_BOUNDARY_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field} must remain false")

    evidence_dir_value = record.get("evidence_dir")
    if not isinstance(evidence_dir_value, str) or not evidence_dir_value:
        errors.append("evidence_dir must be recorded")
        evidence_dir = pathlib.Path("__missing__")
    else:
        evidence_dir = pathlib.Path(evidence_dir_value)
        if not evidence_dir.exists():
            errors.append(f"evidence_dir missing: {evidence_dir}")
    evidence_index_value = record.get("evidence_index")
    if not isinstance(evidence_index_value, str) or not pathlib.Path(evidence_index_value).exists():
        errors.append("evidence_index must exist")
    else:
        checked.append(evidence_index_value)
        index_text = pathlib.Path(evidence_index_value).read_text(encoding="utf-8")
        for marker in [
            "Phase 16 Backend-Backed Seeded E2E Evidence",
            "Mocked API used: false",
            "E2E scope: backend_backed_seeded_journeys",
            "Production release authorised: false",
            "Live learner traffic authorised: false",
            "Runtime KG implementation claimed: false",
        ]:
            if marker not in index_text:
                errors.append(f"evidence index missing marker: {marker}")

    sums_value = record.get("sha256sums")
    if not isinstance(sums_value, str):
        errors.append("sha256sums path must be recorded")
    else:
        sums_path = pathlib.Path(sums_value)
        checked.append(sums_value)
        errors.extend(verify_sha256sums(sums_path))

    raw_payloads = {rel: _json_raw(evidence_dir, rel, errors) for rel in REQUIRED_RAW_FILES}
    checked.extend((evidence_dir / rel).as_posix() for rel in REQUIRED_RAW_FILES)

    git_state = raw_payloads.get("raw/git_state.json") or {}
    if git_state.get("tracked_worktree_clean_before_capture") is not True:
        errors.append("tracked worktree must have been clean before seeded E2E capture")
    if record.get("source_commit") != record.get("remote_target_sha"):
        errors.append("source_commit must match remote_target_sha")
    if git_state.get("head_sha") and record.get("source_commit") != git_state.get("head_sha"):
        errors.append("record source_commit must match raw git_state head_sha")

    phase15 = raw_payloads.get("raw/phase15_backend_backed_e2e_verification.json") or {}
    if phase15.get("valid") is not True:
        errors.append("Phase 15 backend-backed E2E verification raw evidence must be valid")

    result = raw_payloads.get("raw/seeded_backend_backed_e2e_result.json") or {}
    if result.get("valid") is not True:
        errors.append("seeded backend-backed E2E result must be valid")
    if result.get("seeded_e2e_recorded") is not True:
        errors.append("seeded backend-backed E2E result must record seeded_e2e_recorded true")
    if result.get("mocked_api_used") is not False:
        errors.append("seeded backend-backed E2E result must not use mocked API")
    if result.get("e2e_scope") != "backend_backed_seeded_journeys":
        errors.append("seeded backend-backed E2E result has wrong e2e_scope")

    specs = result.get("specs")
    if not isinstance(specs, list):
        errors.append("seeded backend-backed E2E result must list specs")
        specs = []
    for spec in REQUIRED_SPECS:
        if spec not in specs:
            errors.append(f"required seeded E2E spec missing from result: {spec}")
    for spec in specs:
        if "mock" in pathlib.Path(str(spec)).name.lower():
            errors.append(f"mocked spec must not be included: {spec}")

    steps = result.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append("seeded backend-backed E2E result must include execution steps")
    else:
        failing = [step for step in steps if isinstance(step, dict) and step.get("returncode") != 0]
        if failing:
            errors.append(f"all seeded E2E steps must pass; failing steps: {[step.get('name') for step in failing]}")
        step_names = [str(step.get("name")) for step in steps if isinstance(step, dict)]
        for required in ["playwright_seeded_01_auth_setup", "playwright_seeded_02_diagnostic", "playwright_seeded_03_study_plan_and_lesson", "playwright_seeded_04_parent_portal"]:
            if required not in step_names:
                errors.append(f"required ordered execution step missing: {required}")

    for raw_name in ["raw/probe_api_health.json", "raw/probe_api_ready.json", "raw/probe_api_deep.json", "raw/probe_frontend_root.json", "raw/probe_frontend_api_rewrite.json"]:
        probe = raw_payloads.get(raw_name) or {}
        if probe.get("status_code") != 200:
            errors.append(f"{raw_name} must record HTTP 200")

    return {
        "valid": len(errors) == 0,
        "record": record_path.as_posix(),
        "seeded_e2e_recorded": record.get("seeded_e2e_recorded") is True,
        "backend_backed_e2e_valid": record.get("backend_backed_e2e_valid") is True,
        "e2e_scope": record.get("e2e_scope"),
        "mocked_api_used": record.get("mocked_api_used"),
        "production_release_authorised": record.get("production_release_authorised"),
        "deployment_authorised": record.get("deployment_authorised"),
        "release_tag_authorised": record.get("release_tag_authorised"),
        "live_learner_traffic_authorised": record.get("live_learner_traffic_authorised"),
        "runtime_kg_implementation_claimed": record.get("runtime_kg_implementation_claimed"),
        "errors": errors,
        "warnings": warnings,
        "checked": checked,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", default=RECORD_PATH.as_posix())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = verify_record(pathlib.Path(args.record))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid:", result["valid"])
        for error in result["errors"]:
            print("ERROR:", error)
        for warning in result["warnings"]:
            print("WARNING:", warning)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
