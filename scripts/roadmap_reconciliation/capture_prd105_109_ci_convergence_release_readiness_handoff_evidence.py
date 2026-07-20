#!/usr/bin/env python3
"""Capture PRD-1.5-1.9 CI convergence, release-readiness, final evidence, and PRD-2 handoff."""
from __future__ import annotations

import argparse
import json
from scripts._subprocess import check_output, run
from datetime import datetime, timezone
from pathlib import Path

from scripts.production_readiness.apply_prd105_109_ci_convergence_release_readiness_handoff import (
    CONFIG,
    FALSE_BOUNDARIES,
    MERGED_PRD_SLICES,
    PRD_ID,
    RECORD,
    STREAM_ID,
    TRUE_BOUNDARIES,
    apply as apply_authority,
    build_config,
)
from scripts.roadmap_reconciliation.verify_prd100_ci_release_gate_stream_authority import evaluate as evaluate_prd100
from scripts.roadmap_reconciliation.verify_prd101_ci_inventory_authority import evaluate as evaluate_prd101
from scripts.roadmap_reconciliation.verify_prd102_104_required_checks_workflow_release_gate_convergence import evaluate as evaluate_prd102_104
from scripts.roadmap_reconciliation.verify_prd105_109_ci_convergence_release_readiness_handoff import evaluate

ROOT = Path("docs/roadmap/production_readiness")
REGISTER = ROOT / "production_readiness_register.json"
PRD1_REGISTER = ROOT / "prd1_ci_release_gate_register.json"
EVIDENCE_DIR = Path("docs/release-evidence/production-readiness/prd-105-109-ci-convergence-release-readiness-handoff")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_state(target_branch: str) -> dict:
    def run(args: list[str]) -> str | None:
        try:
            return check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    status = run(["git", "status", "--short"])
    return {
        "branch": run(["git", "branch", "--show-current"]),
        "head_sha": run(["git", "rev-parse", "HEAD"]),
        "status_short": status,
        "target_branch": target_branch,
        "git_available": status is not None,
        "clean_git_state_at_capture": status == "" if status is not None else None,
    }


def update_prd1_register(now: str) -> dict:
    data = read_json(PRD1_REGISTER)
    data["last_recorded_item"] = "PRD-1.9"
    data["next_authorised_item"] = "PRD-2"
    data["last_recorded_at"] = now
    data["status"] = "prd1_closed_prd2_authorised"
    data["ci_convergence_evidence_recorded"] = True
    data["release_readiness_register_recorded"] = True
    data["authority_reconciliation_recorded"] = True
    data["final_evidence_capture_recorded"] = True
    data["prd2_handoff_authorised"] = True
    data["prd2_implementation_authorised"] = False
    data.setdefault("implementation_boundaries", {})
    data["implementation_boundaries"].update({
        "ci_inventory_performed": True,
        "required_check_classification_performed": True,
        "workflow_canonicalisation_performed": True,
        "ci_workflow_changes_performed": True,
        "openapi_reconciliation_performed": True,
        "ci_convergence_evidence_recorded": True,
        "release_readiness_register_recorded": True,
        "required_checks_enforced": False,
        "release_gate_enforced": False,
        "branch_protection_modified": False,
    })
    data.setdefault("authority_boundaries", {})
    for key in TRUE_BOUNDARIES:
        data["authority_boundaries"][key] = True
    for key in FALSE_BOUNDARIES:
        data["authority_boundaries"][key] = False
    for item in data.get("prd1_sequence", []):
        if str(item.get("prd_id", "")).startswith("PRD-1."):
            item["authorised"] = True
            item["status"] = "recorded"
    write_json(PRD1_REGISTER, data)
    return data


