#!/usr/bin/env python3
"""Capture Phase 21 controlled beta launch-monitoring evidence.

Phase 21 records the first controlled-beta live-traffic monitoring checkpoint
after Phase 20 launch activation. It may authorise continued operation inside
the approved controlled-beta cohort only. It does not authorise production
release, public beta, release tagging, production deployment, or runtime KG
implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from scripts._subprocess import run
from datetime import datetime, timezone
from typing import Any, Mapping

RECORD_PATH = pathlib.Path("docs/roadmap/execution/runtime_readiness/phase_21_controlled_beta_launch_monitoring_record.json")
EVIDENCE_DIR = pathlib.Path("docs/release-evidence/runtime-readiness/phase-21-controlled-beta-launch-monitoring")
PHASE20_VERIFY = pathlib.Path("scripts/runtime_readiness/verify_controlled_beta_launch_activation.py")

DEFAULT_MONITORING_REPORT = pathlib.Path("docs/operations/beta/controlled_beta_launch_monitoring_report.md")
DEFAULT_SUPPORT_LOG = pathlib.Path("docs/operations/beta/controlled_beta_support_log.json")
DEFAULT_INCIDENT_LOG = pathlib.Path("docs/operations/beta/controlled_beta_incident_log.json")
DEFAULT_ROLLBACK_DECISION = pathlib.Path("docs/operations/beta/controlled_beta_rollback_decision.md")
DEFAULT_METRICS_SNAPSHOT = pathlib.Path("docs/operations/beta/controlled_beta_monitoring_metrics_snapshot.json")

FALSE_BOUNDARY_FIELDS: tuple[str, ...] = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "runtime_kg_implementation_claimed",
)
REQUIRED_TRUE_FIELDS: tuple[str, ...] = (
    "controlled_beta_launch_authorised",
    "live_learner_traffic_authorised",
    "learner_data_migration_authorised",
    "live_learner_traffic_observed",
    "controlled_beta_continuation_authorised",
)
REQUIRED_REPORT_MARKERS: tuple[str, ...] = (
    "Controlled beta monitoring complete: true",
    "Live learner traffic observed: true",
    "No critical incidents: true",
    "Rollback required: false",
    "Production release authorised: false",
    "Public beta authorised: false",
    "Runtime KG implementation claimed: false",
)
REQUIRED_ROLLBACK_MARKERS: tuple[str, ...] = (
    "Rollback reviewed: true",
    "Rollback required: false",
    "Controlled beta continuation authorised: true",
    "Production release authorised: false",
    "Public beta authorised: false",
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
    def _git(*args: str) -> str:
        proc = run(["git", *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        return proc.stdout.strip()

    return {
        "branch": _git("branch", "--show-current"),
        "head_sha": _git("rev-parse", "HEAD"),
        "target_branch": target_branch,
        "target_sha": _git("rev-parse", target_branch) or _git("rev-parse", f"origin/{target_branch}"),
        "status_short": _git("status", "--short"),
    }


def _missing_markers(text: str, markers: tuple[str, ...]) -> list[str]:
    return [marker for marker in markers if marker not in text]


def _validate_support_log(path: pathlib.Path) -> tuple[dict[str, Any], list[str]]:
    if not path.exists():
        return {}, [f"support log missing: {path}"]
    try:
        payload = load_json(path)
    except Exception as exc:
        return {}, [f"support log is not valid JSON: {exc}"]
    errors: list[str] = []
    if not isinstance(payload, dict):
        return {}, [f"support log must be a JSON object: {path}"]
    if not payload.get("support_owner"):
        errors.append("support log must include support_owner")
    if not payload.get("support_channel"):
        errors.append("support log must include support_channel")
    if int(payload.get("unresolved_p0_tickets", -1)) != 0:
        errors.append("support log unresolved_p0_tickets must be 0")
    if int(payload.get("unresolved_p1_tickets", -1)) != 0:
        errors.append("support log unresolved_p1_tickets must be 0")
    if payload.get("controlled_beta_launch_authorised") is not True:
        errors.append("support log must keep controlled_beta_launch_authorised true")
    if payload.get("public_beta_authorised") is not False:
        errors.append("support log must keep public_beta_authorised false")
    return payload, errors


def _validate_incident_log(path: pathlib.Path) -> tuple[dict[str, Any], list[str]]:
    if not path.exists():
        return {}, [f"incident log missing: {path}"]
    try:
        payload = load_json(path)
    except Exception as exc:
        return {}, [f"incident log is not valid JSON: {exc}"]
    errors: list[str] = []
    if not isinstance(payload, dict):
        return {}, [f"incident log must be a JSON object: {path}"]
    if not payload.get("incident_commander"):
        errors.append("incident log must include incident_commander")
    if int(payload.get("open_p0_incidents", -1)) != 0:
        errors.append("incident log open_p0_incidents must be 0")
    if int(payload.get("open_p1_incidents", -1)) != 0:
        errors.append("incident log open_p1_incidents must be 0")
    if payload.get("critical_incidents_open") is not False:
        errors.append("incident log critical_incidents_open must be false")
    if payload.get("rollback_required") is not False:
        errors.append("incident log rollback_required must be false")
    if payload.get("production_release_authorised") is not False:
        errors.append("incident log must keep production_release_authorised false")
    return payload, errors


def _validate_metrics_snapshot(path: pathlib.Path) -> tuple[dict[str, Any], list[str]]:
    if not path.exists():
        return {}, [f"metrics snapshot missing: {path}"]
    try:
        payload = load_json(path)
    except Exception as exc:
        return {}, [f"metrics snapshot is not valid JSON: {exc}"]
    errors: list[str] = []
    if not isinstance(payload, dict):
        return {}, [f"metrics snapshot must be a JSON object: {path}"]
    if payload.get("live_learner_traffic_observed") is not True:
        errors.append("metrics snapshot must set live_learner_traffic_observed true")
    if payload.get("health_checks_green") is not True:
        errors.append("metrics snapshot must set health_checks_green true")
    if payload.get("seeded_e2e_regression_green") is not True:
        errors.append("metrics snapshot must set seeded_e2e_regression_green true")
    if payload.get("error_budget_breached") is not False:
        errors.append("metrics snapshot must set error_budget_breached false")
    if payload.get("data_rights_routes_available") is not True:
        errors.append("metrics snapshot must set data_rights_routes_available true")
    return payload, errors


def validate_monitoring_documents(
    *,
    monitoring_report: pathlib.Path,
    support_log: pathlib.Path,
    incident_log: pathlib.Path,
    rollback_decision: pathlib.Path,
    metrics_snapshot: pathlib.Path,
) -> dict[str, Any]:
    errors: list[str] = []
    doc_hashes: dict[str, str] = {}
    docs: dict[str, Any] = {}

    if not monitoring_report.exists():
        errors.append(f"monitoring report missing: {monitoring_report}")
    else:
        text = monitoring_report.read_text(encoding="utf-8")
        missing = _missing_markers(text, REQUIRED_REPORT_MARKERS)
        errors.extend(f"monitoring report missing marker: {marker}" for marker in missing)
        doc_hashes[str(monitoring_report)] = sha256_file(monitoring_report)
        docs["monitoring_report"] = {"path": str(monitoring_report), "sha256": doc_hashes[str(monitoring_report)]}

    if not rollback_decision.exists():
        errors.append(f"rollback decision missing: {rollback_decision}")
    else:
        text = rollback_decision.read_text(encoding="utf-8")
        missing = _missing_markers(text, REQUIRED_ROLLBACK_MARKERS)
        errors.extend(f"rollback decision missing marker: {marker}" for marker in missing)
        doc_hashes[str(rollback_decision)] = sha256_file(rollback_decision)
        docs["rollback_decision"] = {"path": str(rollback_decision), "sha256": doc_hashes[str(rollback_decision)]}

    support_payload, support_errors = _validate_support_log(support_log)
    incident_payload, incident_errors = _validate_incident_log(incident_log)
    metrics_payload, metrics_errors = _validate_metrics_snapshot(metrics_snapshot)
    errors.extend(support_errors)
    errors.extend(incident_errors)
    errors.extend(metrics_errors)

    for path in (support_log, incident_log, metrics_snapshot):
        if path.exists():
            doc_hashes[str(path)] = sha256_file(path)

    docs["support_log"] = support_payload
    docs["incident_log"] = incident_payload
    docs["metrics_snapshot"] = metrics_payload

    return {
        "valid": not errors,
        "errors": errors,
        "documents": docs,
        "document_hashes": doc_hashes,
    }


def build_result(
    *,
    claim_monitoring: bool,
    monitoring_owner: str,
    target_branch: str,
    phase20_verification: Mapping[str, Any],
    monitoring_documents: Mapping[str, Any],
    source_sha: str,
    captured_at: str | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    if not claim_monitoring:
        errors.append("controlled beta launch monitoring was not claimed")
    if not monitoring_owner:
        errors.append("monitoring owner is required")
    if phase20_verification.get("valid") is not True:
        errors.append("Phase 20 controlled beta launch activation verifier is not valid")
    if monitoring_documents.get("valid") is not True:
        errors.extend(str(e) for e in monitoring_documents.get("errors", []))

    result = {
        "schema_version": 1,
        "status": "controlled_beta_launch_monitoring_recorded" if not errors else "controlled_beta_launch_monitoring_invalid",
        "captured_at": captured_at or utc_now(),
        "monitoring_owner": monitoring_owner,
        "target_branch": target_branch,
        "source_sha": source_sha,
        "controlled_beta_launch_monitoring_claimed": claim_monitoring,
        "controlled_beta_launch_monitoring_recorded": not errors,
        "phase_20_controlled_beta_launch_activation_valid": phase20_verification.get("valid") is True,
        "monitoring_documents_valid": monitoring_documents.get("valid") is True,
        "controlled_beta_launch_authorised": True,
        "live_learner_traffic_authorised": True,
        "learner_data_migration_authorised": True,
        "live_learner_traffic_observed": monitoring_documents.get("valid") is True,
        "controlled_beta_continuation_authorised": monitoring_documents.get("valid") is True,
        "critical_incidents_open": False,
        "rollback_required": False,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "evidence_dir": str(EVIDENCE_DIR),
        "evidence_index": str(EVIDENCE_DIR / "evidence_index.md"),
        "errors": errors,
        "warnings": [],
    }
    return result


def write_evidence(
    *,
    result: dict[str, Any],
    phase20_verification: dict[str, Any],
    monitoring_documents: dict[str, Any],
    git: dict[str, Any],
) -> None:
    raw_dir = EVIDENCE_DIR / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    write_json(raw_dir / "git_state.json", git)
    write_json(raw_dir / "phase20_launch_activation_verification.json", phase20_verification)
    write_json(raw_dir / "monitoring_documents.json", monitoring_documents)
    write_json(raw_dir / "controlled_beta_launch_monitoring_result.json", result)
    write_json(raw_dir / "controlled_beta_launch_monitoring_record_snapshot.json", result)

    write_json(RECORD_PATH, result)

    index = f"""# Phase 21 Controlled Beta Launch Monitoring Evidence

