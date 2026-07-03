#!/usr/bin/env python3
"""Audit RR-013 advanced mastery-model research authority and final evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RR_ID = "RR-013"
BASE = Path("docs/research/mastery_model")
MANIFEST = BASE / "rr013_mastery_model_research_manifest.json"
POLICY = BASE / "rr013_mastery_model_research_policy.md"
AGENDA = BASE / "rr013_mastery_model_research_agenda.md"
CANDIDATE_TEMPLATE = BASE / "rr013_candidate_model_comparison.template.md"
EVALUATION_TEMPLATE = BASE / "rr013_evaluation_protocol.template.md"
DATA_ETHICS_TEMPLATE = BASE / "rr013_data_readiness_and_ethics_review.template.md"
DECISION_TEMPLATE = BASE / "rr013_research_decision_memo.template.md"

FINAL_FILES = {
    "literature_review": BASE / "rr013_mastery_model_literature_review.md",
    "candidate_model_comparison": BASE / "rr013_candidate_model_comparison.md",
    "evaluation_protocol": BASE / "rr013_evaluation_protocol.md",
    "data_readiness_ethics": BASE / "rr013_data_readiness_and_ethics_review.md",
    "research_decision_memo": BASE / "rr013_research_decision_memo.md",
}

EXISTING_EVIDENCE = (
    Path("docs/learning_science/mastery_model.md"),
    Path("docs/diagnostics/mastery_model_assessment_contract.md"),
    Path("app/modules/progress/mastery_model.py"),
)

REQUIRED_MANIFEST_TRUE = (
    "research_only_boundary_recorded",
    "existing_mastery_model_preserved",
    "runtime_kg_boundary_preserved",
    "learner_facing_model_deployment_authorised_false",
    "production_learner_data_training_authorised_false",
    "human_review_required_before_deployment",
    "caps_alignment_evaluation_required",
)

REQUIRED_CANDIDATES = (
    "baseline_mastery_formula",
    "bayesian_knowledge_tracing",
    "performance_factors_analysis",
    "deep_knowledge_tracing",
    "knowledge_tracing_transformer",
)

POLICY_MARKERS = (
    "Advanced mastery-model research authority recorded: true",
    "Research-only boundary recorded: true",
    "Existing mastery model preserved: true",
    "Runtime KG implementation claimed: false",
    "Learner-facing model deployment authorised: false",
    "Model retraining on production learner data authorised: false",
    "Human review required before deployment: true",
    "CAPS alignment evaluation required: true",
    "RR-003",
    "0.0",
    "RR-006",
    "non-required",
    "RR-014",
    "RR-015",
    "RR-016",
)

FINAL_MARKERS = {
    "literature_review": (
        "Advanced mastery-model literature reviewed: true",
        "Research source limitations recorded: true",
        "South African CAPS applicability reviewed: true",
    ),
    "candidate_model_comparison": (
        "Model candidates compared: true",
        "Baseline mastery formula included: true",
        "Bayesian Knowledge Tracing evaluated: true",
        "Deep Knowledge Tracing evaluated: true",
        "Production deployment recommendation recorded: false",
    ),
    "evaluation_protocol": (
        "Evaluation protocol recorded: true",
        "Offline evaluation required: true",
        "A/B test requires separate approval: true",
        "CAPS alignment evaluation required: true",
        "Fairness and bias evaluation required: true",
    ),
    "data_readiness_ethics": (
        "Data readiness and ethics reviewed: true",
        "No learner PII exported for research: true",
        "POPIA lawful basis review required before learner-data research: true",
        "Synthetic or anonymised data preferred: true",
        "Model retraining on production learner data authorised: false",
    ),
    "research_decision_memo": (
        "Research backlog decision recorded: true",
        "Existing mastery model preserved: true",
        "Runtime KG north-star boundary preserved: true",
        "Learner-facing model deployment authorised: false",
        "Runtime KG implementation claimed: false",
    ),
}

BOUNDARY_FALSE_KEYS = (
    "model_deployment_authorised",
    "learner_facing_model_change_authorised",
    "production_learner_data_retraining_authorised",
    "runtime_kg_implementation_claimed",
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
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
    final_checks: dict[str, bool] = {}

    for rel in (MANIFEST, POLICY, AGENDA, CANDIDATE_TEMPLATE, EVALUATION_TEMPLATE, DATA_ETHICS_TEMPLATE, DECISION_TEMPLATE):
        ok = (root / rel).exists()
        authority_checks[f"authority_file_exists:{rel}"] = ok
        if not ok:
            errors.append(f"missing RR-013 authority file: {rel}")

    for rel in EXISTING_EVIDENCE:
        ok = (root / rel).exists()
        authority_checks[f"existing_evidence_exists:{rel}"] = ok
        if not ok:
            errors.append(f"missing existing mastery-model evidence anchor: {rel}")

    manifest = _json(root, MANIFEST)
    if manifest.get("__json_error__"):
        errors.append(f"RR-013 manifest JSON invalid: {manifest['__json_error__']}")
        manifest = {}
    authority_checks["manifest_rr_id"] = manifest.get("rr_id") == RR_ID
    if manifest and manifest.get("rr_id") != RR_ID:
        errors.append("RR-013 manifest must carry rr_id=RR-013")
    for key in REQUIRED_MANIFEST_TRUE:
        ok = manifest.get(key) is True
        authority_checks[f"manifest_true:{key}"] = ok
        if manifest and not ok:
            errors.append(f"RR-013 manifest missing true key: {key}")
    for key in BOUNDARY_FALSE_KEYS:
        ok = manifest.get(key) is False
        authority_checks[f"manifest_boundary_false:{key}"] = ok
        if manifest and not ok:
            errors.append(f"RR-013 manifest boundary must be false: {key}")
    candidates = manifest.get("candidate_model_families", [])
    for candidate in REQUIRED_CANDIDATES:
        ok = candidate in candidates
        authority_checks[f"manifest_candidate:{candidate}"] = ok
        if manifest and not ok:
            errors.append(f"RR-013 manifest missing candidate model family: {candidate}")

    policy = _read(root, POLICY)
    for marker in POLICY_MARKERS:
        ok = marker in policy
        authority_checks[f"policy_marker:{marker}"] = ok
        if not ok:
            errors.append(f"RR-013 policy missing marker: {marker}")

    agenda = _read(root, AGENDA)
    for marker in (
        "Research question 1",
        "Research question 2",
        "Research question 3",
        "Research question 4",
        "Do not implement runtime KG in RR-013",
    ):
        ok = marker in agenda
        authority_checks[f"agenda_marker:{marker}"] = ok
        if not ok:
            errors.append(f"RR-013 agenda missing marker: {marker}")

    authority_valid = not errors
    final_outputs_valid = False

    if require_final:
        for name, rel in FINAL_FILES.items():
            text = _read(root, rel)
            exists = bool(text)
            final_checks[f"final_file_exists:{name}"] = exists
            if not exists:
                errors.append(f"missing final RR-013 evidence file: {rel}")
                continue
            for marker in FINAL_MARKERS[name]:
                ok = marker in text
                final_checks[f"{name}:{marker}"] = ok
                if not ok:
                    errors.append(f"RR-013 final file {rel} missing marker: {marker}")
        final_outputs_valid = not any(not v for v in final_checks.values()) and not errors
    else:
        warnings.append("final RR-013 research evidence files are not required for authority-only audit")

    return {
        "valid": authority_valid and (final_outputs_valid if require_final else True),
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
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
