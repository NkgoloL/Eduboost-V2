#!/usr/bin/env python3
"""Verify RR-001 Atlas phase status reconciliation authority.

This verifier checks that the stale Atlas phase register has been explicitly
reconciled/superseded and that future work is routed through the outstanding
RR register rather than old blocked phase language.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RECON_DIR = ROOT / "docs" / "roadmap" / "reconciliation"
REGISTER = ROOT / "docs" / "roadmap" / "PHASE_STATUS_REGISTER.md"
MATRIX = RECON_DIR / "rr_001_atlas_phase_status_matrix.json"
RECORD = RECON_DIR / "rr_001_atlas_phase_status_record.json"
ROADMAP_RECORD = RECON_DIR / "roadmap_reconciliation_record.json"
OUTSTANDING = RECON_DIR / "outstanding_work_register.md"

REQUIRED_REGISTER_MARKERS = [
    "RR-001 Atlas phase status reconciliation",
    "Supersession notice",
    "not the current implementation queue",
    "docs/roadmap/reconciliation/outstanding_work_register.md",
    "Phase 18-21 beta-operations records are auxiliary governance records",
    "Next implementation work must cite an RR-### item",
]

FORBIDDEN_ACTIVE_MARKERS = [
    "| Overall programme | **Reconciliation in progress** |",
    "| Phase 8 | **Blocked by Phases 0–7 reconciliation** |",
    "| Controlled beta | Blocked |",
]

REQUIRED_MATRIX_PHASES = {str(i) for i in range(0, 9)}
REQUIRED_RECORD_FALSE_FLAGS = [
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "runtime_kg_implementation_claimed",
    "new_unreconciled_work_authorised",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    for path in [REGISTER, MATRIX, RECORD, ROADMAP_RECORD, OUTSTANDING]:
        if not path.exists():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")

    register_text = REGISTER.read_text(encoding="utf-8") if REGISTER.exists() else ""
    for marker in REQUIRED_REGISTER_MARKERS:
        if marker not in register_text:
            errors.append(f"PHASE_STATUS_REGISTER missing marker: {marker}")
    for marker in FORBIDDEN_ACTIVE_MARKERS:
        if marker in register_text:
            errors.append(f"PHASE_STATUS_REGISTER still contains stale active-blocked marker: {marker}")

    if OUTSTANDING.exists():
        outstanding_text = OUTSTANDING.read_text(encoding="utf-8")
        if "| RR-001 |" not in outstanding_text:
            errors.append("outstanding register does not contain RR-001")
        if "Anti-scope-creep rule" not in outstanding_text:
            errors.append("outstanding register missing anti-scope-creep rule")

    if ROADMAP_RECORD.exists():
        roadmap_record = _load_json(ROADMAP_RECORD)
        if roadmap_record.get("roadmap_reconciliation_recorded") is not True:
            errors.append("roadmap reconciliation baseline must be recorded before RR-001 closure")
        if roadmap_record.get("new_work_freeze_active") is not True:
            errors.append("roadmap reconciliation record must keep new_work_freeze_active true")
    else:
        roadmap_record = {}

    if MATRIX.exists():
        matrix = _load_json(MATRIX)
        phases = matrix.get("atlas_phases", [])
        phase_ids = {str(p.get("phase")) for p in phases}
        missing = sorted(REQUIRED_MATRIX_PHASES - phase_ids)
        if missing:
            errors.append(f"matrix missing Atlas phases: {', '.join(missing)}")
        for phase in phases:
            if phase.get("current_classification") not in {"historical_atlas_record", "superseded_by_rr_register"}:
                errors.append(
                    f"phase {phase.get('phase')} has invalid classification: {phase.get('current_classification')}"
                )
            if phase.get("release_authority") is not False:
                errors.append(f"phase {phase.get('phase')} must not be release authority")
        if matrix.get("next_work_source") != "docs/roadmap/reconciliation/outstanding_work_register.md":
            errors.append("matrix next_work_source must be outstanding work register")
    else:
        matrix = {}

    if RECORD.exists():
        record = _load_json(RECORD)
        if record.get("status") not in {"rr001_authority_placeholder", "rr001_atlas_phase_status_reconciled"}:
            errors.append(f"unexpected RR-001 record status: {record.get('status')}")
        if record.get("rr_id") != "RR-001":
            errors.append("RR-001 record must have rr_id RR-001")
        if record.get("atlas_phase_register_reconciled") is not True:
            errors.append("RR-001 record must mark atlas_phase_register_reconciled true")
        if record.get("phase_18_to_21_auxiliary_governance") is not True:
            errors.append("RR-001 record must classify Phase 18-21 as auxiliary governance")
        if record.get("next_work_must_cite_rr_id") is not True:
            errors.append("RR-001 record must require next work to cite RR ID")
        for flag in REQUIRED_RECORD_FALSE_FLAGS:
            if record.get(flag) is not False:
                errors.append(f"{flag} must be false in RR-001 record")
    else:
        record = {}

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "rr_id": "RR-001",
        "atlas_phase_register_reconciled": record.get("atlas_phase_register_reconciled"),
        "phase_18_to_21_auxiliary_governance": record.get("phase_18_to_21_auxiliary_governance"),
        "next_work_must_cite_rr_id": record.get("next_work_must_cite_rr_id"),
        "production_release_authorised": record.get("production_release_authorised"),
        "deployment_authorised": record.get("deployment_authorised"),
        "public_beta_authorised": record.get("public_beta_authorised"),
        "runtime_kg_implementation_claimed": record.get("runtime_kg_implementation_claimed"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid" if result["valid"] else "invalid")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