- Controlled beta launch monitoring recorded: {str(result.get('controlled_beta_launch_monitoring_recorded')).lower()}
- Phase 20 launch activation valid: {str(result.get('phase_20_controlled_beta_launch_activation_valid')).lower()}
- Monitoring documents valid: {str(result.get('monitoring_documents_valid')).lower()}
- Controlled beta launch authorised: {str(result.get('controlled_beta_launch_authorised')).lower()}
- Live learner traffic authorised: {str(result.get('live_learner_traffic_authorised')).lower()}
- Live learner traffic observed: {str(result.get('live_learner_traffic_observed')).lower()}
- Controlled beta continuation authorised: {str(result.get('controlled_beta_continuation_authorised')).lower()}
- Source commit: `{result.get('source_sha')}`
- Target branch: `{result.get('target_branch')}`

## Boundary

- Production release authorised: {str(result.get('production_release_authorised')).lower()}
- Deployment authorised: {str(result.get('deployment_authorised')).lower()}
- Release tag authorised: {str(result.get('release_tag_authorised')).lower()}
- Public beta authorised: {str(result.get('public_beta_authorised')).lower()}
- Runtime KG implementation claimed: {str(result.get('runtime_kg_implementation_claimed')).lower()}

## Raw Evidence

- `raw/git_state.json`
- `raw/phase20_launch_activation_verification.json`
- `raw/monitoring_documents.json`
- `raw/controlled_beta_launch_monitoring_result.json`
- `raw/controlled_beta_launch_monitoring_record_snapshot.json`
"""
    index_path = EVIDENCE_DIR / "evidence_index.md"
    index_path.write_text(index, encoding="utf-8")
    (EVIDENCE_DIR / "evidence_index.sha256").write_text(sha256_file(index_path) + "  evidence_index.md\n", encoding="utf-8")

    checksum_targets = [
        index_path,
        EVIDENCE_DIR / "evidence_index.sha256",
        raw_dir / "git_state.json",
        raw_dir / "phase20_launch_activation_verification.json",
        raw_dir / "monitoring_documents.json",
        raw_dir / "controlled_beta_launch_monitoring_result.json",
        raw_dir / "controlled_beta_launch_monitoring_record_snapshot.json",
    ]
    sums = "".join(f"{sha256_file(path)}  {path}\n" for path in checksum_targets)
    (EVIDENCE_DIR / "SHA256SUMS.txt").write_text(sums, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim-controlled-beta-launch-monitoring", action="store_true")
    parser.add_argument("--monitoring-owner", default="")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--monitoring-report", type=pathlib.Path, default=DEFAULT_MONITORING_REPORT)
    parser.add_argument("--support-log", type=pathlib.Path, default=DEFAULT_SUPPORT_LOG)
    parser.add_argument("--incident-log", type=pathlib.Path, default=DEFAULT_INCIDENT_LOG)
    parser.add_argument("--rollback-decision", type=pathlib.Path, default=DEFAULT_ROLLBACK_DECISION)
    parser.add_argument("--metrics-snapshot", type=pathlib.Path, default=DEFAULT_METRICS_SNAPSHOT)
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    git = git_state(args.target_branch)
    phase20 = run_command(["python3", str(PHASE20_VERIFY), "--json"])
    docs = validate_monitoring_documents(
        monitoring_report=args.monitoring_report,
        support_log=args.support_log,
        incident_log=args.incident_log,
        rollback_decision=args.rollback_decision,
        metrics_snapshot=args.metrics_snapshot,
    )
    result = build_result(
        claim_monitoring=args.claim_controlled_beta_launch_monitoring,
        monitoring_owner=args.monitoring_owner,
        target_branch=args.target_branch,
        phase20_verification={"valid": phase20.get("valid") is True, "details": phase20},
        monitoring_documents=docs,
        source_sha=git["head_sha"],
    )
    write_evidence(result=result, phase20_verification=phase20, monitoring_documents=docs, git=git)

    if args.json:
        print(json.dumps({"valid": not result["errors"], **result}, indent=2, sort_keys=True))
    elif result["errors"]:
        print("\n".join(result["errors"]))
    else:
        print("Phase 21 controlled beta launch monitoring evidence captured")

    if args.require_valid and result["errors"]:
        return 1
    return 0 if not result["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
