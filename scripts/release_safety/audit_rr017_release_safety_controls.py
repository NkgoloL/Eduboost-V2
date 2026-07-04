#!/usr/bin/env python3
"""Audit RR-017 release safety controls authority and final evidence files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RR_ID = "RR-017"
BASE = Path("docs/release_safety")
ROADMAP_DOC = Path("docs/roadmap/reconciliation/rr_017_release_safety_controls.md")
RECORD = Path("docs/roadmap/reconciliation/rr_017_release_safety_controls_record.json")
MANIFEST = BASE / "rr017_release_safety_controls_manifest.json"
POLICY = BASE / "rr017_release_safety_controls_policy.md"
TEMPLATES = [
    BASE / "rr017_release_safety_control_attestation.template.md",
    BASE / "rr017_prohibited_operations_register.template.md",
    BASE / "rr017_migration_window_control.template.md",
    BASE / "rr017_health_probe_immutability_validation.template.md",
    BASE / "rr017_release_change_control_boundary.template.md",
]
FINAL_MARKERS = {
    "release_safety_controls_attested": (
        BASE / "rr017_release_safety_control_attestation.md",
        "Release safety controls attested: true",
    ),
    "prohibited_operations_register_recorded": (
        BASE / "rr017_prohibited_operations_register.md",
        "Prohibited operations register recorded: true",
    ),
    "migration_window_control_recorded": (
        BASE / "rr017_migration_window_control.md",
        "Migration window control recorded: true",
    ),
    "health_probe_immutability_validated": (
        BASE / "rr017_health_probe_immutability_validation.md",
        "Health probe immutability validated: true",
    ),
    "release_change_control_boundary_recorded": (
        BASE / "rr017_release_change_control_boundary.md",
        "Release change-control boundary recorded: true",
    ),
}
REQUIRED_CONTROL_MARKERS = [
    "Destructive audit consent DB changes blocked: true",
    "Alembic stamp head repair blocked: true",
    "Production DB mutation requires migration window: true",
    "Mutating health probes blocked: true",
    "Break-glass exception process recorded: true",
]
BOUNDARY_MARKERS = [
    "Billing launch authorised: false",
    "Live payment processing authorised: false",
    "Production release authorised: false",
    "Deployment authorised: false",
    "Release tag authorised: false",
    "Public beta authorised: false",
    "Public beta live traffic authorised: false",
    "Runtime KG implementation claimed: false",
]
POLICY_MARKERS = [
    "Release safety controls authority recorded: true",
    "Destructive audit consent DB changes blocked: true",
    "Alembic stamp head repair blocked: true",
    "Production DB mutation outside migration window blocked: true",
    "Mutating health probes blocked: true",
    "Break-glass exception process required: true",
    "Release change-control boundary required: true",
    "RR-003",
    "0.0",
    "RR-006",
    "non-required",
    "RR-016",
    "clean_git_state_at_capture",
    "docs/reports/",
    "RR-018",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _has(text: str, marker: str) -> bool:
    return marker.lower() in text.lower()


def audit(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)

    def p(path: Path) -> Path:
        return root / path

    manifest = _json(p(MANIFEST))
    policy = _read(p(POLICY))
    roadmap = _read(p(ROADMAP_DOC))
    record = _json(p(RECORD))
    authority_checks: dict[str, bool] = {
        "roadmap_doc_exists": p(ROADMAP_DOC).exists(),
        "roadmap_doc_cites_rr017": RR_ID in roadmap and "Release Safety Controls" in roadmap,
        "record_exists": p(RECORD).exists(),
        "record_rr_id": record.get("rr_id") == RR_ID,
        "manifest_exists": p(MANIFEST).exists(),
        "manifest_rr_id": manifest.get("rr_id") == RR_ID,
        "manifest_depends_on_rr016": "RR-016" in manifest.get("depends_on", []),
        "policy_exists": p(POLICY).exists(),
    }
    for key in (
        "release_safety_controls_required",
        "destructive_audit_consent_db_changes_blocked",
        "alembic_stamp_head_repair_blocked",
        "production_db_mutation_requires_migration_window",
        "mutating_health_probes_blocked",
        "break_glass_exception_process_required",
        "release_change_control_boundary_required",
        "final_reports_required",
    ):
        authority_checks[f"manifest_true:{key}"] = manifest.get(key) is True
    for key in (
        "billing_launch_authorised",
        "live_payment_processing_authorised",
        "production_release_authorised",
        "deployment_authorised",
        "release_tag_authorised",
        "public_beta_authorised",
        "public_beta_live_traffic_authorised",
        "runtime_kg_implementation_claimed",
    ):
        authority_checks[f"manifest_boundary_false:{key}"] = manifest.get(key) is False
    for marker in POLICY_MARKERS + BOUNDARY_MARKERS:
        authority_checks[f"policy_marker:{marker}"] = _has(policy, marker)
    for path in TEMPLATES:
        text = _read(p(path))
        authority_checks[f"template_exists:{path.name}"] = p(path).exists()
        authority_checks[f"template_boundary:{path.name}"] = all(_has(text, m) for m in BOUNDARY_MARKERS)
        authority_checks[f"template_controls:{path.name}"] = all(_has(text, m) for m in REQUIRED_CONTROL_MARKERS)

    final_checks: dict[str, bool] = {}
    for key, (path, marker) in FINAL_MARKERS.items():
        text = _read(p(path))
        final_checks[f"final_file_exists:{key}"] = p(path).exists()
        final_checks[f"final_marker:{key}"] = _has(text, marker)
        final_checks[f"final_boundary:{key}"] = all(_has(text, m) for m in BOUNDARY_MARKERS)
        final_checks[f"final_controls:{key}"] = all(_has(text, m) for m in REQUIRED_CONTROL_MARKERS)

    authority_valid = all(authority_checks.values())
    final_valid = all(final_checks.values())
    return {
        "rr_id": RR_ID,
        "authority_valid": authority_valid,
        "final_valid": final_valid,
        "authority_checks": authority_checks,
        "final_checks": final_checks,
        "errors": [name for name, ok in {**authority_checks, **final_checks}.items() if not ok],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    result = audit(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"RR-017 authority_valid: {result['authority_valid']}")
        print(f"RR-017 final_valid: {result['final_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["authority_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
