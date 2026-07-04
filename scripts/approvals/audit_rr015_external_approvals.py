#!/usr/bin/env python3
"""Audit RR-015 external approval authority and final evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RR_ID = "RR-015"
BASE = Path("docs/approvals")
MANIFEST = BASE / "rr015_external_approvals_manifest.json"
POLICY = BASE / "rr015_external_approvals_policy.md"
SECURITY_TEMPLATE = BASE / "rr015_security_review_attestation.template.md"
POPIA_TEMPLATE = BASE / "rr015_popia_privacy_review_attestation.template.md"
LEGAL_TEMPLATE = BASE / "rr015_legal_review_attestation.template.md"
CAPS_TEMPLATE = BASE / "rr015_caps_content_review_attestation.template.md"
RELEASE_TEMPLATE = BASE / "rr015_release_owner_go_no_go_signoff.template.md"
BOUNDARY_TEMPLATE = BASE / "rr015_external_approval_boundary.template.md"

FINAL_FILES = {
    "security_review": BASE / "rr015_security_review_attestation.md",
    "popia_privacy_review": BASE / "rr015_popia_privacy_review_attestation.md",
    "legal_review": BASE / "rr015_legal_review_attestation.md",
    "caps_content_review": BASE / "rr015_caps_content_review_attestation.md",
    "release_owner_go_no_go": BASE / "rr015_release_owner_go_no_go_signoff.md",
    "approval_boundary": BASE / "rr015_external_approval_boundary.md",
}

REQUIRED_AUTHORITY_FILES = (
    MANIFEST,
    POLICY,
    SECURITY_TEMPLATE,
    POPIA_TEMPLATE,
    LEGAL_TEMPLATE,
    CAPS_TEMPLATE,
    RELEASE_TEMPLATE,
    BOUNDARY_TEMPLATE,
)

REQUIRED_MANIFEST_TRUE = (
    "security_review_required",
    "popia_privacy_review_required",
    "legal_review_required",
    "caps_content_review_required",
    "release_owner_go_no_go_required",
    "named_approver_required",
    "decision_date_required",
    "evidence_url_required",
    "public_beta_activation_remains_separate",
    "production_release_remains_separate",
)

BOUNDARY_FALSE_KEYS = (
    "external_approval_substitution_allowed",
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
    "External approvals authority recorded: true",
    "Security review required: true",
    "POPIA/privacy review required: true",
    "Legal review required: true",
    "CAPS/content review required: true",
    "Release-owner go/no-go required: true",
    "Repository-only approval substitution allowed: false",
    "Public beta expansion authorised: false",
    "Public beta live traffic authorised: false",
    "Production release authorised: false",
    "Runtime KG implementation claimed: false",
    "RR-003",
    "0.0",
    "RR-006",
    "non-required",
    "RR-016",
    "RR-017",
    "RR-018",
)

FINAL_MARKERS = {
    "security_review": (
        "Security review approved: true",
        "Security reviewer named: true",
        "Security evidence URL recorded: true",
        "Security review date recorded: true",
        "Critical security blockers open: false",
    ),
    "popia_privacy_review": (
        "POPIA/privacy review approved: true",
        "POPIA reviewer named: true",
        "POPIA evidence URL recorded: true",
        "POPIA review date recorded: true",
        "Critical POPIA/privacy blockers open: false",
    ),
    "legal_review": (
        "Legal review approved: true",
        "Legal reviewer named: true",
        "Legal evidence URL recorded: true",
        "Legal review date recorded: true",
        "Critical legal blockers open: false",
    ),
    "caps_content_review": (
        "CAPS/content review approved: true",
        "Curriculum reviewer named: true",
        "CAPS/content evidence URL recorded: true",
        "CAPS/content review date recorded: true",
        "Critical curriculum/content blockers open: false",
    ),
    "release_owner_go_no_go": (
        "Release-owner go/no-go signoff recorded: true",
        "Release owner named: true",
        "Release-owner evidence URL recorded: true",
        "Release-owner decision date recorded: true",
        "Release-owner decision: proceed-to-next-governance-gate",
    ),
    "approval_boundary": (
        "External approval boundary recorded: true",
        "External approvals complete: true",
        "Repository-only approval substitution allowed: false",
        "Public beta expansion authorised: false",
        "Public beta live traffic authorised: false",
        "Production release authorised: false",
        "Runtime KG implementation claimed: false",
    ),
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
            errors.append(f"missing RR-015 authority file: {rel}")

    manifest = _json(root, MANIFEST)
    if manifest.get("__json_error__"):
        errors.append(f"RR-015 manifest JSON invalid: {manifest['__json_error__']}")
        manifest = {}
    authority_checks["manifest_rr_id"] = manifest.get("rr_id") == RR_ID
    if manifest and manifest.get("rr_id") != RR_ID:
        errors.append("RR-015 manifest must carry rr_id=RR-015")
    for key in REQUIRED_MANIFEST_TRUE:
        ok = manifest.get(key) is True
        authority_checks[f"manifest_true:{key}"] = ok
        if manifest and not ok:
            errors.append(f"RR-015 manifest missing true key: {key}")
    for key in BOUNDARY_FALSE_KEYS:
        ok = manifest.get(key) is False
        authority_checks[f"manifest_boundary_false:{key}"] = ok
        if manifest and not ok:
            errors.append(f"RR-015 manifest boundary must be false: {key}")

    policy = _read(root, POLICY)
    for marker in POLICY_MARKERS:
        ok = marker in policy
        authority_checks[f"policy_marker:{marker}"] = ok
        if not ok:
            errors.append(f"RR-015 policy missing marker: {marker}")

    authority_valid = not errors
    final_outputs_valid = False

    if require_final:
        for name, rel in FINAL_FILES.items():
            text = _read(root, rel)
            exists = bool(text)
            final_checks[f"final_file_exists:{name}"] = exists
            if not exists:
                errors.append(f"missing final RR-015 evidence file: {rel}")
                continue
            for marker in FINAL_MARKERS[name]:
                ok = marker in text
                final_checks[f"{name}:{marker}"] = ok
                if not ok:
                    errors.append(f"RR-015 final file {rel} missing marker: {marker}")
        final_outputs_valid = not any(not v for v in final_checks.values()) and not errors
    else:
        warnings.append("final RR-015 external approval evidence files are not required for authority-only audit")

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
