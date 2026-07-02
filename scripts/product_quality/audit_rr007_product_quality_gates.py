#!/usr/bin/env python3
"""Audit RR-007 product completeness / quality-gate anchors."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_DOCS = {
    "product_quality_policy": Path("docs/product_quality/rr007_product_quality_gate_policy.md"),
    "playwright_ci_gate": Path("docs/product_quality/rr007_playwright_ci_gate.md"),
    "accessibility_audit_plan": Path("docs/product_quality/rr007_accessibility_audit_plan.md"),
    "pwa_offline_verification_plan": Path("docs/product_quality/rr007_pwa_offline_verification_plan.md"),
    "multilingual_lesson_proof_plan": Path("docs/product_quality/rr007_multilingual_lesson_proof_plan.md"),
    "load_testing_plan": Path("docs/performance/rr007_load_testing_plan.md"),
    "content_expansion_roadmap": Path("docs/curriculum/rr007_content_expansion_roadmap.md"),
    "supabase_postgres_adr": Path("docs/adr/ADR-035-supabase-vs-raw-postgres-product-quality-gate.md"),
    "quality_gate_manifest": Path("docs/product_quality/rr007_quality_gate_manifest.json"),
}
WORKFLOW = Path(".github/workflows/rr007-product-quality-gates.yml")
EXISTING_E2E_WORKFLOW = Path(".github/workflows/e2e.yml")

REQUIRED_MARKERS = {
    "playwright_ci_gate": "Playwright CI gate recorded: true",
    "accessibility_audit_plan": "Accessibility audit planned: true",
    "pwa_offline_verification_plan": "PWA offline verification planned: true",
    "multilingual_lesson_proof_plan": "Multilingual lesson proof planned: true",
    "load_testing_plan": "Load testing planned: true",
    "content_expansion_roadmap": "Grades R-3 and 5-7 content expansion roadmap recorded: true",
    "supabase_postgres_adr": "Supabase versus raw Postgres decision recorded: true",
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


def audit(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []
    doc_results: dict[str, bool] = {}

    for key, rel in REQUIRED_DOCS.items():
        exists = (root / rel).exists()
        doc_results[f"{key}_exists"] = exists
        if not exists:
            errors.append(f"missing required RR-007 document: {rel}")

    for key, marker in REQUIRED_MARKERS.items():
        rel = REQUIRED_DOCS[key]
        contains = marker in _read(root, rel)
        doc_results[f"{key}_marker_present"] = contains
        if not contains:
            errors.append(f"missing marker in {rel}: {marker}")

    manifest = _json(root, REQUIRED_DOCS["quality_gate_manifest"])
    if manifest.get("__json_error__"):
        errors.append(f"RR-007 manifest JSON invalid: {manifest['__json_error__']}")
    required_manifest_flags = (
        "playwright_ci_visible",
        "content_expansion_roadmap_recorded",
        "load_testing_plan_recorded",
        "accessibility_audit_plan_recorded",
        "pwa_offline_verification_plan_recorded",
        "multilingual_lesson_proof_plan_recorded",
        "supabase_postgres_adr_recorded",
    )
    for flag in required_manifest_flags:
        if manifest.get(flag) is not True:
            errors.append(f"RR-007 manifest flag must be true: {flag}")

    workflow_text = _read(root, WORKFLOW)
    existing_e2e_text = _read(root, EXISTING_E2E_WORKFLOW)
    workflow_checks = {
        "rr007_workflow_exists": (root / WORKFLOW).exists(),
        "rr007_workflow_mentions_playwright_ci": "playwright" in workflow_text.lower(),
        "rr007_workflow_runs_audit": "audit_rr007_product_quality_gates.py" in workflow_text,
        "existing_e2e_workflow_exists": (root / EXISTING_E2E_WORKFLOW).exists(),
        "existing_e2e_workflow_mentions_playwright": "playwright" in existing_e2e_text.lower(),
    }
    for key, passed in workflow_checks.items():
        if not passed:
            errors.append(f"workflow check failed: {key}")

    if manifest.get("production_release_authorised") is not False:
        errors.append("manifest production_release_authorised must be false")
    if manifest.get("public_beta_authorised") is not False:
        errors.append("manifest public_beta_authorised must be false")
    if manifest.get("runtime_kg_implementation_claimed") is not False:
        errors.append("manifest runtime_kg_implementation_claimed must be false")

    valid = not errors
    return {
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
        "documents": doc_results,
        "workflow_checks": workflow_checks,
        "manifest": manifest,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("RR-007 product quality gate audit:", "valid" if result["valid"] else "invalid")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
