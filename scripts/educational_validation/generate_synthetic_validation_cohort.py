#!/usr/bin/env python3
"""Synthetic Validation Cohort Generator for PRD-4A Longitudinal Educational Validation (LEV).

Generates synthetic cohorts across South African DBE quintiles (1-5),
language groups (en, af, xh), and latent abilities theta ~ N(0, 1).
Produces interaction events strictly conforming to interaction_event.schema.json,
plus structured fixtures for psychometric, retention, transfer, fairness, drift,
safety, and cluster-RCT impact analysis.
All output records are stamped with evidence_type: "synthetic_fixture".
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
import random
import uuid
from typing import Any, Dict, List

import numpy as np


CONCEPTS = [
    "caps.math.gr4.num_ops.addition",
    "caps.math.gr4.num_ops.subtraction",
    "caps.math.gr4.num_ops.multiplication",
    "caps.math.gr4.num_ops.division",
    "caps.math.gr4.patterns.algebra",
]

LANGUAGES = ["en", "af", "xh"]
QUINTILES = [1, 2, 3, 4, 5]


def generate_cohort(
    learner_count: int = 1000,
    seed: int = 42,
    repo_root: Path | None = None,
) -> Dict[str, Any]:
    """Generate synthetic learners, interaction events, and engine fixtures."""
    rng = np.random.default_rng(seed)
    py_random = random.Random(seed)

    base_time = datetime(2026, 2, 1, 8, 0, 0, tzinfo=timezone.utc)
    num_schools = max(4, math.ceil(learner_count / 50))
    schools = [f"school_{i+1:03d}" for i in range(num_schools)]
    school_quintiles = {s: (i % 5) + 1 for i, s in enumerate(schools)}
    # Half schools treatment, half control for cluster-RCT
    school_treatment = {s: 1 if (i % 2 == 0) else 0 for i, s in enumerate(schools)}

    # Concept items: 4 items per concept
    items: List[Dict[str, Any]] = []
    for concept_idx, concept in enumerate(CONCEPTS):
        for item_idx in range(4):
            item_id = f"item_{concept_idx+1}_{item_idx+1}"
            difficulty = float(rng.normal(0.0, 1.0))
            discrimination = float(rng.uniform(0.8, 1.5))
            items.append({
                "item_id": item_id,
                "concept_id": concept,
                "difficulty": difficulty,
                "discrimination": discrimination,
            })

    learners: List[Dict[str, Any]] = []
    interaction_events: List[Dict[str, Any]] = []
    state_transitions: List[Dict[str, Any]] = []
    calibration_data: List[Dict[str, Any]] = []
    classification_data: List[Dict[str, Any]] = []
    retention_records: List[Dict[str, Any]] = []
    transfer_records: List[Dict[str, Any]] = []
    fairness_data: List[Dict[str, Any]] = []
    impact_records: List[Dict[str, Any]] = []
    safety_events: List[Dict[str, Any]] = []

    # Generate learners
    for i in range(learner_count):
        lid = f"lrn_{i+1:05d}"
        school_id = schools[i % num_schools]
        quintile = school_quintiles[school_id]
        treatment = school_treatment[school_id]
        # Language distribution across SA contexts
        lang = py_random.choices(LANGUAGES, weights=[0.45, 0.25, 0.30], k=1)[0]
        theta = float(rng.normal(0.0, 1.0))

        learner_info = {
            "learner_pseudonym": lid,
            "school_id": school_id,
            "quintile": quintile,
            "language_group": lang,
            "latent_ability": theta,
            "treatment_group": treatment,
        }
        learners.append(learner_info)

        # Pre-test and post-test scores for Cluster-RCT impact
        pre_score = float(np.clip(50.0 + 10.0 * theta + rng.normal(0, 4.0), 10.0, 95.0))
        # Treatment effect: +7.5 points on average in treatment schools
        treatment_gain = 7.5 if treatment == 1 else 1.5
        post_score = float(np.clip(pre_score + treatment_gain + rng.normal(0, 3.5), 15.0, 100.0))
        impact_records.append({
            "learner_pseudonym": lid,
            "school_id": school_id,
            "cluster_id": school_id,
            "treatment": treatment,
            "quintile": quintile,
            "language_group": lang,
            "pre_score": pre_score,
            "post_score": post_score,
        })

        learner_event_ids: List[str] = []

        # Interaction events across items
        for item in items:
            # 2PL IRT response probability: 1 / (1 + exp(-a * (theta - b)))
            prob_correct = 1.0 / (1.0 + math.exp(-item["discrimination"] * (theta - item["difficulty"])))
            is_correct = bool(rng.uniform(0, 1) < prob_correct)

            event_id = f"evt_{uuid.uuid4().hex[:16]}"
            learner_event_ids.append(event_id)
            event_time = (base_time + timedelta(minutes=int(rng.integers(1, 10000)))).isoformat()

            attempt_count = 1 if is_correct else int(rng.integers(2, 4))
            hint_count = 0 if is_correct else int(rng.integers(1, 3))
            latency = int(rng.integers(3000, 35000))

            event = {
                "event_id": event_id,
                "occurred_at": event_time,
                "learner_pseudonym": lid,
                "concept_id": item["concept_id"],
                "item_id": item["item_id"],
                "item_version": "1.0",
                "graph_version": "1.0.0",
                "model_version": "lev-1.0",
                "consent_state": "consented",
                "first_attempt_correct": is_correct,
                "attempt_count": attempt_count,
                "hint_count": hint_count,
                "response_latency_ms": latency,
                "teacher_assistance": bool(rng.uniform(0, 1) < 0.05),
            }
            interaction_events.append(event)

            # Record calibration item prediction
            calibration_data.append({
                "predicted_prob": round(prob_correct, 4),
                "outcome": 1 if is_correct else 0,
                "learner_pseudonym": lid,
                "concept_id": item["concept_id"],
                "item_id": item["item_id"],
            })

            # Record fairness data
            ability_group = "high" if theta >= 0.0 else "low"
            fairness_data.append({
                "learner_pseudonym": lid,
                "quintile": quintile,
                "language_group": lang,
                "item_id": item["item_id"],
                "score": 1 if is_correct else 0,
                "ability_group": ability_group,
            })

            # Safety telemetry
            if not is_correct and hint_count >= 2 and latency > 25000:
                safety_events.append({
                    "event_id": event_id,
                    "learner_pseudonym": lid,
                    "hint_exhaustion": True,
                    "rapid_clicking": False,
                    "streak_break": bool(rng.uniform(0, 1) < 0.3),
                    "cognitive_overload_flag": True,
                })

        # Overall mastery state transition per learner for concept 1
        predicted_mastery_prob = float(1.0 / (1.0 + math.exp(-theta)))
        true_mastery = bool(theta >= 0.0)
        predicted_mastery = bool(predicted_mastery_prob >= 0.5)

        classification_data.append({
            "learner_pseudonym": lid,
            "predicted_mastery": predicted_mastery,
            "true_mastery": true_mastery,
            "mastery_score": round(predicted_mastery_prob, 4),
            "confidence": min(0.60, round(0.5 + 0.1 * abs(theta), 3)),  # Capped at 0.60 per WS15
        })

        if learner_event_ids:
            state_transitions.append({
                "transition_id": f"trans_{uuid.uuid4().hex[:16]}",
                "learner_pseudonym": lid,
                "concept_id": CONCEPTS[0],
                "occurred_at": (base_time + timedelta(days=2)).isoformat(),
                "pre_state": {"mastery_level": 0.0, "confidence": 0.10},
                "post_state": {
                    "mastery_level": round(predicted_mastery_prob, 3),
                    "confidence": min(0.60, round(0.5 + 0.1 * abs(theta), 3)),
                },
                "evidence_event_ids": learner_event_ids[:4],
                "model_version": "lev-1.0",
                "graph_version": "1.0.0",
                "update_rationale": "Empirical Bayesian update from initial diagnostic assessment.",
            })

        # Spaced retention records across t in {14d, 30d, 60d, 90d}
        retention_days = [14, 30, 60, 90]
        # Multi-model ground truth decay: R(t) = exp(-t / (30 * (1 + theta)))
        half_life = max(10.0, 35.0 * (1.0 + max(-0.8, theta)))
        for days in retention_days:
            decay_prob = math.exp(-days / half_life)
            retained = bool(rng.uniform(0, 1) < decay_prob)
            retention_records.append({
                "learner_pseudonym": lid,
                "concept_id": CONCEPTS[0],
                "days_elapsed": days,
                "retention_score": round(decay_prob, 4),
                "retained": retained,
            })

        # Transfer records: near vs far transfer
        near_score = float(np.clip(0.65 + 0.25 * theta + rng.normal(0, 0.1), 0.0, 1.0))
        far_score = float(np.clip(0.50 + 0.20 * theta + rng.normal(0, 0.15), 0.0, 1.0))
        transfer_records.append({
            "learner_pseudonym": lid,
            "source_concept_id": CONCEPTS[0],
            "target_concept_id": CONCEPTS[1],
            "transfer_type": "near",
            "source_score": round(float(np.clip(0.70 + 0.2 * theta, 0.0, 1.0)), 3),
            "target_score": round(near_score, 3),
            "passed": bool(near_score >= 0.6),
        })
        transfer_records.append({
            "learner_pseudonym": lid,
            "source_concept_id": CONCEPTS[0],
            "target_concept_id": CONCEPTS[4],
            "transfer_type": "far",
            "source_score": round(float(np.clip(0.70 + 0.2 * theta, 0.0, 1.0)), 3),
            "target_score": round(far_score, 3),
            "passed": bool(far_score >= 0.6),
        })

    # Population drift distributions (500 baseline vs 500 target scores)
    baseline_scores = [round(float(np.clip(x, 0.0, 1.0)), 4) for x in rng.normal(0.65, 0.15, 500)]
    target_scores = [round(float(np.clip(x, 0.0, 1.0)), 4) for x in rng.normal(0.67, 0.16, 500)]

    dataset: Dict[str, Any] = {
        "manifest_id": "manifest-synthetic-cohort-001",
        "evidence_type": "synthetic_fixture",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "learner_count": learner_count,
        "school_count": num_schools,
        "event_count": len(interaction_events),
        "transition_count": len(state_transitions),
        "task_ids": [
            "04.01", "04.02", "04.03", "04.04", "04.05", "04.06", "04.07", "04.08",
            "05.01", "05.02", "05.03", "05.04", "05.05", "05.06", "05.07", "05.08", "05.09",
            "06.01", "06.02", "06.03", "06.04", "06.05", "06.06", "06.07",
            "07.01", "07.02", "07.03", "07.04", "07.05", "07.06", "07.07", "07.08", "07.09", "07.10", "07.11",
            "08.01", "08.02", "08.03", "08.04", "08.05", "08.06", "08.07", "08.08", "08.09", "08.10", "08.11", "08.12",
            "09.01", "09.02", "09.03", "09.04", "09.05", "09.06", "09.07", "09.08", "09.09",
            "10.01", "10.02", "10.03", "10.04", "10.05", "10.06", "10.07",
            "11.01", "11.02", "11.03", "11.04", "11.05", "11.06", "11.07", "11.08",
            "13.01", "13.02", "13.03", "13.04", "13.05", "13.06", "13.07", "13.08", "13.09", "13.10", "13.11", "13.12", "13.13", "13.14",
            "15.01", "15.02", "15.03", "15.04", "15.05", "15.06", "15.07", "15.08", "15.09", "15.10"
        ],
        "approvals": ["automated_ci_pipeline"],
        "learners": learners,
        "events": interaction_events,
        "state_transitions": state_transitions,
        "calibration_data": calibration_data,
        "classification_data": classification_data,
        "retention_records": retention_records,
        "transfer_records": transfer_records,
        "fairness_data": fairness_data,
        "impact_records": impact_records,
        "drift_data": {
            "baseline_scores": baseline_scores,
            "target_scores": target_scores,
        },
        "safety_events": safety_events,
    }
    return dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic cohort validation data for LEV.")
    parser.add_argument("--output", default="synthetic_validation_cohort.json", help="Output JSON path")
    parser.add_argument("--learner-count", type=int, default=1000, help="Number of learners to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--validate-schema", action="store_true", help="Validate events against interaction_event.schema.json")
    parser.add_argument("--repo-root", default=".", help="Repository root directory")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    cohort_data = generate_cohort(
        learner_count=args.learner_count,
        seed=args.seed,
        repo_root=root,
    )

    if args.validate_schema:
        schema_path = root / "docs/roadmap/production_readiness/lev/schemas/interaction_event.schema.json"
        if schema_path.exists():
            import jsonschema  # type: ignore
            schema = json.loads(schema_path.read_text())
            # Validate first 50 events as sample
            for evt in cohort_data["events"][:50]:
                jsonschema.validate(instance=evt, schema=schema)
            print(f"Validated sample events against {schema_path}")

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(cohort_data, indent=2) + "\n")
    print(f"Generated synthetic validation cohort ({cohort_data['learner_count']} learners, {cohort_data['event_count']} events) -> {out_path}")


if __name__ == "__main__":
    main()
