#!/usr/bin/env python3
"""Verify TA Phase 08 remote CI / branch-integration evidence bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVIDENCE_DIR = ROOT / "docs/release-evidence/technical-audit/remote-ci-branch-integration"

REQUIRED_RAW_JSON = [
    "remote_ci_branch_integration_verification.json",
    "backend_fast_gate_evidence_check.json",
    "frontend_tooling_authority_evidence_check.json",
    "ci_authority_workflow_evidence_check.json",
    "dependency_scan_enforcement_evidence_check.json",
    "e2e_playwright_authority_evidence_check.json",
    "openapi_frontend_contract_evidence_check.json",
    "git_state.json",
    "remote_ci_status.json",
    "branch_integration_summary.json",
]

PRIOR_CHECKS = [
    "backend_fast_gate_evidence_check.json",
    "frontend_tooling_authority_evidence_check.json",
    "ci_authority_workflow_evidence_check.json",
    "dependency_scan_enforcement_evidence_check.json",
    "e2e_playwright_authority_evidence_check.json",
    "openapi_frontend_contract_evidence_check.json",
]


def _load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.exists():
        errors.append(f"missing JSON evidence file: {path}")
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"malformed JSON evidence file {path.name}: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"JSON evidence file {path.name} must contain an object")
        return {}
    return data


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _verify_sha_manifest(raw_dir: Path, errors: list[str]) -> dict[str, Any]:
    manifest = raw_dir / "SHA256SUMS.txt"
    result = {"present": manifest.exists(), "checked": [], "mismatches": []}
    if not manifest.exists():
        errors.append("missing raw/SHA256SUMS.txt")
        return result
    for lineno, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            expected, rel = line.split(maxsplit=1)
        except ValueError:
            errors.append(f"invalid SHA256SUMS line {lineno}: {line!r}")
            continue
        rel = rel.strip().lstrip("*")
        if rel in {"SHA256SUMS.txt", "remote_ci_branch_integration_evidence_check.json"}:
            errors.append(f"self-mutating evidence file must not be listed in SHA256SUMS.txt: {rel}")
            continue
        target = raw_dir / rel
        if not target.exists():
            errors.append(f"SHA256SUMS references missing file: {rel}")
            continue
        actual = _sha256(target)
        item = {"file": rel, "expected": expected, "actual": actual, "match": expected == actual}
        result["checked"].append(item)
        if expected != actual:
            result["mismatches"].append(item)
            errors.append(f"raw/SHA256SUMS.txt digest mismatch for {rel}")
    return result


def verify(evidence_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    raw_dir = evidence_dir / "raw"
    if not evidence_dir.exists():
        errors.append(f"missing evidence directory: {evidence_dir}")
    if not raw_dir.exists():
        errors.append("missing raw evidence directory")

    index = evidence_dir / "evidence_index.md"
    if not index.exists():
        errors.append("missing evidence_index.md")

    loaded: dict[str, dict[str, Any]] = {}
    if raw_dir.exists():
        for filename in REQUIRED_RAW_JSON:
            loaded[filename] = _load_json(raw_dir / filename, errors)
        sha_result = _verify_sha_manifest(raw_dir, errors)
    else:
        sha_result = {"present": False, "checked": [], "mismatches": []}

    authority = loaded.get("remote_ci_branch_integration_verification.json", {})
    if authority and authority.get("valid") is not True:
        errors.append("remote CI branch integration authority verifier did not pass")

    for filename in PRIOR_CHECKS:
        data = loaded.get(filename, {})
        if data.get("valid") is not True:
            errors.append(f"prior evidence verifier did not pass: {filename}")

    remote_status = loaded.get("remote_ci_status.json", {})
    remote_ci_run_claimed = remote_status.get("remote_ci_run_claimed")
    if remote_ci_run_claimed is True:
        conclusion = remote_status.get("conclusion")
        head_sha = remote_status.get("head_sha")
        workflow = remote_status.get("workflow")
        if conclusion != "success":
            errors.append("remote CI run is claimed but conclusion is not success")
        if not isinstance(head_sha, str) or len(head_sha) < 7:
            errors.append("remote CI run is claimed but head_sha is missing/invalid")
        if not workflow:
            errors.append("remote CI run is claimed but workflow name/id is missing")
    elif remote_ci_run_claimed is False:
        warnings.append("remote hosted CI success is not claimed by this evidence bundle")
    else:
        errors.append("remote_ci_status.remote_ci_run_claimed must be boolean")

    summary = loaded.get("branch_integration_summary.json", {})
    if summary:
        if summary.get("branch_integration_authority_result") != "valid":
            errors.append("branch integration summary must record valid result")
        if summary.get("release_readiness_claimed") is not False:
            errors.append("release readiness must not be claimed in Phase 08 evidence")
        if summary.get("runtime_kg_implementation_claimed") is not False:
            errors.append("runtime KG implementation must not be claimed in Phase 08 evidence")

    git_state = loaded.get("git_state.json", {})
    if git_state:
        if git_state.get("working_tree_clean") is not True:
            errors.append("Phase 08 evidence must be collected from a clean working tree")
        if not git_state.get("head"):
            errors.append("git_state.head is missing")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "evidence_dir": str(evidence_dir),
        "sha256sums": sha_result,
        "remote_ci_run_claimed": remote_status.get("remote_ci_run_claimed"),
        "branch_integration_authority_result": summary.get("branch_integration_authority_result"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify(args.evidence_dir)
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
