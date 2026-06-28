#!/usr/bin/env python3
"""Verify final hosted-CI + branch-protection merge-readiness authority."""

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
        target = pathlib.Path(rel.strip())
        if not target.exists():
            errors.append(f"SHA256SUMS references missing file: {target}")
            continue
        actual = sha256_file(target)
        if expected != actual:
            errors.append(f"SHA mismatch for {target}: expected {expected}, got {actual}")
    return errors


def verify_record(record_path: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []

    record = load_json(record_path)
    if not isinstance(record, dict):
        raise AssertionError("authority record must contain a JSON object")
    checked.append(record_path.as_posix())

    if record.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if record.get("slice") != "TA-PHASE-09-HOSTED-CI-RUN-EVIDENCE":
        errors.append("slice must be TA-PHASE-09-HOSTED-CI-RUN-EVIDENCE")
    if record.get("hosted_ci_run_claimed") is not True:
        errors.append("hosted_ci_run_claimed must be true")
    if record.get("hosted_ci_status") != "completed":
        errors.append("hosted_ci_status must be completed")
    if record.get("hosted_ci_conclusion") != "success":
        errors.append("hosted_ci_conclusion must be success")
    if not isinstance(record.get("head_sha"), str) or not SHA_RE.match(record["head_sha"]):
        errors.append("head_sha must be a 40-character lowercase git SHA")
    if record.get("branch_protection_claimed") is not True:
        errors.append("branch_protection_claimed must be true")
    if record.get("merge_readiness_authorised") is not True:
        errors.append("merge_readiness_authorised must be true")

    sums = record.get("sha256sums")
    if isinstance(sums, str):
        checked.append(sums)
        errors.extend(verify_sha256sums(pathlib.Path(sums)))
    else:
        errors.append("sha256sums must point to a SHA256SUMS file")

    evidence_path = record.get("branch_protection_evidence")
    if not isinstance(evidence_path, str):
        errors.append("branch_protection_evidence must point to a JSON evidence file")
        branch_result = {}
    else:
        evidence_file = pathlib.Path(evidence_path)
        checked.append(evidence_file.as_posix())
        if not evidence_file.exists():
            errors.append(f"branch_protection_evidence missing: {evidence_path}")
            branch_result = {}
        else:
            branch_result = load_json(evidence_file)

    if isinstance(branch_result, dict) and branch_result:
        if branch_result.get("schema_version") != 1:
            errors.append("branch_protection_result.schema_version must be 1")
        if branch_result.get("branch_protection_claimed") is not True:
            errors.append("branch_protection_result.branch_protection_claimed must be true")
        if branch_result.get("release_readiness_claimed") is not False:
            errors.append("branch_protection_result must not claim release readiness")
        if branch_result.get("runtime_kg_implementation_claimed") is not False:
            errors.append("branch_protection_result must not claim runtime KG implementation")
        if branch_result.get("target_branch") != record.get("target_branch"):
            errors.append("branch_protection_result target_branch must match authority record")
        if branch_result.get("mechanism") not in {"classic_branch_protection", "active_branch_rulesets", "classic_and_rulesets"}:
            errors.append("branch protection mechanism must be classic protection and/or active rulesets")
    else:
        errors.append("branch protection result payload is missing or invalid")

    if record.get("release_readiness_claimed") is True:
        errors.append("authority record must not claim release readiness")
    if record.get("runtime_kg_implementation_claimed") is True:
        errors.append("authority record must not claim runtime KG implementation")

    stale_diagnostics = pathlib.Path("docs/release-evidence/technical-audit/hosted-ci-merge-readiness")
    if stale_diagnostics.exists():
        warnings.append(
            "legacy hosted-ci-merge-readiness diagnostics directory exists; keep it uncommitted unless deliberately recollected"
        )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "checked": checked,
        "hosted_ci_run_claimed": record.get("hosted_ci_run_claimed") is True,
        "branch_protection_claimed": record.get("branch_protection_claimed") is True,
        "merge_readiness_authorised": record.get("merge_readiness_authorised") is True,
        "branch_protection_mechanism": record.get("branch_protection_mechanism"),
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
