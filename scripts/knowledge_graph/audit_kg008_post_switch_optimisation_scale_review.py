#!/usr/bin/env python3
"""Audit KG-8 post-switch optimisation and scale review authority/evidence."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_post_switch_review import validate_post_switch_review_pack

AUTHORITY_FILES = [
    Path("docs/roadmap/knowledge_graph/kg_008_post_switch_optimisation_scale_review.md"),
    Path("docs/roadmap/knowledge_graph/kg_008_post_switch_optimisation_scale_review_record.json"),
    Path("docs/knowledge_graph/post_switch_review/kg008_post_switch_review_manifest.json"),
    Path("docs/knowledge_graph/post_switch_review/kg008_post_switch_review_policy.md"),
    Path("docs/knowledge_graph/post_switch_review/kg008_post_switch_review_schema.md"),
    Path("docs/knowledge_graph/post_switch_review/kg008_optimisation_backlog_contract.md"),
    Path("docs/knowledge_graph/post_switch_review/kg008_scale_review_contract.md"),
    Path("docs/knowledge_graph/post_switch_review/kg008_monitoring_review_contract.md"),
    Path("docs/knowledge_graph/post_switch_review/kg008_post_switch_boundary.template.md"),
    Path("docs/knowledge_graph/post_switch_review/kg008_post_switch_review_manifest_review.json"),
]

FINAL_DOCS = [
    Path("docs/knowledge_graph/post_switch_review/kg008_post_switch_go_no_go_review.md"),
    Path("docs/knowledge_graph/post_switch_review/kg008_optimisation_backlog_review.md"),
    Path("docs/knowledge_graph/post_switch_review/kg008_scale_review.md"),
    Path("docs/knowledge_graph/post_switch_review/kg008_monitoring_observability_review.md"),
    Path("docs/knowledge_graph/post_switch_review/kg008_rollback_observability_review.md"),
    Path("docs/knowledge_graph/post_switch_review/kg008_popia_post_switch_boundary_review.md"),
    Path("docs/knowledge_graph/post_switch_review/kg008_post_switch_boundary.md"),
]

FINAL_PACK = Path("data/knowledge_graph/post_switch_review/grade4_mathematics_post_switch_optimisation_scale_review_pack.json")
FINAL_SUMMARY = Path("data/knowledge_graph/post_switch_review/grade4_mathematics_post_switch_optimisation_scale_review_pack_summary.json")

REQUIRED_MARKERS = {
    "kg008_post_switch_go_no_go_review.md": [
        ("Reviewer named", "true"),
        ("Reviewed at recorded", "true"),
        ("Post-switch optimisation and scale review approved", "true"),
        ("KG-ACT-001 dependency confirmed", "true"),
        ("Decision", "approve-kg8-post-switch-review-evidence"),
    ],
    "kg008_optimisation_backlog_review.md": [
        ("Reviewer named", "true"),
        ("Reviewed at recorded", "true"),
        ("Optimisation backlog reviewed", "true"),
        ("Optimisation execution authorised", "false"),
    ],
    "kg008_scale_review.md": [
        ("Reviewer named", "true"),
        ("Reviewed at recorded", "true"),
        ("Scale review completed", "true"),
        ("Scale load test execution authorised", "false"),
    ],
    "kg008_monitoring_observability_review.md": [
        ("Reviewer named", "true"),
        ("Reviewed at recorded", "true"),
        ("Monitoring observability review completed", "true"),
        ("Runtime authority state monitoring recorded", "true"),
    ],
    "kg008_rollback_observability_review.md": [
        ("Reviewer named", "true"),
        ("Reviewed at recorded", "true"),
        ("Rollback observability review completed", "true"),
        ("Rollback path remains available", "true"),
    ],
    "kg008_popia_post_switch_boundary_review.md": [
        ("Reviewer named", "true"),
        ("Reviewed at recorded", "true"),
        ("POPIA post-switch boundary reviewed", "true"),
        ("No live learner data in review evidence", "true"),
        ("No guardian PII in review evidence", "true"),
    ],
    "kg008_post_switch_boundary.md": [
        ("Reviewer named", "true"),
        ("Reviewed at recorded", "true"),
        ("Post-switch boundary recorded", "true"),
        ("Production release authorised", "false"),
        ("Deployment authorised", "false"),
        ("Release tag authorised", "false"),
        ("Public beta authorised", "false"),
        ("Billing launch authorised", "false"),
        ("Live payment processing authorised", "false"),
    ],
}


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def marker_value(text: str, label: str) -> str | None:
    pattern = re.compile(rf"^\s*(?:[-*]\s*)?{re.escape(label)}\s*:\s*`?([^`\n]+)`?\s*$", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def marker_matches(path: Path, label: str, expected: str) -> bool:
    if not path.exists():
        return False
    actual = marker_value(path.read_text(encoding="utf-8"), label)
    return (actual or "").strip().lower() == expected.strip().lower()


def review_metadata_errors(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    reviewer = marker_value(text, "Reviewer")
    reviewed_at = marker_value(text, "Reviewed at")
    problems: list[str] = []
    invalid_fragments = ("<", ">", "replace", "template", "tbd", "todo", "name")
    if not reviewer or any(fragment in reviewer.lower() for fragment in invalid_fragments):
        problems.append(f"{path}: Reviewer must be a real named reviewer, not a placeholder")
    if not reviewed_at or not re.match(r"^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}Z)?$", reviewed_at):
        problems.append(f"{path}: Reviewed at must be an ISO date or UTC timestamp")
    return problems


def audit(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    missing_authority = [str(path) for path in AUTHORITY_FILES if not (root / path).exists()]
    if missing_authority:
        errors.extend([f"missing authority file: {path}" for path in missing_authority])
    record = read_json(root / "docs/roadmap/knowledge_graph/kg_008_post_switch_optimisation_scale_review_record.json")
    if record.get("kg_id") != "KG-8":
        errors.append("KG-8 record must have kg_id KG-8")
    if record.get("kgact001_controlled_runtime_activation_valid") is not True:
        errors.append("KG-8 must record valid KG-ACT-001 dependency")

    final_doc_errors = []
    missing_final = [str(path) for path in FINAL_DOCS if not (root / path).exists()]
    for path in FINAL_DOCS:
        for label, expected in REQUIRED_MARKERS.get(path.name, []):
            if not marker_matches(root / path, label, expected):
                final_doc_errors.append(f"{path}: expected marker {label}: {expected}")
        final_doc_errors.extend(review_metadata_errors(root / path))

    final_pack = read_json(root / FINAL_PACK)
    validation = validate_post_switch_review_pack(final_pack) if final_pack else {"valid": False, "errors": ["post-switch review pack missing"]}
    final_valid = not missing_final and not final_doc_errors and validation.get("valid") is True
    return {
        "authority_valid": not errors,
        "final_valid": final_valid,
        "errors": errors + [f"missing final doc: {path}" for path in missing_final] + final_doc_errors + [f"post-switch review pack failed: {err}" for err in validation.get("errors", [])],
        "missing_authority_files": missing_authority,
        "missing_final_docs": missing_final,
        "final_pack_path": str(FINAL_PACK),
        "final_summary_path": str(FINAL_SUMMARY),
        "final_validation": validation,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"authority_valid={result['authority_valid']}")
        print(f"final_valid={result['final_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["authority_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
