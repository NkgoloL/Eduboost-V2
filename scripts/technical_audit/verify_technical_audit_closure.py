#!/usr/bin/env python3
"""Verify final technical-audit remediation closure authority evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

DEFAULT_RECORD = pathlib.Path(
    "docs/roadmap/execution/technical_audit_remediation/technical_audit_closure_record.json"
)
REGISTER_PATH = pathlib.Path("docs/roadmap/execution/technical_audit_remediation/blocker_register.json")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_RAW_FILES = [
    "raw/git_state.json",
    "raw/blocker_register_snapshot.json",
    "raw/hosted_ci_authority_record_snapshot.json",
    "raw/release_readiness_record_snapshot.json",
    "raw/release_readiness_verification.json",
    "raw/technical_audit_closure_result.json",
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
        if pathlib.Path(rel).name == pathlib.Path(path).name:
            errors.append("SHA256SUMS must not include itself")
            continue
        target = pathlib.Path(rel)
        seen.add(target.as_posix())
        if not target.exists():
            errors.append(f"SHA256SUMS references missing file: {target}")
            continue
        actual = sha256_file(target)
        if expected != actual:
            errors.append(f"SHA mismatch for {target}: expected {expected}, got {actual}")
    if not seen:
        errors.append("SHA256SUMS contains no file entries")
    return errors


def verify_record(record_path: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []

    record = load_json(record_path)
    if not isinstance(record, dict):
        raise AssertionError("closure record must contain a JSON object")
    checked.append(record_path.as_posix())

    if record.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if record.get("slice") != "TA-PHASE-12-TECHNICAL-AUDIT-REMEDIATION-CLOSURE":
        errors.append("slice must be TA-PHASE-12-TECHNICAL-AUDIT-REMEDIATION-CLOSURE")
    if record.get("status") != "technical_audit_remediation_closed":
        errors.append("status must be technical_audit_remediation_closed")
    if record.get("technical_audit_remediation_closure_claimed") is not True:
        errors.append("technical_audit_remediation_closure_claimed must be true")
    if record.get("technical_audit_remediation_closed") is not True:
        errors.append("technical_audit_remediation_closed must be true")
    if record.get("technical_audit_release_readiness_claimed") is not True:
        errors.append("technical_audit_release_readiness_claimed must be true")
    if record.get("release_readiness_claimed") is not True:
        errors.append("release_readiness_claimed must be true")
    if record.get("production_release_authorised") is not False:
        errors.append("production_release_authorised must remain false")
    if record.get("deployment_authorised") is not False:
        errors.append("deployment_authorised must remain false")
    if record.get("release_tag_authorised") is not False:
        errors.append("release_tag_authorised must remain false")
    if record.get("live_learner_traffic_authorised") is not False:
        errors.append("live_learner_traffic_authorised must remain false")
    if record.get("runtime_kg_implementation_claimed") is not False:
        errors.append("runtime_kg_implementation_claimed must remain false")
    if record.get("full_backend_backed_e2e_claimed") is not False:
        errors.append("full_backend_backed_e2e_claimed must remain false")
    if record.get("closure_decision") != "authorised":
        errors.append("closure_decision must be authorised")
    if not isinstance(record.get("closure_owner"), str) or not record["closure_owner"].strip():
        errors.append("closure_owner is required")
    if not isinstance(record.get("source_commit"), str) or not SHA_RE.match(record["source_commit"]):
        errors.append("source_commit must be a 40-character lowercase git SHA")

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
        errors.append("sha256sums path is required")
    else:
        sums_path = pathlib.Path(sums_value)
        checked.append(sums_path.as_posix())
        errors.extend(verify_sha256sums(sums_path))

    raw_payloads: dict[str, Any] = {}
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
        if git_state.get("head_sha") != record.get("source_commit"):
            errors.append("git_state.head_sha must match record.source_commit")

    release_verification = raw_payloads.get("raw/release_readiness_verification.json") or {}
    if release_verification:
        if release_verification.get("valid") is not True:
            errors.append("release_readiness_verification.valid must be true")
        if release_verification.get("release_readiness_claimed") is not True:
            errors.append("release_readiness_verification.release_readiness_claimed must be true")
        if release_verification.get("technical_audit_release_readiness_claimed") is not True:
            errors.append("release_readiness_verification.technical_audit_release_readiness_claimed must be true")
        if release_verification.get("production_release_authorised") is not False:
            errors.append("release_readiness_verification.production_release_authorised must be false")

    release_record = raw_payloads.get("raw/release_readiness_record_snapshot.json") or {}
    if release_record:
        if release_record.get("status") != "technical_audit_release_readiness_authorised":
            errors.append("release_readiness_record_snapshot.status must be technical_audit_release_readiness_authorised")
        if release_record.get("technical_audit_release_readiness_claimed") is not True:
            errors.append("release_readiness_record_snapshot.technical_audit_release_readiness_claimed must be true")
        if release_record.get("production_release_authorised") is not False:
            errors.append("release_readiness_record_snapshot.production_release_authorised must be false")
        if release_record.get("runtime_kg_implementation_claimed") is not False:
            errors.append("release_readiness_record_snapshot.runtime_kg_implementation_claimed must be false")

    closure_result = raw_payloads.get("raw/technical_audit_closure_result.json") or {}
    if closure_result:
        if closure_result.get("valid") is not True:
            errors.append("technical_audit_closure_result.valid must be true")
        if closure_result.get("technical_audit_remediation_closed") is not True:
            errors.append("technical_audit_closure_result.technical_audit_remediation_closed must be true")
        if closure_result.get("production_release_authorised") is not False:
            errors.append("technical_audit_closure_result.production_release_authorised must be false")
        if closure_result.get("runtime_kg_implementation_claimed") is not False:
            errors.append("technical_audit_closure_result.runtime_kg_implementation_claimed must be false")

    index_value = record.get("evidence_index")
    if not isinstance(index_value, str):
        errors.append("evidence_index path is required")
    else:
        index_path = pathlib.Path(index_value)
        checked.append(index_path.as_posix())
        if not index_path.exists():
            errors.append(f"evidence_index missing: {index_path}")
        else:
            text = index_path.read_text(encoding="utf-8")
            for phrase in [
                "Technical-audit remediation closure authorised",
                "Production release authorised: false",
                "Runtime KG implementation claimed: false",
            ]:
                if phrase not in text:
                    errors.append(f"evidence_index.md missing required phrase: {phrase}")

    if REGISTER_PATH.exists():
        checked.append(REGISTER_PATH.as_posix())
        register = load_json(REGISTER_PATH)
        allowed_statuses = {
            "phase_12_technical_audit_remediation_closed",
            "phase_13b_post_merge_baseline_recorded",
        }
        allowed_slices = {
            "technical-audit-remediation-closed",
            "technical-audit-post-merge-baseline-recorded",
        }
        if register.get("status") not in allowed_statuses:
            errors.append(
                "blocker_register.status must be phase_12_technical_audit_remediation_closed or phase_13b_post_merge_baseline_recorded"
            )
        if register.get("active_slice") not in allowed_slices:
            errors.append(
                "blocker_register.active_slice must be technical-audit-remediation-closed or technical-audit-post-merge-baseline-recorded"
            )
        phase = register.get("phase_12_technical_audit_closure_authority")
        if not isinstance(phase, dict):
            errors.append("blocker_register.phase_12_technical_audit_closure_authority is required")
        else:
            if phase.get("technical_audit_remediation_closed") is not True:
                errors.append("phase_12_technical_audit_closure_authority.technical_audit_remediation_closed must be true")
            if phase.get("production_release_authorised") is not False:
                errors.append("phase_12_technical_audit_closure_authority.production_release_authorised must be false")
            if phase.get("authority_record") != record_path.as_posix():
                errors.append("phase_12_technical_audit_closure_authority.authority_record must match closure record path")

    legacy_diagnostics = pathlib.Path("docs/release-evidence/technical-audit/hosted-ci-merge-readiness")
    if legacy_diagnostics.exists():
        warnings.append(
            "legacy hosted-ci-merge-readiness diagnostics directory exists; keep it uncommitted unless deliberately recollected"
        )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "checked": checked,
        "technical_audit_remediation_closure_claimed": record.get("technical_audit_remediation_closure_claimed") is True,
        "technical_audit_remediation_closed": record.get("technical_audit_remediation_closed") is True,
        "technical_audit_release_readiness_claimed": record.get("technical_audit_release_readiness_claimed") is True,
        "production_release_authorised": record.get("production_release_authorised") is True,
        "deployment_authorised": record.get("deployment_authorised") is True,
        "release_tag_authorised": record.get("release_tag_authorised") is True,
        "live_learner_traffic_authorised": record.get("live_learner_traffic_authorised") is True,
        "runtime_kg_implementation_claimed": record.get("runtime_kg_implementation_claimed") is True,
        "source_commit": record.get("source_commit"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", default=str(DEFAULT_RECORD))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = verify_record(pathlib.Path(args.record))
    except AssertionError as exc:
        result = {
            "valid": False,
            "errors": [str(exc)],
            "warnings": [],
            "checked": [],
            "technical_audit_remediation_closure_claimed": False,
            "technical_audit_remediation_closed": False,
            "technical_audit_release_readiness_claimed": False,
            "production_release_authorised": False,
        }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid" if result["valid"] else "invalid")
        for warning in result["warnings"]:
            print(f"WARN: {warning}")
        for error in result["errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
