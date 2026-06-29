#!/usr/bin/env python3
"""Verify TA Phase 13B post-merge protected-branch baseline evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

DEFAULT_RECORD = pathlib.Path(
    "docs/roadmap/execution/technical_audit_remediation/technical_audit_post_merge_baseline_record.json"
)
REGISTER_PATH = pathlib.Path("docs/roadmap/execution/technical_audit_remediation/blocker_register.json")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_RAW_FILES = [
    "raw/git_state.json",
    "raw/blocker_register_snapshot.json",
    "raw/hosted_ci_authority_record_snapshot.json",
    "raw/hosted_ci_authority_verification.json",
    "raw/merge_readiness_verification.json",
    "raw/release_readiness_verification.json",
    "raw/technical_audit_closure_verification.json",
    "raw/github_branch_state.json",
    "raw/github_branch_protection.json",
    "raw/github_check_runs.json",
    "raw/post_merge_baseline_result.json",
]
FALSE_BOUNDARY_FIELDS = [
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "live_learner_traffic_authorised",
    "runtime_kg_implementation_claimed",
    "full_backend_backed_e2e_claimed",
]


def load_json(path: pathlib.Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AssertionError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AssertionError(f"invalid JSON file: {path}: {exc}") from exc


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_sha256sums(path: pathlib.Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing SHA256SUMS file: {path}"]
    seen: set[str] = set()
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            expected, rel = line.split(maxsplit=1)
        except ValueError:
            errors.append(f"invalid SHA256SUMS line {idx}: {line!r}")
            continue
        rel = rel.strip().lstrip("*")
        target = pathlib.Path(rel)
        if target.name == path.name:
            errors.append("SHA256SUMS must not include itself")
            continue
        seen.add(target.as_posix())
        if not target.exists():
            errors.append(f"SHA256SUMS references missing file: {target}")
            continue
        actual = sha256_file(target)
        if actual != expected:
            errors.append(f"SHA mismatch for {target}: expected {expected}, got {actual}")
    if not seen:
        errors.append("SHA256SUMS contains no file entries")
    return errors


def verify_record(record_path: pathlib.Path = DEFAULT_RECORD) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []
    raw_payloads: dict[str, Any] = {}

    record = load_json(record_path)
    checked.append(record_path.as_posix())
    if not isinstance(record, dict):
        raise AssertionError("post-merge baseline record must be a JSON object")

    if record.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if record.get("slice") != "TA-PHASE-13B-POST-MERGE-PROTECTED-BRANCH-BASELINE":
        errors.append("slice must be TA-PHASE-13B-POST-MERGE-PROTECTED-BRANCH-BASELINE")
    if record.get("status") != "post_merge_protected_branch_baseline_recorded":
        errors.append("status must be post_merge_protected_branch_baseline_recorded")
    if record.get("post_merge_baseline_claimed") is not True:
        errors.append("post_merge_baseline_claimed must be true")
    if record.get("post_merge_baseline_recorded") is not True:
        errors.append("post_merge_baseline_recorded must be true")
    if record.get("technical_audit_remediation_closed") is not True:
        errors.append("technical_audit_remediation_closed must be true")
    if record.get("hosted_ci_authority_valid") is not True:
        errors.append("hosted_ci_authority_valid must be true")
    if record.get("merge_readiness_authorised") is not True:
        errors.append("merge_readiness_authorised must be true")
    if record.get("technical_audit_release_readiness_claimed") is not True:
        errors.append("technical_audit_release_readiness_claimed must be true")
    if record.get("hosted_ci_provenance_model") != "split_ci_run_evidence_closure_terminal_sha":
        errors.append("hosted_ci_provenance_model must use split provenance")

    for field in ["source_commit", "remote_target_sha", "post_merge_baseline_sha", "ci_run_sha", "evidence_commit_sha", "closure_commit_sha", "current_terminal_sha"]:
        value = record.get(field)
        if not isinstance(value, str) or not SHA_RE.match(value):
            errors.append(f"{field} must be a 40-character lowercase git SHA")
    if record.get("source_commit") != record.get("remote_target_sha"):
        errors.append("source_commit must match remote_target_sha")
    if record.get("source_commit") != record.get("post_merge_baseline_sha"):
        errors.append("source_commit must match post_merge_baseline_sha")
    if not isinstance(record.get("baseline_owner"), str) or not record["baseline_owner"].strip():
        errors.append("baseline_owner is required")
    if not isinstance(record.get("repository"), str) or "/" not in record["repository"]:
        errors.append("repository must be owner/name")
    if record.get("target_branch") != "master":
        errors.append("target_branch must be master")
    if not isinstance(record.get("required_check"), str) or not record["required_check"].strip():
        errors.append("required_check is required")
    for field in FALSE_BOUNDARY_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field} must remain false")

    evidence_dir_value = record.get("evidence_dir")
    if not isinstance(evidence_dir_value, str):
        errors.append("evidence_dir is required")
        evidence_dir = pathlib.Path("missing-evidence-dir")
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

    if evidence_dir.exists():
        for rel in REQUIRED_RAW_FILES:
            path = evidence_dir / rel
            checked.append(path.as_posix())
            if not path.exists():
                errors.append(f"required raw evidence file missing: {path}")
                continue
            try:
                raw_payloads[rel] = load_json(path)
            except AssertionError as exc:
                errors.append(str(exc))

    git_state = raw_payloads.get("raw/git_state.json") or {}
    if git_state:
        if git_state.get("tracked_worktree_clean_before_capture") is not True:
            errors.append("git_state.tracked_worktree_clean_before_capture must be true")
        if git_state.get("branch") != record.get("target_branch"):
            errors.append("git_state.branch must match target_branch")
        if git_state.get("head_sha") != record.get("source_commit"):
            errors.append("git_state.head_sha must match source_commit")
        if git_state.get("remote_target_sha") != record.get("source_commit"):
            errors.append("git_state.remote_target_sha must match source_commit")

    for rel, label in [
        ("raw/hosted_ci_authority_verification.json", "hosted CI authority"),
        ("raw/merge_readiness_verification.json", "merge readiness"),
        ("raw/release_readiness_verification.json", "release readiness"),
        ("raw/technical_audit_closure_verification.json", "technical audit closure"),
    ]:
        payload = raw_payloads.get(rel) or {}
        if payload.get("valid") is not True:
            errors.append(f"{label} verification must be valid")

    hosted_snapshot = raw_payloads.get("raw/hosted_ci_authority_record_snapshot.json") or {}
    for field in ["ci_run_sha", "evidence_commit_sha", "closure_commit_sha", "current_terminal_sha"]:
        if hosted_snapshot.get(field) != record.get(field):
            errors.append(f"hosted CI snapshot {field} must match record")

    branch_state = raw_payloads.get("raw/github_branch_state.json") or {}
    if branch_state:
        if branch_state.get("ok") is not True:
            errors.append("github_branch_state.ok must be true")
        if (branch_state.get("commit") or {}).get("sha") != record.get("source_commit"):
            errors.append("github branch state commit SHA must match source_commit")

    protection = raw_payloads.get("raw/github_branch_protection.json") or {}
    if protection:
        if protection.get("ok") is not True:
            errors.append("github_branch_protection.ok must be true")
        status_checks = protection.get("required_status_checks") or {}
        if status_checks.get("strict") is not True:
            errors.append("branch protection must require up-to-date status checks")
        contexts = status_checks.get("contexts") or []
        checks = status_checks.get("checks") or []
        check_contexts = {item for item in contexts if isinstance(item, str)}
        for item in checks:
            if isinstance(item, dict):
                if isinstance(item.get("context"), str):
                    check_contexts.add(item["context"])
                if isinstance(item.get("name"), str):
                    check_contexts.add(item["name"])
        if record.get("required_check") not in check_contexts:
            errors.append("required_check must be configured by branch protection")
        if (protection.get("allow_force_pushes") or {}).get("enabled") is not False:
            errors.append("branch protection must not allow force pushes")
        if (protection.get("allow_deletions") or {}).get("enabled") is not False:
            errors.append("branch protection must not allow deletions")

    check_runs = raw_payloads.get("raw/github_check_runs.json") or {}
    if check_runs:
        if check_runs.get("ok") is not True:
            errors.append("github_check_runs.ok must be true")
        matches = [c for c in check_runs.get("check_runs", []) or [] if c.get("name") == record.get("required_check")]
        if not matches:
            errors.append("required check run must exist on post-merge baseline commit")
        elif not any(c.get("status") == "completed" and c.get("conclusion") == "success" for c in matches):
            errors.append("required check run must be successful on post-merge baseline commit")

    baseline_result = raw_payloads.get("raw/post_merge_baseline_result.json") or {}
    if baseline_result:
        if baseline_result.get("valid") is not True:
            errors.append("post_merge_baseline_result.valid must be true")
        if baseline_result.get("post_merge_baseline_recorded") is not True:
            errors.append("post_merge_baseline_result.post_merge_baseline_recorded must be true")
        if baseline_result.get("production_release_authorised") is not False:
            errors.append("post_merge_baseline_result.production_release_authorised must be false")

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
                "Post-merge protected-branch technical-audit baseline recorded",
                "Production release authorised: false",
                "Runtime KG implementation claimed: false",
            ]:
                if phrase not in text:
                    errors.append(f"evidence_index.md missing required phrase: {phrase}")

    if REGISTER_PATH.exists():
        checked.append(REGISTER_PATH.as_posix())
        register = load_json(REGISTER_PATH)
        if register.get("status") != "phase_13b_post_merge_baseline_recorded":
            errors.append("blocker_register.status must be phase_13b_post_merge_baseline_recorded")
        if register.get("active_slice") != "technical-audit-post-merge-baseline-recorded":
            errors.append("blocker_register.active_slice must be technical-audit-post-merge-baseline-recorded")
        phase = register.get("phase_13b_post_merge_baseline_authority")
        if not isinstance(phase, dict):
            errors.append("blocker_register.phase_13b_post_merge_baseline_authority is required")
        else:
            if phase.get("post_merge_baseline_recorded") is not True:
                errors.append("phase_13b_post_merge_baseline_authority.post_merge_baseline_recorded must be true")
            if phase.get("source_commit") != record.get("source_commit"):
                errors.append("phase_13b_post_merge_baseline_authority.source_commit must match record.source_commit")
            for field in ["production_release_authorised", "deployment_authorised", "release_tag_authorised", "live_learner_traffic_authorised", "runtime_kg_implementation_claimed"]:
                if phase.get(field) is not False:
                    errors.append(f"phase_13b_post_merge_baseline_authority.{field} must remain false")
    else:
        errors.append(f"missing blocker register: {REGISTER_PATH}")

    return {
        "valid": len(errors) == 0,
        "record": record_path.as_posix(),
        "post_merge_baseline_recorded": bool(record.get("post_merge_baseline_recorded")),
        "technical_audit_remediation_closed": bool(record.get("technical_audit_remediation_closed")),
        "hosted_ci_authority_valid": bool(record.get("hosted_ci_authority_valid")),
        "merge_readiness_authorised": bool(record.get("merge_readiness_authorised")),
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
    parser.add_argument("--record", default=str(DEFAULT_RECORD))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = verify_record(pathlib.Path(args.record))
    except AssertionError as exc:
        result = {
            "valid": False,
            "record": args.record,
            "post_merge_baseline_recorded": False,
            "errors": [str(exc)],
            "warnings": [],
            "checked": [],
        }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid:", result["valid"])
        for warning in result.get("warnings", []):
            print("warning:", warning)
        for error in result.get("errors", []):
            print("error:", error, file=sys.stderr)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
