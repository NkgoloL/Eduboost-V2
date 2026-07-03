---
title: "RR-013 Candidate Model Comparison"
status: active
owner: research
reviewers: [research, learning-science, privacy]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-07-03
review_interval_days: 60
evidence_command: "PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_rr013_advanced_mastery_model_research.py --json"
code_anchors: [docs/research/mastery_model, scripts/mastery_research]
---

# RR-013 Candidate Model Comparison

Model candidates compared: true
Baseline mastery formula included: true
Bayesian Knowledge Tracing evaluated: true
Deep Knowledge Tracing evaluated: true
Production deployment recommendation recorded: false

## Comparison summary

- Baseline mastery formula: strongest interpretability and easiest to preserve as the reference model.
- Bayesian Knowledge Tracing: useful for structured latent-skill inference, but still needs CAPS and fairness review.
- Performance Factors Analysis: helpful as a comparator, mainly because it remains transparent and lightweight.
- Deep Knowledge Tracing: potentially expressive, but harder to explain and more sensitive to data quality.
- Knowledge-tracing transformer: a research comparator only; not a deployment recommendation here.

## Decision boundary

The comparison is for research and offline evaluation only.
Learner-facing model deployment authorised: false.
Runtime KG implementation claimed: false.
