#!/usr/bin/env python3
"""Audit RR-016 operational drill authority and final evidence files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RR_ID = "RR-016"
BASE = Path("docs/operations/drills")
ROADMAP_DOC = Path("docs/roadmap/reconciliation/rr_016_operational_drills.md")
RECORD = Path("docs/roadmap/reconciliation/rr_016_operational_drills_record.json")
MANIFEST = BASE / "rr016_operational_drills_manifest.json"
POLICY = BASE / "rr016_operational_drills_policy.md"
TEMPLATES = [
    BASE / "rr016_backup_drill_report.template.md",
    BASE / "rr016_restore_drill_report.template.md",
    BASE / "rr016_rollback_drill_report.template.md",
    BASE / "rr016_monitoring_dashboard_verification.template.md",
    BASE / "rr016_incident_handoff_verification.template.md",
]
FINAL_MARKERS = {
    "backup_drill_completed": (BASE / "rr016_backup_drill_report.md", "Backup drill completed: true"),
    "restore_drill_completed": (BASE / "rr016_restore_drill_report.md", "Restore drill completed: true"),
    "rollback_drill_completed": (BASE / "rr016_rollback_drill_report.md", "Rollback drill completed: true"),
    "monitoring_dashboard_verified": (BASE / "rr016_monitoring_dashboard_verification.md", "Monitoring dashboard verified: true"),
    "incident_handoff_verified": (BASE / "rr016_incident_handoff_verification.md", "Incident handoff verified: true"),
}
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
    "Operational drills authority recorded: true",
    "Backup drill required: true",
    "Restore drill required: true",
    "Rollback drill required: true",
    "Monitoring dashboard verification required: true",
    "Incident handoff verification required: true",
    "RR-003",
    "0.0",
    "RR-006",
    "non-required",
    "RR-017",
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
        "roadmap_doc_cites_rr016": RR_ID in roadmap and "Operational Drills" in roadmap,
        "record_exists": p(RECORD).exists(),
        "manifest_exists": p(MANIFEST).exists(),
        "manifest_rr_id": manifest.get("rr_id") == RR_ID,
        "manifest_depends_on_rr015": "RR-015" in manifest.get("depends_on", []),
        "policy_exists": p(POLICY).exists(),
    }
    for key in (
        "backup_drill_required", "restore_drill_required", "rollback_drill_required",
        "monitoring_dashboard_verification_required", "incident_handoff_verification_required",
        "final_reports_required",
    ):
        authority_checks[f"manifest_true:{key}"] = manifest.get(key) is True
    for key in (
        "billing_launch_authorised", "live_payment_processing_authorised", "production_release_authorised",
        "deployment_authorised", "release_tag_authorised", "public_beta_authorised",
        "public_beta_live_traffic_authorised", "runtime_kg_implementation_claimed",
    ):
        authority_checks[f"manifest_boundary_false:{key}"] = manifest.get(key) is False
    for marker in POLICY_MARKERS + BOUNDARY_MARKERS:
        authority_checks[f"policy_marker:{marker}"] = _has(policy, marker)
    for path in TEMPLATES:
        text = _read(p(path))
        authority_checks[f"template_exists:{path.name}"] = p(path).exists()
        authority_checks[f"template_boundary:{path.name}"] = all(_has(text, m) for m in BOUNDARY_MARKERS)

    final_checks: dict[str, bool] = {}
    for key, (path, marker) in FINAL_MARKERS.items():
        text = _read(p(path))
        final_checks[f"final_file_exists:{key}"] = p(path).exists()
        final_checks[f"final_marker:{key}"] = _has(text, marker)
        final_checks[f"final_boundary:{key}"] = all(_has(text, m) for m in BOUNDARY_MARKERS)

    authority_valid = all(authority_checks.values()) and record.get("rr_id") == RR_ID
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
        print(f"RR-016 authority_valid: {result['authority_valid']}")
        print(f"RR-016 final_valid: {result['final_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["authority_valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
