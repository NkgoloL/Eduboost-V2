#!/usr/bin/env python3
"""Capture Phase 20 controlled beta launch-activation evidence.

This is the first runtime-readiness gate that may explicitly authorise a
controlled beta launch and live learner traffic for a named, bounded cohort.
It still does not authorise production release, public beta, release tagging,
production deployment, or runtime KG implementation.
"""

from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import argparse
import hashlib
import json
import pathlib
from scripts._subprocess import run
from datetime import datetime, timezone
from typing import Any, Mapping

RECORD_PATH = pathlib.Path("docs/roadmap/execution/runtime_readiness/phase_20_controlled_beta_launch_activation_record.json")
EVIDENCE_DIR = pathlib.Path("docs/release-evidence/runtime-readiness/phase-20-controlled-beta-launch-activation")
PHASE19_VERIFY = pathlib.Path("scripts/runtime_readiness/verify_controlled_beta_activation_preflight.py")
DEFAULT_GO_NO_GO = pathlib.Path("docs/operations/beta/controlled_beta_go_no_go_decision.md")
DEFAULT_COHORT_MANIFEST = pathlib.Path("docs/operations/beta/controlled_beta_candidate_cohort_manifest.json")
DEFAULT_CONSENT_ATTESTATION = pathlib.Path("docs/operations/beta/controlled_beta_consent_pack_attestation.md")
DEFAULT_TRAFFIC_WINDOW = pathlib.Path("docs/operations/beta/controlled_beta_live_traffic_window.json")

