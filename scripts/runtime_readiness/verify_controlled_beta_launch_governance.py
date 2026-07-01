#!/usr/bin/env python3
"""Verify Phase 18 controlled beta launch-governance authority evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from typing import Any

RECORD_PATH = pathlib.Path("docs/roadmap/execution/runtime_readiness/phase_18_controlled_beta_launch_governance_record.json")
FALSE_BOUNDARY_FIELDS: tuple[str, ...] = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "controlled_beta_launch_authorised",
    "live_learner_traffic_authorised",
    "learner_data_migration_authorised",
    "runtime_kg_implementation_claimed",
)
REQUIRED_TRUE_FIELDS: tuple[str, ...] = (
    "controlled_beta_launch_governance_claimed",
    "controlled_beta_launch_governance_recorded",
    "phase_17_controlled_beta_readiness_valid",
    "launch_operations_documents_valid",
)
REQUIRED_RAW_FILES: tuple[str, ...] = (
    "raw/git_state.json",
    "raw/phase17_controlled_beta_readiness_verification.json",
    "raw/launch_operations_documents.json",
    "raw/launch_governance_boundary.json",
    "raw/controlled_beta_launch_governance_result.json",
    "raw/controlled_beta_launch_governance_record_snapshot.json",
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


def _raw_json(evidence_dir: pathlib.Path, rel: str, errors: list[str]) -> dict[str, Any]:
    path = evidence_dir / rel
    if not path.exists():
        errors.append(f"required evidence file missing: {path}")
        return {}
    try:
        payload = load_json(path)
    except Exception as exc:
        errors.append(f"invalid JSON evidence file {path}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"evidence file must contain an object: {path}")
        return {}
    return payload


def verify_record(record_path: pathlib.Path = RECORD_PATH) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []
    if not record_path.exists():
        return {"valid": False, "record": record_path.as_posix(), "controlled_beta_launch_governance_recorded": False, "errors": [f"record missing: {record_path}"], "warnings": warnings, "checked": checked}
    record = load_json(record_path)
    checked.append(record_path.as_posix())
    if record.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if record.get("slice") != "PHASE-18-CONTROLLED-BETA-LAUNCH-GOVERNANCE-AUTHORITY":
        errors.append("slice must be PHASE-18-CONTROLLED-BETA-LAUNCH-GOVERNANCE-AUTHORITY")
    if record.get("status") != "controlled_beta_launch_governance_recorded":
        errors.append("status must be controlled_beta_launch_governance_recorded")
    if record.get("beta_scope") != "controlled_beta_launch_governance_gate":
        errors.append("beta_scope must be controlled_beta_launch_governance_gate")
    for field in REQUIRED_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field} must be true")
    for field in FALSE_BOUNDARY_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field} must remain false")
    evidence_dir_value = record.get("evidence_dir")
    evidence_dir = pathlib.Path(evidence_dir_value) if isinstance(evidence_dir_value, str) else pathlib.Path("__missing__")
    if not isinstance(evidence_dir_value, str) or not evidence_dir.exists():
        errors.append(f"evidence_dir must exist: {evidence_dir_value}")
    index_value = record.get("evidence_index")
    if not isinstance(index_value, str) or not pathlib.Path(index_value).exists():
        errors.append("evidence_index must exist")
    else:
        checked.append(index_value)
        index_text = pathlib.Path(index_value).read_text(encoding="utf-8")
        for marker in (
            "Phase 18 Controlled Beta Launch Governance Evidence",
            "Controlled beta launch governance recorded: true",
            "Production release authorised: false",
            "Deployment authorised: false",
            "Controlled beta launch authorised: false",
            "Live learner traffic authorised: false",
            "Runtime KG implementation claimed: false",
        ):
            if marker not in index_text:
                errors.append(f"evidence index missing marker: {marker}")
    sums_value = record.get("sha256sums")
    if not isinstance(sums_value, str):
        errors.append("sha256sums path must be recorded")
    else:
        checked.append(sums_value)
        errors.extend(verify_sha256sums(pathlib.Path(sums_value)))
    raw_payloads = {rel: _raw_json(evidence_dir, rel, errors) for rel in REQUIRED_RAW_FILES}
    checked.extend((evidence_dir / rel).as_posix() for rel in REQUIRED_RAW_FILES)
    result = raw_payloads.get("raw/controlled_beta_launch_governance_result.json") or {}
    if result.get("valid") is not True:
        errors.append("controlled beta launch-governance raw result must be valid")
    if result.get("controlled_beta_launch_governance_recorded") is not True:
        errors.append("controlled beta launch-governance raw result must record true")
    for field in FALSE_BOUNDARY_FIELDS:
        if result.get(field) is not False:
            errors.append(f"raw result {field} must remain false")
    phase17 = raw_payloads.get("raw/phase17_controlled_beta_readiness_verification.json") or {}
    if phase17.get("valid") is not True or phase17.get("returncode") != 0:
        errors.append("Phase 17 readiness verification must be valid with returncode 0")
    docs = raw_payloads.get("raw/launch_operations_documents.json") or {}
    if docs.get("valid") is not True:
        errors.append("launch operations documents raw evidence must be valid")
    git_state = raw_payloads.get("raw/git_state.json") or {}
    if git_state.get("tracked_worktree_clean_before_capture") is not True:
        errors.append("tracked worktree must have been clean before launch-governance capture")
    if record.get("source_commit") != record.get("remote_target_sha"):
        errors.append("source_commit must match remote_target_sha for final launch-governance evidence")
    if git_state.get("head_sha") and record.get("source_commit") != git_state.get("head_sha"):
        errors.append("record source_commit must match raw git_state head_sha")
    snapshot = raw_payloads.get("raw/controlled_beta_launch_governance_record_snapshot.json") or {}
    if snapshot.get("status") != record.get("status"):
        errors.append("record snapshot status must match record")
    return {
        "valid": len(errors) == 0,
        "record": record_path.as_posix(),
        "controlled_beta_launch_governance_recorded": record.get("controlled_beta_launch_governance_recorded") is True,
        "phase_17_controlled_beta_readiness_valid": record.get("phase_17_controlled_beta_readiness_valid") is True,
        "launch_operations_documents_valid": record.get("launch_operations_documents_valid") is True,
        "production_release_authorised": record.get("production_release_authorised"),
        "deployment_authorised": record.get("deployment_authorised"),
        "release_tag_authorised": record.get("release_tag_authorised"),
        "public_beta_authorised": record.get("public_beta_authorised"),
        "controlled_beta_launch_authorised": record.get("controlled_beta_launch_authorised"),
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