def update_production_register(now: str, prd1_register: dict) -> dict:
    register = read_json(REGISTER)
    register["last_recorded_item"] = "PRD-1.9"
    register["last_recorded_at"] = now
    register["next_authorised_item"] = "PRD-2"
    register["status"] = "prd1_closed_prd2_authorised"
    register["prd1_next_authorised_item"] = "PRD-2"
    register["prd1_closed"] = True
    register["prd1_closed_at"] = now
    register["prd1_ci_convergence_evidence_recorded"] = True
    register["prd1_release_readiness_register_recorded"] = True
    register["prd1_authority_reconciliation_recorded"] = True
    register["prd1_final_evidence_recorded"] = True
    register["prd2_handoff_authorised"] = True
    register["prd2_implementation_authorised"] = False
    register["prd1_sequence"] = prd1_register.get("prd1_sequence", [])
    register.setdefault("current_truth", {})
    register["current_truth"].update({
        "prd1_closed": True,
        "prd1_next_authorised_item": "PRD-2",
        "prd1_ci_convergence_evidence_recorded": True,
        "prd1_release_readiness_register_recorded": True,
        "prd1_authority_reconciliation_recorded": True,
        "prd1_final_evidence_recorded": True,
        "prd2_handoff_authorised": True,
        "prd2_runtime_kg_integration_authorised_next": True,
    })
    register.setdefault("authority_boundaries", {})
    for key in TRUE_BOUNDARIES:
        register["authority_boundaries"][key] = True
    register["authority_boundaries"]["prd1_implementation_authorised"] = False
    for key in FALSE_BOUNDARIES:
        register["authority_boundaries"][key] = False
    for item in register.get("production_readiness_sequence", []):
        if item.get("prd_id") == "PRD-1":
            item["authorised"] = True
            item["status"] = "recorded"
        elif item.get("prd_id") == "PRD-2":
            item["authorised"] = True
            item["status"] = "authorised"
    write_json(REGISTER, register)
    return register


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-prd105-109-ci-convergence-release-readiness-handoff", action="store_true")
    parser.add_argument("--prd-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.claim_prd105_109_ci_convergence_release_readiness_handoff:
        raise SystemExit("must pass --claim-prd105-109-ci-convergence-release-readiness-handoff")

    before = evaluate(Path("."))
    if not before.get("authority_valid"):
        raise SystemExit(json.dumps(before, indent=2, sort_keys=True))

    now = datetime.now(timezone.utc).isoformat()
    state = git_state(args.target_branch)
    config = apply_authority(Path("."), write_files=True)
    prd100 = evaluate_prd100(Path("."))
    prd101 = evaluate_prd101(Path("."))
    prd102_104 = evaluate_prd102_104(Path("."))

    config["ci_convergence_evidence"]["ci_convergence_evidence_recorded"] = True
    config["ci_convergence_evidence"]["branch_protection_evidence_recorded"] = True
    config["release_readiness_register"]["release_readiness_register_recorded"] = True
    config["authority_reconciliation"]["prd1_sequence_complete"] = True
    config["authority_reconciliation"]["prd1_final_reconciliation_recorded"] = True
    config["final_evidence_capture"]["final_evidence_recorded"] = True
    config["handoff_to_prd2"]["prd2_handoff_authorised_after_capture"] = True
    write_json(CONFIG, config)

    prd1_register = update_prd1_register(now)
    production_register = update_production_register(now, prd1_register)

    record = read_json(RECORD)
    record.update({
        "schema_version": "prd1-ci-convergence-release-readiness-handoff-record/v1",
        "prd_id": PRD_ID,
        "merged_prd_slices": MERGED_PRD_SLICES,
        "stream_id": STREAM_ID,
        "status": "prd1_closed_prd2_authorised",
        "evidence_captured_at": now,
        "evidence_owner": args.prd_owner,
        "target_branch": args.target_branch,
        "git_state": state,
        "clean_git_state_at_capture": state.get("clean_git_state_at_capture"),
        "ci_convergence_evidence_recorded": True,
        "release_readiness_register_recorded": True,
        "prd1_final_reconciliation_recorded": True,
        "prd1_final_evidence_recorded": True,
        "prd1_sequence_complete": True,
        "prd2_handoff_authorised": True,
        "prd2_implementation_authorised": False,
        "no_prd2_implementation_performed": True,
        "no_production_release_performed": True,
        "no_deployment_performed": True,
        "no_release_tag_created": True,
        "no_public_beta_authorised": True,
        "no_live_learner_traffic_authorised": True,
        "next_authorised_item": "PRD-2",
        "verification_chain": {
            "PRD-1.0": prd100,
            "PRD-1.1": prd101,
            "PRD-1.2-1.4": prd102_104,
        },
        "release_readiness_register": config["release_readiness_register"],
        "ci_convergence_evidence": config["ci_convergence_evidence"],
        "authority_reconciliation": config["authority_reconciliation"],
        "handoff_to_prd2": config["handoff_to_prd2"],
        **{key: True for key in TRUE_BOUNDARIES},
        **{key: False for key in FALSE_BOUNDARIES},
        "required_checks_enforced": False,
        "release_gate_enforced": False,
        "branch_protection_modified": False,
        "production_release_deployed": False,
        "release_tag_created": False,
        "prd2_runtime_kg_implementation_performed": False,
    })
    write_json(RECORD, record)

    after = evaluate(Path("."))
    if args.require_valid and not after.get("valid"):
        raise SystemExit(json.dumps(after, indent=2, sort_keys=True))

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    write_json(EVIDENCE_DIR / "verification.json", after)
    write_json(EVIDENCE_DIR / "prd1_ci_release_gate_register.json", prd1_register)
    write_json(EVIDENCE_DIR / "production_readiness_register.json", production_register)
    write_json(EVIDENCE_DIR / "ci_convergence_release_readiness_handoff.json", config)
    write_json(EVIDENCE_DIR / "git_state.json", state)
    index = f"""# PRD-1.5-1.9 Evidence Index\n\nCaptured at: {now}\nOwner: {args.prd_owner}\nTarget branch: {args.target_branch}\n\n## Result\n\n- valid: {after.get('valid')}\n- authority_valid: {after.get('authority_valid')}\n- next_authorised_item: {after.get('next_authorised_item')}\n- PRD-2 handoff authorised: {after.get('prd2_handoff_authorised')}\n- PRD-2 implementation authorised: {after.get('prd2_implementation_authorised')}\n\n## Boundary\n\nNo production deployment, release tag, public beta, billing, live learner traffic, or Runtime KG implementation was performed in PRD-1.\n"""
    (EVIDENCE_DIR / "evidence_index.md").write_text(index, encoding="utf-8")

    if args.json:
        print(json.dumps(after, indent=2, sort_keys=True))
    else:
        print(f"PRD-1.5-1.9 valid: {after.get('valid')}")
    return 0 if after.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