FALSE_BOUNDARY_FIELDS: tuple[str, ...] = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "runtime_kg_implementation_claimed",
)
TRUE_ACTIVATION_FIELDS: tuple[str, ...] = (
    "controlled_beta_launch_authorised",
    "live_learner_traffic_authorised",
    "learner_data_migration_authorised",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: pathlib.Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_command(args: list[str]) -> dict[str, Any]:
    proc = run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    payload: dict[str, Any] | None = None
    if proc.stdout.strip():
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            payload = None
    return {
        "args": args,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "valid": proc.returncode == 0 and (payload or {}).get("valid") is True,
        "payload": payload,
    }


def git_state(target_branch: str) -> dict[str, Any]:
    head = run(["git", "rev-parse", "HEAD"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False).stdout.strip()
    branch = run(["git", "branch", "--show-current"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False).stdout.strip()
    status = run(["git", "status", "--short"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    remote = run(["git", "rev-parse", f"origin/{target_branch}"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    remote_sha = remote.stdout.strip() if remote.returncode == 0 else ""
    return {
        "branch": branch,
        "head_sha": head,
        "target_branch": target_branch,
        "remote_target_sha": remote_sha,
        "head_matches_remote_target": bool(head and remote_sha and head == remote_sha),
        "git_status_short": status.stdout.splitlines(),
        "tracked_worktree_clean_before_capture": status.stdout.strip() == "",
    }


def boundary_payload(*, authorise_launch: bool, authorise_live_traffic: bool, authorise_migration: bool) -> dict[str, Any]:
    return {
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "controlled_beta_launch_authorised": authorise_launch,
        "live_learner_traffic_authorised": authorise_live_traffic,
        "learner_data_migration_authorised": authorise_migration,
        "runtime_kg_implementation_claimed": False,
        "scope": "controlled_beta_launch_activation_only",
    }


def _text_markers(path: pathlib.Path, markers: tuple[str, ...], errors: list[str]) -> dict[str, Any]:
    item: dict[str, Any] = {"path": path.as_posix(), "exists": path.exists()}
    if not path.exists():
        errors.append(f"missing activation document: {path}")
        return item
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    item.update({"sha256": sha256_file(path), "bytes": path.stat().st_size})
    for marker in markers:
        if marker.lower() not in lower:
            errors.append(f"{path} missing marker: {marker}")
    return item


def _validate_cohort_manifest(path: pathlib.Path, errors: list[str]) -> dict[str, Any]:
    item: dict[str, Any] = {"path": path.as_posix(), "exists": path.exists()}
    if not path.exists():
        errors.append(f"missing cohort manifest: {path}")
        return item
    item.update({"sha256": sha256_file(path), "bytes": path.stat().st_size})
    try:
        payload = load_json(path)
    except Exception as exc:  # pragma: no cover - defensive parse reporting
        errors.append(f"invalid cohort manifest JSON {path}: {exc}")
        return item
    item["payload"] = payload
    if not isinstance(payload, dict):
        errors.append("cohort manifest must be a JSON object")
        return item
    if not payload.get("cohort_id"):
        errors.append("cohort manifest must include cohort_id")
    if payload.get("public_beta_authorised") is not False:
        errors.append("cohort manifest public_beta_authorised must be false")
    if payload.get("controlled_beta_launch_authorised") is not True:
        errors.append("cohort manifest controlled_beta_launch_authorised must be true")
    if payload.get("live_learner_traffic_authorised") is not True:
        errors.append("cohort manifest live_learner_traffic_authorised must be true")
    if payload.get("guardian_consent_required") is not True:
        errors.append("cohort manifest guardian_consent_required must be true")
    learner_count = payload.get("learner_count")
    if not isinstance(learner_count, int) or learner_count <= 0:
        errors.append("cohort manifest learner_count must be a positive integer")
    if isinstance(learner_count, int) and learner_count > int(payload.get("max_allowed_learners", 50)):
        errors.append("cohort manifest learner_count exceeds max_allowed_learners")
    grades = payload.get("grades")
    if grades != [4]:
        errors.append("cohort manifest grades must be [4]")
    subjects = payload.get("subjects")
    if not isinstance(subjects, list) or "Mathematics" not in subjects:
        errors.append("cohort manifest subjects must include Mathematics")
    required_owners = ("launch_owner", "support_owner", "incident_commander", "data_protection_reviewer", "rollback_owner")
    for owner in required_owners:
        if not payload.get(owner):
            errors.append(f"cohort manifest must include {owner}")
    return item


def _validate_traffic_window(path: pathlib.Path, errors: list[str]) -> dict[str, Any]:
    item: dict[str, Any] = {"path": path.as_posix(), "exists": path.exists()}
    if not path.exists():
        errors.append(f"missing live traffic window: {path}")
        return item
    item.update({"sha256": sha256_file(path), "bytes": path.stat().st_size})
    try:
        payload = load_json(path)
    except Exception as exc:  # pragma: no cover
        errors.append(f"invalid live traffic window JSON {path}: {exc}")
        return item
    item["payload"] = payload
    if not isinstance(payload, dict):
        errors.append("live traffic window must be a JSON object")
        return item
    for field in ("activation_start_utc", "activation_end_utc", "support_owner", "incident_commander", "rollback_owner", "monitoring_channel"):
        if not payload.get(field):
            errors.append(f"live traffic window must include {field}")
    pct = payload.get("cohort_traffic_percentage")
    if not isinstance(pct, int) or pct <= 0 or pct > 100:
        errors.append("live traffic window cohort_traffic_percentage must be an integer from 1 to 100")
    if payload.get("public_beta_authorised") is not False:
        errors.append("live traffic window public_beta_authorised must be false")
    if payload.get("controlled_beta_launch_authorised") is not True:
        errors.append("live traffic window controlled_beta_launch_authorised must be true")
    if payload.get("live_learner_traffic_authorised") is not True:
        errors.append("live traffic window live_learner_traffic_authorised must be true")
    return item


def validate_activation_documents(
    *,
    go_no_go: pathlib.Path = DEFAULT_GO_NO_GO,
    cohort_manifest: pathlib.Path = DEFAULT_COHORT_MANIFEST,
    consent_attestation: pathlib.Path = DEFAULT_CONSENT_ATTESTATION,
    traffic_window: pathlib.Path = DEFAULT_TRAFFIC_WINDOW,
) -> dict[str, Any]:
    errors: list[str] = []
    documents: list[dict[str, Any]] = []
    documents.append(_text_markers(go_no_go, (
        "Decision: go",
        "Controlled beta launch authorised: true",
        "Live learner traffic authorised: true",
        "Production release authorised: false",
        "Public beta authorised: false",
        "Runtime KG implementation claimed: false",
    ), errors))
    documents.append(_validate_cohort_manifest(cohort_manifest, errors))
    documents.append(_text_markers(consent_attestation, (
        "Guardian consent reviewed: true",
        "POPIA notice issued: true",
        "Data export route reviewed: true",
        "Right-to-erasure route reviewed: true",
        "Learner data migration authorised: true",
    ), errors))
    documents.append(_validate_traffic_window(traffic_window, errors))
    return {"valid": not errors, "documents": documents, "errors": errors}


def build_result(
    *,
    claimed: bool,
    authorise_launch: bool,
    authorise_live_traffic: bool,
    authorise_migration: bool,
    phase19: dict[str, Any],
    git: dict[str, Any],
    documents: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not claimed:
        errors.append("controlled beta launch activation was not claimed")
    if not authorise_launch:
        errors.append("controlled beta launch must be explicitly authorised")
    if not authorise_live_traffic:
        errors.append("live learner traffic must be explicitly authorised for controlled beta activation")
    if not authorise_migration:
        errors.append("learner data migration must be explicitly authorised for controlled beta activation")
    if phase19.get("valid") is not True:
        errors.append("Phase 19 activation-preflight verifier is not valid")
    if git.get("tracked_worktree_clean_before_capture") is not True:
        errors.append("tracked worktree must be clean before launch-activation capture")
    if git.get("head_matches_remote_target") is not True:
        errors.append("HEAD must match origin target branch before launch-activation capture")
    if documents.get("valid") is not True:
        errors.extend(documents.get("errors") or ["controlled beta launch activation documents are invalid"])
    return {
        "valid": not errors,
        "controlled_beta_launch_activation_claimed": claimed,
        "controlled_beta_launch_activation_recorded": not errors,
        "phase_19_controlled_beta_activation_preflight_valid": phase19.get("valid") is True,
        "launch_activation_documents_valid": documents.get("valid") is True,
        "errors": errors,
        "warnings": warnings,
        **boundary_payload(
            authorise_launch=authorise_launch,
            authorise_live_traffic=authorise_live_traffic,
            authorise_migration=authorise_migration,
        ),
    }


def write_evidence_index(path: pathlib.Path, record: dict[str, Any], result: dict[str, Any], documents: dict[str, Any]) -> None:
    document_lines = "\n".join(f"- `{item['path']}`" for item in documents.get("documents", []))
    text = f"""# Phase 20 Controlled Beta Launch Activation Evidence

- Controlled beta launch activation recorded: {str(result.get('controlled_beta_launch_activation_recorded') is True).lower()}
- Phase 19 activation preflight valid: {str(result.get('phase_19_controlled_beta_activation_preflight_valid') is True).lower()}
- Launch activation documents valid: {str(result.get('launch_activation_documents_valid') is True).lower()}
- Controlled beta launch authorised: {str(result.get('controlled_beta_launch_authorised') is True).lower()}
- Live learner traffic authorised: {str(result.get('live_learner_traffic_authorised') is True).lower()}
- Learner data migration authorised: {str(result.get('learner_data_migration_authorised') is True).lower()}
- Source commit: `{record.get('source_commit')}`
- Target branch: `{record.get('target_branch')}`

## Boundary

- Production release authorised: false
- Deployment authorised: false
- Release tag authorised: false
- Public beta authorised: false
- Runtime KG implementation claimed: false

## Checked Documents

{document_lines}

## Raw Evidence

- `raw/git_state.json`
- `raw/phase19_activation_preflight_verification.json`
- `raw/launch_activation_documents.json`
- `raw/launch_activation_boundary.json`
- `raw/controlled_beta_launch_activation_result.json`
- `raw/controlled_beta_launch_activation_record_snapshot.json`
"""
    path.write_text(text, encoding="utf-8")


def write_sha256sums(evidence_dir: pathlib.Path) -> pathlib.Path:
    sums_path = evidence_dir / "SHA256SUMS.txt"
    lines: list[str] = []
    for path in sorted(evidence_dir.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            lines.append(f"{sha256_file(path)}  {path.as_posix()}")
    sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return sums_path


def capture(args: argparse.Namespace) -> dict[str, Any]:
    phase19 = run_command(["python3", PHASE19_VERIFY.as_posix(), "--json"])
    git = git_state(args.target_branch)
    documents = validate_activation_documents(
        go_no_go=pathlib.Path(args.go_no_go_decision),
        cohort_manifest=pathlib.Path(args.cohort_manifest),
        consent_attestation=pathlib.Path(args.consent_attestation),
        traffic_window=pathlib.Path(args.traffic_window),
    )
    result = build_result(
        claimed=args.claim_controlled_beta_launch_activation,
        authorise_launch=args.authorise_controlled_beta_launch,
        authorise_live_traffic=args.authorise_live_learner_traffic,
        authorise_migration=args.authorise_learner_data_migration,
        phase19=phase19,
        git=git,
        documents=documents,
    )

    record = {
        "schema_version": 1,
        "slice": "PHASE-20-CONTROLLED-BETA-LAUNCH-ACTIVATION-AUTHORITY",
        "status": "controlled_beta_launch_activation_recorded" if result["valid"] else "controlled_beta_launch_activation_invalid",
        "beta_scope": "controlled_beta_launch_activation_gate",
        "captured_at": utc_now(),
        "activation_owner": args.activation_owner,
        "source_commit": git.get("head_sha"),
        "target_branch": args.target_branch,
        "remote_target_sha": git.get("remote_target_sha"),
        "evidence_dir": EVIDENCE_DIR.as_posix(),
        "evidence_index": (EVIDENCE_DIR / "evidence_index.md").as_posix(),
        **result,
    }
    if result["valid"]:
        raw = EVIDENCE_DIR / "raw"
        raw.mkdir(parents=True, exist_ok=True)
        write_json(raw / "git_state.json", git)
        write_json(raw / "phase19_activation_preflight_verification.json", phase19)
        write_json(raw / "launch_activation_documents.json", documents)
        write_json(raw / "launch_activation_boundary.json", boundary_payload(
            authorise_launch=args.authorise_controlled_beta_launch,
            authorise_live_traffic=args.authorise_live_learner_traffic,
            authorise_migration=args.authorise_learner_data_migration,
        ))
        write_json(raw / "controlled_beta_launch_activation_result.json", result)
        write_json(raw / "controlled_beta_launch_activation_record_snapshot.json", record)
        write_evidence_index(EVIDENCE_DIR / "evidence_index.md", record, result, documents)
        sums = write_sha256sums(EVIDENCE_DIR)
        record["sha256sums"] = sums.as_posix()
        write_json(raw / "controlled_beta_launch_activation_record_snapshot.json", record)
        write_evidence_index(EVIDENCE_DIR / "evidence_index.md", record, result, documents)
        sums = write_sha256sums(EVIDENCE_DIR)
        record["sha256sums"] = sums.as_posix()
    write_json(RECORD_PATH, record)
    if args.require_valid and not result["valid"]:
        return record | {"valid": False}
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim-controlled-beta-launch-activation", action="store_true")
    parser.add_argument("--authorise-controlled-beta-launch", action="store_true")
    parser.add_argument("--authorise-live-learner-traffic", action="store_true")
    parser.add_argument("--authorise-learner-data-migration", action="store_true")
    parser.add_argument("--activation-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--go-no-go-decision", default=DEFAULT_GO_NO_GO.as_posix())
    parser.add_argument("--cohort-manifest", default=DEFAULT_COHORT_MANIFEST.as_posix())
    parser.add_argument("--consent-attestation", default=DEFAULT_CONSENT_ATTESTATION.as_posix())
    parser.add_argument("--traffic-window", default=DEFAULT_TRAFFIC_WINDOW.as_posix())
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = capture(args)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"controlled beta launch activation valid: {result.get('valid') is True}")
    return 0 if result.get("valid") is True or not args.require_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
