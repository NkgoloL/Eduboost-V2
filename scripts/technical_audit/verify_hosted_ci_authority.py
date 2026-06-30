#!/usr/bin/env python3
"""Verify TA Phase 09 hosted CI authority evidence.

Default mode requires a real completed/successful hosted CI run. Use
--allow-unclaimed only for the preparatory commit before GitHub Actions has run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

DEFAULT_RECORD = pathlib.Path(
    "docs/roadmap/execution/technical_audit_remediation/hosted_ci_authority_record.json"
)
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


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
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            expected, rel = line.split(maxsplit=1)
        except ValueError:
            errors.append(f"invalid SHA256SUMS line {idx}: {line!r}")
            continue
        rel = rel.strip()
        file_path = pathlib.Path(rel)
        if not file_path.exists():
            errors.append(f"SHA256SUMS references missing file: {rel}")
            continue
        actual = sha256_file(file_path)
        if actual != expected:
            errors.append(f"SHA mismatch for {rel}: expected {expected}, got {actual}")
    return errors


def verify_record(record: dict[str, Any], *, allow_unclaimed: bool) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if record.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if record.get("slice") != "TA-PHASE-09-HOSTED-CI-RUN-EVIDENCE":
        errors.append("slice must be TA-PHASE-09-HOSTED-CI-RUN-EVIDENCE")


    sha = record.get("head_sha")
    if not isinstance(sha, str) or not SHA_RE.match(sha):
        errors.append("head_sha must be a 40-character lowercase git SHA")

    provenance_fields = {
        "ci_run_sha": record.get("ci_run_sha"),
        "evidence_commit_sha": record.get("evidence_commit_sha"),
        "closure_commit_sha": record.get("closure_commit_sha"),
        "current_terminal_sha": record.get("current_terminal_sha"),
    }
    has_split_provenance = any(value is not None for value in provenance_fields.values())
    if has_split_provenance:
        for key, value in provenance_fields.items():
            if not isinstance(value, str) or not SHA_RE.match(value):
                errors.append(f"{key} must be a 40-character lowercase git SHA")

    if not isinstance(record.get("hosted_ci_run_claimed"), bool):
        errors.append("hosted_ci_run_claimed must be boolean")

    raw_files = record.get("raw_evidence_files") or []
    if not isinstance(raw_files, list):
        errors.append("raw_evidence_files must be a list")
        raw_files = []
    for raw in raw_files:
        if not isinstance(raw, str) or not pathlib.Path(raw).exists():
            errors.append(f"raw evidence file missing or invalid: {raw!r}")

    sums = record.get("sha256sums")
    if isinstance(sums, str):
        errors.extend(verify_sha256sums(pathlib.Path(sums)))
    else:
        errors.append("sha256sums must point to a SHA256SUMS file")

    if not record.get("hosted_ci_run_claimed"):
        if allow_unclaimed:
            if record.get("merge_readiness_authorised"):
                errors.append("merge_readiness_authorised cannot be true while hosted CI is unclaimed")
            warnings.append("Hosted CI run is formally unclaimed; preparatory verification only.")
            return len(errors) == 0, errors, warnings
        errors.append("hosted CI run is unclaimed; rerun without --allow-unclaimed only after real GitHub Actions evidence is captured")
        return False, errors, warnings

    required = [
        "repository",
        "branch",
        "head_sha",
        "workflow_name",
        "hosted_ci_run_id",
        "hosted_ci_run_url",
    ]
    for key in required:
        if record.get(key) in (None, ""):
            errors.append(f"{key} is required when hosted_ci_run_claimed is true")

    if record.get("hosted_ci_status") != "completed":
        errors.append("hosted_ci_status must be completed")
    if record.get("hosted_ci_conclusion") != "success":
        errors.append("hosted_ci_conclusion must be success")

    view_files = [p for p in raw_files if "gh_run_view_" in str(p)]
    if not view_files:
        errors.append("missing gh_run_view raw evidence file")
    else:
        view = load_json(pathlib.Path(view_files[0]))
        expected_run_sha = record.get("ci_run_sha") if has_split_provenance else record.get("head_sha")
        if view.get("headSha") != expected_run_sha:
            errors.append("run view headSha does not match hosted CI run provenance SHA")
        if view.get("status") != "completed":
            errors.append("run view status is not completed")
        if view.get("conclusion") != "success":
            errors.append("run view conclusion is not success")
        if str(view.get("databaseId")) != str(record.get("hosted_ci_run_id")):
            errors.append("run view databaseId does not match hosted_ci_run_id")

    if record.get("merge_readiness_authorised") and not record.get("branch_protection_claimed"):
        errors.append("merge readiness cannot be authorised without branch protection evidence")

    branch_protection_file = record.get("branch_protection_evidence")
    if record.get("branch_protection_claimed"):
        if not isinstance(branch_protection_file, str) or not pathlib.Path(branch_protection_file).exists():
            errors.append("branch_protection_claimed is true but evidence file is missing")
    elif record.get("merge_readiness_authorised"):
        errors.append("branch protection must be claimed before merge readiness is authorised")

    return len(errors) == 0, errors, warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", default=str(DEFAULT_RECORD))
    parser.add_argument("--allow-unclaimed", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    record_path = pathlib.Path(args.record)
    try:
        record = load_json(record_path)
        valid, errors, warnings = verify_record(record, allow_unclaimed=args.allow_unclaimed)
    except AssertionError as exc:
        valid, errors, warnings = False, [str(exc)], []

    result = {
        "valid": valid,
        "record": str(record_path),
        "hosted_ci_run_claimed": bool(record.get("hosted_ci_run_claimed")) if isinstance(locals().get("record"), dict) else False,
        "merge_readiness_authorised": bool(record.get("merge_readiness_authorised")) if isinstance(locals().get("record"), dict) else False,
        "errors": errors,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid:", valid)
        for warning in warnings:
            print("warning:", warning)
        for error in errors:
            print("error:", error, file=sys.stderr)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
