#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/roadmap/reconciliation/rr_002_privacy_popia_completion_record.json"
REQUIRED_MARKERS = {
    "app/services/popia_erasure_safety.py": ["build_erasure_preflight_decision", "legal_hold_checked=True", "export_requirement_satisfied", "preserve_audit_records=True"],
    "app/services/popia_service.py": ["from app.services.popia_erasure_safety import build_erasure_preflight_decision", "export_offered=preflight_result.get(\"export_offered\", False)", "\"export_offered\": preflight_result.get(\"export_offered\", False)", "\"preserve_audit_records\": True"],
    "app/api_v2_routers/learners.py": ["POPIADataRightsService", "status.HTTP_202_ACCEPTED", "request_erasure(learner_id=learner_id"],
    "app/api_v2_routers/parents.py": ["POPIADataRightsService", "status.HTTP_202_ACCEPTED", "request_erasure(learner_id=learner_id"],
}
BOUNDARY_FALSE_FIELDS = ["production_release_authorised", "deployment_authorised", "release_tag_authorised", "public_beta_authorised", "runtime_kg_implementation_claimed"]
COMPLETION_FIELDS = ["legal_hold_checks_before_erasure", "export_offered_before_erasure", "deletion_flow_persisted", "repository_backed_authorization_enforced", "audit_immutability_preserved"]

def _json(path: Path) -> dict[str, Any]:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError: return {}

def verify() -> dict[str, Any]:
    errors: list[str] = []
    required = [*REQUIRED_MARKERS, "docs/roadmap/reconciliation/outstanding_work_register.md", "docs/roadmap/reconciliation/rr_002_privacy_popia_completion.md", str(RECORD.relative_to(ROOT))]
    for rel in required:
        if not (ROOT / rel).exists(): errors.append(f"required file missing: {rel}")
    for rel, markers in REQUIRED_MARKERS.items():
        path = ROOT / rel
        if not path.exists(): continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text: errors.append(f"missing marker in {rel}: {marker}")
    reg = ROOT / "docs/roadmap/reconciliation/outstanding_work_register.md"
    if reg.exists():
        rtext = reg.read_text(encoding="utf-8")
        if "RR-002" not in rtext or "Privacy / POPIA" not in rtext: errors.append("RR-002 register item missing")
    record = _json(RECORD)
    if record.get("rr_id") != "RR-002": errors.append("record rr_id must be RR-002")
    for field in BOUNDARY_FALSE_FIELDS:
        if record.get(field) is not False: errors.append(f"boundary field must remain false: {field}")
    if record.get("privacy_popia_completion_recorded"):
        for field in COMPLETION_FIELDS:
            if record.get(field) is not True: errors.append(f"claimed completion missing field: {field}")
    return {"valid": not errors, "rr_id":"RR-002", "errors":errors, "record_path": str(RECORD.relative_to(ROOT))}

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--json", action="store_true"); args=p.parse_args(); result=verify()
    if args.json: print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid" if result["valid"] else "invalid")
        for e in result["errors"]: print(f"ERROR: {e}")
    return 0 if result["valid"] else 1
if __name__ == "__main__": raise SystemExit(main())
