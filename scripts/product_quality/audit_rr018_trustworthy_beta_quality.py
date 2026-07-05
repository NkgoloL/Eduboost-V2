#!/usr/bin/env python3
"""Audit RR-018 trustworthy beta product quality authority and final evidence files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RR_ID = "RR-018"
BASE = Path("docs/product_quality/trustworthy_beta")
ROADMAP_DOC = Path("docs/roadmap/reconciliation/rr_018_trustworthy_beta_product_quality.md")
RECORD = Path("docs/roadmap/reconciliation/rr_018_trustworthy_beta_product_quality_record.json")
MANIFEST = BASE / "rr018_trustworthy_beta_quality_manifest.json"
POLICY = BASE / "rr018_trustworthy_beta_quality_policy.md"
FRONTEND_COMPONENT = Path("app/frontend/src/components/eduboost/TrustworthyBetaQualityPanel.tsx")
FRONTEND_TEST = Path("app/frontend/__tests__/TrustworthyBetaQualityPanel.test.tsx")
DOMAIN = Path("app/domain/trustworthy_beta_quality.py")
SERVICE = Path("app/services/trustworthy_beta_quality.py")
TEMPLATES = [
    BASE / "rr018_feedback_report_issue_validation.template.md",
    BASE / "rr018_content_correction_workflow.template.md",
    BASE / "rr018_human_review_queue.template.md",
    BASE / "rr018_educator_caps_priority_review.template.md",
    BASE / "rr018_trustworthy_beta_quality_boundary.template.md",
]
FINAL_MARKERS = {
    "feedback_report_issue_button_validated": (
        BASE / "rr018_feedback_report_issue_validation.md",
        "Feedback/report issue button validated: true",
    ),
    "content_correction_workflow_recorded": (
        BASE / "rr018_content_correction_workflow.md",
        "Content correction workflow recorded: true",
    ),
    "human_review_queue_recorded": (
        BASE / "rr018_human_review_queue.md",
        "Human review queue recorded: true",
    ),
    "educator_caps_priority_review_recorded": (
        BASE / "rr018_educator_caps_priority_review.md",
        "Educator CAPS priority review recorded: true",
    ),
    "trustworthy_beta_quality_boundary_recorded": (
        BASE / "rr018_trustworthy_beta_quality_boundary.md",
        "Trustworthy beta quality boundary recorded: true",
    ),
}
REQUIRED_PRODUCT_MARKERS = [
    "Feedback/report issue button validated: true",
    "Content correction workflow recorded: true",
    "Human review queue recorded: true",
    "Educator CAPS priority review recorded: true",
    "Content correction SLA recorded: true",
    "Guardian/learner feedback privacy boundary recorded: true",
    "No learner PII in feedback evidence: true",
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
    "Trustworthy beta product quality authority recorded: true",
    "Feedback/report issue button required: true",
    "Content correction workflow required: true",
    "Human review queue required: true",
    "Educator CAPS priority review required: true",
    "Feedback privacy boundary required: true",
    "RR-003",
    "0.0",
    "RR-006",
    "non-required",
    "RR-016",
    "clean_git_state_at_capture",
    "RR-017",
]
COMPONENT_MARKERS = [
    "Report issue",
    "Content correction workflow",
    "Human review queue",
    "Educator CAPS priority review",
    "Privacy boundary",
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
    component = _read(p(FRONTEND_COMPONENT))
    component_test = _read(p(FRONTEND_TEST))
    domain = _read(p(DOMAIN))
    service = _read(p(SERVICE))
    authority_checks: dict[str, bool] = {
        "roadmap_doc_exists": p(ROADMAP_DOC).exists(),
        "roadmap_doc_cites_rr018": RR_ID in roadmap and "Trustworthy Beta Product Quality" in roadmap,
        "record_exists": p(RECORD).exists(),
        "record_rr_id": record.get("rr_id") == RR_ID,
        "manifest_exists": p(MANIFEST).exists(),
        "manifest_rr_id": manifest.get("rr_id") == RR_ID,
        "manifest_depends_on_rr017": "RR-017" in manifest.get("depends_on", []),
        "policy_exists": p(POLICY).exists(),
        "frontend_component_exists": p(FRONTEND_COMPONENT).exists(),
        "frontend_component_has_quality_markers": all(_has(component, marker) for marker in COMPONENT_MARKERS),
        "frontend_test_exists": p(FRONTEND_TEST).exists(),
        "frontend_test_has_quality_markers": all(_has(component_test, marker) for marker in COMPONENT_MARKERS[:4]),
        "domain_contract_exists": p(DOMAIN).exists(),
        "domain_contract_has_requirements": "TRUSTWORTHY_BETA_REQUIRED_REQUIREMENTS" in domain,
        "service_helper_exists": p(SERVICE).exists(),
        "service_helper_has_completion_check": "trustworthy_beta_quality_complete" in service,
    }
    for key in (
        "feedback_report_issue_button_required",
        "content_correction_workflow_required",
        "human_review_queue_required",
        "educator_caps_priority_review_required",
        "feedback_privacy_boundary_required",
        "final_validation_files_required",
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
        authority_checks[f"template_product_markers:{path.name}"] = all(_has(text, m) for m in REQUIRED_PRODUCT_MARKERS)

    final_checks: dict[str, bool] = {}
    for key, (path, marker) in FINAL_MARKERS.items():
        text = _read(p(path))
        final_checks[f"final_file_exists:{key}"] = p(path).exists()
        final_checks[f"final_marker:{key}"] = _has(text, marker)
        final_checks[f"final_boundary:{key}"] = all(_has(text, m) for m in BOUNDARY_MARKERS)
        final_checks[f"final_product_markers:{key}"] = all(_has(text, m) for m in REQUIRED_PRODUCT_MARKERS)

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
        print(f"RR-018 authority_valid: {result['authority_valid']}")
        print(f"RR-018 final_valid: {result['final_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["authority_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
