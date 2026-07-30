#!/usr/bin/env python3
"""Capture final technical-audit remediation closure evidence.

This gate closes only the controlled technical-audit remediation stream. It is
fail-closed and requires an explicit closure-owner claim plus valid Phase 11
technical-audit release-readiness evidence. It does not authorise production
launch, release tagging, deployment, live learner traffic, or runtime KG work.
"""

from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
from scripts._subprocess import run
import sys
from typing import Any

REGISTER_PATH = pathlib.Path("docs/roadmap/execution/technical_audit_remediation/blocker_register.json")
HOSTED_RECORD_PATH = pathlib.Path("docs/roadmap/execution/technical_audit_remediation/hosted_ci_authority_record.json")
RELEASE_RECORD_PATH = pathlib.Path(
    "docs/roadmap/execution/technical_audit_remediation/technical_audit_release_readiness_record.json"
)
CLOSURE_RECORD_PATH = pathlib.Path(
    "docs/roadmap/execution/technical_audit_remediation/technical_audit_closure_record.json"
)
EVIDENCE_DIR = pathlib.Path("docs/release-evidence/technical-audit/phase-12-closure")
RAW_DIR = EVIDENCE_DIR / "raw"
RELEASE_VERIFIER = pathlib.Path("scripts/technical_audit/verify_release_readiness_authority.py")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(cmd, check=check, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def git_value(args: list[str], default: str | None = None) -> str | None:
    try:
        return run(["git", *args]).stdout.strip()
    except Exception:
        return default


def git_is_ancestor_or_equal(candidate: str, descendant: str) -> bool:
    if candidate == descendant:
        return True
    try:
        result = run(
            ["git", "merge-base", "--is-ancestor", candidate, descendant],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def tracked_worktree_clean() -> bool:
    diff = run(["git", "diff", "--quiet"], text=True)
    staged = run(["git", "diff", "--cached", "--quiet"], text=True)
    return diff.returncode == 0 and staged.returncode == 0


def untracked_files() -> list[str]:
    try:
        out = run(["git", "ls-files", "--others", "--exclude-standard"]).stdout
    except Exception:
        return []
    return [line for line in out.splitlines() if line.strip()]


def load_json(path: pathlib.Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON file: {path}: {exc}") from exc


def write_json(path: pathlib.Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_sha256sums(files: list[pathlib.Path], sums_path: pathlib.Path) -> None:
    unique = sorted({p for p in files if p.exists()}, key=lambda p: p.as_posix())
    lines = [f"{sha256_file(path)}  {path.as_posix()}" for path in unique]
    sums_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def run_release_verifier() -> dict[str, Any]:
    if not RELEASE_VERIFIER.exists():
        return {
            "valid": False,
            "errors": [f"missing release-readiness verifier: {RELEASE_VERIFIER}"],
            "warnings": [],
            "checked": [],
        }
    completed = run([sys.executable, str(RELEASE_VERIFIER), "--json"], check=False)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {
            "valid": False,
            "errors": ["release-readiness verifier did not return JSON"],
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    payload.setdefault("command", f"{sys.executable} {RELEASE_VERIFIER} --json")
    payload.setdefault("returncode", completed.returncode)
    return payload


def evaluate_closure(
    *,
    claim: bool,
    closure_owner: str | None,
    source_commit: str | None,
    tracked_clean: bool,
    register: dict[str, Any],
    hosted_record: dict[str, Any],
    release_record: dict[str, Any],
    release_verification: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not claim:
        errors.append("technical-audit remediation closure is not claimed; rerun with --claim-closure")
    if not closure_owner or not closure_owner.strip():
        errors.append("closure_owner is required")
    if not source_commit or not SHA_RE.match(source_commit):
        errors.append("source_commit must be a 40-character lowercase git SHA")
    if tracked_clean is not True:
        errors.append("tracked worktree must be clean before closure capture")

    if release_verification.get("valid") is not True:
        errors.append("release-readiness verifier must be valid")
    if release_verification.get("release_readiness_claimed") is not True:
        errors.append("release-readiness verifier must report release_readiness_claimed=true")
    if release_verification.get("technical_audit_release_readiness_claimed") is not True:
        errors.append("release-readiness verifier must report technical_audit_release_readiness_claimed=true")
    if release_verification.get("production_release_authorised") is not False:
        errors.append("release-readiness verifier must report production_release_authorised=false")
    if release_verification.get("merge_readiness_authorised") is not True:
        errors.append("release-readiness verifier must report merge_readiness_authorised=true")

    for field in ["hosted_ci_run_claimed", "branch_protection_claimed", "merge_readiness_authorised"]:
        if hosted_record.get(field) is not True:
            errors.append(f"hosted authority record must have {field}=true")
    if hosted_record.get("production_release_authorised") is True:
        errors.append("hosted authority record must not authorise production release")
    if hosted_record.get("runtime_kg_implementation_claimed") is True:
        errors.append("hosted authority record must not claim runtime KG implementation")

    required_release_true = [
        "release_readiness_claimed",
        "technical_audit_release_readiness_claimed",
        "required_blockers_closed",
        "hosted_ci_run_claimed",
        "branch_protection_claimed",
        "merge_readiness_authorised",
    ]
    for field in required_release_true:
        if release_record.get(field) is not True:
            errors.append(f"release-readiness record must have {field}=true")
    required_release_false = [
        "production_release_authorised",
        "runtime_kg_implementation_claimed",
        "full_backend_backed_e2e_claimed",
    ]
    for field in required_release_false:
        if release_record.get(field) is not False:
            errors.append(f"release-readiness record must have {field}=false")
    if release_record.get("status") != "technical_audit_release_readiness_authorised":
        errors.append("release-readiness record status must be technical_audit_release_readiness_authorised")
    release_sha = release_record.get("source_commit")
    if not isinstance(release_sha, str) or not SHA_RE.match(release_sha):
        errors.append("release-readiness record source_commit is missing or invalid")
    elif source_commit and not git_is_ancestor_or_equal(release_sha, source_commit):
        errors.append(
            f"release-readiness record source_commit ({release_sha[:12]}) must be an ancestor of current HEAD ({source_commit[:12]})"
        )

    allowed_register_states = {
        "phase_11_technical_audit_release_readiness_closed",
        "phase_12_technical_audit_closure_authority_ready",
        "phase_12_technical_audit_remediation_closed",
    }
    if register.get("status") not in allowed_register_states:
        errors.append(f"blocker register status is not an allowed closure precursor: {register.get('status')}")
    phase_11 = register.get("phase_11_release_readiness_authority")
    if not isinstance(phase_11, dict) or phase_11.get("technical_audit_release_readiness_claimed") is not True:
        errors.append("blocker register phase_11_release_readiness_authority must claim technical-audit release readiness")
    if register.get("active_slice") == "technical-audit-remediation-closed":
        warnings.append("blocker register already reports technical-audit remediation closed")

    valid = not errors
    return {
        "schema_version": 1,
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
        "technical_audit_remediation_closure_claimed": bool(claim and valid),
        "technical_audit_remediation_closed": bool(claim and valid),
        "technical_audit_release_readiness_claimed": release_record.get("technical_audit_release_readiness_claimed") is True,
        "release_readiness_claimed": release_record.get("release_readiness_claimed") is True,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "live_learner_traffic_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "full_backend_backed_e2e_claimed": False,
        "source_commit": source_commit,
        "closure_owner": closure_owner.strip() if closure_owner else None,
        "scope": "technical-audit remediation stream closure only; not production launch",
    }


def write_evidence_index(result: dict[str, Any], git_state: dict[str, Any], evidence_files: list[pathlib.Path]) -> pathlib.Path:
    status = (
        "Technical-audit remediation closure authorised"
        if result.get("technical_audit_remediation_closed")
        else "Technical-audit remediation closure not claimed"
    )
    lines = [
        "# TA Phase 12 — Technical-Audit Remediation Closure Evidence",
        "",
        f"Status: {status}",
        f"Captured at UTC: {utc_now()}",
        f"Source commit: `{git_state.get('head_sha')}`",
        f"Branch: `{git_state.get('branch')}`",
        f"Closure owner: `{result.get('closure_owner') or 'unclaimed'}`",
        "",
        "## Claims",
        "",
        f"- Technical-audit remediation closed: {str(result.get('technical_audit_remediation_closed')).lower()}",
        f"- Technical-audit release readiness claimed: {str(result.get('technical_audit_release_readiness_claimed')).lower()}",
        f"- Production release authorised: {str(result.get('production_release_authorised')).lower()}",
        f"- Deployment authorised: {str(result.get('deployment_authorised')).lower()}",
        f"- Release tag authorised: {str(result.get('release_tag_authorised')).lower()}",
        f"- Live learner traffic authorised: {str(result.get('live_learner_traffic_authorised')).lower()}",
        f"- Runtime KG implementation claimed: {str(result.get('runtime_kg_implementation_claimed')).lower()}",
        "",
        "## Evidence files",
        "",
    ]
    for path in evidence_files:
        lines.append(f"- `{path.as_posix()}`")
    lines.extend([
        "",
        "## Boundary",
        "",
        "This evidence closes only the controlled technical-audit remediation stream. It does not deploy the product, create a production release tag, authorise live learner traffic, change POPIA processing scope, or implement runtime knowledge graphs.",
        "",
    ])
    index = EVIDENCE_DIR / "evidence_index.md"
    index.write_text("\n".join(lines), encoding="utf-8")
    return index


def update_register(register: dict[str, Any], result: dict[str, Any], record_path: pathlib.Path, evidence_dir: pathlib.Path) -> dict[str, Any]:
    phase = register.setdefault("phase_12_technical_audit_closure_authority", {})
    phase.update(
        {
            "id": "TA-CLOSURE-001",
            "title": "Technical-audit remediation closure authority",
            "status": "technical_audit_remediation_closed" if result.get("technical_audit_remediation_closed") else "closure_unclaimed",
            "authority_record": record_path.as_posix(),
            "evidence_path": evidence_dir.as_posix(),
            "technical_audit_remediation_closure_claimed": result.get("technical_audit_remediation_closure_claimed") is True,
            "technical_audit_remediation_closed": result.get("technical_audit_remediation_closed") is True,
            "technical_audit_release_readiness_claimed": result.get("technical_audit_release_readiness_claimed") is True,
            "production_release_authorised": False,
            "deployment_authorised": False,
            "release_tag_authorised": False,
            "live_learner_traffic_authorised": False,
            "runtime_kg_implementation_claimed": False,
            "closure_owner": result.get("closure_owner"),
            "updated_at_utc": utc_now(),
        }
    )
    if result.get("technical_audit_remediation_closed"):
        register["active_slice"] = "technical-audit-remediation-closed"
        register["status"] = "phase_12_technical_audit_remediation_closed"
    else:
        register["active_slice"] = "technical-audit-remediation-closure-authority"
        register["status"] = "phase_12_technical_audit_closure_authority_ready"
    return register


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim-closure", action="store_true", help="explicitly claim scoped technical-audit remediation closure")
    parser.add_argument("--closure-owner", help="name of the closure owner making the claim")
    parser.add_argument("--evidence-dir", default=str(EVIDENCE_DIR))
    parser.add_argument("--record", default=str(CLOSURE_RECORD_PATH))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    global EVIDENCE_DIR, RAW_DIR
    EVIDENCE_DIR = pathlib.Path(args.evidence_dir)
    RAW_DIR = EVIDENCE_DIR / "raw"
    record_path = pathlib.Path(args.record)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    source_commit = git_value(["rev-parse", "HEAD"])
    branch = git_value(["branch", "--show-current"], default="unknown")
    tracked_clean = tracked_worktree_clean()
    untracked = untracked_files()

    git_state = {
        "schema_version": 1,
        "branch": branch,
        "head_sha": source_commit,
        "tracked_worktree_clean_before_capture": tracked_clean,
        "untracked_files_present": bool(untracked),
        "untracked_files_sample": untracked[:20],
        "captured_at_utc": utc_now(),
    }
    register = load_json(REGISTER_PATH)
    hosted_record = load_json(HOSTED_RECORD_PATH)
    release_record = load_json(RELEASE_RECORD_PATH)
    release_verification = run_release_verifier()
    result = evaluate_closure(
        claim=args.claim_closure,
        closure_owner=args.closure_owner,
        source_commit=source_commit,
        tracked_clean=tracked_clean,
        register=register,
        hosted_record=hosted_record,
        release_record=release_record,
        release_verification=release_verification,
    )

    raw_files: list[pathlib.Path] = []
    payloads = {
        RAW_DIR / "git_state.json": git_state,
        RAW_DIR / "blocker_register_snapshot.json": register,
        RAW_DIR / "hosted_ci_authority_record_snapshot.json": hosted_record,
        RAW_DIR / "release_readiness_record_snapshot.json": release_record,
        RAW_DIR / "release_readiness_verification.json": release_verification,
        RAW_DIR / "technical_audit_closure_result.json": result,
    }
    for path, payload in payloads.items():
        write_json(path, payload)
        raw_files.append(path)

    index = write_evidence_index(result, git_state, raw_files)
    index_hash = EVIDENCE_DIR / "evidence_index.sha256"
    index_hash.write_text(f"{sha256_file(index)}  {index.as_posix()}\n", encoding="utf-8")
    sums = EVIDENCE_DIR / "SHA256SUMS.txt"
    write_sha256sums([*raw_files, index, index_hash], sums)

    record = {
        "schema_version": 1,
        "slice": "TA-PHASE-12-TECHNICAL-AUDIT-REMEDIATION-CLOSURE",
        "status": "technical_audit_remediation_closed" if result.get("technical_audit_remediation_closed") else "closure_unclaimed",
        "repository": hosted_record.get("repository"),
        "branch": branch,
        "source_commit": source_commit,
        "closure_owner": result.get("closure_owner"),
        "closure_decision": "authorised" if result.get("technical_audit_remediation_closed") else "unclaimed",
        "claimed_at_utc": utc_now() if result.get("technical_audit_remediation_closed") else None,
        "technical_audit_remediation_closure_claimed": result.get("technical_audit_remediation_closure_claimed") is True,
        "technical_audit_remediation_closed": result.get("technical_audit_remediation_closed") is True,
        "technical_audit_release_readiness_claimed": result.get("technical_audit_release_readiness_claimed") is True,
        "release_readiness_claimed": result.get("release_readiness_claimed") is True,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "live_learner_traffic_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "full_backend_backed_e2e_claimed": False,
        "evidence_dir": EVIDENCE_DIR.as_posix(),
        "evidence_index": index.as_posix(),
        "sha256sums": sums.as_posix(),
        "constraints": [
            "Closure is scoped to the technical-audit remediation stream only.",
            "Production launch, release tagging, deployment, and live learner traffic remain out of scope.",
            "Runtime knowledge-graph implementation remains out of scope.",
            "The closure claim requires explicit --claim-closure and a closure owner.",
            "Phase 11 technical-audit release readiness must verify valid before closure.",
        ],
        "created_at_utc": utc_now(),
        "updated_at_utc": utc_now(),
    }
    write_json(record_path, record)
    update_register(register, result, record_path, EVIDENCE_DIR)
    write_json(REGISTER_PATH, register)

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

