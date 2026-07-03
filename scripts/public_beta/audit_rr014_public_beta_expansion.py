#!/usr/bin/env python3
"""Audit RR-014 public beta expansion authority and final evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RR_ID = "RR-014"
BASE = Path("docs/public_beta")
MANIFEST = BASE / "rr014_public_beta_expansion_manifest.json"
POLICY = BASE / "rr014_public_beta_expansion_policy.md"
READINESS_TEMPLATE = BASE / "rr014_public_beta_expansion_readiness_plan.template.md"
COHORT_TEMPLATE = BASE / "rr014_public_beta_cohort_plan.template.json"
CONSENT_TEMPLATE = BASE / "rr014_public_beta_consent_and_privacy_attestation.template.md"
SUPPORT_TEMPLATE = BASE / "rr014_public_beta_support_and_incident_plan.template.md"
BOUNDARY_TEMPLATE = BASE / "rr014_public_beta_launch_boundary.template.md"

FINAL_FILES = {
    "readiness_plan": BASE / "rr014_public_beta_expansion_readiness_plan.md",
    "cohort_plan": BASE / "rr014_public_beta_cohort_plan.json",
    "consent_privacy": BASE / "rr014_public_beta_consent_and_privacy_attestation.md",
    "support_incident": BASE / "rr014_public_beta_support_and_incident_plan.md",
    "launch_boundary": BASE / "rr014_public_beta_launch_boundary.md",
}

REQUIRED_AUTHORITY_FILES = (
    MANIFEST,
    POLICY,
    READINESS_TEMPLATE,
    COHORT_TEMPLATE,
    CONSENT_TEMPLATE,
    SUPPORT_TEMPLATE,
    BOUNDARY_TEMPLATE,
)

REQUIRED_MANIFEST_TRUE = (
    "public_beta_expansion_planning_boundary_recorded",
    "controlled_beta_outcome_review_required",
    "public_beta_scope_bounded_required",
    "public_beta_success_metrics_required",
    "public_beta_rollback_criteria_required",
    "consent_privacy_attestation_required",
    "support_incident_plan_required",
    "external_approvals_required_before_public_beta",
    "operational_drills_required_before_public_beta",
    "release_safety_controls_required_before_public_beta",
    "trustworthy_beta_quality_required_before_public_beta",
)

BOUNDARY_FALSE_KEYS = (
    "public_beta_expansion_authorised",
    "public_beta_live_traffic_authorised",
    "expanded_learner_data_migration_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "runtime_kg_implementation_claimed",
)

POLICY_MARKERS = (
    "Public beta expansion authority recorded: true",
    "Public beta expansion planning boundary recorded: true",
    "Controlled beta outcome reviewed before public beta: true",
    "Public beta expansion authorised: false",
    "Public beta live traffic authorised: false",
    "Expanded learner data migration authorised: false",
    "Production release authorised: false",
    "Runtime KG implementation claimed: false",
    "RR-003",
    "0.0",
    "RR-006",
    "non-required",
    "RR-015",
    "RR-016",
    "RR-017",
    "RR-018",
)

FINAL_MARKERS = {
    "readiness_plan": (
        "Public beta expansion readiness recorded: true",
        "Controlled beta outcome reviewed: true",
        "Public beta scope bounded: true",
        "Public beta success metrics defined: true",
        "Public beta rollback criteria defined: true",
    ),
    "consent_privacy": (
        "Consent and privacy attestation recorded: true",
        "POPIA/privacy review required before public beta activation: true",
        "No learner PII exposed in public beta evidence: true",
        "Guardian consent update path defined: true",
        "Data subject rights path confirmed: true",
    ),
    "support_incident": (
        "Support and incident plan recorded: true",
        "Support escalation path defined: true",
        "Incident response path linked: true",
        "Public beta support owner assigned: true",
        "Critical incident rollback trigger defined: true",
    ),
    "launch_boundary": (
        "Public beta launch boundary recorded: true",
        "Public beta expansion authorised: false",
        "Public beta live traffic authorised: false",
        "Expanded learner data migration authorised: false",
        "Production release authorised: false",
        "Runtime KG implementation claimed: false",
    ),
}

REQUIRED_COHORT_JSON = {
    "public_beta_cohort_plan_recorded": True,
    "initial_public_beta_cohort_bounded": True,
    "phased_rollout_required": True,
    "guardian_consent_required": True,
    "educator_or_support_monitoring_required": True,
    "public_beta_expansion_authorised": False,
}


def _read(root: Path, path: Path) -> str:
    full = root / path
    return full.read_text(encoding="utf-8") if full.exists() else ""


def _json(root: Path, path: Path) -> dict[str, Any]:
    full = root / path
    if not full.exists():
        return {}
    try:
        return json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"__json_error__": str(exc)}


def audit(root: Path | str = Path("."), require_final: bool = False) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []
    authority_checks: dict[str, bool] = {}
    final_checks: dict[str, bool] = {}

    for rel in REQUIRED_AUTHORITY_FILES:
        ok = (root / rel).exists()
        authority_checks[f"authority_file_exists:{rel}"] = ok
        if not ok:
            errors.append(f"missing RR-014 authority file: {rel}")

    manifest = _json(root, MANIFEST)
    if manifest.get("__json_error__"):
        errors.append(f"RR-014 manifest JSON invalid: {manifest['__json_error__']}")
        manifest = {}
    authority_checks["manifest_rr_id"] = manifest.get("rr_id") == RR_ID
    if manifest and manifest.get("rr_id") != RR_ID:
        errors.append("RR-014 manifest must carry rr_id=RR-014")
    for key in REQUIRED_MANIFEST_TRUE:
        ok = manifest.get(key) is True
        authority_checks[f"manifest_true:{key}"] = ok
        if manifest and not ok:
            errors.append(f"RR-014 manifest missing true key: {key}")
    for key in BOUNDARY_FALSE_KEYS:
        ok = manifest.get(key) is False
        authority_checks[f"manifest_boundary_false:{key}"] = ok
        if manifest and not ok:
            errors.append(f"RR-014 manifest boundary must be false: {key}")

    policy = _read(root, POLICY)
    for marker in POLICY_MARKERS:
        ok = marker in policy
        authority_checks[f"policy_marker:{marker}"] = ok
        if not ok:
            errors.append(f"RR-014 policy missing marker: {marker}")

    authority_valid = not errors
    final_outputs_valid = False

    if require_final:
        for name, rel in FINAL_FILES.items():
            if name == "cohort_plan":
                data = _json(root, rel)
                exists = bool(data) and not data.get("__json_error__")
                final_checks[f"final_file_exists:{name}"] = exists
                if not exists:
                    errors.append(f"missing or invalid final RR-014 evidence file: {rel}")
                    continue
                for key, expected in REQUIRED_COHORT_JSON.items():
                    ok = data.get(key) is expected
                    final_checks[f"cohort_plan:{key}={expected}"] = ok
                    if not ok:
                        errors.append(f"RR-014 cohort plan {rel} must set {key}={expected}")
                size = data.get("initial_public_beta_cohort_size")
                size_ok = isinstance(size, int) and 1 <= size <= 200
                final_checks["cohort_plan:initial_public_beta_cohort_size_bounded"] = size_ok
                if not size_ok:
                    errors.append("RR-014 cohort plan must set initial_public_beta_cohort_size between 1 and 200")
                continue
            text = _read(root, rel)
            exists = bool(text)
            final_checks[f"final_file_exists:{name}"] = exists
            if not exists:
                errors.append(f"missing final RR-014 evidence file: {rel}")
                continue
            for marker in FINAL_MARKERS[name]:
                ok = marker in text
                final_checks[f"{name}:{marker}"] = ok
                if not ok:
                    errors.append(f"RR-014 final file {rel} missing marker: {marker}")
        final_outputs_valid = not any(not v for v in final_checks.values()) and not errors
    else:
        warnings.append("final RR-014 public beta expansion evidence files are not required for authority-only audit")

    return {
        "valid": authority_valid and (final_outputs_valid if require_final else True),
        "authority_valid": authority_valid,
        "final_outputs_valid": final_outputs_valid,
        "rr_id": RR_ID,
        "authority_checks": authority_checks,
        "final_checks": final_checks,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--require-final", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit(Path(args.root), require_final=args.require_final)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid=" + str(result["valid"]))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
