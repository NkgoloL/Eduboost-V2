#!/usr/bin/env python3
"""Verify technical-audit release-readiness authority evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

DEFAULT_RECORD = pathlib.Path(
    "docs/roadmap/execution/technical_audit_remediation/technical_audit_release_readiness_record.json"
)
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_RAW_FILES = [
    "raw/git_state.json",
    "raw/blocker_register_snapshot.json",
    "raw/hosted_ci_authority_record_snapshot.json",
    "raw/merge_readiness_verification.json",
    "raw/required_blocker_summary.json",
    "raw/release_readiness_result.json",
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
        raise AssertionError("release-readiness record must contain a JSON object")
    checked.append(record_path.as_posix())

    if record.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if record.get("slice") != "TA-PHASE-11-TECHNICAL-AUDIT-RELEASE-READINESS":
        errors.append("slice must be TA-PHASE-11-TECHNICAL-AUDIT-RELEASE-READINESS")
    if record.get("status") != "technical_audit_release_readiness_authorised":
        errors.append("status must be technical_audit_release_readiness_authorised")
    if record.get("release_readiness_claimed") is not True:
        errors.append("release_readiness_claimed must be true")
    if record.get("technical_audit_release_readiness_claimed") is not True:
        errors.append("technical_audit_release_readiness_claimed must be true")
    if record.get("production_release_authorised") is not False:
        errors.append("production_release_authorised must remain false")
    if record.get("runtime_kg_implementation_claimed") is not False:
        errors.append("runtime_kg_implementation_claimed must remain false")
    if record.get("full_backend_backed_e2e_claimed") is not False:
        errors.append("full_backend_backed_e2e_claimed must remain false")
    if record.get("release_decision") != "authorised":
        errors.append("release_decision must be authorised")
    if not isinstance(record.get("release_owner"), str) or not record["release_owner"].strip():
        errors.append("release_owner is required")
    if not isinstance(record.get("source_commit"), str) or not SHA_RE.match(record["source_commit"]):
        errors.append("source_commit must be a 40-character lowercase git SHA")
    if record.get("hosted_ci_run_claimed") is not True:
        errors.append("hosted_ci_run_claimed must be true")
    if record.get("branch_protection_claimed") is not True:
        errors.append("branch_protection_claimed must be true")
    if record.get("merge_readiness_authorised") is not True:
        errors.append("merge_readiness_authorised must be true")
    if record.get("required_blockers_closed") is not True:
        errors.append("required_blockers_closed must be true")

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

    merge = raw_payloads.get("raw/merge_readiness_verification.json") or {}
    if merge:
        if merge.get("valid") is not True:
            errors.append("merge_readiness_verification.valid must be true")
        if merge.get("hosted_ci_run_claimed") is not True:
            errors.append("merge_readiness_verification.hosted_ci_run_claimed must be true")
        if merge.get("branch_protection_claimed") is not True:
            errors.append("merge_readiness_verification.branch_protection_claimed must be true")
        if merge.get("merge_readiness_authorised") is not True:
            errors.append("merge_readiness_verification.merge_readiness_authorised must be true")

    blocker_summary = raw_payloads.get("raw/required_blocker_summary.json") or {}
    if blocker_summary:
        if blocker_summary.get("required_blockers_closed") is not True:
            errors.append("required_blocker_summary.required_blockers_closed must be true")
        failed = blocker_summary.get("failed_blockers")
        if failed:
            errors.append(f"required_blocker_summary has failed blockers: {failed}")

    result = raw_payloads.get("raw/release_readiness_result.json") or {}
    if result:
        if result.get("valid") is not True:
            errors.append("release_readiness_result.valid must be true")
        if result.get("release_readiness_claimed") is not True:
            errors.append("release_readiness_result.release_readiness_claimed must be true")
        if result.get("production_release_authorised") is not False:
            errors.append("release_readiness_result.production_release_authorised must be false")
        if result.get("runtime_kg_implementation_claimed") is not False:
            errors.append("release_readiness_result.runtime_kg_implementation_claimed must be false")

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
                "Technical-audit release readiness authorised",
                "Production release authorised: false",
                "Runtime KG implementation claimed: false",
            ]:
                if phrase not in text:
                    errors.append(f"evidence_index.md missing required phrase: {phrase}")

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
        "release_readiness_claimed": record.get("release_readiness_claimed") is True,
        "technical_audit_release_readiness_claimed": record.get("technical_audit_release_readiness_claimed") is True,
        "production_release_authorised": record.get("production_release_authorised") is True,
        "hosted_ci_run_claimed": record.get("hosted_ci_run_claimed") is True,
        "branch_protection_claimed": record.get("branch_protection_claimed") is True,
        "merge_readiness_authorised": record.get("merge_readiness_authorised") is True,
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
            "release_readiness_claimed": False,
            "technical_audit_release_readiness_claimed": False,
            "production_release_authorised": False,
            "hosted_ci_run_claimed": False,
            "branch_protection_claimed": False,
            "merge_readiness_authorised": False,
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

