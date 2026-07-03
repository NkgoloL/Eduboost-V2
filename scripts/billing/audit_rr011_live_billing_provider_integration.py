#!/usr/bin/env python3
"""Audit RR-011 live billing provider integration evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RR_ID = "RR-011"

AUTHORITY_FILES = {
    "policy": Path("docs/billing/rr011_live_billing_provider_integration_policy.md"),
    "manifest": Path("docs/billing/rr011_live_billing_provider_manifest.json"),
    "provider_template": Path("docs/billing/rr011_live_billing_provider_attestation.template.md"),
    "checkout_template": Path("docs/billing/rr011_hosted_checkout_sandbox_validation.template.md"),
    "webhook_template": Path("docs/billing/rr011_webhook_endpoint_validation.template.md"),
    "pricing_template": Path("docs/billing/rr011_pricing_catalogue_approval.template.md"),
    "boundary_template": Path("docs/billing/rr011_billing_launch_boundary.template.md"),
}

EXISTING_BILLING_CONTRACTS = {
    "provider_adr": Path("docs/adr/ADR-009-billing-provider.md"),
    "architecture_contract": Path("docs/billing/production_billing_provider_architecture_contract.md"),
    "subscription_state_machine": Path("docs/billing/subscription_state_machine_contract.md"),
    "webhook_contract": Path("docs/billing/webhook_security_idempotency_contract.md"),
    "pricing_rules": Path("docs/billing/pricing_product_rules_contract.md"),
    "ux_audit": Path("docs/billing/billing_ux_audit_contract.md"),
    "billing_contracts_module": Path("app/modules/billing/production_readiness_contracts.py"),
    "billing_check_script": Path("scripts/check_billing_monetization_production_readiness.py"),
}

FINAL_FILES = {
    "provider_attestation": Path("docs/billing/rr011_live_billing_provider_attestation.md"),
    "checkout_validation": Path("docs/billing/rr011_hosted_checkout_sandbox_validation.md"),
    "webhook_validation": Path("docs/billing/rr011_webhook_endpoint_validation.md"),
    "pricing_approval": Path("docs/billing/rr011_pricing_catalogue_approval.md"),
    "launch_boundary": Path("docs/billing/rr011_billing_launch_boundary.md"),
}

REQUIRED_MARKERS = {
    "provider_attestation": (
        "Billing provider selected: stripe",
        "Live billing provider integration attested: true",
        "Hosted checkout configured: true",
        "No raw card storage confirmed: true",
        "Secret values committed: false",
        "Provider secret references documented: true",
        "Billing launch authorised: false",
        "Live payment processing authorised: false",
    ),
    "checkout_validation": (
        "Hosted checkout sandbox validated: true",
        "Subscription lifecycle sandbox validated: true",
        "Invoice and receipt sandbox validated: true",
        "Payment failure sandbox validated: true",
        "Cancellation sandbox validated: true",
        "Raw card data handled by provider only: true",
    ),
    "webhook_validation": (
        "Webhook endpoint configured: true",
        "Webhook signature validation recorded: true",
        "Webhook replay protection recorded: true",
        "Webhook idempotency validation recorded: true",
        "Webhook audit logging recorded: true",
        "Duplicate provider event handling recorded: true",
        "Out-of-order provider event handling recorded: true",
        "Live webhook traffic authorised: false",
    ),
    "pricing_approval": (
        "Pricing catalogue approved: true",
        "Parent plan configured: true",
        "School plan configured: true",
        "Sponsored learner plan configured: true",
        "NGO/community plan configured: true",
        "Trial length approved: true",
        "Refund and cancellation policy approved: true",
        "Data access after cancellation policy approved: true",
    ),
    "launch_boundary": (
        "Billing launch boundary recorded: true",
        "Billing launch authorised: false",
        "Live payment processing authorised: false",
        "Production release authorised: false",
        "Deployment authorised: false",
        "Release tag authorised: false",
        "Public beta authorised: false",
        "Runtime KG implementation claimed: false",
    ),
}

AUTHORITY_MARKERS = (
    "Live billing provider integration authority recorded: true",
    "RR-003",
    "0.0",
    "RR-006",
    "non-required",
    "RR-012",
    "RR-015",
    "RR-016",
    "Billing launch authorised: false",
    "Runtime KG implementation claimed: false",
)


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
    for name, path in AUTHORITY_FILES.items():
        exists = (root / path).exists()
        authority_checks[f"{name}_exists"] = exists
        if not exists:
            errors.append(f"missing RR-011 authority file: {path}")

    for name, path in EXISTING_BILLING_CONTRACTS.items():
        exists = (root / path).exists()
        authority_checks[f"existing_{name}_exists"] = exists
        if not exists:
            errors.append(f"missing existing billing contract: {path}")

    policy = _read(root, AUTHORITY_FILES["policy"])
    for marker in AUTHORITY_MARKERS:
        key = f"policy_marker:{marker}"
        authority_checks[key] = marker in policy
        if marker not in policy:
            errors.append(f"RR-011 policy missing marker: {marker}")

    manifest = _json(root, AUTHORITY_FILES["manifest"])
    if manifest.get("__json_error__"):
        errors.append(f"RR-011 manifest JSON invalid: {manifest['__json_error__']}")
    else:
        authority_checks["manifest_rr_id"] = manifest.get("rr_id") == RR_ID
        authority_checks["manifest_provider_stripe"] = manifest.get("provider") == "stripe"
        boundary = manifest.get("boundary", {}) if isinstance(manifest.get("boundary"), dict) else {}
        for key in (
            "billing_launch_authorised",
            "live_payment_processing_authorised",
            "production_release_authorised",
            "deployment_authorised",
            "release_tag_authorised",
            "public_beta_authorised",
            "runtime_kg_implementation_claimed",
        ):
            authority_checks[f"manifest_boundary_false:{key}"] = boundary.get(key) is False
            if boundary.get(key) is not False:
                errors.append(f"RR-011 manifest boundary must be false: {key}")

    final_checks: dict[str, bool] = {}
    if require_final:
        for name, path in FINAL_FILES.items():
            text = _read(root, path)
            exists = bool(text)
            final_checks[f"{name}_exists"] = exists
            if not exists:
                errors.append(f"missing final RR-011 evidence file: {path}")
                continue
            for marker in REQUIRED_MARKERS[name]:
                ok = marker in text
                final_checks[f"{name}:{marker}"] = ok
                if not ok:
                    errors.append(f"final RR-011 evidence file {path} missing marker: {marker}")
    else:
        for name, path in FINAL_FILES.items():
            if not (root / path).exists():
                warnings.append(f"missing final RR-011 evidence file before capture: {path}")

    authority_valid = not [e for e in errors if not e.startswith("missing final RR-011") and "final RR-011 evidence file" not in e]
    final_outputs_valid = require_final and not errors
    valid = authority_valid and (final_outputs_valid if require_final else True)

    return {
        "valid": valid,
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
        for error in result.get("errors", []):
            print(f"ERROR: {error}")
        for warning in result.get("warnings", []):
            print(f"WARNING: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
