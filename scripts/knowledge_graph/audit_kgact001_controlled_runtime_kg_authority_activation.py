#!/usr/bin/env python3
"""Audit KG-ACT-001 controlled runtime KG authority activation authority/evidence."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from app.domain.knowledge_graph_runtime_activation import validate_runtime_activation_pack

AUTHORITY_FILES = [
    Path("docs/roadmap/knowledge_graph/kg_act_001_controlled_runtime_kg_authority_activation.md"),
    Path("docs/roadmap/knowledge_graph/kg_act_001_controlled_runtime_kg_authority_activation_record.json"),
    Path("docs/knowledge_graph/runtime_activation/kgact001_runtime_activation_manifest.json"),
    Path("docs/knowledge_graph/runtime_activation/kgact001_runtime_activation_policy.md"),
    Path("docs/knowledge_graph/runtime_activation/kgact001_runtime_activation_schema.md"),
    Path("docs/knowledge_graph/runtime_activation/kgact001_runtime_activation_review_manifest.json"),
    Path("docs/knowledge_graph/runtime_activation/kgact001_runtime_activation_boundary.template.md"),
]

FINAL_DOCS = [
    Path("docs/knowledge_graph/runtime_activation/kgact001_runtime_authority_go_no_go.md"),
    Path("docs/knowledge_graph/runtime_activation/kgact001_feature_flag_activation_contract.md"),
    Path("docs/knowledge_graph/runtime_activation/kgact001_switch_execution_report.md"),
    Path("docs/knowledge_graph/runtime_activation/kgact001_rollback_validation.md"),
    Path("docs/knowledge_graph/runtime_activation/kgact001_learner_safety_validation.md"),
    Path("docs/knowledge_graph/runtime_activation/kgact001_popia_runtime_boundary_confirmation.md"),
    Path("docs/knowledge_graph/runtime_activation/kgact001_runtime_activation_boundary.md"),
]

FINAL_PACK = Path("data/knowledge_graph/runtime_activation/grade4_mathematics_runtime_kg_activation_pack.json")
FINAL_SUMMARY = Path("data/knowledge_graph/runtime_activation/grade4_mathematics_runtime_kg_activation_pack_summary.json")

REQUIRED_MARKERS = {
    "kgact001_runtime_authority_go_no_go.md": [
        ("Reviewer named", "true"),
        ("Reviewed at recorded", "true"),
        ("Runtime KG authority activation approved", "true"),
        ("Activation owner named", "true"),
        ("Evidence URL recorded", "true"),
        ("Decision", "approve-controlled-runtime-kg-authority-activation"),
    ],
    "kgact001_feature_flag_activation_contract.md": [
        ("Reviewer named", "true"),
        ("Reviewed at recorded", "true"),
        ("Activation feature flag contract recorded", "true"),
        ("Default off outside approved KG scope", "true"),
        ("Rollback flag documented", "true"),
    ],
    "kgact001_switch_execution_report.md": [
        ("Reviewer named", "true"),
        ("Reviewed at recorded", "true"),
        ("Runtime KG authority switch authorised", "true"),
        ("Authority switch executed", "true"),
        ("Execution evidence recorded", "true"),
    ],
    "kgact001_rollback_validation.md": [
        ("Reviewer named", "true"),
        ("Reviewed at recorded", "true"),
        ("Rollback validation recorded", "true"),
        ("Rollback validated before activation", "true"),
        ("Rollback owner named", "true"),
    ],
    "kgact001_learner_safety_validation.md": [
        ("Reviewer named", "true"),
        ("Reviewed at recorded", "true"),
        ("Learner safety validation recorded", "true"),
        ("No live learner data in activation evidence", "true"),
        ("Learner-facing release remains unauthorised", "true"),
    ],
    "kgact001_popia_runtime_boundary_confirmation.md": [
        ("Reviewer named", "true"),
        ("Reviewed at recorded", "true"),
        ("POPIA runtime boundary confirmed", "true"),
        ("No guardian PII in activation evidence", "true"),
        ("No live payment processing authorised", "true"),
    ],
    "kgact001_runtime_activation_boundary.md": [
        ("Reviewer named", "true"),
        ("Reviewed at recorded", "true"),
        ("Runtime activation boundary recorded", "true"),
        ("Production release authorised", "false"),
        ("Deployment authorised", "false"),
        ("Release tag authorised", "false"),
        ("Public beta authorised", "false"),
        ("Billing launch authorised", "false"),
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
    record = read_json(root / "docs/roadmap/knowledge_graph/kg_act_001_controlled_runtime_kg_authority_activation_record.json")
    if record.get("kg_id") != "KG-ACT-001":
        errors.append("KG-ACT-001 record must have kg_id KG-ACT-001")
    if record.get("kg7_authority_switch_readiness_valid") is not True:
        errors.append("KG-ACT-001 must record valid KG-7 dependency")

    final_doc_errors = []
    missing_final = [str(path) for path in FINAL_DOCS if not (root / path).exists()]
    for path in FINAL_DOCS:
        checks = REQUIRED_MARKERS.get(path.name, [])
        for label, expected in checks:
            if not marker_matches(root / path, label, expected):
                final_doc_errors.append(f"{path}: expected marker {label}: {expected}")
        final_doc_errors.extend(review_metadata_errors(root / path))
    final_pack = read_json(root / FINAL_PACK)
    validation = validate_runtime_activation_pack(final_pack) if final_pack else {"valid": False, "errors": ["runtime activation pack missing"]}
    final_valid = not missing_final and not final_doc_errors and validation.get("valid") is True
    return {
        "authority_valid": not errors,
        "final_valid": final_valid,
        "errors": errors + [f"missing final doc: {path}" for path in missing_final] + final_doc_errors + [f"activation pack failed: {err}" for err in validation.get("errors", [])],
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
