#!/usr/bin/env python3
"""Verify TA Phase 09 hosted-CI / merge-readiness evidence.

A valid Phase 09 bundle requires a real hosted CI success artifact. The verifier
fails closed when remote CI is not claimed, has a non-success conclusion, or is
for a different head SHA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REQUIRED_RAW_JSON = [
    "branch_state.json",
    "prior_gate_evidence_summary.json",
    "hosted_ci_status.json",
    "merge_readiness_result.json",
]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _verify_sha_manifest(raw_dir: Path) -> list[str]:
    errors: list[str] = []
    manifest = raw_dir / "SHA256SUMS.txt"
    if not manifest.exists():
        return ["raw/SHA256SUMS.txt missing"]
    for line_no, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            expected, rel = line.split(maxsplit=1)
        except ValueError:
            errors.append(f"raw/SHA256SUMS.txt line {line_no} is malformed")
            continue
        rel = rel.strip().lstrip("*")
        if Path(rel).name == "SHA256SUMS.txt":
            errors.append("raw/SHA256SUMS.txt must not include itself")
            continue
        target = raw_dir / rel
        if not target.exists():
            errors.append(f"raw/SHA256SUMS.txt references missing file: {rel}")
            continue
        actual = _sha256(target)
        if actual != expected:
            errors.append(f"raw/SHA256SUMS.txt digest mismatch for {rel}")
    return errors


def verify_evidence_dir(evidence_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []
    raw_dir = evidence_dir / "raw"

    if not evidence_dir.exists():
        return {"valid": False, "errors": [f"evidence dir missing: {evidence_dir}"], "warnings": [], "checked": []}
    if not raw_dir.exists():
        errors.append("raw evidence directory missing")
    else:
        checked.append("raw")

    docs = ["evidence_index.md", "evidence_index.sha256"]
    for name in docs:
        path = evidence_dir / name
        checked.append(name)
        if not path.exists():
            errors.append(f"{name} missing")

    evidence_index = evidence_dir / "evidence_index.md"
    evidence_hash = evidence_dir / "evidence_index.sha256"
    if evidence_index.exists() and evidence_hash.exists():
        expected = evidence_hash.read_text(encoding="utf-8").split()[0].strip()
        actual = _sha256(evidence_index)
        if expected != actual:
            errors.append("evidence_index.sha256 mismatch")

    raw: dict[str, Any] = {}
    if raw_dir.exists():
        errors.extend(_verify_sha_manifest(raw_dir))
        for name in REQUIRED_RAW_JSON:
            path = raw_dir / name
            checked.append(f"raw/{name}")
            if not path.exists():
                errors.append(f"raw/{name} missing")
                continue
            try:
                raw[name] = _load_json(path)
            except Exception as exc:
                errors.append(f"raw/{name} is not valid JSON: {exc}")

    branch_state = raw.get("branch_state.json") or {}
    ci_status = raw.get("hosted_ci_status.json") or {}
    prior = raw.get("prior_gate_evidence_summary.json") or {}
    merge = raw.get("merge_readiness_result.json") or {}

    source_commit = branch_state.get("head_sha")
    if not source_commit or not isinstance(source_commit, str):
        errors.append("branch_state.head_sha missing")
    if branch_state.get("clean_worktree_before_collection") is not True:
        errors.append("branch_state.clean_worktree_before_collection must be true")

    if not isinstance(prior.get("checks"), dict):
        errors.append("prior_gate_evidence_summary.checks missing")
    else:
        failed_prior = [name for name, item in prior["checks"].items() if not isinstance(item, dict) or item.get("valid") is not True]
        if failed_prior:
            errors.append(f"prior gate evidence checks are not all valid: {failed_prior}")

    if ci_status.get("remote_ci_run_claimed") is not True:
        errors.append("hosted_ci_status.remote_ci_run_claimed must be true for Phase 09 closure")
    if ci_status.get("conclusion") != "success":
        errors.append("hosted_ci_status.conclusion must be success")
    if ci_status.get("head_sha") != source_commit:
        errors.append("hosted_ci_status.head_sha must match branch_state.head_sha")
    if not ci_status.get("workflow"):
        errors.append("hosted_ci_status.workflow is required")
    if not (ci_status.get("run_id") or ci_status.get("run_url") or ci_status.get("html_url")):
        errors.append("hosted_ci_status must include run_id, run_url, or html_url")

    if merge.get("valid") is not True:
        errors.append("merge_readiness_result.valid must be true")
    if merge.get("release_readiness_claimed") is not False:
        errors.append("merge_readiness_result.release_readiness_claimed must be false")
    if merge.get("runtime_kg_implementation_claimed") is not False:
        errors.append("merge_readiness_result.runtime_kg_implementation_claimed must be false")
    if merge.get("remote_ci_run_claimed") is not True:
        errors.append("merge_readiness_result.remote_ci_run_claimed must be true")

    index_text = evidence_index.read_text(encoding="utf-8") if evidence_index.exists() else ""
    if "Hosted CI merge-readiness passed" not in index_text:
        errors.append("evidence_index.md must record Hosted CI merge-readiness passed")
    if "Release readiness claimed: false" not in index_text:
        errors.append("evidence_index.md must explicitly avoid release-readiness claim")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "checked": checked,
        "source_commit": source_commit,
        "remote_ci_run_claimed": ci_status.get("remote_ci_run_claimed"),
        "remote_ci_conclusion": ci_status.get("conclusion"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify_evidence_dir(Path(args.evidence_dir))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid" if result["valid"] else "invalid")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARN: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
