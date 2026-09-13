#!/usr/bin/env python3
"""Verify RR-007 product completeness / quality-gate authority and evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RR_ID = "RR-007"
REGISTER = Path("docs/roadmap/reconciliation/outstanding_work_register.md")
RR005_RECORD = Path("docs/roadmap/reconciliation/rr_005_technical_debt_burndown_record.json")
RR006_RECORD = Path("docs/roadmap/reconciliation/rr_006_security_posture_deepening_record.json")
RECORD = Path("docs/roadmap/reconciliation/rr_007_product_quality_gates_record.json")
RR_DOC = Path("docs/roadmap/reconciliation/rr_007_product_quality_gates.md")
MANIFEST = Path("docs/product_quality/rr007_quality_gate_manifest.json")
POLICY = Path("docs/product_quality/rr007_product_quality_gate_policy.md")
PLAYWRIGHT_DOC = Path("docs/product_quality/rr007_playwright_ci_gate.md")
ACCESSIBILITY_DOC = Path("docs/product_quality/rr007_accessibility_audit_plan.md")
PWA_DOC = Path("docs/product_quality/rr007_pwa_offline_verification_plan.md")
MULTILINGUAL_DOC = Path("docs/product_quality/rr007_multilingual_lesson_proof_plan.md")
LOAD_DOC = Path("docs/performance/rr007_load_testing_plan.md")
CONTENT_DOC = Path("docs/curriculum/rr007_content_expansion_roadmap.md")
ADR_DOC = Path("docs/adr/ADR-035-supabase-vs-raw-postgres-product-quality-gate.md")
WORKFLOW = Path(".github/workflows/rr007-product-quality-gates.yml")
AUDIT_SCRIPT = Path("scripts/product_quality/audit_rr007_product_quality_gates.py")
CAPTURE_SCRIPT = Path("scripts/roadmap_reconciliation/capture_rr007_product_quality_gates_evidence.py")
VERIFY_SCRIPT = Path("scripts/roadmap_reconciliation/verify_rr007_product_quality_gates.py")
MAKEFILE = Path("Makefile")

BOUNDARY_FALSE_KEYS = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "runtime_kg_implementation_claimed",
)
REQUIRED_TRUE_KEYS = (
    "product_quality_gates_recorded",
    "playwright_ci_visible",
    "content_expansion_roadmap_recorded",
    "load_testing_plan_recorded",
    "accessibility_audit_plan_recorded",
    "pwa_offline_verification_plan_recorded",
    "multilingual_lesson_proof_plan_recorded",
    "supabase_postgres_adr_recorded",
    "rr003_fallback_coverage_caveat_visible",
)


_ARCHIVE = Path("archive/github_workflows")


def _resolve_wf(root: Path, path: Path) -> Path:
    """Return root/path, with archive fallback for missing workflow files."""
    full = root / path
    if not full.exists() and str(path).startswith(".github/workflows/"):
        archived = root / _ARCHIVE / path.name
        if archived.exists():
            return archived
    return full


def _read(root: Path, path: Path) -> str:
    full = _resolve_wf(root, path)
    return full.read_text(encoding="utf-8") if full.exists() else ""


def _json(root: Path, path: Path) -> dict[str, Any]:
    full = root / path
    if not full.exists():
        return {}
    try:
        return json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"__json_error__": str(exc)}


def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []

    register = _read(root, REGISTER)
    rr005_record = _json(root, RR005_RECORD)
    rr006_record = _json(root, RR006_RECORD)
    record = _json(root, RECORD)
    manifest = _json(root, MANIFEST)
    rr_doc = _read(root, RR_DOC)
    policy = _read(root, POLICY)
    playwright_doc = _read(root, PLAYWRIGHT_DOC)
    accessibility_doc = _read(root, ACCESSIBILITY_DOC)
    pwa_doc = _read(root, PWA_DOC)
    multilingual_doc = _read(root, MULTILINGUAL_DOC)
    load_doc = _read(root, LOAD_DOC)
    content_doc = _read(root, CONTENT_DOC)
    adr_doc = _read(root, ADR_DOC)
    workflow = _read(root, WORKFLOW)
    audit_script = _read(root, AUDIT_SCRIPT)
    makefile = _read(root, MAKEFILE)

    checks = {
        "rr007_in_outstanding_register": RR_ID in register and "Product completeness" in register,
        "rr005_predecessor_recorded": rr005_record.get("technical_debt_burndown_recorded") is True,
        "rr006_prior_security_recorded": rr006_record.get("security_posture_deepening_recorded") is True,
        "rr_doc_exists": (root / RR_DOC).exists(),
        "record_exists": (root / RECORD).exists(),
        "manifest_exists": (root / MANIFEST).exists(),
        "policy_exists": (root / POLICY).exists(),
        "playwright_doc_exists": (root / PLAYWRIGHT_DOC).exists(),
        "accessibility_doc_exists": (root / ACCESSIBILITY_DOC).exists(),
        "pwa_doc_exists": (root / PWA_DOC).exists(),
        "multilingual_doc_exists": (root / MULTILINGUAL_DOC).exists(),
        "load_doc_exists": (root / LOAD_DOC).exists(),
        "content_doc_exists": (root / CONTENT_DOC).exists(),
        "adr_doc_exists": (root / ADR_DOC).exists(),
        "workflow_exists": _resolve_wf(root, WORKFLOW).exists(),
        "audit_script_exists": (root / AUDIT_SCRIPT).exists(),
        "capture_script_exists": (root / CAPTURE_SCRIPT).exists(),
        "verify_script_exists": (root / VERIFY_SCRIPT).exists(),
        "rr_doc_cites_register_id": RR_ID in rr_doc,
        "policy_mentions_rr003_caveat": "RR-003" in policy and "0.0" in policy,
        "policy_preserves_boundaries": "Runtime KG" in policy and "not authorised" in policy,
        "playwright_doc_has_marker": "Playwright CI gate recorded: true" in playwright_doc,
        "accessibility_doc_has_marker": "Accessibility audit planned: true" in accessibility_doc,
        "pwa_doc_has_marker": "PWA offline verification planned: true" in pwa_doc,
        "multilingual_doc_has_marker": "Multilingual lesson proof planned: true" in multilingual_doc,
        "load_doc_has_marker": "Load testing planned: true" in load_doc,
        "content_doc_has_marker": "Grades R-3 and 5-7 content expansion roadmap recorded: true" in content_doc,
        "adr_doc_has_marker": "Supabase versus raw Postgres decision recorded: true" in adr_doc,
        "workflow_mentions_audit_script": "audit_rr007_product_quality_gates.py" in workflow,
        "workflow_mentions_playwright": "playwright" in workflow.lower(),
        "audit_script_checks_all_gate_areas": all(
            token in audit_script
            for token in (
                "playwright_ci_visible",
                "content_expansion_roadmap_recorded",
                "load_testing_plan_recorded",
                "accessibility_audit_plan_recorded",
                "pwa_offline_verification_plan_recorded",
                "multilingual_lesson_proof_plan_recorded",
                "supabase_postgres_adr_recorded",
            )
        ),
        "makefile_has_rr007_audit_target": "rr007-product-quality-audit" in makefile,
        "makefile_has_rr007_check_target": "rr007-product-quality-check" in makefile,
    }

    for key, passed in checks.items():
        if not passed:
            errors.append(f"missing or failed check: {key}")

    if manifest.get("__json_error__"):
        errors.append(f"manifest JSON invalid: {manifest['__json_error__']}")
    elif manifest:
        for key in (
            "playwright_ci_visible",
            "content_expansion_roadmap_recorded",
            "load_testing_plan_recorded",
            "accessibility_audit_plan_recorded",
            "pwa_offline_verification_plan_recorded",
            "multilingual_lesson_proof_plan_recorded",
            "supabase_postgres_adr_recorded",
        ):
            if manifest.get(key) is not True:
                errors.append(f"manifest flag must be true: {key}")
        for key in ("production_release_authorised", "public_beta_authorised", "runtime_kg_implementation_claimed"):
            if manifest.get(key) is not False:
                errors.append(f"manifest boundary flag must be false: {key}")
    else:
        errors.append("RR-007 quality gate manifest is missing")

    if record.get("__json_error__"):
        errors.append(f"record JSON invalid: {record['__json_error__']}")
    elif record:
        if record.get("rr_id") != RR_ID:
            errors.append(f"record rr_id must be {RR_ID}")
        for key in BOUNDARY_FALSE_KEYS:
            if record.get(key) is not False:
                errors.append(f"boundary flag must remain false: {key}")
        if record.get("product_quality_gates_recorded") is True:
            for key in REQUIRED_TRUE_KEYS:
                if record.get(key) is not True:
                    errors.append(f"record flag must be true after evidence capture: {key}")
            if not isinstance(record.get("product_quality_audit"), dict):
                errors.append("product_quality_audit must be embedded after capture")
        else:
            warnings.append("record is still pending evidence capture")
    else:
        errors.append("record JSON is missing")

    authority_errors = [
        err for err in errors
        if not err.startswith("record flag must be true")
        and err != "product_quality_audit must be embedded after capture"
    ]
    authority_valid = not authority_errors
    valid = not errors and record.get("product_quality_gates_recorded") is True

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "rr_id": RR_ID,
        "record_path": str(RECORD),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "product_quality_gates_recorded": record.get("product_quality_gates_recorded") is True,
        "playwright_ci_visible": record.get("playwright_ci_visible") is True,
        "content_expansion_roadmap_recorded": record.get("content_expansion_roadmap_recorded") is True,
        "load_testing_plan_recorded": record.get("load_testing_plan_recorded") is True,
        "accessibility_audit_plan_recorded": record.get("accessibility_audit_plan_recorded") is True,
        "pwa_offline_verification_plan_recorded": record.get("pwa_offline_verification_plan_recorded") is True,
        "multilingual_lesson_proof_plan_recorded": record.get("multilingual_lesson_proof_plan_recorded") is True,
        "supabase_postgres_adr_recorded": record.get("supabase_postgres_adr_recorded") is True,
        "rr003_fallback_coverage_caveat_visible": record.get("rr003_fallback_coverage_caveat_visible") is True,
        "production_release_authorised": record.get("production_release_authorised"),
        "deployment_authorised": record.get("deployment_authorised"),
        "release_tag_authorised": record.get("release_tag_authorised"),
        "public_beta_authorised": record.get("public_beta_authorised"),
        "runtime_kg_implementation_claimed": record.get("runtime_kg_implementation_claimed"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--authority-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = evaluate(Path(args.root))
    if args.authority_only:
        result = dict(result)
        result["valid"] = bool(result["authority_valid"])
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("valid=" + str(result["valid"]))
        for error in result["errors"]:
            print("ERROR:", error)
        for warning in result["warnings"]:
            print("WARNING:", warning)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
