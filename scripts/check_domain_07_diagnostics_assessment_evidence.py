#!/usr/bin/env python3
"""Verify repo-side evidence for Diagnostics & Assessment roadmap branch."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_EVIDENCE = [
    "app/modules/diagnostics",
    "app/modules/progress",
    "app/modules/practice",
    "app/modules/diagnostics/production_readiness_contracts.py",
    "scripts/ci/check_diagnostics_assessment.py",
    "scripts/check_diagnostics_assessment_production_readiness.py",
    "scripts/check_learning_evidence.py",
    "scripts/check_caps_learning_proof.py",
    "docs/caps",
    "docs/diagnostics/production_diagnostics_assessment_readiness_contract.md",
    "docs/diagnostics/item_bank_launch_coverage_contract.md",
    "docs/diagnostics/mastery_model_assessment_contract.md",
    "docs/diagnostics/assessment_quality_fairness_contract.md",
    "tests/unit/test_diagnostics_assessment_production_readiness.py",
    "tests/unit/modules/diagnostics",
    "tests/unit/modules/progress",
    "tests/unit/modules/practice",
    ".github/workflows/ci_diagnostics_assessment.yml",
]

EXTERNAL_GATES = [
    "GitHub branch-protection / required-check UI settings require repository-admin access.",
    "Green GitHub Actions status must be verified on GitHub after push.",
    "Human owner, legal/privacy, security, curriculum, and release approvals cannot be supplied by an agent.",
    "Psychometric/curriculum review of diagnostics and item bias requires educator/human review.",
    "Bayesian Knowledge Tracing and Deep Knowledge Tracing require sufficient post-launch usage data.",
]

TRACKED_GAPS = [
    "Live item-bank launch volume must be confirmed against approved seed data before production rollout.",
    "Educator sign-off and bias review remain human governance evidence outside static repo checks.",
]


def main() -> int:
    missing = [item for item in REQUIRED_EVIDENCE if not (ROOT / item).exists()]
    print("Domain 07: Diagnostics & Assessment")
    print(f"Repo evidence checked: {len(REQUIRED_EVIDENCE)} item(s)")
    if missing:
        print("Missing repo evidence:")
        for item in missing:
            print(f"- {item}")
        return 1
    print("Repo-side evidence files are present.")
    if TRACKED_GAPS:
        print("Tracked repo gaps from roadmap scope:")
        for item in TRACKED_GAPS:
            print(f"- {item}")
    if EXTERNAL_GATES:
        print("External/human gates remain outside repository verification:")
        for item in EXTERNAL_GATES:
            print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
